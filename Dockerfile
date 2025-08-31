FROM golang:1.25-alpine AS builder

WORKDIR /app

# Copy go mod and sum files
COPY go.mod go.sum ./
RUN go mod download

# Copy the source code
COPY . .

# Build the Go app (assuming main is in cmd/collector.go)
RUN go build -o collector ./cmd/collector.go

# Final image
FROM alpine:latest

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/collector .

# Use non-root user for security
RUN adduser -D appuser
USER appuser

CMD ["./collector"]