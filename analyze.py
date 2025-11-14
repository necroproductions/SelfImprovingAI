# analyze.py: Enhanced performance analysis
import time
import ast  # For syntax checking
from logger import log_change

def analyze_performance(func, test_cases):
    """Run tests and measure time/accuracy."""
    results = []
    try:
        for case, expected in test_cases:
            start = time.time()
            result = func(case)
            end = time.time()
            accuracy = 1 if result == expected else 0
            results.append({"time": end - start, "accuracy": accuracy})
        avg_time = sum(r["time"] for r in results) / len(results)
        avg_acc = sum(r["accuracy"] for r in results) / len(results)
        return {"avg_time": avg_time, "avg_acc": avg_acc}
    except Exception as e:
        log_change("Analysis error", str(e))
        return {"avg_time": float('inf'), "avg_acc": 0}

def detect_fail_state(perf_metrics, generated_code, threshold_acc=0.8, threshold_time=1.0, min_code_len=50):
    """Check performance and code quality."""
    try:
        if perf_metrics['avg_acc'] < threshold_acc or perf_metrics['avg_time'] > threshold_time:
            return True
        if len(generated_code) < min_code_len:
            return True  # Too short, likely failure
        ast.parse(generated_code)  # Syntax check
        return False
    except (KeyError, SyntaxError) as e:
        log_change("Fail state detected", str(e))
        return True

# Example usage (comment out for production)
if __name__ == "__main__":
    from core import process_query
    tests = [("hello", "Hello! How can I help?"), ("sort 3 1 2", [1, 2, 3])]
    metrics = analyze_performance(process_query, tests)
    print(detect_fail_state(metrics, "def func(): pass", min_code_len=10))