# Document Similarity Analyzer (Text Input Version)

A beginner-friendly college project using HTML, CSS, Python Flask, and C. Users paste two documents into text boxes; no file upload or C file-reading functions are required.

## Requirements
- Python 3.10+
- GCC compiler (`gcc` or `cc`)

## Run locally
1. Install Python and GCC.
2. Open this project folder in a terminal.
3. Install Flask: `pip install -r requirements.txt`
4. Start: `python app.py`
5. Open `http://127.0.0.1:5000`.
6. Paste text into both boxes and click **Compare Documents**.

## How it works
- HTML provides two text boxes.
- Flask receives the text and sends it to the C program through standard input.
- The C program reads two lines using `fgets()`, splits words with simple loops, and compares them using `strcmp()`.
- Flask shows the estimated word overlap.

## Limitations
This is an educational demo, not a professional plagiarism detector. It checks exact word matches only, is case-sensitive, and does not understand meaning or paraphrasing. Each text box is limited to 5,000 characters. The C code uses fixed-size arrays to keep the example beginner-friendly.
