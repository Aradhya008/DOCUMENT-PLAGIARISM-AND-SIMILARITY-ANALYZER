FROM python:3.12-slim

# Install the C compiler AND standard C development headers (stdio.h, string.h, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=10000
CMD ["sh", "-c", "python app.py"]
