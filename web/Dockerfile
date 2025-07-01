FROM node:22-alpine

ARG APP_ENV
ENV APP_ENV=${APP_ENV}
ARG REACT_APP_API_BASE_URL
ENV REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL}

WORKDIR /app

COPY package*.json ./
RUN npm install
COPY . /app

EXPOSE 5173

RUN npm install -g serve
RUN chmod +x /app/web_init.sh

CMD ["/bin/sh", "/app/web_init.sh"]
