# =========================
# FALLBACK AI ENGINE
# =========================

def fallback(rule_id, message):

    explanations = {
        "HARDCODED_PASSWORD": {
            "explanation": "A password is directly written in the source code instead of secure storage.",
            "danger": "Attackers can easily extract credentials and gain unauthorized access.",
            "hacker": "An attacker scans the repository, finds the password, and logs into the system without permission.",
            "fix": "Store passwords in environment variables or secure secret management systems."
        },

        "HARDCODED_SECRET": {
            "explanation": "Sensitive API keys or tokens are exposed in the source code.",
            "danger": "This can lead to data leaks and unauthorized API usage.",
            "hacker": "Attacker steals the key and misuses backend services or APIs.",
            "fix": "Use environment variables or secret vault services."
        },

        "DANGEROUS_EVAL": {
            "explanation": "eval() executes dynamic code which is unsafe.",
            "danger": "It allows execution of attacker-controlled code.",
            "hacker": "Attacker injects malicious code that gets executed by eval().",
            "fix": "Avoid eval() and use safe parsing alternatives."
        },

        "DANGEROUS_EXEC": {
            "explanation": "exec() executes arbitrary Python code dynamically.",
            "danger": "It can lead to full system compromise.",
            "hacker": "Attacker injects code that gets executed on the system.",
            "fix": "Remove exec() or strictly validate inputs."
        },

        "COMMAND_INJECTION": {
            "explanation": "User input is directly passed into system commands.",
            "danger": "Attackers can execute unauthorized OS commands.",
            "hacker": "Attacker injects shell commands to control system behavior.",
            "fix": "Sanitize input and avoid unsafe system calls."
        },

        "UNSAFE_DESERIALIZATION": {
            "explanation": "Unsafe deserialization of objects like pickle.",
            "danger": "Can lead to remote code execution.",
            "hacker": "Attacker sends malicious serialized object to execute code.",
            "fix": "Avoid unsafe deserialization or validate input strictly."
        },

        "DEBUG_MODE_ON": {
            "explanation": "Debug mode is enabled in production environment.",
            "danger": "It exposes sensitive system information.",
            "hacker": "Attacker uses debug information to discover vulnerabilities.",
            "fix": "Disable debug mode in production."
        },

        "INSECURE_HTTP": {
            "explanation": "HTTP is used instead of HTTPS.",
            "danger": "Data can be intercepted during transmission.",
            "hacker": "Attacker performs man-in-the-middle attack to steal data.",
            "fix": "Always use HTTPS for secure communication."
        },

        "HIDDEN_EXCEPTION": {
            "explanation": "Exceptions are silently ignored in the code.",
            "danger": "Errors are hidden, making debugging and security monitoring difficult.",
            "hacker": "Attacker triggers errors without detection.",
            "fix": "Log exceptions properly instead of ignoring them."
        },

        "WEAK_RANDOM_USAGE": {
            "explanation": "Weak random generator is used for security purposes.",
            "danger": "Outputs are predictable and can be exploited.",
            "hacker": "Attacker predicts random values and bypasses security.",
            "fix": "Use cryptographically secure random generators."
        }
    }

    if rule_id in explanations:
        rule = explanations[rule_id]

        return f"""
Explanation: {rule['explanation']}

Why dangerous: {rule['danger']}

Hacker perspective: {rule['hacker']}

Fix: {rule['fix']}
"""

    # Default fallback (for unknown rules)
    return f"""
Explanation: {message}

Why dangerous: This vulnerability may lead to security risks or unexpected behavior.

Hacker perspective: Attackers may analyze and exploit this weakness.

Fix: Follow secure coding practices and validate all inputs properly.
"""