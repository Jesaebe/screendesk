FROM python:3.12-slim-bookworm

ARG SCREENDECK_GIT_COMMIT=unknown
ARG SCREENDECK_BUILD_TIME=unknown
ENV SCREENDECK_GIT_COMMIT=$SCREENDECK_GIT_COMMIT \
    SCREENDECK_BUILD_TIME=$SCREENDECK_BUILD_TIME

RUN useradd --create-home --uid 1000 dashboard \
    && install -d -o dashboard -g dashboard /data /backup-status

WORKDIR /app
COPY --chown=dashboard:dashboard VERSION ./VERSION
COPY --chown=dashboard:dashboard src ./src
COPY --chown=dashboard:dashboard static ./static

USER dashboard
EXPOSE 8080
ENTRYPOINT ["python3", "-m", "src.server"]
