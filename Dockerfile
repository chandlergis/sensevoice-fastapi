# 使用 Ubuntu 22.04 作为基础镜像
FROM ubuntu:22.04

# 设置工作目录
WORKDIR /app

# 安装基本依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3 \
    python3-pip \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# 克隆 SenseVoice.cpp 仓库
RUN git clone https://github.com/lovemefan/SenseVoice.cpp.git \
    && cd SenseVoice.cpp \
    && git submodule sync \
    && git submodule update --init --recursive

# 编译 SenseVoice.cpp
RUN cd SenseVoice.cpp \
    && mkdir build \
    && cd build \
    && cmake -DCMAKE_BUILD_TYPE=Release .. \
    && make -j$(nproc)

# 复制编译好的二进制文件到 /app/bin
RUN mkdir -p /app/bin \
    && cp /app/SenseVoice.cpp/build/bin/sense-voice-main /app/bin/

# 下载模型文件（这里使用 Hugging Face 的模型）
# 下载模型文件（使用新的 Hugging Face 链接）
RUN mkdir -p /models \
    && wget -O /models/sense-voice-small-q5_0.gguf \
       https://huggingface.co/lovemefan/sense-voice-gguf/resolve/main/sense-voice-small-q5_0.gguf

# 安装 Python 依赖
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制 FastAPI 应用代码
COPY main.py .
COPY sensevoice_wrapper.py .

# 设置环境变量
ENV MODEL_PATH=/models/sense-voice-small-q5_0.gguf
ENV THREADS=6
# 暴露 FastAPI 端口
EXPOSE 30088

# 启动 FastAPI 服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "30088"]