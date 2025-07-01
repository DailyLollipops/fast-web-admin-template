FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y \
       supervisor \
       curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && /root/.local/bin/poetry config virtualenvs.create false \
    && /root/.local/bin/poetry install

RUN chmod +x api_init.sh

EXPOSE 8000

CMD ["/usr/bin/supervisord"]
