FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
COPY templates/ templates/

RUN pip install --no-cache-dir ".[gateway]"

ENV LOOM_TRANSPORT=sse
ENV LOOM_LOG_LEVEL=info

EXPOSE 8443

HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost:8443/health || exit 1

# Initialize workspace if not mounted
RUN mkdir -p /workspace/.loom

WORKDIR /workspace

CMD ["loom", "gateway", "start", "--port", "8443"]
