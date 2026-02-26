import os
import sys

vulnerabilities_found = False

print("🔍 Starting Security Scan...\n")

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)

            with open(path, "r", errors="ignore") as f:
                code = f.read()

                # Rule 1: Hardcoded password
                if "password" in code and "=" in code:
                    print(f"[!] HARDCODED_SECRET detected in {path}")
                    vulnerabilities_found = True

                # Rule 2: Unsafe eval
                if "eval(" in code:
                    print(f"[!] UNSAFE_EVAL detected in {path}")
                    vulnerabilities_found = True

                # Rule 3: Unsafe deserialization
                if "pickle.load" in code:
                    print(f"[!] UNSAFE_DESERIALIZATION detected in {path}")
                    vulnerabilities_found = True


if vulnerabilities_found:
    print("\n❌ Vulnerabilities Found! Failing the pipeline.")
    sys.exit(1)
else:
    print("\n✅ No vulnerabilities found.")