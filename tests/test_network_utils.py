from backend.core.network_utils import ping_device


def test_ping_localhost():

    result = ping_device("127.0.0.1")

    assert result["ip"] == "127.0.0.1"
    assert result["status"] == "ONLINE"
    assert result["packet_loss"] == 0.0

    print("Localhost test passed!")