# monitor.py: Quiet resource monitoring with web-alert queue
import psutil
import time
from logger import log_change

alert_queue = []  # Global queue for web to poll

def monitor_resources(max_cpu=95, max_mem=28000, quiet=True):
    """Monitor system resources. Alerts queued for web display."""
    global alert_queue
    try:
        while True:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().used / (1024 ** 2)
            if not quiet:
                print(f"Current - CPU: {cpu:.1f}%, Memory: {mem:.0f} MB")  # Legacy
            if cpu > max_cpu or mem > max_mem:
                alert = f"⚠️ Resource limit exceeded! CPU: {cpu:.1f}% (max: {max_cpu}%), Memory: {mem:.0f} MB (max: {max_mem} MB)"
                alert_queue.append(alert)
                log_change("Resource alert", alert)
                print(alert)  # Fallback console
                raise SystemExit
            time.sleep(1)
    except Exception as e:
        alert_queue.append(f"Monitor error: {e}")
        log_change("Monitor error", str(e))

def get_alerts():
    """Pop alerts for web."""
    global alert_queue
    alerts = alert_queue.copy()
    alert_queue.clear()
    return alerts