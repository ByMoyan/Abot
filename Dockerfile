FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxfixes3 \
    libxext6 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libasound2 \
    libpangocairo-1.0-0 \
    cups \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

COPY . .

EXPOSE 5000

CMD ["python3", "main.py"]
