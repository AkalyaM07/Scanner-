def explain_issue(issue):
    """
    Converts raw vulnerability details into simple, student-friendly explanation.
    """
    rule_id = issue.get("check_id", "Unknown")
    path = issue.get("path", "Unknown file")
    start_line = issue.get("start", {}).get("line", "N/A")
    message = issue.get("extra", {}).get("message", "No details")

    explanation = f"""
🔴 Issue: {rule_id}
📄 File: {path} (Line {start_line})
⚠️ Risk: {message}
✅ Suggestion: Follow secure coding practices for this type of issue.
"""
    return explanation