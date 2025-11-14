import psutil
import time

def monitor_resources(max_cpu=80, max_mem=500):  # max_cpu in %, max_mem in MB
    """Monitor system resources to prevent exhaustion."""
    try:
        while True:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().used / (1024 ** 2)  # Convert to MB
            if cpu > max_cpu or mem > max_mem:
                print("Resource limit exceeded! Shutting down.")
                raise SystemExit  # Simulate shutdown
            time.sleep(1)
    except Exception as e:
        print(f"Error in monitoring: {e}")

# Run in background (simulate with thread if needed)
import threading
threading.Thread(target=monitor_resources).start()

print("Sandbox monitoring active.")
