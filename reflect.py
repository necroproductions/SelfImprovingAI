import os
import threading
from core import process_query
from logger import log_change
# Removed: from phase import get_current_phase, advance_phase, PHASES
from monitor import get_alerts 
from modify import self_modify # Must import self_modify here to use it in process_patch_decision

# --- New Global State for Web Interaction ---
# Store patch proposals waiting for user approval
PENDING_PATCH = threading.Lock()
PENDING_PATCH_QUERY = None
PENDING_PATCH_TESTS = None
PENDING_PATCH_TARGET = 'core.py'
# -------------------------------------------

# New, high-level continuous goal for the LLM to target
CONTINUOUS_GOAL = "towards a general intelligence system"

def generate_improvement_queries():
    """Query the LLM for a single, incremental improvement idea based on the continuous goal."""
    try:
        # Instruction focuses on continuous, incremental improvement without phase limits
        prompt = f"As a world-class AI developer, propose ONE single, atomic, and incremental improvement to move the current codebase closer to achieving general intelligence. State the improvement concisely as a patch request (e.g., 'Patch to add feature X'). The current high-level goal is: {CONTINUOUS_GOAL}"

        # Call process_query without history to prevent reflection from causing new reflection
        self_idea = process_query(prompt, history=[]) 

        if isinstance(self_idea, str) and self_idea:
            # We return a list containing the single best idea found
            return [self_idea]
        return []
    except Exception as e:
        log_change("Query generation error", str(e))
        return []

def reflect_and_expand(test_cases):
    """Continuously reflect and propose patches towards the abstract goal."""
    global PENDING_PATCH_QUERY, PENDING_PATCH_TESTS, PENDING_PATCH_TARGET
    try:

        # Check if a patch is already pending
        with PENDING_PATCH:
            if PENDING_PATCH_QUERY is not None:
                log_change("Skipping reflection", "Another patch is already pending approval.")
                get_alerts().append("Reflection paused: A patch is already awaiting your approval.")
                return

        queries = generate_improvement_queries()

        if not queries:
            log_change("Reflection finished", "No improvement queries generated.")
            get_alerts().append("Reflection: No viable improvement queries could be generated at this time.")
            return

        q = queries[0]

        # Self-evaluation focuses purely on the atomicity and scope control (as requested by user)
        eval_prompt = f"Is the following patch query a single, atomic, and incremental change? Respond ONLY with the single word 'YES' or 'NO'. Query: '{q}'"

        eval_response = process_query(eval_prompt, history=[])

        if "yes" in str(eval_response).lower():
            log_change("Patch Proposal Generated", f"Query: {q}")

            with PENDING_PATCH:
                PENDING_PATCH_QUERY = q
                PENDING_PATCH_TESTS = test_cases
                PENDING_PATCH_TARGET = 'core.py'
                log_change("Patch Proposal Awaiting Approval", q)
        else:
            log_change("Patch Proposal Rejected by Self-Evaluation", q)
            get_alerts().append(f"Reflection Failed: Self-evaluation rejected the query because it was not considered atomic or incremental: '{q}'.")

    except Exception as e:
        log_change("Reflection error", str(e))
        get_alerts().append(f"Reflection Error: An unexpected error occurred during the process: {e}")

def process_patch_decision(decision):
    """Called by the web API to handle user's patch approval or rejection."""
    global PENDING_PATCH_QUERY, PENDING_PATCH_TESTS, PENDING_PATCH_TARGET

    with PENDING_PATCH:
        if PENDING_PATCH_QUERY is None:
            return "No patch pending."

        q = PENDING_PATCH_QUERY
        tests = PENDING_PATCH_TESTS
        target = PENDING_PATCH_TARGET

        PENDING_PATCH_QUERY = None
        PENDING_PATCH_TESTS = None

        if decision.lower() == 'approve':
            log_change("User Approved Patch", q)
            try:
                # Removed max_diff_lines limit. Scope is controlled by LLM instruction.
                self_modify(q, target_file=target, test_cases=tests) 

                # Removed advance_phase() call. The system just returns to reflection loop.
                return f"Patch applied successfully! The system will now continue its self-improvement cycle."
            except Exception as e:
                # Ensure the exception message is clear
                return f"Patch execution failed. Codebase rolled back. Error: {e}"
        else:
            log_change("User Rejected Patch", q)
            return "Patch proposal rejected by user."

# Example (comment out for production)
if __name__ == "__main__":
    tests = [("hello", "Hello! How can I help?"), ("sort 3 1 2", [1, 2, 3])]
    reflect_and_expand(tests)

