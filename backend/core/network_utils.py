import subprocess
import re

def ping_device(ip_address):

    result = subprocess.run(
        ["ping", "-c", "4", "-W", "2", ip_address],
        capture_output=True,
        text=True
    )

    output = result.stdout

    packet_match = re.search(
        r"(\d+) packets transmitted, (\d+) received",
        output
    )

    latency_match = re.search(
        r"= ([\d.]+)/([\d.]+)/([\d.]+)",
        output
    )

    if packet_match:
        sent = int(packet_match.group(1))
        received = int(packet_match.group(2))
    else:
        sent = 4
        received = 0

    packet_loss = ((sent - received) / sent) * 100

    latency = (
        float(latency_match.group(2))
        if latency_match else None
    )

    return {
        "ip": ip_address,
        "status": "ONLINE" if received > 0 else "NO_RESPONSE",
        "latency_ms": latency,
        "packet_loss": packet_loss
    }