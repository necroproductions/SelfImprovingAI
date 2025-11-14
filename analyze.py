# analyze.py: Analyze performance
import time

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
        print(f"Analysis error: {e}")
        return {"avg_time": float('inf'), "avg_acc": 0}

# Example tests for process_query
tests = [("hello", "Hello! How can I help?"), ("sort 3 1 2", [1, 2, 3])]
print(analyze_performance(process_query, tests))