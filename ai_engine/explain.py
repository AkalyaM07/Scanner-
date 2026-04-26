import os
import requests
import time

# =========================
# CONFIG
# =========================

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
HF_TOKEN = os.getenv("HF_TOKEN")

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
    Calls Hugging Face API safely
    """

    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"inputs": prompt},
            timeout=60
        )

        # Model loading case
        if response.status_code == 503:
            print("⏳ Model is loading... retrying")
            time.sleep(3)
            return call_ai(prompt)

        # API failed
        if response.status_code != 200:
            print(f"⚠ API Error: {response.status_code}")
            return None

        data = response.json()

        # Normal Hugging Face response
        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text", "")

        if isinstance(data, dict):
            return data.get("generated_text", "")

        return None

    except Exception as e:
        print(f"⚠ API Exception: {e}")
        return None


# =========================
# GENERIC FALLBACK
# =========================

def fallback(rule_id, message):
    """
    Generic fallback if AI API fails
    No hardcoded vulnerability map
    """

    return f"""
Explanation:
This vulnerability indicates an insecure coding practice that may create security risks in the application.

It can expose sensitive information, allow unauthorized access, or help attackers misuse the system if not fixed properly.

Why dangerous:
Attackers may exploit this weakness to steal data, access restricted areas, or execute malicious actions inside the system.

Hacker perspective:
An attacker may use {rule_id} to identify weak points in the code and perform unauthorized actions against the application.

Fix:
Follow secure coding practices, validate all inputs properly, avoid unsafe functions, and store sensitive information securely.
"""


# =========================
# MAIN FUNCTION
# =========================

def explain_issue(issue):
    """
    Main AI explanation function
    """

    rule_id = issue.get("check_id", "Unknown")
    path = issue.get("path", "Unknown file")
    line = issue.get("start", {}).get("line", "N/A")
    message = issue.get("extra", {}).get("message", "No details")

    cache_key = f"{rule_id}_{path}_{line}"

    # =========================
    # Use cache if already generated
    # =========================

    if cache_key in CACHE:
        ai_output = CACHE[cache_key]

    else:

        # =========================
        # Better AI Prompt
        # =========================

        prompt = f"""
You are a cybersecurity expert helping beginner developers.

Explain the following vulnerability in simple student-friendly language.

Vulnerability Name: {rule_id}
Detected Message: {message}

Instructions:
- Do NOT just repeat the vulnerability name
- First explain what this vulnerability actually means
- Keep explanation simple and clear
- Explain how hackers may exploit it
- Explain how to fix it securely

Return ONLY in this format:

Explanation:
(Explain what this vulnerability means in 2 to 3 simple lines)

Why dangerous:
(Explain why this vulnerability is risky)

Hacker perspective:
(Explain how attackers may use this vulnerability)

Fix:
(Explain how to fix this securely)
"""

        # =========================
        # AI FIRST → fallback only if needed
        # =========================

        if HF_TOKEN:
            ai_output = call_ai(prompt)

            if not ai_output or len(ai_output.strip()) < 20:
                print("⚠ AI response weak, using fallback")
                ai_output = fallback(rule_id, message)

        else:
            print("⚠ HF_TOKEN not found, using fallback")
            ai_output = fallback(rule_id, message)

        CACHE[cache_key] = ai_output

    # =========================
    # Final formatted output
    # =========================

    return f"""
==============================

🔴 Issue: {rule_id}
📄 File: {path} (Line {line})

⚠ Detected Message:
{message}

🤖 AI Analysis:
{ai_output}

==============================
"""