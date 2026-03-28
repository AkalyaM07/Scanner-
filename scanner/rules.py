import re

def check_code(code):
    issues = []

    # 1. Hardcoded password
    if re.search(r'password\s*=\s*["\'].*["\']', code, re.IGNORECASE):
        issues.append("HARDCODED_PASSWORD")

    # 2. Hardcoded secrets (API keys, tokens)
    if re.search(r'(api_key|secret|token)\s*=\s*["\'].*["\']', code, re.IGNORECASE):
        issues.append("HARDCODED_SECRET")

    # 3. eval usage
    if re.search(r'\beval\s*\(', code):
        issues.append("DANGEROUS_EVAL")

    # 4. exec usage
    if re.search(r'\bexec\s*\(', code):
        issues.append("DANGEROUS_EXEC")

    # 5. SQL Injection risk
    if re.search(r'execute\s*\(.*\+.*\)', code):
        issues.append("SQL_INJECTION_RISK")

    # 6. Command Injection (os.system)
    if re.search(r'os\.system\s*\(', code):
        issues.append("COMMAND_INJECTION")

    # 7. Unsafe subprocess
    if re.search(r'subprocess\.Popen\s*\(', code):
        issues.append("UNSAFE_SUBPROCESS")

    # 8. Unsafe deserialization (pickle)
    if re.search(r'pickle\.load\s*\(', code):
        issues.append("UNSAFE_DESERIALIZATION")

    # 9. Debug mode enabled
    if re.search(r'debug\s*=\s*True', code):
        issues.append("DEBUG_MODE_ON")

    # 10. Insecure HTTP usage
    if re.search(r'http://', code):
        issues.append("INSECURE_HTTP")

    # 11. Bare except (hides errors)
    if re.search(r'except\s*:\s*pass', code):
        issues.append("HIDDEN_EXCEPTION")

    # 12. Weak random usage
    if re.search(r'random\.random\s*\(', code):
        issues.append("WEAK_RANDOM_USAGE")

    return issues