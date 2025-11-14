# reflect.py: Incremental meta-reflection with patching (web-friendly outputs)
import os
import json  # For phase.json
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
        if isinstance(self_idea, str) and self_idea and "don't understand" not in self_idea.lower():
            base_queries.append(self_idea)
        return base_queries
    except Exception as e:
        log_change("Query generation error", str(e))
        return []

def reflect_and_expand(test_cases, auto_approve=False):
    """Reflect phase-by-phase with patches. Returns list of output lines for web rendering."""
    output_lines = []  # Collect for web chat
    try:
        phase = get_current_phase()
        output_lines.append(f"=== Starting reflection for Phase {phase} ===")

        # Check if reached terminal phase
        if phase >= len(PHASES):
            log_change("System reached terminal phase", "All self-improvement phases complete")
            output_lines.append("🎉 System has completed all self-improvement phases!")
            return output_lines

        queries = generate_improvement_queries(phase)
        if not queries:
            output_lines.append("No queries generated—skipping reflection.")
            return output_lines

        output_lines.append(f"Found {len(queries)} queries to evaluate.")
        for q in queries:
            output_lines.append(f"Query: {q}")
            eval_prompt = f"Is this small, safe patch incremental? {q}"
            eval_response = process_query(eval_prompt)
            output_lines.append(f"Eval response: '{eval_response}'")

            # Bypass eval for Phase 0 (early AI can't self-assess yet)
            approved = ("yes" in str(eval_response).lower() or 
                        auto_approve or 
                        phase == 0)
            if approved:
                output_lines.append("Query approved for patching!")
                # For web, simulate approval (or pass callback; here assume auto for demo)
                if auto_approve:
                    approve = 'y'
                else:
                    # In web, this would be handled via session—default 'y' for now
                    approve = input(f"Approve patch for '{q}'? (y/n): ").strip()  # Fallback for console
                if approve.lower() == 'y':
                    output_lines.append("Applying patch...")
                    self_modify(q, test_cases=test_cases, max_diff_lines=30)
                    log_change("Incremental patch via reflection", q)
                    advance_phase()
                    output_lines.append(f"Reflection complete! Advanced to Phase {get_current_phase()}.")
                    output_lines.append("Check changes.log for details and core.py for updates.")
                    return output_lines  # One at a time for safety
                else:
                    output_lines.append("Patch declined by user.")
            else:
                output_lines.append("Query skipped—not approved.")
        output_lines.append("=== Reflection ended (no patches applied) ===")
        return output_lines
    except Exception as e:
        log_change("Reflection error", str(e))
        output_lines.append(f"DEBUG: Reflection error: {e}")
        return output_lines