import os
import requests

API_KEY = os.getenv("API_KEY")

# 🔁 Cache to avoid repeated API calls
cache = {}

def explain_issue(issue):
    rule_id = issue.get("check_id", "Unknown")
    path = issue.get("path", "Unknown file")
    start_line = issue.get("start", {}).get("line", "N/A")
    message = issue.get("extra", {}).get("message", "No details")

    # 🧠 If already explained, reuse it
    if rule_id in cache:
        ai_output = cache[rule_id]
    else:
        prompt = f"""
Explain this security issue in very simple English for a beginner.

Issue: {rule_id}
Details: {message}

Give:
Explanation:
Impact:
Fix:
"""

        # ❗ If API key missing
        if not API_KEY:
            ai_output = "No API key found. Cannot generate AI explanation."
        else:
            try:
                response = requests.post(
                    "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    json={"inputs": prompt}
                )

                data = response.json()

                # ✅ Handle different response formats safely
                if isinstance(data, list) and "generated_text" in data[0]:
                    ai_output = data[0]["generated_text"]
                elif "error" in data:
                    ai_output = f"API Error: {data['error']}"
                else:
                    ai_output = "Unexpected response from AI."

                # 💾 Save in cache
                cache[rule_id] = ai_output

            except Exception as e:
                ai_output = f"Request failed: {str(e)}"

    # ✅ Final formatted output
    explanation = f"""
🔴 Issue: {rule_id}
📄 File: {path} (Line {start_line})

⚠️ Detected Message:
{message}

🤖 AI Explanation:
{ai_output}
"""

    return explanation