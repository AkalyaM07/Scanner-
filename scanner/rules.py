import re


def check_file(file_path):
    """
    Read a file and check for vulnerabilities
    """
    issues = []

    try:
        with open(file_path, "r", errors="ignore") as f:
            code = f.read()
    except Exception:
        return issues

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