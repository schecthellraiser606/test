FROM python:3.6

ENV PYTHONUNBUFFERED=1  \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUTF8=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    CHOKIDAR_USEPOLLING=true

WORKDIR /code
ADD requirements.txt /code/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt