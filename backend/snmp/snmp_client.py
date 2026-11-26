import ipaddress
import math
import re
import subprocess
import unicodedata


MAX_OID_SUBIDENTIFIERS = 128
MAX_OID_SUBIDENTIFIER_VALUE = "4294967295"


def _validate_target(target):
    if not isinstance(target, str) or not target or target != target.strip():
        raise ValueError(
            "A valid SNMP target (IP address or hostname) is required."
        )

    try:
        ipaddress.ip_address(target)
        return
    except ValueError:
        pass

    hostname = target[:-1] if target.endswith(".") else target

    if not hostname or len(hostname) > 253:
        raise ValueError(
            "A valid SNMP target (IP address or hostname) is required."
        )

    labels = hostname.split(".")
    for label in labels:
        if (
            len(label) > 63
            or not re.fullmatch(
                r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?",
                label
            )
        ):
            raise ValueError(
                "A valid SNMP target (IP address or hostname) is required."
            )


def _validate_oid(oid):
    if not isinstance(oid, str) or not oid:
        raise ValueError("A valid numeric SNMP OID is required.")

    oid_body = oid[1:] if oid.startswith(".") else oid

    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)+", oid_body):
        raise ValueError("A valid numeric SNMP OID is required.")

    arcs = oid_body.split(".")

    if len(arcs) > MAX_OID_SUBIDENTIFIERS:
        raise ValueError("A valid numeric SNMP OID is required.")

    if any(len(arc) > 1 and arc.startswith("0") for arc in arcs):
        raise ValueError("A valid numeric SNMP OID is required.")

    if any(
        len(arc) > len(MAX_OID_SUBIDENTIFIER_VALUE)
        or (
            len(arc) == len(MAX_OID_SUBIDENTIFIER_VALUE)
            and arc > MAX_OID_SUBIDENTIFIER_VALUE
        )
        for arc in arcs
    ):
        raise ValueError("A valid numeric SNMP OID is required.")

    if arcs[0] not in {"0", "1", "2"}:
        raise ValueError("A valid numeric SNMP OID is required.")

    second_arc = arcs[1]
    if arcs[0] in {"0", "1"}:
        if len(second_arc) > 2 or (
            len(second_arc) == 2 and second_arc > "39"
        ):
            raise ValueError("A valid numeric SNMP OID is required.")


def _validate_community(community):
    if (
        not isinstance(community, str)
        or not community
        or any(
            character.isspace()
            or unicodedata.category(character) == "Cc"
            for character in community
        )
    ):
        raise ValueError(
            "SNMP community must be a non-empty string without "
            "whitespace or control characters."
        )


def _validate_timeout(timeout):
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise ValueError("SNMP timeout must be a positive, finite number.")

    try:
        finite_timeout = math.isfinite(float(timeout))
    except (OverflowError, TypeError, ValueError):
        finite_timeout = False

    if not finite_timeout or timeout <= 0:
        raise ValueError("SNMP timeout must be a positive, finite number.")


def get_snmp_value(
    target,
    oid,
    community="public",
    timeout=5
):
    """Retrieve one SNMP value using Net-SNMP."""

    _validate_target(target)
    _validate_oid(oid)
    _validate_community(community)
    _validate_timeout(timeout)

    command = [
        "snmpget",
        "-v2c",
        "-c", community,
        "-Oqv",
        "-t", str(timeout),
        "-r", "1",
        target,
        oid
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout + 3
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip() or "SNMP request failed."
            )

        value = result.stdout.strip()

        if not value:
            raise RuntimeError("SNMP returned an empty response.")

        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

        return value

    except subprocess.TimeoutExpired:
        raise RuntimeError("SNMP request timed out.")

    except FileNotFoundError:
        raise RuntimeError(
            "snmpget is not installed or not available in PATH."
        )
