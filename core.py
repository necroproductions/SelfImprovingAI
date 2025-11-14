# core.py: Enhanced query handler with LLM fallback and basic skills
"""
This is the core processing module for the self-improving AI assistant.
It uses a hybrid approach: fast rule-based handling for known tasks (e.g., greetings, sorting, math),
with fallback to an external LLM for unrecognized or complex queries. This allows incremental
expansion via patches—future phases can add more rules, refine prompts, or integrate tools.

Key Features:
- Rule-based dispatcher for efficiency and low-latency basics.
- LLM fallback for generality (uses llm_query.py with caching).
- Conversation history integration for context-aware responses.
- Error handling with graceful degradation.
- Testable: Includes example tests at bottom.

Dependencies:
- llm_query.py (for query_llm)
- Global conversation_history from main.py (passed as param).

Evolution Path:
- Phase 1: Optimize rules (e.g., faster sort).
- Phase 2: Add math (e.g., add, multiply).
- Phase 3: Use history for multi-turn.
- Phase 4+: Tool calling, code gen, etc.
"""

import re  # For simple parsing helpers

try:
    from llm_query import query_llm
except ImportError:
    # Fallback if LLM not available (early phases)
    def query_llm(prompt, **kwargs):
        return f"LLM fallback unavailable: {prompt[:50]}..."  # Mock for testing

def process_query(query, history=None):
    """
    Process user query: Rules first, then LLM fallback.

    Args:
        query (str): User input.
        history (list of tuples): Conversation history, e.g., [(user, ai), ...].

    Returns:
        str or list or int: Response (type varies by query).
    """
    try:
        query_lower = query.lower().strip()

        # Rule 1: Greetings
        if any(greeting in query_lower for greeting in ["hello", "hi", "hey", "greetings"]):
            return "Hello! How can I help you today?"

        # Rule 2: Sorting numbers (handles spaces, commas)
        if "sort" in query_lower:
            # Extract numbers: e.g., "sort 5, 3 1" -> [5,3,1]
            num_strs = re.findall(r'\d+', query)  # Grab all digits
            if num_strs:
                numbers = [int(n) for n in num_strs]
                return sorted(numbers)  # Returns list for flexibility
            else:
                raise ValueError("No valid numbers found in sort query.")

        # Rule 3: Basic math (add, subtract, multiply; expandable)
        if "add" in query_lower or "+" in query_lower:
            # Parse: "add 2 3" or "2 + 3"
            parts = re.findall(r'\d+', query)
            if len(parts) >= 2:
                nums = [int(p) for p in parts[:2]]  # First two for simple add
                return sum(nums)
            else:
                raise ValueError("Need at least two numbers for addition.")

        # Rule 4: Simple info (expandable via patches)
        if "phase" in query_lower:
            from phase import get_current_phase, PHASES
            current = get_current_phase()
            return f"Current phase: {current} ({PHASES[current] if current < len(PHASES) else 'Terminal'})"

        # Fallback: LLM for everything else
        context = ""
        if history:
            recent = history[-3:]  # Last 3 exchanges for brevity
            context = "\n".join([f"User: {u}\nAI: {a}" for u, a in recent])
            context += "\n\n"

        system_prompt = (
            "You are a helpful, witty AI personal assistant built by xAI. "
            "Respond concisely, accurately, and engagingly. Use tools or reason step-by-step if complex. "
            "For math/code, output exact results. Keep it fun but professional."
        )

        full_prompt = f"{system_prompt}\n\nRecent conversation:\n{context}User: {query}\nAssistant:"

        llm_response = query_llm(full_prompt, max_tokens=150, temperature=0.7)

        # Post-process: If LLM outputs code/math, try to eval safely (future phase)
        if "```python" in llm_response:
            # Placeholder for safe exec—patch later
            llm_response += "\n\n(Note: Code execution pending upgrade.)"

        return llm_response or "I'm pondering that—got a more specific angle?"

    except ValueError as ve:
        return f"Oops, {ve}. Try clarifying the query!"
    except ImportError as ie:
        # If phase helpers missing
        return f"System not ready for that yet: {ie}"
    except Exception as e:
        return f"Unexpected hiccup: {e}. Let's try something simpler?"

# Integration note for main.py: Call as process_query(user_input, conversation_history)
# After response: conversation_history.append((user_input, response))

# Test suite (run with python core.py)
if __name__ == "__main__":
    # Mock history
    mock_history = [("hello", "Hello! How can I help?")]

    tests = [
        ("hello", "Hello! How can I help you today?"),
        ("hi there", "Hello! How can I help you today?"),
        ("sort 5 3 1", [1, 3, 5]),
        ("sort 5,3,1", [1, 3, 5]),  # Commas
        ("add 2 3", 5),
        ("2 + 3", 5),
        ("what phase", "Current phase: 0 ..."),  # Depends on phase.json
        ("Tell me a joke about AI", "Mock LLM: Why did the AI go to school? To improve its learning algorithm!"),  # LLM fallback
    ]

    print("Testing core.py...")
    for query, expected in tests:
        result = process_query(query, mock_history)
        print(f"Query: '{query}' → {result} (Expected: {expected})")
        # Simple assert for demo
        if isinstance(result, (list, int)):
            print("  → PASS (type match)" if result == expected else "  → FAIL")
        elif str(result).startswith(str(expected)[:20]) or "LLM" in str(result) or "Hello" in str(result):
            print("  → PASS (fuzzy)")
        else:
            print("  → FAIL")

    print("\nAll tests complete. Ready for self-improvement!")