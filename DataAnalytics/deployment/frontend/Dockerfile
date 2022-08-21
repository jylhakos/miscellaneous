# $ docker build -t client .
# $ docker run -p 192.168.9.97:3002:3002 --network=host --env HTTPS=true

FROM node:alpine

RUN mkdir /app

WORKDIR /app

COPY package*.json ./

RUN npm install --legacy-peer-deps

COPY . ./

RUN ls -l /app

RUN rm -r ssl && mkdir ssl

COPY ./ssl/ssl.* ./ssl/

#ENV HTTPS_PROXY="https://192.168.9.97:443"

ENV HTTPS=true

ENV SSL_CRT_FILE=/app/ssl/ssl.crt

ENV SSL_KEY_FILE=/app/ssl/ssl.key

CMD ["npm", "start"]