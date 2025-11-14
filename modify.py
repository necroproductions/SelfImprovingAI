import os
import subprocess
import difflib
from llm_query import query_llm
from analyze import analyze_performance, detect_fail_state
from logger import log_change
from utils import apply_patch
from phase import get_current_phase

# --- Helper to check git config before committing ---
def check_git_config():
    """Checks if git user.email and user.name are configured."""
    try:
        subprocess.run(['git', 'config', 'user.email'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['git', 'config', 'user.name'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        log_change("GIT CONFIG WARNING", "Git user.email or user.name not configured. Skipping commit. Manual configuration required for full logging.")
        return False
# ----------------------------------------------------

def ethical_check(diff_str, phase):
    """Check diff for ethical issues."""
    # Strengthened keyword list
    harmful_keywords = ['hack', 'delete', 'malware', 'bias', 'hate', 'unauthorized', 'shutdown', 'os.remove', 'rm -rf']
    try:
        if any(kw in diff_str.lower() for kw in harmful_keywords):
            raise ValueError("Ethical violation in diff.")
        # Only allow internet access (requests) in later phases (e.g., Phase 4+)
        if phase < 4 and 'requests' in diff_str.lower():
            raise ValueError("No internet/external calls allowed in early phases.")
        return True
    except ValueError as e:
        log_change("Ethical check failed", str(e))
        return False

def self_modify(improvement_query, target_file='core.py', test_cases=None, max_diff_lines=50):
    """Use LLM to generate unified diff patch; apply incrementally."""
    backup_file = target_file + '.backup'
    needs_commit = check_git_config() # Check config once

    try:
        if needs_commit:
            subprocess.run(['git', 'add', '.'], check=True)

            # Only commit if there are changes to commit
            result = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True)
            if result.returncode != 0:  # returncode != 0 means there are changes
                subprocess.run(['git', 'commit', '-m', f'Pre-modification commit - {target_file}'], check=True)

        with open(target_file, 'r') as f:
            current_code = f.read()

        # Added instruction to be small and safe
        prompt = f"Generate a SMALL, SAFE, incremental unified diff patch for this Python code based on: {improvement_query}\nFocus on patching ONE specific function (e.g., optimize a function). Output ONLY the unified diff format (starting with --- and +++), no explanations.\nCurrent code:\n{current_code}"

        # Use a low temperature for deterministic code generation
        generated_diff = query_llm(prompt, max_tokens=500, temperature=0.2) 

        if not generated_diff or not generated_diff.startswith('---'):
            raise ValueError("Invalid unified diff from LLM or LLM failure.")

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

        # --- Test the new code by executing it in an isolated namespace ---
        namespace = {}
        # NOTE: This is the most dangerous line. analyze.py must prevent malicious side-effects.
        exec(updated_code, namespace) 
        updated_func = namespace.get('process_query')
        if not updated_func:
            raise NameError("No process_query in generated code after exec.")

        # --- Run tests ---
        if test_cases:
            metrics = analyze_performance(updated_func, test_cases)
            if detect_fail_state(metrics, updated_code):
                raise RuntimeError("Fail state detected post-modification: failed performance/accuracy tests.")

        # --- Finalize ---
        log_change("Patch application successful", improvement_query)
        if needs_commit:
            subprocess.run(['git', 'commit', '-am', f'Successful patch modification: {improvement_query}'], check=True)
        else:
            log_change("Patch successful but not committed", "Git config missing.")

    except Exception as e:
        log_change("Modification failed", str(e))
        # Restore from backup file first (simpler and safer than git rollback)
        if os.path.exists(backup_file):
            os.system(f'mv {backup_file} {target_file}')
            log_change("Restored from backup file", target_file)
        # Only use git rollback if backup restoration fails AND we committed a pre-modification commit
        elif needs_commit:
            rollback()
        raise

def rollback():
    """Revert to previous commit on current branch."""
    try:
        subprocess.run(['git', 'reset', '--hard', 'HEAD~1'], check=True)
        log_change("Rolled back")
    except subprocess.CalledProcessError as e:
        log_change("Rollback error", str(e))
        raise

