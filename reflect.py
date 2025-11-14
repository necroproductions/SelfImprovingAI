# reflect.py: Incremental meta-reflection with patching
import os
from core import process_query
from modify import self_modify
from analyze import analyze_performance
from logger import log_change
from phase import get_current_phase, advance_phase, PHASES

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
        
        # Check if reached terminal phase
        if phase >= len(PHASES):
            log_change("System reached terminal phase", "All self-improvement phases complete")
            print("🎉 System has completed all self-improvement phases!")
            return
        
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