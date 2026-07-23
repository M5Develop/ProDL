FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    ffmpeg curl unzip && \
    rm -rf /var/lib/apt/lists/*

# Install deno for yt-dlp JS challenges
RUN curl -fsSL https://deno.land/install.sh | sh
ENV PATH="/root/.deno/bin:$PATH"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
