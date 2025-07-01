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

RUN npm run build
RUN npm install -g serve

CMD ["/app/web_init.sh"]
