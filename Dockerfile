FROM golang:1.25-alpine AS builder

# Labels
LABEL org.opencontainers.image.authors="NotAussie <notaussie@duck.com>"
LABEL org.opencontainers.image.vendor="GitHub"
LABEL org.opencontainers.image.licenses="AGPL-3.0"
LABEL org.opencontainers.image.title="Bustinel"
LABEL org.opencontainers.image.description="Golang microservice for GTFS-RT vehicles to MongoDB."


WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN go build -o collector ./cmd/collector.go

FROM alpine:latest

WORKDIR /app

COPY --from=builder /app/collector .
RUN apk add --no-cache ca-certificates

RUN adduser -D bustinel
USER bustinel

CMD ["./collector"]