from backend.monitoring.device_monitor import monitor_devices
from backend.storage.history import (
    initialize_database,
    save_results,
    get_monitoring_history
)


def test_save_monitoring_history():

    initialize_database()

    results = monitor_devices(["127.0.0.1", "1.1.1.1"])

    save_results(results)

    print("\nMonitoring results saved to database!")

    history = get_monitoring_history()

    print("\n========== NETPULSE HISTORY ==========")

    for record in history:
        print(record)