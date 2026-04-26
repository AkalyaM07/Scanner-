import re


def check_code(code):
    issues = []

    if re.search(
        r'password\s*=\s*["\'].*["\']',
        code,
        re.IGNORECASE
    ):
        issues.append("HARDCODED_PASSWORD")

    if re.search(
        r'(api_key|secret|token)\s*=\s*["\'].*["\']',
        code,
        re.IGNORECASE
    ):
        issues.append("HARDCODED_SECRET")

    if re.search(r'\beval\s*\(', code):
        issues.append("DANGEROUS_EVAL")

    if re.search(r'\bexec\s*\(', code):
        issues.append("DANGEROUS_EXEC")

    if re.search(r'execute\s*\(.*\+.*\)', code):
        issues.append("SQL_INJECTION_RISK")

    if re.search(r'os\.system\s*\(', code):
        issues.append("COMMAND_INJECTION")

    if re.search(r'subprocess\.Popen\s*\(', code):
        issues.append("UNSAFE_SUBPROCESS")

    if re.search(r'pickle\.load\s*\(', code):
        issues.append("UNSAFE_DESERIALIZATION")

    if re.search(r'debug\s*=\s*True', code):
        issues.append("DEBUG_MODE_ON")

    if re.search(r'http://', code):
        issues.append("INSECURE_HTTP")

    if re.search(r'except\s*:\s*pass', code):
        issues.append("HIDDEN_EXCEPTION")

    if re.search(r'random\.random\s*\(', code):
        issues.append("WEAK_RANDOM_USAGE")

    return issues