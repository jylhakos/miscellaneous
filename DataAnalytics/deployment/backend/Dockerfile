# $ docker build -t server .
# $ docker run -p 192.168.9.97:8001:8001 --network=host --env HTTPS_PROXY="https://192.168.9.97:443" server

FROM golang:alpine

RUN mkdir /app

WORKDIR /app

ENV GO111MODULE=on GOPROXY=https://goproxy.cn,direct

#RUN rm $GOPATH/go.mod

COPY go.mod go.sum ./

RUN go mod download

COPY . ./

RUN ls -l /app

RUN go build -o server .

RUN ls -l /app

ENV HTTPS_PROXY="https://192.168.9.97:443"

ENV PORT=8001

EXPOSE $PORT

CMD ["./server"]