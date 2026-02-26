from flask import Flask, jsonify, request
from scanner.scanner import scan_path
from ai_engine.explain import explain_issue

app = Flask(__name__)

@app.route("/scan", methods=["POST"])
def scan():
    path = request.json.get("path")  # Path of code folder
    results = scan_path(path)
    explained = []

    # Loop through findings and generate AI explanation
    for issue in results.get("results", []):
        explained.append(explain_issue(issue))

    return jsonify({
        "raw_results": results,
        "explained_results": explained
    })

if __name__ == "__main__":
    app.run(debug=True)