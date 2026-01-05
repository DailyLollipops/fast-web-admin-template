FROM debian:bookworm-slim AS base_python

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

RUN apt-get update \
    && apt-get install -y curl libffi-dev build-essential \
    && rm -rf /var/lib/apt/lists/* 

RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && uv venv /workspace

COPY uv.lock pyproject.toml .python-version /workspace/
WORKDIR /workspace/app

FROM base_python AS api

RUN uv sync --group api

FROM base_python AS worker

RUN uv sync --group worker

FROM node:22-slim AS base_node

WORKDIR /workspace/app/web

FROM base_node AS web
COPY ./web/package*.json /workspace/app/web/
RUN npm install
RUN npm install -D vite

FROM web AS web_prod

COPY ./web /workspace/app/web
COPY .env /workspace/app/web/.env

RUN apt-get update && apt-get install -y xsel && rm -rf /var/lib/apt/lists/*
RUN npm install -g serve
RUN npm run build

FROM base_python AS testing

COPY --from=base_node /usr/local /usr/local

RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

COPY ./provision/testing/supervisord-testing.conf /etc/supervisord.conf
COPY ./web/package*.json /workspace/web/

WORKDIR /workspace
RUN uv sync --all-groups
RUN uv run playwright install

WORKDIR /workspace/web
RUN npm install
RUN npm install -D vite

WORKDIR /workspace/testing

COPY ./provision/testing/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf", "-n"]
