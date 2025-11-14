# phase.py: Shared phase management utilities
import json
import os
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
