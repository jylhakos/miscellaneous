# $ docker build -t client .
# $ $ docker run -p 192.168.9.97:3002:3002 --network=host --env HTTPS_PROXY="https://192.168.9.97:443" --env HTTP=true --env SSL_CRT_FILE=ssl.crt --env SSL_KEY_FILE=ssl.key client

FROM node:alpine

RUN mkdir /app

WORKDIR /app

COPY package.json package-lock.json ./

RUN ls -l /app

RUN npm install --legacy-peer-deps

COPY . ./

RUN ls -l /app

ENV HTTPS_PROXY="https://192.168.9.97:443"

ENV HTTPS=true

ENV SSL_CRT_FILE=ssl.crt

ENV SSL_KEY_FILE=ssl.key

CMD ["npm", "start"]