import subprocess

import pytest

from backend.snmp.snmp_client import get_snmp_value


MAX_OID_SUBIDENTIFIER = "4294967295"
TOO_MANY_SUBIDENTIFIERS_OID = ".".join(["1", "3"] + ["0"] * 127)
TOO_LARGE_SUBIDENTIFIER_OID = "1.3.6.1.4.1.4294967296"


@pytest.fixture
def block_subprocess(monkeypatch):
    def fail_if_called(*args, **kwargs):
        pytest.fail("subprocess.run must not be called for invalid input")

    monkeypatch.setattr(
        "backend.snmp.snmp_client.subprocess.run",
        fail_if_called
    )


def test_get_snmp_value_success(monkeypatch):
    def fake_run(command, **kwargs):
        assert command == [
            "snmpget",
            "-v2c",
            "-c", "public",
            "-Oqv",
            "-t", "5",
            "-r", "1",
            "localhost",
            "1.3.6.1.2.1.1.5.0",
        ]
        assert kwargs == {
            "capture_output": True,
            "text": True,
            "timeout": 8,
        }

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout='"harshith"\n',
            stderr=""
        )

    monkeypatch.setattr(
        "backend.snmp.snmp_client.subprocess.run",
        fake_run
    )

    value = get_snmp_value(
        "localhost",
        "1.3.6.1.2.1.1.5.0"
    )

    assert value == "harshith"


def test_get_snmp_value_timeout(monkeypatch):
    def fake_run(command, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=command,
            timeout=kwargs["timeout"]
        )

    monkeypatch.setattr(
        "backend.snmp.snmp_client.subprocess.run",
        fake_run
    )

    with pytest.raises(RuntimeError, match="SNMP request timed out"):
        get_snmp_value("localhost", "1.3.6.1.2.1.1.5.0")


def test_get_snmp_value_missing_executable(monkeypatch):
    def fake_run(command, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(
        "backend.snmp.snmp_client.subprocess.run",
        fake_run
    )

    with pytest.raises(RuntimeError, match="snmpget is not installed"):
        get_snmp_value("localhost", "1.3.6.1.2.1.1.5.0")


def test_get_snmp_value_command_failure(monkeypatch):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(
            args=command,
            returncode=1,
            stdout="",
            stderr="No response from localhost"
        )

    monkeypatch.setattr(
        "backend.snmp.snmp_client.subprocess.run",
        fake_run
    )

    with pytest.raises(RuntimeError, match="No response from localhost"):
        get_snmp_value("localhost", "1.3.6.1.2.1.1.5.0")


@pytest.mark.parametrize(
    "target",
    [
        "192.0.2.10",
        "2001:db8::10",
        "router.example.com",
    ],
)
def test_valid_target_reaches_subprocess(monkeypatch, target):
    def fake_run(command, **kwargs):
        assert command[-2] == target
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="reachable\n",
            stderr=""
        )

    monkeypatch.setattr(
        "backend.snmp.snmp_client.subprocess.run",
        fake_run
    )

    value = get_snmp_value(target, "1.3.6.1.2.1.1.5.0")

    assert value == "reachable"


def test_oid_at_snmp_limits_reaches_subprocess(monkeypatch):
    oid = ".".join(
        ["2", MAX_OID_SUBIDENTIFIER]
        + [MAX_OID_SUBIDENTIFIER] * 126
    )
    assert len(oid.split(".")) == 128

    def fake_run(command, **kwargs):
        assert command[-1] == oid
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="accepted\n",
            stderr=""
        )

    monkeypatch.setattr(
        "backend.snmp.snmp_client.subprocess.run",
        fake_run
    )

    value = get_snmp_value("localhost", oid)

    assert value == "accepted"


@pytest.mark.parametrize(
    "target",
    [
        None,
        "",
        " localhost",
        "bad host",
        "-option",
        "bad/host",
        "[::1]",
    ],
)
def test_invalid_target_rejected_before_subprocess(
    block_subprocess,
    target
):
    with pytest.raises(ValueError, match="SNMP target"):
        get_snmp_value(target, "1.3.6.1.2.1.1.5.0")


@pytest.mark.parametrize(
    "oid",
    [
        None,
        "",
        "not-an-oid",
        "1",
        "3.1",
        "1.40.1",
        "1.03.6",
        "1..3",
        TOO_MANY_SUBIDENTIFIERS_OID,
        TOO_LARGE_SUBIDENTIFIER_OID,
    ],
)
def test_invalid_oid_rejected_before_subprocess(
    block_subprocess,
    oid
):
    with pytest.raises(ValueError, match="numeric SNMP OID"):
        get_snmp_value("localhost", oid)


@pytest.mark.parametrize(
    "community",
    [
        None,
        "",
        123,
        "two words",
        "line\nbreak",
        "null\x00byte",
    ],
)
def test_invalid_community_rejected_before_subprocess(
    block_subprocess,
    community
):
    with pytest.raises(ValueError, match="SNMP community"):
        get_snmp_value(
            "localhost",
            "1.3.6.1.2.1.1.5.0",
            community=community
        )


@pytest.mark.parametrize(
    "timeout",
    [
        0,
        -1,
        True,
        "5",
        float("nan"),
        float("inf"),
    ],
)
def test_invalid_timeout_rejected_before_subprocess(
    block_subprocess,
    timeout
):
    with pytest.raises(ValueError, match="SNMP timeout"):
        get_snmp_value(
            "localhost",
            "1.3.6.1.2.1.1.5.0",
            timeout=timeout
        )
