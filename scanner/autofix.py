import os
from datetime import datetime
from ai_engine.explain import explain_issue

def generate_autofix(vulnerabilities):

    suggestions = []

    # =========================
    # 🔧 RULE-BASED FIX MAPPING
    # =========================
    FIX_MAP = {
        "HARDCODED_PASSWORD": "Use environment variables.\nExample:\nimport os\npassword = os.getenv('PASSWORD')",

        "HARDCODED_SECRET": "Move secrets to environment variables or .env files.\nNever hardcode API keys.",

        "DANGEROUS_EVAL": "Avoid eval(). Use ast.literal_eval() or proper parsing.",

        "DANGEROUS_EXEC": "Avoid exec(). It can execute arbitrary code.",

        "SQL_INJECTION_RISK": "Use parameterized queries.\nExample:\ncursor.execute('SELECT * FROM users WHERE id=%s', (user_id,))",

        "COMMAND_INJECTION": "Avoid os.system(). Use subprocess.run() with safe arguments.",

        "UNSAFE_SUBPROCESS": "Use subprocess.run() with shell=False and validated inputs.",

        "UNSAFE_DESERIALIZATION": "Avoid pickle.load() on untrusted data. Use JSON instead.",

        "DEBUG_MODE_ON": "Disable debug mode in production.\nSet debug=False.",

        "INSECURE_HTTP": "Use HTTPS instead of HTTP.",

        "HIDDEN_EXCEPTION": "Avoid bare except. Specify exception type and log errors.",

        "WEAK_RANDOM_USAGE": "Use secrets module instead.\nExample:\nimport secrets\nsecrets.token_hex()"
    }

    # =========================
    # PROCESS VULNERABILITIES
    # =========================
    for v in vulnerabilities:

        issue = v.get("check_id", "UNKNOWN")
        path = v.get("path", "")
        message = v.get("extra", {}).get("message", "")

        suggestion = FIX_MAP.get(issue, "No direct fix available.")

        # 🤖 AI Explanation (reuse your model)
        try:
            ai_text = explain_issue(v)
        except:
            ai_text = "AI explanation not available"

        suggestions.append({
            "issue": issue,
            "file": path,
            "problem": message,
            "fix": suggestion,
            "ai": ai_text
        })

    # =========================
    # 📄 GENERATE PDF
    # =========================
    pdf_path = "autofix_report.pdf"

    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        doc = SimpleDocTemplate(pdf_path)
        styles = getSampleStyleSheet()

        content = []

        # Title
        content.append(Paragraph("🛠 Auto-Fix Suggestion Report", styles["Title"]))
        content.append(Spacer(1, 10))

        # Summary
        content.append(Paragraph(f"Total Issues: {len(suggestions)}", styles["Normal"]))
        content.append(Paragraph(f"Generated At: {datetime.now()}", styles["Normal"]))
        content.append(Spacer(1, 15))

        # Each issue
        for s in suggestions:
            content.append(Paragraph(f"Issue: {s['issue']}", styles["Normal"]))
            content.append(Paragraph(f"File: {s['file']}", styles["Normal"]))
            content.append(Paragraph(f"Problem: {s['problem']}", styles["Normal"]))
            content.append(Paragraph(f"Suggested Fix: {s['fix']}", styles["Normal"]))
            content.append(Paragraph(f"AI Insight: {s['ai']}", styles["Normal"]))
            content.append(Spacer(1, 12))

        doc.build(content)

        print(f"\n🛠 Auto-fix PDF generated: {pdf_path}")

    except Exception as e:
        print(f"⚠ PDF generation failed: {e}")

    return pdf_path