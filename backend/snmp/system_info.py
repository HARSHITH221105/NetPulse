from backend.snmp.snmp_client import get_snmp_value


SYSTEM_OIDS = {
    "system_description": "1.3.6.1.2.1.1.1.0",
    "system_object_id": "1.3.6.1.2.1.1.2.0",
    "system_uptime": "1.3.6.1.2.1.1.3.0",
    "system_name": "1.3.6.1.2.1.1.5.0",
}


def get_system_info(target, community="public", timeout=5):
    """Retrieve standard SNMP system information from one device."""

    return {
        name: get_snmp_value(
            target,
            oid,
            community=community,
            timeout=timeout
        )
        for name, oid in SYSTEM_OIDS.items()
    }
