FROM golang:1.27-alpine AS build
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o rooms .

FROM alpine:3.22
WORKDIR /app
COPY --from=build /build/rooms rooms
COPY openapi.yaml openapi.yaml
EXPOSE 4003
CMD ["./rooms"]
