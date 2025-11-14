import requests
import os
import json
from logger import log_change

CACHE_FILE = 'llm_cache.json'

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def query_llm(prompt, model="meta-llama/Meta-Llama-3-8B-Instruct", max_tokens=200, temperature=0.7):
    """
    Query Hugging Face API (initially); cache results.
    Accepts temperature for control over response creativity.
    """
    cache = load_cache()
    # Cache key includes temperature to prevent conflicting results for the same prompt
    cache_key = f"{prompt}::{temperature}"

    if cache_key in cache:
        return cache[cache_key]

    api_key = os.environ.get("HF_TOKEN") or os.environ.get("HF_API_KEY")
    if not api_key:
        log_change("No API key; using mock response for testing", prompt)
        # Mock for testing: return a simple diff or response based on prompt
        if "sort" in prompt and temperature < 0.3:
            return '''--- core.py
+++ core.py
@@ -10,7 +10,8 @@ def process_query(query):
             numbers = [int(x) for x in query.split()[1:]]  # e.g., "sort 3 1 2"
-            return sorted(numbers)
+            numbers.sort()  # In-place sort for better efficiency on large lists
+            return numbers
 '''
        return "Mock response: Improvement applied."

    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature # CORRECTED: Pass temperature to payload
    }
    response = None
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        generated = response.json()["choices"][0]["message"]["content"].strip()
        if generated:
            cache[cache_key] = generated
            save_cache(cache)
        return generated
    except requests.exceptions.RequestException as e:
        log_change("LLM query error", str(e))
        if response is not None:
            try:
                error_details = response.json()
                log_change("LLM error details", str(error_details))
            except:
                pass
        return None
    except KeyError:
        log_change("Invalid LLM response")
        return None

