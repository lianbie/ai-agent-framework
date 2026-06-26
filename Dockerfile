# 后端服务Dockerfile
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/python:3.11-slim

# 设置工作目录
WORKDIR /app

# 使用国内Debian镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码
COPY . .

# 创建日志目录
RUN mkdir -p logs uploads/knowledge

# 暴露端口
EXPOSE 7777

# 启动命令
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7777"]
