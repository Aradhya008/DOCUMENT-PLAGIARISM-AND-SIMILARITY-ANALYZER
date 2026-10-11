# Document Similarity Analyzer (HTML + CSS + Python Flask + C)

A beginner-friendly local demo that uploads two `.txt` documents, invokes a C program, and displays a basic word-overlap estimate.

## Requirements
- Python 3.10+
- GCC compiler available as `gcc` (MinGW-w64 GCC on Windows)
- Internet is only needed to install Flask the first time

## Run on Windows
1. Install Python and GCC, and ensure both `python` and `gcc` work in Command Prompt.
2. Open this folder in Command Prompt.
3. Create a virtual environment (optional but recommended):
   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bat
   pip install -r requirements.txt
   ```
5. Start the website:
   ```bat
   python app.py
   ```
6. Open `http://127.0.0.1:5000` in your browser.
7. Upload two UTF-8 `.txt` files and click **Analyze documents**.

The backend compiles `analyzer.c` automatically when you submit files. You can also compile it manually:
```bat
gcc analyzer.c -O2 -o analyzer.exe
```

## Project files
- `index.html` — upload form and results
- `static/style.css` — page styling
- `app.py` — Flask backend and C integration
- `analyzer.c` — C word-overlap calculation

## Important limitations
- This is an educational demo, not a professional plagiarism detector.
- It counts exact word matches without semantic analysis, sentence matching, citations, or paraphrase detection. The C code demonstrates basic `string.h` functions: `strlen()`, `strcpy()`, `strcmp()`, and `strtok()`.
- It supports plain-text `.txt` uploads only, limited to 100 KB per file.
- The C program has fixed-size buffers and only processes up to 10,000 bytes per document and 1,000 words from Document 1.
- Run locally for coursework/demo use. Before public deployment, add production server configuration, CSRF protection, rate limits, robust parsing, and security review. Do not use Flask's development server for production.
- Temporary uploaded files are removed automatically after the analysis request.


## Deploy from GitHub (Render using Docker)
1. Create a GitHub repository and upload all project files (including `Dockerfile`).
2. On Render, create a new **Web Service** and connect the GitHub repository.
3. Choose **Docker** as the runtime/environment.
4. Create the service and wait for the build and deploy to finish.
5. Open the public URL Render provides.

The Docker image installs GCC and Python dependencies, so the C program can be compiled by the Flask backend. Set a strong `SECRET_KEY` environment variable in the hosting dashboard before using the service publicly.

Note: This is an educational demo. Before public use, add stronger request limits, CSRF protection, secure upload handling, and production testing. Free hosting availability and sleep/usage limits may change by provider.
