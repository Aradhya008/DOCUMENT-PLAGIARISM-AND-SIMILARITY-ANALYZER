from flask import Flask, render_template, request, flash
from pathlib import Path
import subprocess
import tempfile
import os
import re
import shutil

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-development-key")
BASE_DIR = Path(__file__).resolve().parent
MAX_BYTES = 100 * 1024

def compile_c_program():
    """Compile analyzer.c when GCC is available."""
    source = BASE_DIR / "analyzer.c"
    if os.name == "nt":
        executable = BASE_DIR / "analyzer.exe"
        compiler = shutil.which("gcc")
        command = [compiler, str(source), "-O2", "-o", str(executable)] if compiler else None
    else:
        executable = BASE_DIR / "analyzer"
        compiler = shutil.which("gcc") or shutil.which("cc")
        command = [compiler, str(source), "-O2", "-o", str(executable)] if compiler else None

    if command is None:
        raise RuntimeError("GCC/CC was not found. Install GCC and try again.")
    result = subprocess.run(command, capture_output=True, text=True, timeout=20)
    if result.returncode != 0:
        raise RuntimeError("Could not compile analyzer.c: " + result.stderr[:500])
    return executable

def parse_c_result(output):
    match = re.search(r"Similarity:\s*([0-9]+(?:\.[0-9]+)?)%", output)
    count = re.search(r"MATCHED=(\d+)\s+TOTAL=(\d+)", output)
    if not match or not count:
        raise RuntimeError("The C program returned an unexpected result.")
    return float(match.group(1)), int(count.group(1)), int(count.group(2))

@app.get("/")
def index():
    return render_template("index.html", result=None)

@app.post("/analyze")
def analyze():
    upload1 = request.files.get("file1")
    upload2 = request.files.get("file2")

    if not upload1 or not upload2 or not upload1.filename or not upload2.filename:
        flash("Please select both text files.")
        return render_template("index.html", result=None), 400

    if Path(upload1.filename).suffix.lower() != ".txt" or Path(upload2.filename).suffix.lower() != ".txt":
        flash("For this version, upload only .txt files.")
        return render_template("index.html", result=None), 400

    data1 = upload1.read(MAX_BYTES + 1)
    data2 = upload2.read(MAX_BYTES + 1)
    if len(data1) > MAX_BYTES or len(data2) > MAX_BYTES:
        flash("Each file must be 100 KB or smaller.")
        return render_template("index.html", result=None), 400
    if not data1.strip() or not data2.strip():
        flash("Both files must contain text.")
        return render_template("index.html", result=None), 400

    try:
        text1 = data1.decode("utf-8-sig")
        text2 = data2.decode("utf-8-sig")
    except UnicodeDecodeError:
        flash("Please save both files as UTF-8 plain text.")
        return render_template("index.html", result=None), 400

    try:
        executable = compile_c_program()
        with tempfile.TemporaryDirectory(prefix="similarity_") as tmp:
            file1 = Path(tmp) / "document1.txt"
            file2 = Path(tmp) / "document2.txt"
            file1.write_text(text1, encoding="utf-8")
            file2.write_text(text2, encoding="utf-8")

            completed = subprocess.run(
                [str(executable), str(file1), str(file2)],
                capture_output=True, text=True, timeout=10, cwd=tmp
            )
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr or completed.stdout or "C analyzer failed.")
            percentage, matched, total = parse_c_result(completed.stdout)

        result = {
            "percentage": max(0.0, min(100.0, percentage)),
            "matched": matched,
            "total": total,
            "file1": Path(upload1.filename).name,
            "file2": Path(upload2.filename).name,
        }
        return render_template("index.html", result=result)
    except (RuntimeError, subprocess.SubprocessError, OSError) as exc:
        flash("Analysis failed: " + str(exc))
        return render_template("index.html", result=None), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
