FROM debian:bookworm-slim AS base_python

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

RUN apt-get update \
    && apt-get install -y curl build-essential \
    && rm -rf /var/lib/apt/lists/* 

RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && uv venv /workspace

COPY uv.lock pyproject.toml /workspace/
WORKDIR /workspace/app

FROM base_python AS api

RUN uv sync --group api

FROM base_python AS worker

RUN uv sync --group worker

FROM node:22-alpine AS web

WORKDIR /workspace/app

COPY ./web/package*.json /workspace/app/
RUN npm install
RUN npm install -D vite

FROM web AS web_prod

COPY ./web /workspace/app/
COPY .env /workspace/app/.env

RUN apk add xsel
RUN npm install -g serve
RUN npm run build
