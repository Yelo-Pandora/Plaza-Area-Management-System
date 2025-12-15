# 1. 使用官方的、轻量的 Python 基础镜像
FROM python:3.12-slim

# 2. 设置环境变量，确保 Python 输出是即时的，并且不生成 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. 设置工作目录
WORKDIR /app

# 安装 GDAL 等系统级依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       binutils \
       libproj-dev \
       gdal-bin \
       libgdal-dev \
    # 清理 apt 缓存以减小镜像体积
    && rm -rf /var/lib/apt/lists/*

# 4. 复制并安装依赖
#    我们先只复制 requirements.txt 文件，这样可以利用 Docker 的层缓存。
#    只有当 requirements.txt 变化时，才会重新安装依赖。
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 复制所有项目代码到工作目录
#    这一步在安装完依赖之后，这样代码的改动就不会触发依赖的重新安装。
COPY . .

# 6. (可选) 暴露端口。这一步在 docker-compose.yml 中也会定义，这里写上更规范。
EXPOSE 8000

# 7. 默认启动命令。在开发环境中，我们通常会在 docker-compose.yml 中覆盖它。
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]