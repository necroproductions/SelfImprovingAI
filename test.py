import psutil
import time

def monitor_resources(max_cpu=95, max_mem=28000):  # max_cpu in %, max_mem in MB
    """Monitor system resources to prevent exhaustion."""
    try:
        while True:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().used / (1024 ** 2)  # Convert to MB
            print(f"Current - CPU: {cpu:.1f}%, Memory: {mem:.0f} MB")
            if cpu > max_cpu or mem > max_mem:
                print(f"⚠️ Resource limit exceeded! CPU: {cpu:.1f}% (max: {max_cpu}%), Memory: {mem:.0f} MB (max: {max_mem} MB)")
                raise SystemExit  # Simulate shutdown
            time.sleep(1)
    except Exception as e:
        print(f"Error in monitoring: {e}")

# Run in background (simulate with thread if needed)
import threading
threading.Thread(target=monitor_resources).start()

print("Sandbox monitoring active.")
