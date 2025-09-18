FROM nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04 AS base

ENV DEBIAN_FRONTEND=noninteractive

# 1. 使用清华源替换 apt 源
RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|https://mirrors.tuna.tsinghua.edu.cn/ubuntu/|g' /etc/apt/sources.list && \
    sed -i 's|http://security.ubuntu.com/ubuntu/|https://mirrors.tuna.tsinghua.edu.cn/ubuntu/|g' /etc/apt/sources.list

# 2. 安装 Python3.11 + pip + ffmpeg + git
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.11 python3.11-venv python3.11-dev \
    python3-pip ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

# 3. 确保 python/pip 指向 3.11
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

WORKDIR /app

# 4. 配置 pip 使用清华源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn

# 5. 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. 拷贝应用代码
COPY ./main.py . 

# 7. 默认参数（可被 API 参数覆盖）
ENV WHISPER_MODEL=medium
ENV DEVICE=cpu

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
