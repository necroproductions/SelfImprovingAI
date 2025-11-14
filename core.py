# core.py: Basic query handler
def process_query(query):
    """Simple rule-based response to user queries."""
    try:
        if "hello" in query.lower():
            return "Hello! How can I help?"
        elif "sort" in query.lower():
            # Basic sorting example as nod to initial idea
            numbers = [int(x) for x in query.split()[1:]]  # e.g., "sort 3 1 2"
            return sorted(numbers)
        else:
            return "I don't understand that yet."
    except ValueError as e:
        return f"Error: {e}. Please provide numbers for sorting."
    except Exception as e:
        return f"Unexpected error: {e}"

# Test
print(process_query("hello"))
print(process_query("sort 5 3 1"))
