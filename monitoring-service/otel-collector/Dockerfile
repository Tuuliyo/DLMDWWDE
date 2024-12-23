# ------------------------------------------------------------------------------
# Dockerfile for creating a lightweight image based on Alpine Linux.
# This image includes:
# - Bash shell and CA certificates.
# - OpenTelemetry Collector Contrib binaries.
# ------------------------------------------------------------------------------

# Use the latest Alpine Linux as the base image
FROM alpine:latest

# Install Bash shell and CA certificates
RUN apk add --no-cache bash ca-certificates

# Copy binaries from the OpenTelemetry Collector Contrib image
COPY --from=otel/opentelemetry-collector-contrib:latest / /

# Set the default entrypoint to Bash
ENTRYPOINT ["/bin/bash"]
