FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        ca-certificates \
        mariadb-client \
        postgresql-client \
        rclone \
        tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 1000 backup
WORKDIR /app
COPY --chown=backup:backup src ./src
USER backup

ENTRYPOINT ["python3", "-m", "src.main"]
CMD ["scheduler"]
