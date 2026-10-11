
from flask import Flask, render_template, request, flash, redirect, url_for
from pathlib import Path
import subprocess
import os
import shutil
import re

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY", "change-this-development-key"
)

BASE_DIR = Path(__file__).resolve().parent
MAX_CHARS = 5000



def compile_c_program():
    """Compile analyzer.c using GCC or CC."""
    source = BASE_DIR / "analyzer.c"

    if not source.exists():
        raise RuntimeError("analyzer.c file was not found.")

    if os.name == "nt":
    if os.name == "nt":
        executable = BASE_DIR / "analyzer.exe"
    else:
        executable = BASE_DIR / "analyzer"

    compiler = shutil.which("gcc") or shutil.which("cc")

    if not compiler:
        raise RuntimeError(
            "C compiler not found. Install GCC in the server."
        )

    command = [
        compiler,
        str(source),
        "-O2",
        "-o",
        str(executable)
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=20
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("C compilation timed out.")

    if completed.returncode != 0:
        raise RuntimeError(
            "Could not compile analyzer.c: "
            + completed.stderr[:500]
        )

    return executable


def parse_c_result(output):
    similarity_match = re.search(
        r"Similarity:\s*([0-9]+(?:\.[0-9]+)?)%",
        output
    )

    count_match = re.search(
        r"MATCHED=(\d+)\s+TOTAL=(\d+)",
        output
    )

    if not similarity_match or not count_match:
        raise RuntimeError(
            "The C program returned an unexpected result."
        )

    percentage = float(similarity_match.group(1))
    matched = int(count_match.group(1))
    total = int(count_match.group(2))

    return percentage, matched, total


def parse_result(output):
    return parse_c_result(output)


def parse_result(output):
    match = re.search(r"Similarity:\s*([0-9]+(?:\.[0-9]+)?)%", output)
    counts = re.search(r"MATCHED=(\d+)\s+TOTAL=(\d+)", output)
    if not match or not counts:
        raise RuntimeError("C program se result sahi format mein nahi aaya.")
    return float(match.group(1)), int(counts.group(1)), int(counts.group(2))


@app.route("/", methods=["GET"])
def index():
    """Display the homepage."""
    return render_template("index.html", result=None)


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    """Analyze two input texts or uploaded text files."""

    if request.method == "GET":
        return redirect(url_for("index"))

    upload1 = request.files.get("file1")
    upload2 = request.files.get("file2")

    if upload1 and upload2 and upload1.filename and upload2.filename:
        if (
            Path(upload1.filename).suffix.lower() != ".txt"
            or Path(upload2.filename).suffix.lower() != ".txt"
        ):
            flash("Please upload only .txt files.")
            return redirect(url_for("index"))

        data1 = upload1.read(MAX_BYTES + 1)
        data2 = upload2.read(MAX_BYTES + 1)

        if len(data1) > MAX_BYTES or len(data2) > MAX_BYTES:
            flash("Each file must be 100 KB or smaller.")
            return redirect(url_for("index"))

        if not data1.strip() or not data2.strip():
            flash("Both files must contain text.")
            return redirect(url_for("index"))

        try:
            text1 = data1.decode("utf-8-sig")
            text2 = data2.decode("utf-8-sig")
        except UnicodeDecodeError:
            flash("Please save both files as UTF-8 plain text.")
            return redirect(url_for("index"))
    else:
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
    text1 = " ".join(text1.split())
    text2 = " ".join(text2.split())
    try:
        executable = compile_c_program()

        if upload1 and upload2 and upload1.filename and upload2.filename:
            with tempfile.TemporaryDirectory(
                prefix="similarity_"
            ) as tmp:
                temp_dir = Path(tmp)

                file1 = temp_dir / "document1.txt"
                file2 = temp_dir / "document2.txt"

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
                    error_message = (
                        completed.stderr
                        or completed.stdout
                        or "C analyzer failed."
                    )
                    raise RuntimeError(error_message[:500])

                percentage, matched, total = parse_c_result(
                    completed.stdout
                )

            result = {
                "percentage": max(
                    0.0, min(100.0, percentage)
                ),
                "matched": matched,
                "total": total,
                "file1": Path(upload1.filename).name,
                "file2": Path(upload2.filename).name,
            }
        else:
            completed = subprocess.run(
                [str(executable)],
                input=text1 + "\n" + text2 + "\n",
                capture_output=True,
                text=True,
                timeout=10,
                cwd=BASE_DIR
            )
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr or "C analyzer failed.")
            percentage, matched, total = parse_result(completed.stdout)
            result = {"percentage": percentage, "matched": matched, "total": total}

        return render_template("index.html", result=result)
    except (
        RuntimeError,
        subprocess.SubprocessError,
        OSError
    ) as exc:
        app.logger.exception("Document analysis failed")
        flash("Analysis failed: " + str(exc))
        return render_template(
            "index.html",
            result=None
        )

        flash("Analysis failed: " + str(exc))
        return render_template(
            "index.html",
            result=None
        ), 500



if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
