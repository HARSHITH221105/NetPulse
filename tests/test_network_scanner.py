
import subprocess

from backend.discovery.network_scanner import discover_devices


SAMPLE_XML = """<?xml version="1.0"?>
<nmaprun>
    <host>
        <status state="up" reason="echo-reply"/>
        <address addr="192.168.0.1" addrtype="ipv4"/>
        <hostnames>
            <hostname name="gateway.local" type="PTR"/>
        </hostnames>
    </host>

    <host>
        <status state="up" reason="syn-ack"/>
        <address addr="192.168.0.100" addrtype="ipv4"/>
        <hostnames></hostnames>
    </host>

    <host>
        <status state="down" reason="no-response"/>
        <address addr="192.168.0.105" addrtype="ipv4"/>
        <hostnames></hostnames>
    </host>
</nmaprun>
"""


def test_discover_devices(monkeypatch):

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=SAMPLE_XML,
            stderr=""
        )

    monkeypatch.setattr(
        "backend.discovery.network_scanner.subprocess.run",
        fake_run
    )

    devices = discover_devices("192.168.0.0/24")

    assert len(devices) == 2

    assert devices[0]["ip"] == "192.168.0.1"
    assert devices[0]["status"] == "UP"
    assert devices[0]["hostname"] == "gateway.local"

    assert devices[1]["ip"] == "192.168.0.100"
    assert devices[1]["status"] == "UP"
    assert devices[1]["hostname"] is None


def test_empty_discovery_results(monkeypatch):

    empty_xml = '<?xml version="1.0"?><nmaprun></nmaprun>'

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=empty_xml,
            stderr=""
        )

    monkeypatch.setattr(
        "backend.discovery.network_scanner.subprocess.run",
        fake_run
    )

    devices = discover_devices("192.168.0.0/24")

    assert devices == []


def test_nmap_failure(monkeypatch):

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args,
            returncode=1,
            stdout="",
            stderr="Nmap execution failed"
        )

    monkeypatch.setattr(
        "backend.discovery.network_scanner.subprocess.run",
        fake_run
    )

    devices = discover_devices("192.168.0.0/24")

    assert devices == []


def test_invalid_network():

    devices = discover_devices("invalid-network")

    assert devices == []


def test_public_network_rejected():

    devices = discover_devices("8.8.8.0/24")

    assert devices == []

