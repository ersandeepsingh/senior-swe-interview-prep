# Dockerfile Commands — Quick Reference

A **Dockerfile** defines the steps needed to build a Docker image: start from a base image, add files, install packages, set environment, and specify the default command.

---

## Common Dockerfile Commands

| Command      | Description                                                                   | Example usage                             |
|--------------|-------------------------------------------------------------------------------|-------------------------------------------|
| `FROM`       | Set the **base image** to use for the container                              | `FROM python:3.10-slim`                   |
| `WORKDIR`    | Set the **working directory** inside the image                               | `WORKDIR /app`                            |
| `COPY`       | **Copy files** from the local filesystem to the image                        | `COPY . /app`                             |
| `ADD`        | Like `COPY`, but also supports remote URLs and tar extraction                | `ADD myfile.tar.gz /`                     |
| `RUN`        | **Run a command** during build (e.g., install packages)                      | `RUN pip install -r requirements.txt`     |
| `CMD`        | **Default command** to run when the container starts                         | `CMD ["python", "main.py"]`               |
| `ENTRYPOINT` | Set a **fixed executable** for the container                                 | `ENTRYPOINT ["python", "main.py"]`        |
| `EXPOSE`     | Inform Docker that the container **listens on a port** (docs only)           | `EXPOSE 8080`                             |
| `ENV`        | Set an **environment variable**                                               | `ENV ENVIRONMENT=production`              |
| `ARG`        | Define a **build-time variable** (can only be used during the build)         | `ARG VERSION=latest`                      |
| `USER`       | Sets which **user** to run subsequent commands as                            | `USER appuser`                            |
| `VOLUME`     | Mark a **mount point** for external storage                                  | `VOLUME /data`                            |
| `LABEL`      | Add **metadata** to the image                                                | `LABEL maintainer="me@example.com"`       |

---

## Sample Dockerfile

```Dockerfile
# Start from the official Golang image to build the Go binary
FROM golang:1.21-alpine AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy go.mod and go.sum files first (for better caching of dependencies)
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy the rest of the application source code
COPY . .

# Build the Go app for Linux
RUN go build -o app .

# Use a minimal image for the final container
FROM alpine:latest

# Set working directory
WORKDIR /app

# Copy the built binary from the builder stage
COPY --from=builder /app/app .

# Set environment variables (example)
ENV GIN_MODE=release

# Expose the application port (change as needed)
EXPOSE 8080

# Run the Go binary when the container launches
CMD ["./app"]
```

**How to build and run:**
```sh
docker build -t my-go-app .
docker run -p 8080:8080 my-go-app
```

---