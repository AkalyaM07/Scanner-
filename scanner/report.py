import os
from datetime import datetime
from ai_engine.explain import explain_issue

def clean_text(text):
    if not text:
        return ""
    return text.encode("ascii", "ignore").decode("ascii").strip()


def get_ai_explanation(issue):
    try:
        rule_id = issue.get("check_id", "Unknown")
        message = issue.get("extra", {}).get("message", "No details")

        from ai_engine.explain import call_ai, fallback, CACHE

        cache_key = f"{rule_id}_{issue.get('path', '')}_{issue.get('start', {}).get('line', 'N/A')}"

        if cache_key in CACHE:
            cached = CACHE[cache_key]
            if "AI Analysis:" in cached:
                return cached.split("AI Analysis:")[-1].strip().replace("==============================", "").strip()

        prompt = f"""A security vulnerability called "{rule_id}" was found in a student's code.

Explain this to a beginner student in simple English:

1. What is {rule_id}?
2. Why is it dangerous?
3. How can a hacker misuse it?
4. How to fix it?

Use very simple words."""

        ai_output = call_ai(prompt)
        if not ai_output:
            ai_output = fallback(rule_id, message)

        return ai_output

    except Exception as e:
        print(f"[DEBUG] AI explanation error: {e}")
        return "AI explanation not available."


def generate_report(vulnerabilities):
    os.makedirs("reports", exist_ok=True)
    pdf_path = "reports/report.pdf"

    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors

        doc = SimpleDocTemplate(
            pdf_path,
            rightMargin=inch * 0.75,
            leftMargin=inch * 0.75,
            topMargin=inch * 0.75,
            bottomMargin=inch * 0.75
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            fontSize=20,
            spaceAfter=10
        )

        heading_style = ParagraphStyle(
            "Heading",
            parent=styles["Normal"],
            fontSize=12,
            textColor=colors.darkred,
            fontName="Helvetica-Bold",
            spaceAfter=4
        )

        label_style = ParagraphStyle(
            "Label",
            parent=styles["Normal"],
            fontSize=10,
            fontName="Helvetica-Bold",
            spaceAfter=2
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=10,
            spaceAfter=4,
            leading=14
        )

        content = []

        content.append(Paragraph("Security Scan Report", title_style))
        content.append(Spacer(1, 6))
        content.append(Paragraph(f"Total Vulnerabilities Found: {len(vulnerabilities)}", body_style))
        content.append(Paragraph(f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
        content.append(Spacer(1, 16))
        content.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        content.append(Spacer(1, 12))

        for i, v in enumerate(vulnerabilities, 1):
            rule_id = clean_text(v.get("check_id", "Unknown"))
            path = clean_text(v.get("path", "Unknown file"))
            line = v.get("start", {}).get("line", "N/A")
            message = clean_text(v.get("extra", {}).get("message", "No details"))

            content.append(Paragraph(f"Issue #{i}: {rule_id}", heading_style))
            content.append(Paragraph(f"File: {path}  |  Line: {line}", label_style))
            content.append(Paragraph(f"Detected: {message}", body_style))
            content.append(Spacer(1, 6))

            content.append(Paragraph("AI Explanation:", label_style))
            ai_text = clean_text(get_ai_explanation(v))
            content.append(Paragraph(ai_text, body_style))

            content.append(Spacer(1, 10))
            content.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
            content.append(Spacer(1, 10))

        doc.build(content)
        print(f"\nPDF Report generated: {pdf_path}")

    except Exception as e:
        print(f"[WARNING] PDF generation failed: {e}")

    return pdf_path