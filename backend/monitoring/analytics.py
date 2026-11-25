
from backend.storage.history import get_monitoring_history


def get_device_analytics(ip_address):

    history = get_monitoring_history()

    device_records = [
        record for record in history
        if record["ip_address"] == ip_address
    ]

    if not device_records:
        return None

    latencies = [
        record["latency_ms"]
        for record in device_records
        if record["latency_ms"] is not None
    ]

    packet_losses = [
        record["packet_loss"]
        for record in device_records
        if record["packet_loss"] is not None
    ]

    total_checks = len(device_records)

    successful_checks = sum(
        1 for record in device_records
        if record["status"] == "ONLINE"
    )

    failed_checks = total_checks - successful_checks

    success_percentage = round(
        (successful_checks / total_checks) * 100, 2
    )

    average_latency = (
        round(sum(latencies) / len(latencies), 2)
        if latencies else None
    )

    average_packet_loss = (
        round(sum(packet_losses) / len(packet_losses), 2)
        if packet_losses else None
    )

    if successful_checks == 0:
        health = "CRITICAL"

    elif (
        average_latency is None
        or average_latency > 200
        or average_packet_loss is None
        or average_packet_loss > 10
    ):
        health = "CRITICAL"

    elif average_latency > 100 or average_packet_loss > 2:
        health = "WARNING"

    else:
        health = "HEALTHY"

    return {
        "ip": ip_address,
        "total_checks": total_checks,
        "successful_checks": successful_checks,
        "failed_checks": failed_checks,
        "success_percentage": success_percentage,
        "average_latency": average_latency,
        "minimum_latency": min(latencies) if latencies else None,
        "maximum_latency": max(latencies) if latencies else None,
        "average_packet_loss": average_packet_loss,
        "health": health
    }


def get_all_device_analytics():

    history = get_monitoring_history()

    device_ips = sorted({
        record["ip_address"] for record in history
    })

    report = []

    for ip in device_ips:

        analytics = get_device_analytics(ip)

        if analytics:
            report.append(analytics)

    return report
