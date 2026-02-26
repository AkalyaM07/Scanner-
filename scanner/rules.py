import re

def check_vulnerabilities(code):
    issues = []

    # Hardcoded password
    if re.search(r'password\s*=\s*["\'].*["\']', code, re.IGNORECASE):
        issues.append("HARDCODED_PASSWORD")

    # eval usage
    if re.search(r'\beval\s*\(', code):
        issues.append("DANGEROUS_EVAL")

    # exec usage
    if re.search(r'\bexec\s*\(', code):
        issues.append("DANGEROUS_EXEC")

    # unsafe pickle
    if re.search(r'pickle\.load\s*\(', code):
        issues.append("UNSAFE_DESERIALIZATION")

    return issues