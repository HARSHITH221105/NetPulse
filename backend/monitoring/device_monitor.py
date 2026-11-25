from backend.core.network_utils import ping_device


def monitor_devices(devices):
    results = []

    for ip in devices:
        result = ping_device(ip)
        results.append(result)

    return results