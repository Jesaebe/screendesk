FROM python:3.12-slim-bookworm

RUN useradd --create-home --uid 1000 dashboard \
    && install -d -o dashboard -g dashboard /data /backup-status

WORKDIR /app
COPY --chown=dashboard:dashboard src ./src
COPY --chown=dashboard:dashboard static ./static

USER dashboard
EXPOSE 8080
ENTRYPOINT ["python3", "-m", "src.server"]
