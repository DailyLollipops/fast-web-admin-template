FROM python:3.12-slim-trixie AS base_python

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv venv /workspace/app --python python3.12

COPY uv.lock pyproject.toml .python-version /workspace/app/
WORKDIR /workspace/app

FROM base_python AS api

RUN uv sync --no-cache --group api
WORKDIR /workspace/app/api

FROM base_python AS worker

RUN apt-get update \
    && apt-get install -y supervisor \
    && rm -rf /var/lib/apt/lists/*

RUN uv sync --no-cache --group worker
COPY ./provision/worker/supervisord-worker.conf /etc/supervisord.conf

WORKDIR /workspace/app/api

COPY ./provision/worker/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

FROM node:22-slim AS base_node

WORKDIR /workspace/app/web

FROM base_node AS web
COPY ./web/package*.json /workspace/app/web/
RUN npm install
RUN npm install -D vite

FROM web AS web_builder

COPY ./web /workspace/app/web
COPY .env /workspace/app/web/.env

RUN apt-get update && apt-get install -y xsel && rm -rf /var/lib/apt/lists/*
RUN npm run build

FROM base_node AS web_prod

COPY --from=web_builder /workspace/app/web/dist /workspace/app/web/dist
RUN npm install -g serve

CMD ["serve", "-s", "dist", "-l", "5173"]

FROM base_python AS testing

ENV DISPLAY=:99
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV VITE_BASE_API_URL=http://localhost:8000

EXPOSE 6080 5900

COPY --from=base_node /usr/local /usr/local

RUN apt-get update && apt-get install -y \
    supervisor iproute2 net-tools lsof curl xvfb x11vnc fluxbox websockify novnc xsel \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/app/api
RUN uv sync --all-groups
RUN uv run playwright install --with-deps
COPY ./api /workspace/app/api

WORKDIR /workspace/app/web/*
COPY ./web /workspace/app/web
RUN npm install
RUN npm install -D vite
RUN npm install -g serve
RUN npm run build

WORKDIR /workspace/app/testing
COPY ./provision/testing/supervisord-testing.conf /etc/supervisord.conf
COPY ./provision/testing/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
