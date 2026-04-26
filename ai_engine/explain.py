import os
import requests
import time

# =========================
# CONFIG
# =========================
API_URL = "https://router.huggingface.co/sambanova/v1/chat/completions"
HF_TOKEN = os.getenv("HF_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

CACHE = {}


# =========================
# AI CALL FUNCTION
# =========================
def call_ai(prompt):
    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={
                "model": "Meta-Llama-3.2-1B-Instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a cybersecurity teacher explaining vulnerabilities to beginner students in simple English."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 300
            },
            timeout=60
        )

        if response.status_code == 503:
            print("[INFO] Model loading, retrying in 5s...")
            time.sleep(5)
            return call_ai(prompt)

        if response.status_code != 200:
            print(f"[DEBUG] Status: {response.status_code}")
            print(f"[DEBUG] Error: {response.text}")
            return None

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"[DEBUG] Exception: {e}")
        return None


# =========================
# FALLBACK
# =========================
def fallback(rule_id, message):
    return f"""
1. What is {rule_id}?
{message}. This means unsafe code is present directly in your source code.

2. Why is it dangerous?
Anyone who accesses your code can exploit this weakness to attack your system.

3. How can a hacker misuse it?
A hacker can find this vulnerability and use it to gain unauthorized access or damage your system.

4. How to fix it?
Follow secure coding practices and never expose sensitive data or use unsafe functions.
"""


# =========================
# MAIN FUNCTION
# =========================
def explain_issue(issue):
    rule_id = issue.get("check_id", "Unknown")
    path = issue.get("path", "Unknown file")
    line = issue.get("start", {}).get("line", "N/A")
    message = issue.get("extra", {}).get("message", "No details")

    cache_key = f"{rule_id}_{path}_{line}"

    if cache_key in CACHE:
        return CACHE[cache_key]

    prompt = f"""A security vulnerability called "{rule_id}" was found in a student's code.

Explain this to a beginner student in simple English:

1. What is {rule_id}? (explain in 2-3 simple lines what this means)
2. Why is it dangerous? (explain the risk in 1-2 lines)
3. How can a hacker misuse it? (give one simple real example)
4. How to fix it? (give a simple solution in 1-2 lines)

Use very simple words. Assume the student has never heard of this before."""

    ai_output = call_ai(prompt)

    if not ai_output:
        print("⚠ AI failed → using fallback")
        ai_output = fallback(rule_id, message)

    result = f"""
==============================

🔴 Issue: {rule_id}
📄 File: {path} (Line {line})

⚠️ Message:
{message}

🤖 AI Analysis:
{ai_output}

==============================
"""

    CACHE[cache_key] = result
    return result