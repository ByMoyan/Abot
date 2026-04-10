FROM python:3.11-slim

# ===== 系统依赖 =====
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
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
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libgbm1 \
    libpango-1.0-0 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# ===== 工作目录 =====
WORKDIR /app

# ===== 复制依赖 =====
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ===== 安装 Playwright 浏览器 =====
RUN python -m playwright install chromium

# ===== 复制代码 =====
COPY . .

# ===== 环境变量 =====
ENV PYTHONUNBUFFERED=1

# ===== 端口 =====
EXPOSE 5000

# ===== 启动 =====
CMD ["python", "main.py"]
