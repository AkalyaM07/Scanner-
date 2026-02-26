from scanner.scanner import scan_path

print("🔍 Running DevSecOps Security Scan...\n")

results = scan_path(".")

if not results:
    print("✅ No vulnerabilities found")
else:
    print("⚠️ Vulnerabilities detected:\n")
    for issue, path in results:
        print(f"{issue} → {path}")