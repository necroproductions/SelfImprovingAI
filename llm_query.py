# llm_query.py: LLM query with caching
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

def query_llm(prompt, model="bigcode/starcoder2-3b", max_tokens=200):
    """Query Hugging Face API (initially); cache results."""
    cache = load_cache()
    if prompt in cache:
        return cache[prompt]

    api_key = os.environ.get("HF_API_KEY")
    if not api_key:
        raise ValueError("HF_API_KEY not set.")
    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        generated = response.json()["choices"][0]["message"]["content"].strip()
        if generated:
            cache[prompt] = generated
            save_cache(cache)
        return generated
    except requests.exceptions.RequestException as e:
        log_change("LLM query error", str(e))
        return None
    except KeyError:
        log_change("Invalid LLM response")
        return None

# Test (comment out for production)
if __name__ == "__main__":
    print(query_llm("Write a simple Python hello world."))