from backend.snmp.system_info import SYSTEM_OIDS, get_system_info


def test_get_system_info_returns_standard_values(monkeypatch):
    values_by_oid = {
        SYSTEM_OIDS["system_description"]: "Linux test-host",
        SYSTEM_OIDS["system_object_id"]: "1.3.6.1.4.1.8072.3.2.10",
        SYSTEM_OIDS["system_uptime"]: "Timeticks: (12345) 0:02:03.45",
        SYSTEM_OIDS["system_name"]: "test-host",
    }
    calls = []

    def fake_get_snmp_value(target, oid, community, timeout):
        calls.append((target, oid, community, timeout))
        return values_by_oid[oid]

    monkeypatch.setattr(
        "backend.snmp.system_info.get_snmp_value",
        fake_get_snmp_value
    )

    info = get_system_info(
        "localhost",
        community="local-test",
        timeout=2
    )

    assert info == {
        "system_description": "Linux test-host",
        "system_object_id": "1.3.6.1.4.1.8072.3.2.10",
        "system_uptime": "Timeticks: (12345) 0:02:03.45",
        "system_name": "test-host",
    }
    assert calls == [
        ("localhost", oid, "local-test", 2)
        for oid in SYSTEM_OIDS.values()
    ]
