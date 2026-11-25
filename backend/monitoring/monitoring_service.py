
import time

from backend.monitoring.device_monitor import monitor_devices
from backend.monitoring.report import display_report
from backend.storage.history import initialize_database, save_results


def start_monitoring(devices, interval=10):

    initialize_database()

    print("NETPULSE CONTINUOUS MONITORING STARTED")
    print("Database connection initialized.")
    print(f"Checking every {interval} seconds")
    print("Press CTRL + C to stop.\n")

    try:
        while True:

            results = monitor_devices(devices)

            save_results(results)

            display_report(results)

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nNetPulse monitoring stopped.")
