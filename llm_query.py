# llm_query.py: Updated LLM query using 2025 Hugging Face endpoint
import requests
import os

def query_llm(prompt, model="meta-llama/Meta-Llama-3-8B-Instruct", max_tokens=200):
    """Query Hugging Face's new OpenAI-compatible API for code generation."""
    api_key = os.environ.get("HF_TOKEN") or os.environ.get("HF_API_KEY")
    if not api_key:
        raise ValueError("HF_TOKEN or HF_API_KEY not set.")
    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7  # For creative code gen
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        generated = response.json()["choices"][0]["message"]["content"].strip()
        return generated
    except requests.exceptions.RequestException as e:
        print(f"LLM query error: {e}")
        try:
            error_details = response.json()
            print(f"Error details: {error_details}")
        except:
            print(f"Response text: {response.text}")
        return None
    except KeyError:
        print("Invalid response from LLM.")
        return None

# Test prompt for code generation
test_prompt = "Write a Python function to implement quicksort algorithm."
generated_code = query_llm(test_prompt)
print(generated_code if generated_code else "Error occurred.")
