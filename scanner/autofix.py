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

        "DANGEROUS_EVAL": "Avoid eval(). Use ast.literal_eval() or safe parsing.",

        "DANGEROUS_EXEC": "Avoid exec(). It can execute arbitrary code.",

        "SQL_INJECTION_RISK": "Use parameterized queries.\nExample:\ncursor.execute('SELECT * FROM users WHERE id=%s', (user_id,))",

        "COMMAND_INJECTION": "Avoid os.system(). Use subprocess.run() safely.",

        "UNSAFE_SUBPROCESS": "Use subprocess.run(shell=False) with validated input.",

        "UNSAFE_DESERIALIZATION": "Avoid pickle.load() on untrusted data. Use JSON.",

        "DEBUG_MODE_ON": "Disable debug mode in production (debug=False).",

        "INSECURE_HTTP": "Use HTTPS instead of HTTP.",

        "HIDDEN_EXCEPTION": "Avoid bare except. Specify exception and log it.",

        "WEAK_RANDOM_USAGE": "Use secrets module.\nExample:\nimport secrets\nsecrets.token_hex()"
    }

    # =========================
    # PROCESS VULNERABILITIES
    # =========================
    for v in vulnerabilities:

        issue = v.get("check_id", "UNKNOWN")
        path = v.get("path", "")
        message = v.get("extra", {}).get("message", "")

        suggestion = FIX_MAP.get(issue, "No direct fix available.")

        # 🤖 AI Explanation
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
    # 📁 CREATE REPORT FOLDER (IMPORTANT FIX)
    # =========================
    os.makedirs("reports", exist_ok=True)

    # =========================
    # 📄 GENERATE PDF
    # =========================
    pdf_path = "reports/autofix_report.pdf"

    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        doc = SimpleDocTemplate(pdf_path)
        styles = getSampleStyleSheet()

        content = []

        # Title
        content.append(Paragraph("Auto-Fix Suggestion Report", styles["Title"]))
        content.append(Spacer(1, 10))

        # Summary
        content.append(Paragraph(f"Total Issues: {len(suggestions)}", styles["Normal"]))
        content.append(Paragraph(f"Generated At: {datetime.now()}", styles["Normal"]))
        content.append(Spacer(1, 15))

        # Issues
        for s in suggestions:
            content.append(Paragraph(f"Issue: {s['issue']}", styles["Normal"]))
            content.append(Paragraph(f"File: {s['file']}", styles["Normal"]))
            content.append(Paragraph(f"Problem: {s['problem']}", styles["Normal"]))
            content.append(Paragraph(f"Suggested Fix: {s['fix']}", styles["Normal"]))
            content.append(Spacer(1, 6))
            content.append(Paragraph("AI Insight:", styles["Heading3"]))
            content.append(Paragraph(s['ai'], styles["Normal"]))
            content.append(Spacer(1, 12))

        doc.build(content)

        print(f"\n🛠 Auto-fix PDF generated: {pdf_path}")

    except Exception as e:
        print(f"⚠ PDF generation failed: {e}")

    return pdf_path