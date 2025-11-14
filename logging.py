# logger.py: Enhanced logging (full file)
import datetime
import os

def log_change(message, details=None, prompt=None, generated=None):
    """Log to file with optional details, LLM prompt, and generated output."""
    try:
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"{timestamp}: {message}"
        if details:
            log_entry += f"\nDetails: {details}"
        if prompt:
            log_entry += f"\nLLM Prompt: {prompt}"
        if generated:
            log_entry += f"\nGenerated: {generated}"
        with open('changes.log', 'a') as f:
            f.write(log_entry + "\n\n")
    except IOError as e:
        print(f"Logging error: {e}")
    except Exception as e:
        print(f"Unexpected logging error: {e}")

# Example usage
log_change("Test log", details="Detail here", prompt="Test prompt", generated="Test code")