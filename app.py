
from flask import Flask, render_template, request, flash
from pathlib import Path
import subprocess
import tempfile
import os
import shutil
import re

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "development-key")

BASE_DIR = Path(__file__).resolve().parent
MAX_CHARS = 10000


def compile_c_program():
    source = BASE_DIR / "analyzer.c"

    if os.name == "nt":
        executable = BASE_DIR / "analyzer.exe"
        compiler = shutil.which("gcc")
    else:
        executable = BASE_DIR / "analyzer"
        compiler = shutil.which("gcc") or shutil.which("cc")

    if compiler is None:
        raise RuntimeError("GCC/CC compiler not found.")

    command = [
        compiler,
        str(source),
        "-O2",
        "-o",
        str(executable)
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=20
    )

    if result.returncode != 0:
        raise RuntimeError(
            "C compilation failed: " + result.stderr[:500]
        )

    return executable


def parse_result(output):
    match = re.search(
        r"Similarity:\s*([0-9]+(?:\.[0-9]+)?)%",
        output
    )

    if not match:
        raise RuntimeError(
            "Could not read similarity from C program output."
        )

    return float(match.group(1))


@app.get("/")
def index():
    return render_template("index.html", result=None)


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    if request.method == "GET":
        return render_template("index.html", result=None)

    text1 = request.form.get("text1", "").strip()
    text2 = request.form.get("text2", "").strip()

    if not text1 or not text2:
        flash("Please enter text in both document boxes.")
        return render_template("index.html", result=None), 400

    if len(text1) > MAX_CHARS or len(text2) > MAX_CHARS:
        flash("Each document can contain up to 10000 characters.")
        return render_template("index.html", result=None), 400

    try:
        executable = compile_c_program()

        with tempfile.TemporaryDirectory(
            prefix="similarity_"
        ) as tmp:

            file1 = Path(tmp) / "document1.txt"
            file2 = Path(tmp) / "document2.txt"

            file1.write_text(text1, encoding="utf-8")
            file2.write_text(text2, encoding="utf-8")

            completed = subprocess.run(
                [
                    str(executable),
                    str(file1),
                    str(file2)
                ],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=tmp
            )

            if completed.returncode != 0:
                raise RuntimeError(
                    completed.stderr
                    or completed.stdout
                    or "C analyzer failed."
                )

            percentage = parse_result(completed.stdout)

        result = {
            "percentage": max(0.0, min(100.0, percentage)),
            "text1_length": len(text1),
            "text2_length": len(text2)
        }

        return render_template(
            "index.html",
            result=result
        )

    except (
        RuntimeError,
        subprocess.SubprocessError,
        OSError
    ) as error:
        flash("Analysis failed: " + str(error))
        return render_template("index.html", result=None), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
