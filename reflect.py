import os
import threading
from core import process_query
from logger import log_change
from phase import get_current_phase, advance_phase, PHASES

# --- New Global State for Web Interaction ---
# Store patch proposals waiting for user approval
PENDING_PATCH = threading.Lock()
PENDING_PATCH_QUERY = None
PENDING_PATCH_TESTS = None
PENDING_PATCH_TARGET = 'core.py'
# -------------------------------------------

def generate_improvement_queries(phase):
    """Generate phase-specific patch queries."""
    try:
        base_queries = {
            0: ["Patch sorting for faster performance on large lists."],
            1: ["Patch to add a simple math addition handler to queries."],
            2: ["Patch to add query history memory to remember last input."],
            3: ["Patch to handle follow-up questions based on history."],
            4: ["Patch to implement a basic template-based code generator to reduce LLM dependency."]
        }.get(phase, [])
        # Call process_query without history to prevent reflection from causing new reflection
        self_idea = process_query(f"Suggest one small patch idea for {PHASES[phase]}", history=[]) 
        if isinstance(self_idea, str) and self_idea:
            base_queries.append(self_idea)
        return base_queries
    except Exception as e:
        log_change("Query generation error", str(e))
        return []

def reflect_and_expand(test_cases):
    """Reflect phase-by-phase without interactive prompts."""
    global PENDING_PATCH_QUERY, PENDING_PATCH_TESTS, PENDING_PATCH_TARGET
    try:
        phase = get_current_phase()

        # Check if reached terminal phase
        if phase >= len(PHASES):
            log_change("System reached terminal phase", "All self-improvement phases complete")
            return

        # Check if a patch is already pending
        with PENDING_PATCH:
            if PENDING_PATCH_QUERY is not None:
                log_change("Skipping reflection", "Another patch is already pending approval.")
                return

        queries = generate_improvement_queries(phase)

        # For simplicity, we only propose the first idea generated
        if not queries:
            log_change("Reflection finished", "No improvement queries generated.")
            return

        q = queries[0]
        eval_prompt = f"Is this small, safe patch incremental? Answer YES or NO. {q}"
        eval_response = process_query(eval_prompt, history=[])

        if "yes" in str(eval_response).lower():
            log_change("Patch Proposal Generated", f"Query: {q}")

            # Save the proposal to the global state for the web app to pick up
            with PENDING_PATCH:
                PENDING_PATCH_QUERY = q
                PENDING_PATCH_TESTS = test_cases
                PENDING_PATCH_TARGET = 'core.py' # Default target
                log_change("Patch Proposal Awaiting Approval", q)
        else:
            log_change("Patch Proposal Rejected by Self-Evaluation", q)

    except Exception as e:
        log_change("Reflection error", str(e))

def process_patch_decision(decision):
    """Called by the web API to handle user's patch approval or rejection."""
    global PENDING_PATCH_QUERY, PENDING_PATCH_TESTS, PENDING_PATCH_TARGET
    from modify import self_modify

    with PENDING_PATCH:
        if PENDING_PATCH_QUERY is None:
            return "No patch pending."

        q = PENDING_PATCH_QUERY
        tests = PENDING_PATCH_TESTS
        target = PENDING_PATCH_TARGET

        # Clear the pending state immediately after retrieving
        PENDING_PATCH_QUERY = None
        PENDING_PATCH_TESTS = None

        if decision.lower() == 'approve':
            log_change("User Approved Patch", q)
            try:
                # Execution happens in the main thread for simplicity, blocking web response briefly
                self_modify(q, target_file=target, test_cases=tests, max_diff_lines=30)
                advance_phase()
                return f"Patch applied successfully! Advanced to Phase {get_current_phase()}"
            except Exception as e:
                return f"Patch failed to apply/test: {e}"
        else:
            log_change("User Rejected Patch", q)
            return "Patch proposal rejected."

# Example (comment out for production)
if __name__ == "__main__":
    tests = [("hello", "Hello! How can I help?"), ("sort 3 1 2", [1, 2, 3])]
    # Now non-interactive in main module loop
    reflect_and_expand(tests)

