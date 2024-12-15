FROM alpine:latest
RUN apk add --no-cache bash ca-certificates
COPY --from=otel/opentelemetry-collector-contrib:latest / /
ENTRYPOINT ["/bin/bash"]