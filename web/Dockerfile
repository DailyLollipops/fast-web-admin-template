FROM node:22-alpine

ARG APP_ENV
ENV APP_ENV=${APP_ENV}
ARG VITE_BASE_API_URL
ENV VITE_BASE_API_URL=${VITE_BASE_API_URL}

WORKDIR /app

COPY package*.json ./
RUN npm install
COPY . /app

EXPOSE 5173

RUN npm install -g serve
RUN chmod +x /app/web_init.sh

CMD ["/bin/sh", "/app/web_init.sh"]
