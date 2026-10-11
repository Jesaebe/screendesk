"""Build safe argv lists for native logical backup tools."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    identifier: str
    display_name: str
    engine: str
    version: str
    host: str
    port: int
    database: str
    username: str
    password_file: str
    sslmode: str
    schedule: tuple[str, ...]
    timezone: str
    estimated_size_mb: int
    enabled: bool
    readiness_note: str


def build_dump_command(source: Source, destination: str) -> list[str]:
    """Return argv without invoking a shell or embedding a password."""
    if source.engine == "postgresql":
        return [
            "pg_dump",
            "--format=custom",
            "--no-password",
            "--host",
            source.host,
            "--port",
            str(source.port),
            "--username",
            source.username,
            "--file",
            destination,
            source.database,
        ]
    if source.engine in {"mysql", "mariadb"}:
        return [
            "mariadb-dump",
            "--single-transaction",
            "--quick",
            "--host",
            source.host,
            "--port",
            str(source.port),
            "--user",
            source.username,
            "--result-file",
            destination,
            source.database,
        ]
    raise ValueError(f"unsupported database engine: {source.engine}")


def build_dump_environment(source: Source, password: str) -> dict[str, str]:
    """Return client-specific secrets and TLS settings for subprocess env."""
    if source.engine == "postgresql":
        return {"PGPASSWORD": password, "PGSSLMODE": source.sslmode}
    if source.engine in {"mysql", "mariadb"}:
        # MYSQL_PWD avoids a password in argv, but the future runner should prefer
        # a temporary mode-0600 option file when the client version supports it.
        return {"MYSQL_PWD": password}
    raise ValueError(f"unsupported database engine: {source.engine}")
