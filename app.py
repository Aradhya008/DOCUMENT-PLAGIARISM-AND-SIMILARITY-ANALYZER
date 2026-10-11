from flask import Flask, render_template, request, flash
from pathlib import Path
import subprocess
import os
import shutil
import re

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-development-key")
BASE_DIR = Path(__file__).resolve().parent
MAX_CHARS = 5000


def compile_c_program():
    source = BASE_DIR / "analyzer.c"
    if os.name == "nt":
        compiler = shutil.which("gcc")
        executable = BASE_DIR / "analyzer.exe"
    else:
        compiler = shutil.which("gcc") or shutil.which("cc")
        executable = BASE_DIR / "analyzer"
    if not compiler:
        raise RuntimeError("GCC/CC nahi mila. GCC install karke dobara try karo.")
    result = subprocess.run([compiler, str(source), "-O2", "-o", str(executable)], capture_output=True, text=True, timeout=20)
    if result.returncode != 0:
        raise RuntimeError("C program compile nahi hua: " + result.stderr[:400])
    return executable


def parse_result(output):
    match = re.search(r"Similarity:\s*([0-9]+(?:\.[0-9]+)?)%", output)
    counts = re.search(r"MATCHED=(\d+)\s+TOTAL=(\d+)", output)
    if not match or not counts:
        raise RuntimeError("C program se result sahi format mein nahi aaya.")
    return float(match.group(1)), int(counts.group(1)), int(counts.group(2))


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", result=None)


@app.route("/analyze", methods=["POST"])
def analyze():
    text1 = request.form.get("text1", "").strip()
    text2 = request.form.get("text2", "").strip()
    if not text1 or not text2:
        flash("Dono boxes mein document ka text enter karo.")
        return render_template("index.html", result=None), 400
    if len(text1) > MAX_CHARS or len(text2) > MAX_CHARS:
        flash("Har document ka text 5,000 characters ya usse kam hona chahiye.")
        return render_template("index.html", result=None), 400

    # The C program reads two lines from standard input, so normalize line breaks.
    text1 = " ".join(text1.split())
    text2 = " ".join(text2.split())
    try:
        executable = compile_c_program()
        completed = subprocess.run([str(executable)], input=text1 + "\n" + text2 + "\n", capture_output=True, text=True, timeout=10, cwd=BASE_DIR)
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr or "C analyzer failed.")
        percentage, matched, total = parse_result(completed.stdout)
        result = {"percentage": percentage, "matched": matched, "total": total}
        return render_template("index.html", result=result)
    except (RuntimeError, subprocess.SubprocessError, OSError) as exc:
        flash("Analysis failed: " + str(exc))
        return render_template("index.html", result=None), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
