from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_playwright():
    # run your Playwright file
    result = subprocess.run(
        ["python3", "Rishi.py"],  # your automation file
        capture_output=True,
        text=True
    )
    return jsonify({
        "status": "completed",
        "stdout": result.stdout,
        "stderr": result.stderr
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API Running"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
