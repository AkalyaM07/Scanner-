import os
import requests
import time

# =========================
# CONFIG
# =========================

# ✅ Correct stable Hugging Face Router API
API_URL = "https://router.huggingface.co/hf-inference/models/google/flan-t5-base"

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    print("⚠️ WARNING: HF_TOKEN not set.")

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
} if HF_TOKEN else {}

# Cache to avoid repeated API calls
CACHE = {}


# =========================
# AI CALL FUNCTION
# =========================

def call_ai(prompt):
    """
    Safe Hugging Face API call
    """

    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={
                "inputs": prompt
            },
            timeout=60
        )

        print(f"[DEBUG] Status: {response.status_code}")

        # Model loading case
        if response.status_code == 503:
            print("⏳ Model loading... retrying...")
            time.sleep(3)
            return call_ai(prompt)

        # API failed
        if response.status_code != 200:
            print(f"[DEBUG] Error: {response.text}")
            return "AI explanation unavailable."

        data = response.json()
        print(f"[DEBUG] Response: {data}")

        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text", "AI explanation unavailable.")

        if isinstance(data, dict):
            return data.get("generated_text", "AI explanation unavailable.")

        return "AI explanation unavailable."

    except Exception as e:
        print(f"[DEBUG] Exception: {e}")
        return "AI explanation unavailable."


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
        ai_output = CACHE[cache_key]

    else:
        # ✅ Strong prompt for better explanation quality
        prompt = f"""
You are a cybersecurity expert helping beginner developers understand vulnerabilities.

You must explain each vulnerability clearly and uniquely.

Do NOT repeat only the vulnerability name.

Example:

Vulnerability: HARDCODED_PASSWORD

Explanation:
A hardcoded password means the password is directly written inside the source code instead of storing it securely outside the code using environment variables.

Why dangerous:
If someone gets access to the source code, they can easily see the password and use it to access the system without permission.

Hacker perspective:
Hackers often search GitHub repositories for exposed passwords. Once found, they can use them to log in to admin panels, databases, or servers.

Fix:
Store passwords in environment variables or secret managers instead of writing them directly inside code.


Example:

Vulnerability: DANGEROUS_EVAL

Explanation:
Using eval() allows Python to execute input as code. If untrusted user input is passed into eval(), attackers can run malicious commands.

Why dangerous:
This can lead to remote code execution where attackers gain full control over the server or application.

Hacker perspective:
Hackers may inject harmful Python commands through user input and execute malicious operations like deleting files or stealing data.

Fix:
Avoid using eval(). Use safer alternatives like ast.literal_eval() or proper input validation.


Now explain this vulnerability:

Vulnerability: {rule_id}
Details: {message}

Return ONLY in this format:

Explanation:
Why dangerous:
Hacker perspective:
Fix:
"""

        ai_output = call_ai(prompt)
        CACHE[cache_key] = ai_output

    return f"""
==============================

🔴 Issue: {rule_id}
📄 File: {path} (Line {line})

⚠️ Detected Message:
{message}

🤖 AI Analysis:
{ai_output}

==============================
"""