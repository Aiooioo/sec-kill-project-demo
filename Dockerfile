FROM python:3.12-slim-bookworm

WORKDIR /app

# 设置时区为 UTC+8
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

ENV PYTHONPATH=.

RUN pip install uv -i https://pypi.tuna.tsinghua.edu.cn/simple

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_SYSTEM_PYTHON=1
ENV UV_DEFAULT_INDEX="https://mirrors.aliyun.com/pypi/simple"

COPY ./app/uv.lock ./app/pyproject.toml /app/

# 第一次 sync：基于锁文件安装依赖，禁用可编辑模式，冻结版本
RUN uv sync --frozen --no-editable

COPY ./app /app

RUN uv lock

# Sync the project
RUN uv sync --no-editable

RUN uv cache clean

EXPOSE 8000

CMD ["uv", "run", "startup.py"]
