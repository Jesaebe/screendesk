"""Load and validate versionable backup source definitions."""

from pathlib import Path
import re
import tomllib

from .dump import Source


IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")
VALID_ENGINES = {"postgresql", "mysql", "mariadb"}
POSTGRES_SSL_MODES = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}
MYSQL_SSL_MODES = {"disabled", "preferred", "required", "verify-ca", "verify-identity"}


def validate_time(value: str) -> None:
    try:
        hour_text, minute_text = value.split(":", 1)
        hour, minute = int(hour_text), int(minute_text)
    except (ValueError, AttributeError) as error:
        raise ValueError(f"invalid schedule time: {value!r}") from error
    if len(value) != 5 or not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError(f"invalid schedule time: {value!r}")


def load_sources(path: Path) -> list[Source]:
    with path.open("rb") as stream:
        payload = tomllib.load(stream)

    raw_sources = payload.get("source", [])
    if not isinstance(raw_sources, list) or not raw_sources:
        raise ValueError("configuration must contain at least one [[source]]")

    sources: list[Source] = []
    identifiers: set[str] = set()
    for raw in raw_sources:
        identifier = str(raw["id"])
        engine = str(raw["engine"])
        schedule = tuple(str(item) for item in raw["schedule"])
        if not IDENTIFIER.fullmatch(identifier):
            raise ValueError(f"invalid source id: {identifier!r}")
        if identifier in identifiers:
            raise ValueError(f"duplicate source id: {identifier}")
        if engine not in VALID_ENGINES:
            raise ValueError(f"unsupported database engine: {engine}")
        sslmode = str(raw.get("sslmode", "require"))
        valid_ssl_modes = POSTGRES_SSL_MODES if engine == "postgresql" else MYSQL_SSL_MODES
        if sslmode not in valid_ssl_modes:
            raise ValueError(f"invalid sslmode for {identifier}: {sslmode}")
        if not schedule:
            raise ValueError(f"source {identifier} has no schedule")
        for scheduled_time in schedule:
            validate_time(scheduled_time)

        source = Source(
            identifier=identifier,
            display_name=str(raw.get("display_name", identifier)),
            engine=engine,
            version=str(raw.get("version", "")),
            host=str(raw["host"]),
            port=int(raw["port"]),
            database=str(raw["database"]),
            username=str(raw["username"]),
            password_file=str(raw["password_file"]),
            sslmode=sslmode,
            schedule=schedule,
            timezone=str(raw.get("timezone", "UTC")),
            estimated_size_mb=int(raw.get("estimated_size_mb", 0)),
            enabled=bool(raw.get("enabled", False)),
            readiness_note=str(raw.get("readiness_note", "")),
        )
        if not 1 <= source.port <= 65535:
            raise ValueError(f"invalid port for {identifier}: {source.port}")
        password_path = Path(source.password_file)
        if not password_path.is_absolute() or password_path.parent != Path("/run/secrets"):
            raise ValueError(
                f"password_file for {identifier} must be an absolute path below /run/secrets"
            )
        identifiers.add(identifier)
        sources.append(source)
    return sources
