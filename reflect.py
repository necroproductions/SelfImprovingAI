# reflect.py: Incremental meta-reflection with patching
import json
import os
from core import process_query
from modify import self_modify
from analyze import analyze_performance
from logger import log_change

PHASE_FILE = 'phase.json'
PHASES = [
    "Phase 1: Patch to optimize existing functions for efficiency (e.g., better algorithms).",
    "Phase 2: Patch to add simple new functions (e.g., basic math or string ops).",
    "Phase 3: Patch to introduce state and memory for query history.",
    "Phase 4: Patch to enable multi-turn conversational handling.",
    "Phase 5: Patch to implement a self-contained code generator (e.g., template-based) to replace external LLM."
]

def get_current_phase():
    """Load or initialize phase."""
    try:
        if os.path.exists(PHASE_FILE):
            with open(PHASE_FILE, 'r') as f:
                return json.load(f).get('phase', 0)
        return 0
    except Exception as e:
        log_change("Phase load error", str(e))
        return 0

def advance_phase():
    """Move to next phase after success."""
    phase = get_current_phase() + 1
    if phase < len(PHASES):
        with open(PHASE_FILE, 'w') as f:
            json.dump({'phase': phase}, f)
        log_change("Advanced to phase", PHASES[phase])

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
        self_idea = process_query(f"Suggest one small patch idea for {PHASES[phase]}")
        if isinstance(self_idea, str) and self_idea:
            base_queries.append(self_idea)
        return base_queries
    except Exception as e:
        log_change("Query generation error", str(e))
        return []

def reflect_and_expand(test_cases):
    """Reflect phase-by-phase with patches."""
    try:
        phase = get_current_phase()
        queries = generate_improvement_queries(phase)
        for q in queries:
            eval_prompt = f"Is this small, safe patch incremental? {q}"
            eval_response = process_query(eval_prompt)
            if "yes" in str(eval_response).lower():
                approve = input(f"Approve patch for '{q}'? (y/n): ")
                if approve.lower() == 'y':
                    self_modify(q, test_cases=test_cases, max_diff_lines=30)
                    log_change("Incremental patch via reflection", q)
                    advance_phase()
    except Exception as e:
        log_change("Reflection error", str(e))

# Example (comment out for production)
if __name__ == "__main__":
    tests = [("hello", "Hello! How can I help?"), ("sort 3 1 2", [1, 2, 3])]
    reflect_and_expand(tests)