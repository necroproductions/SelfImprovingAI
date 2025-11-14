# main.py: Core loop with phases
import threading
import time
import os
from monitor import monitor_resources
from reflect import reflect_and_expand, get_current_phase
from core import process_query
from logger import log_change

conversation_history = []  # Prep for later phases

def main():
    threading.Thread(target=monitor_resources).start()
    query_count = 0
    tests = [
        ("hello", "Hello! How can I help?"),
        ("sort 5 3 1", [1, 3, 5]),
        ("add 2 3", 5)  # For Phase 2+
    ]
    print(f"Current Phase: {get_current_phase()}")
    while True:
        try:
            user_input = input("Enter query (or 'reflect' to self-improve or 'advance' to next phase): ")
            if user_input.lower() == 'reflect':
                reflect_and_expand(tests)
            elif user_input.lower() == 'advance':
                from reflect import advance_phase
                advance_phase()
            else:
                response = process_query(user_input)
                print(response)
                conversation_history.append((user_input, response))
            query_count += 1
            if query_count % 5 == 0:
                reflect_and_expand(tests)
            time.sleep(1)
        except Exception as e:
            log_change("Main loop error", str(e))

if __name__ == "__main__":
    main()