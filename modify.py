# modify.py: Self-modify with unified diff patching
import os
import subprocess
import difflib
import json
from llm_query import query_llm
from analyze import analyze_performance, detect_fail_state
from logger import log_change
from utils import apply_patch

def get_current_phase():
    """Load current phase from phase.json file."""
    try:
        if os.path.exists('phase.json'):
            with open('phase.json', 'r') as f:
                return json.load(f).get('phase', 0)
        return 0
    except Exception as e:
        log_change("Phase load error", str(e))
        return 0

def ethical_check(diff_str, phase):
    """Check diff for ethical issues."""
    harmful_keywords = ['hack', 'delete', 'malware', 'bias', 'hate', 'unauthorized']
    try:
        if any(kw in diff_str.lower() for kw in harmful_keywords):
            raise ValueError("Ethical violation in diff.")
        if phase < 4 and 'requests' in diff_str.lower():
            raise ValueError("No internet in early phases.")
        return True
    except ValueError as e:
        log_change("Ethical check failed", str(e))
        return False

def self_modify(improvement_query, target_file='core.py', test_cases=None, max_diff_lines=50):
    """Use LLM to generate unified diff patch; apply incrementally."""
    backup_file = target_file + '.backup'
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Pre-modification commit'], check=True)

        with open(target_file, 'r') as f:
            current_code = f.read()
        prompt = f"Generate a SMALL, incremental unified diff patch for this Python code based on: {improvement_query}\nFocus on patching one specific part (e.g., optimize a function). Output ONLY the unified diff format (starting with --- and +++), no explanations.\nCurrent code:\n{current_code}"
        generated_diff = query_llm(prompt, max_tokens=500)
        if not generated_diff or not generated_diff.startswith('---'):
            raise ValueError("Invalid unified diff from LLM.")

        log_change("Generated diff", improvement_query, prompt=prompt, generated=generated_diff)

        diff_lines = generated_diff.splitlines()
        if len(diff_lines) > max_diff_lines:
            raise ValueError("Generated diff too large; rejecting for safety.")

        current_phase = get_current_phase()
        if not ethical_check(generated_diff, current_phase):
            raise ValueError("Ethical fail")

        updated_code = apply_patch(current_code, generated_diff)

        os.system(f'cp {target_file} {backup_file}')

        with open(target_file, 'w') as f:
            f.write(updated_code)

        namespace = {}
        exec(updated_code, namespace)
        updated_func = namespace.get('process_query')
        if not updated_func:
            raise NameError("No process_query in generated code.")

        if test_cases:
            metrics = analyze_performance(updated_func, test_cases)
            if detect_fail_state(metrics, updated_code):
                raise RuntimeError("Fail state detected post-modification.")

        log_change("Patch application successful", improvement_query)
        subprocess.run(['git', 'commit', '-am', 'Successful patch modification'], check=True)

    except Exception as e:
        log_change("Modification failed", str(e))
        os.system(f'mv {backup_file} {target_file}')
        rollback()
        raise

def rollback():
    """Revert to previous commit."""
    try:
        subprocess.run(['git', 'checkout', 'HEAD~1'], check=True)
        log_change("Rolled back")
    except subprocess.CalledProcessError as e:
        log_change("Rollback error", str(e))

# Example (comment out for production)
if __name__ == "__main__":
    tests = [("hello", "Hello! How can I help?"), ("sort 5 3 1", [1, 3, 5])]
    self_modify("Patch the sorting logic in process_query to use a custom quicksort function.", test_cases=tests)