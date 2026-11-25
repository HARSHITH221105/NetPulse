def display_report(results):

    print("\n========== NETPULSE MONITORING REPORT ==========\n")

    print(f"{'IP ADDRESS':<20} {'STATUS':<15} {'LATENCY':<15} {'PACKET LOSS'}")

    print("-" * 70)

    for device in results:

        ip = device["ip"]
        status = device["status"]

        latency = (
            f"{device['latency_ms']} ms"
            if device["latency_ms"] is not None
            else "N/A"
        )

        packet_loss = f"{device['packet_loss']}%"

        print(f"{ip:<20} {status:<15} {latency:<15} {packet_loss}")

    print("\n================================================\n")