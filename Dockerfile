FROM debian:bookworm-slim AS api

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

COPY uv.lock pyproject.toml /workspace/
RUN apt-get update \
    && apt-get install -y curl build-essential \
    && rm -rf /var/lib/apt/lists/* 

WORKDIR /workspace/app
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && uv venv /workspace \
    && uv sync

FROM node:22-alpine AS web

ARG APP_ENV
ARG VITE_APP_NAME
ARG VITE_BASE_API_URL

ENV APP_ENV=${APP_ENV} \
    VITE_APP_NAME=${VITE_APP_NAME} \
    VITE_BASE_API_URL=${VITE_BASE_API_URL}

WORKDIR /workspace/app

COPY ./web/package*.json /workspace/app/
RUN npm install
RUN npm install -D vite

FROM web AS web_prod

COPY ./web /workspace/app/

RUN apk add xsel
RUN npm install -g serve
RUN npm run build
