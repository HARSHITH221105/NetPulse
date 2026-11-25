
from backend.monitoring.analytics import get_all_device_analytics


def display_analytics_report():

    devices = get_all_device_analytics()

    print("\n")
    print("=" * 95)
    print("                    NETPULSE DEVICE ANALYTICS DASHBOARD")
    print("=" * 95)

    if not devices:
        print("No monitoring history available.")
        return

    print(
        f"{'IP ADDRESS':<18}"
        f"{'HEALTH':<12}"
        f"{'CHECKS':<10}"
        f"{'SUCCESS':<12}"
        f"{'AVG LATENCY':<15}"
        f"{'PACKET LOSS':<13}"
    )

    print("-" * 95)

    for device in devices:

        latency = (
            f"{device['average_latency']} ms"
            if device["average_latency"] is not None
            else "N/A"
        )

        packet_loss = (
            f"{device['average_packet_loss']}%"
            if device["average_packet_loss"] is not None
            else "N/A"
        )

        success = f"{device['success_percentage']}%"

        print(
            f"{device['ip']:<18}"
            f"{device['health']:<12}"
            f"{device['total_checks']:<10}"
            f"{success:<12}"
            f"{latency:<15}"
            f"{packet_loss:<13}"
        )

    print("-" * 95)
    print(f"Total monitored devices: {len(devices)}")
    print("=" * 95)
    print("\n")
