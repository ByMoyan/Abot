FROM python:3.11-slim

# 安装系统依赖（Chromium 运行必须）
RUN apt-get update && apt-get install -y \
    chromium \
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

# 设置环境变量
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# 复制项目文件
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python3", "main.py"]
