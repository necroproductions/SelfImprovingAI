import psutil
import time
import threading
from collections import deque
from logger import log_change

# A thread-safe queue to hold system alerts
ALERT_QUEUE = deque(maxlen=20)

def get_alerts():
    """Retrieves all current alerts from the queue and clears it."""
    alerts = list(ALERT_QUEUE)
    ALERT_QUEUE.clear()
    return alerts

def monitor_resources(max_cpu=95, max_mem=28000, quiet=False):  # max_cpu in %, max_mem in MB
    """Monitor system resources to prevent exhaustion, adding alerts to the queue."""
    log_change("Starting resource monitor...")
    try:
        while True:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().used / (1024 ** 2)  # Convert to MB

            if not quiet:
                print(f"Current - CPU: {cpu:.1f}%, Memory: {mem:.0f} MB")

            if cpu > max_cpu:
                alert = f"Resource limit exceeded: CPU at {cpu:.1f}% (max: {max_cpu}%)"
                ALERT_QUEUE.append(alert)
                log_change("RESOURCE ALERT", alert)

            if mem > max_mem:
                alert = f"Resource limit exceeded: Memory at {mem:.0f} MB (max: {max_mem} MB)"
                ALERT_QUEUE.append(alert)
                log_change("RESOURCE ALERT", alert)

            time.sleep(1)
    except Exception as e:
        log_change("Error in monitoring thread", str(e))
        if not quiet:
            print(f"Error in monitoring: {e}")

# Start the monitoring thread if run directly (useful for testing)
if __name__ == "__main__":
    threading.Thread(target=monitor_resources, daemon=True).start()
    print("Sandbox monitoring active. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
            alerts = get_alerts()
            if alerts:
                for alert in alerts:
                    print(f"[ALERT]: {alert}")
    except KeyboardInterrupt:
        print("Monitoring stopped.")

