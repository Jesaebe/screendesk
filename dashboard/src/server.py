"""Small dependency-free dashboard and API server."""

from __future__ import annotations

import base64
import calendar
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import hmac
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import re
import secrets
import time
import tomllib
from .host_metrics import HostMetrics
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlencode, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


APP_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = APP_ROOT / "static"
DATA_ROOT = Path(os.environ.get("DASHBOARD_DATA_ROOT", "/data"))
BACKUP_ROOT = Path(os.environ.get("BACKUP_STATUS_ROOT", "/backup-status"))
SETTINGS_PATH = DATA_ROOT / "settings.json"
TOKEN_PATH = DATA_ROOT / "google-token.json"
PUBLIC_URL = os.environ.get("DASHBOARD_PUBLIC_URL", "http://localhost:8123").rstrip("/")
GOOGLE_SECRET = Path(os.environ.get("GOOGLE_CLIENT_SECRET_FILE", "/run/secrets/google-client.json"))
SMARTTHINGS_TOKEN = Path(os.environ.get("SMARTTHINGS_TOKEN_FILE", "/run/secrets/smartthings-token"))
PASSWORD_FILE = Path(os.environ.get("DASHBOARD_PASSWORD_FILE", "/run/secrets/dashboard-password"))
BACKUP_CONFIG_PATH = Path(os.environ.get("BACKUP_CONFIG_PATH", "/backup-config/sources.toml"))
BACKUP_CONTROL_URL = os.environ.get("BACKUP_CONTROL_URL", "http://backup:8090/test")
USERNAME = os.environ.get("DASHBOARD_USERNAME", "admin")
OAUTH_STATES: dict[str, float] = {}
WEATHER_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
TESTED_BACKUP_SOURCES: dict[str, str] = {}
HOST_METRICS = HostMetrics(
    Path(os.environ.get("HOST_PROC_ROOT", "/host/proc")),
    Path(os.environ.get("HOST_ROOT_PATH", "/host/root")),
    Path(os.environ.get("HOST_BACKUP_PATH", "/host/backups")),
    DATA_ROOT / "host-metrics.jsonl",
    BACKUP_ROOT / "service-status.json",
    interval_seconds=int(os.environ.get("HOST_METRICS_INTERVAL_SECONDS", "1")),
    history_interval_seconds=int(os.environ.get("HOST_METRICS_HISTORY_INTERVAL_SECONDS", "60")),
)


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, PermissionError, json.JSONDecodeError):
        return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(temporary, 0o600)
    temporary.replace(path)


SOURCE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")
SOURCE_FIELDS = ("id", "display_name", "engine", "version", "host", "port", "database", "sslmode",
                 "schedule", "timezone", "estimated_size_mb", "enabled", "readiness_note")


def validate_backup_source(raw: dict[str, Any]) -> dict[str, Any]:
    source = {key: raw.get(key) for key in SOURCE_FIELDS}
    source["id"] = str(source["id"] or "").strip().lower()
    source["display_name"] = str(source["display_name"] or source["id"]).strip()
    source["engine"] = str(source["engine"] or "").lower()
    source["version"] = str(source["version"] or "").strip()
    source["host"] = str(source["host"] or "").strip()
    source["database"] = str(source["database"] or "").strip()
    source["sslmode"] = str(source["sslmode"] or "require").lower()
    source["timezone"] = str(source["timezone"] or "America/Bahia")
    source["readiness_note"] = str(source["readiness_note"] or "Gerenciado pelo dashboard.").strip()
    if not SOURCE_ID.fullmatch(source["id"]):
        raise ValueError("Identificador deve usar letras minúsculas, números e hífens")
    if source["engine"] not in {"postgresql", "mysql", "mariadb"}:
        raise ValueError("Tipo de banco inválido")
    valid_ssl = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"} if source["engine"] == "postgresql" else {"disabled", "preferred", "required", "verify-ca", "verify-identity"}
    if source["sslmode"] not in valid_ssl:
        raise ValueError("Modo SSL inválido para o tipo de banco")
    if not source["host"] or not source["database"] or not source["display_name"]:
        raise ValueError("Nome, host e banco são obrigatórios")
    source["port"] = int(source["port"])
    source["estimated_size_mb"] = int(source["estimated_size_mb"] or 0)
    if not 1 <= source["port"] <= 65535 or source["estimated_size_mb"] < 0:
        raise ValueError("Porta ou tamanho estimado inválido")
    schedule = source["schedule"]
    if isinstance(schedule, str):
        schedule = [value.strip() for value in schedule.split(",") if value.strip()]
    if not isinstance(schedule, list) or not schedule:
        raise ValueError("Informe ao menos um horário")
    for value in schedule:
        if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", str(value)):
            raise ValueError(f"Horário inválido: {value}")
    source["schedule"] = [str(value) for value in schedule]
    ZoneInfo(source["timezone"])
    source["enabled"] = bool(source["enabled"])
    source["username"] = "cyriusBackup"
    source["password_file"] = "/run/secrets/maker-password"
    return source


def backup_source_fingerprint(source: dict[str, Any]) -> str:
    fields = {key: source[key] for key in ("id", "engine", "host", "port", "database", "sslmode")}
    return hashlib.sha256(json.dumps(fields, sort_keys=True).encode()).hexdigest()


def load_backup_sources() -> list[dict[str, Any]]:
    with BACKUP_CONFIG_PATH.open("rb") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_SH)
        payload = tomllib.load(stream)
    return [validate_backup_source(item) for item in payload.get("source", [])]


def serialize_backup_sources(sources: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for source in sources:
        lines.extend(["[[source]]", *[
            f'{key} = {json.dumps(source[key], ensure_ascii=False)}'
            for key in ("id", "display_name", "engine", "version", "host")
        ], f'port = {source["port"]}', f'database = {json.dumps(source["database"], ensure_ascii=False)}',
            'username = "cyriusBackup"', 'password_file = "/run/secrets/maker-password"',
            f'sslmode = {json.dumps(source["sslmode"])}',
            "schedule = [" + ", ".join(json.dumps(value) for value in source["schedule"]) + "]",
            f'timezone = {json.dumps(source["timezone"])}', f'estimated_size_mb = {source["estimated_size_mb"]}',
            f'enabled = {str(source["enabled"]).lower()}',
            f'readiness_note = {json.dumps(source["readiness_note"], ensure_ascii=False)}', ""])
    return "\n".join(lines)


def save_backup_sources(sources: list[dict[str, Any]]) -> None:
    validated = [validate_backup_source(source) for source in sources]
    if not validated or len({source["id"] for source in validated}) != len(validated):
        raise ValueError("O cadastro precisa ter origens com identificadores únicos")
    content = serialize_backup_sources(validated)
    with BACKUP_CONFIG_PATH.open("r+", encoding="utf-8") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        previous = stream.read()
        write_json(DATA_ROOT / "sources-config-backup.json", {"toml": previous})
        stream.seek(0)
        stream.write(content)
        stream.truncate()
        stream.flush()
        os.fsync(stream.fileno())


def request_json(url: str, *, method: str = "GET", headers: dict[str, str] | None = None,
                 body: dict[str, Any] | None = None, form: dict[str, str] | None = None) -> dict[str, Any]:
    data = None
    final_headers = {"Accept": "application/json", **(headers or {})}
    if body is not None:
        data = json.dumps(body).encode()
        final_headers["Content-Type"] = "application/json"
    elif form is not None:
        data = urlencode(form).encode()
        final_headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = Request(url, data=data, headers=final_headers, method=method)
    try:
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode())
    except HTTPError as error:
        detail = error.read().decode(errors="replace")[:500]
        raise RuntimeError(f"Serviço externo retornou HTTP {error.code}: {detail}") from error
    except URLError as error:
        raise RuntimeError("Não foi possível acessar o serviço externo") from error


def google_client() -> dict[str, Any] | None:
    payload = read_json(GOOGLE_SECRET, None)
    if not payload:
        return None
    return payload.get("web") or payload.get("installed")


def google_token() -> dict[str, Any] | None:
    token = read_json(TOKEN_PATH, None)
    if not token:
        return None
    if token.get("expires_at", 0) > time.time() + 60:
        return token
    client = google_client()
    if not client or not token.get("refresh_token"):
        return None
    refreshed = request_json(
        "https://oauth2.googleapis.com/token",
        method="POST",
        form={
            "client_id": client["client_id"],
            "client_secret": client["client_secret"],
            "refresh_token": token["refresh_token"],
            "grant_type": "refresh_token",
        },
    )
    token.update(refreshed)
    token["expires_at"] = time.time() + int(refreshed.get("expires_in", 3600))
    write_json(TOKEN_PATH, token)
    return token


def google_api(url: str, *, method: str = "GET", body: dict[str, Any] | None = None) -> dict[str, Any]:
    token = google_token()
    if not token:
        raise PermissionError("Google ainda não foi conectado")
    return request_json(url, method=method, headers={"Authorization": f"Bearer {token['access_token']}"}, body=body)


def weather(city: str) -> dict[str, Any]:
    normalized = city.strip()[:100]
    cached = WEATHER_CACHE.get(normalized.casefold())
    if cached and cached[0] > time.time():
        return cached[1]
    geo = request_json(
        "https://geocoding-api.open-meteo.com/v1/search?" +
        urlencode({"name": normalized, "count": 1, "language": "pt", "format": "json"})
    )
    results = geo.get("results", [])
    if not results:
        raise ValueError("Cidade não encontrada")
    place = results[0]
    forecast = request_json(
        "https://api.open-meteo.com/v1/forecast?" + urlencode({
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto",
            "forecast_days": 5,
        })
    )
    result = {"place": {"name": place["name"], "admin1": place.get("admin1"), "country": place.get("country")}, **forecast}
    WEATHER_CACHE[normalized.casefold()] = (time.time() + 600, result)
    return result


def google_data(month: str | None = None) -> dict[str, Any]:
    settings = read_json(SETTINGS_PATH, {})
    calendar_ids = settings.get("calendar_ids", [])
    tasklist_ids = settings.get("tasklist_ids", [])
    calendars = google_api("https://www.googleapis.com/calendar/v3/users/me/calendarList").get("items", [])
    tasklists = google_api("https://tasks.googleapis.com/tasks/v1/users/@me/lists").get("items", [])
    if not calendar_ids:
        calendar_ids = [item["id"] for item in calendars]
    if not tasklist_ids:
        tasklist_ids = [item["id"] for item in tasklists]
    current = datetime.now(timezone.utc)
    if month:
        try:
            year, month_number = (int(value) for value in month.split("-", 1))
            month_start = datetime(year, month_number, 1, tzinfo=timezone.utc)
        except (TypeError, ValueError):
            raise ValueError("Mês inválido; use AAAA-MM") from None
    else:
        month_start = datetime(current.year, current.month, 1, tzinfo=timezone.utc)
    month_end = month_start + timedelta(days=calendar.monthrange(month_start.year, month_start.month)[1])
    time_min = month_start.isoformat().replace("+00:00", "Z")
    time_max = month_end.isoformat().replace("+00:00", "Z")
    events: list[dict[str, Any]] = []
    for calendar_id in calendar_ids[:20]:
        url = "https://www.googleapis.com/calendar/v3/calendars/" + quote(calendar_id, safe="") + "/events?" + urlencode({
            "timeMin": time_min, "timeMax": time_max, "singleEvents": "true", "orderBy": "startTime", "maxResults": 50,
        })
        for event in google_api(url).get("items", []):
            events.append({"id": event.get("id"), "summary": event.get("summary", "Sem título"),
                           "start": event.get("start", {}), "end": event.get("end", {}),
                           "calendar_id": calendar_id})
    tasks: list[dict[str, Any]] = []
    for tasklist_id in tasklist_ids[:20]:
        url = "https://tasks.googleapis.com/tasks/v1/lists/" + quote(tasklist_id, safe="") + "/tasks?" + urlencode({
            "showCompleted": "false", "showHidden": "false", "maxResults": 30,
        })
        for task in google_api(url).get("items", []):
            tasks.append({"id": task["id"], "title": task.get("title", "Sem título"), "due": task.get("due"),
                          "notes": task.get("notes"), "tasklist_id": tasklist_id})
    events.sort(key=lambda item: item["start"].get("dateTime") or item["start"].get("date") or "")
    return {"month": month_start.strftime("%Y-%m"), "calendars": calendars, "tasklists": tasklists,
            "events": events[:100], "tasks": tasks[:60]}


def smartthings(path: str, *, method: str = "GET", body: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        token = SMARTTHINGS_TOKEN.read_text(encoding="utf-8").strip()
    except (FileNotFoundError, PermissionError):
        raise PermissionError("SmartThings ainda não foi conectado") from None
    return request_json("https://api.smartthings.com/v1" + path, method=method,
                        headers={"Authorization": f"Bearer {token}"}, body=body)


class Handler(SimpleHTTPRequestHandler):
    server_version = "ScreenDeck/1"

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"{self.client_address[0]} {fmt % args}")

    def authenticated(self) -> bool:
        if not PASSWORD_FILE.exists():
            return True
        try:
            expected_password = PASSWORD_FILE.read_text(encoding="utf-8").strip()
            scheme, encoded = self.headers.get("Authorization", " ").split(" ", 1)
            supplied = base64.b64decode(encoded).decode().split(":", 1)
            return scheme.lower() == "basic" and len(supplied) == 2 and supplied[0] == USERNAME and hmac.compare_digest(supplied[1], expected_password)
        except (ValueError, UnicodeError):
            return False

    def require_auth(self) -> bool:
        if self.authenticated():
            return False
        self.send_response(HTTPStatus.UNAUTHORIZED)
        self.send_header("WWW-Authenticate", 'Basic realm="ScreenDeck"')
        self.end_headers()
        return True

    def send_json(self, value: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        payload = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def body_json(self) -> dict[str, Any]:
        length = min(int(self.headers.get("Content-Length", "0")), 65536)
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/healthz":
            self.send_json({"status": "ok"})
            return
        if self.require_auth():
            return
        try:
            if parsed.path == "/api/overview":
                settings = read_json(SETTINGS_PATH, {"city": "Salvador"})
                self.send_json({"settings": settings, "backup": read_json(BACKUP_ROOT / "latest.json", None),
                                "google_connected": google_token() is not None,
                                "smartthings_connected": SMARTTHINGS_TOKEN.exists()})
            elif parsed.path == "/api/backup/status":
                self.send_json({
                    "latest": read_json(BACKUP_ROOT / "latest.json", None),
                    "active": read_json(BACKUP_ROOT / "active-backup.json", None),
                })
            elif parsed.path == "/api/backups":
                lines = []
                try:
                    lines = (BACKUP_ROOT / "history.jsonl").read_text(encoding="utf-8").splitlines()[-30:]
                except (FileNotFoundError, PermissionError):
                    pass
                self.send_json({"items": [json.loads(line) for line in reversed(lines) if line.strip()]})
            elif parsed.path == "/api/backup/sources":
                self.send_json({"items": load_backup_sources(), "username": "cyriusBackup"})
            elif parsed.path == "/api/host/metrics":
                self.send_json({"current": HOST_METRICS.snapshot(), "history": HOST_METRICS.history()})
            elif parsed.path == "/api/weather":
                query = parse_qs(parsed.query)
                city = query.get("city", [read_json(SETTINGS_PATH, {}).get("city", "Salvador")])[0]
                self.send_json(weather(city))
            elif parsed.path == "/api/google/data":
                query = parse_qs(parsed.query)
                self.send_json(google_data(query.get("month", [None])[0]))
            elif parsed.path == "/api/google/auth/start":
                client = google_client()
                if not client:
                    raise FileNotFoundError("Credencial OAuth do Google não instalada")
                state = secrets.token_urlsafe(32)
                OAUTH_STATES[state] = time.time() + 600
                params = {"client_id": client["client_id"], "redirect_uri": PUBLIC_URL + "/oauth/google/callback",
                          "response_type": "code", "access_type": "offline", "prompt": "consent", "state": state,
                          "scope": "https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/tasks"}
                self.send_response(HTTPStatus.FOUND)
                self.send_header("Location", "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params))
                self.end_headers()
            elif parsed.path == "/oauth/google/callback":
                query = parse_qs(parsed.query)
                state = query.get("state", [""])[0]
                if OAUTH_STATES.pop(state, 0) < time.time():
                    raise PermissionError("Estado OAuth inválido ou expirado")
                client = google_client() or {}
                token = request_json("https://oauth2.googleapis.com/token", method="POST", form={
                    "code": query["code"][0], "client_id": client["client_id"], "client_secret": client["client_secret"],
                    "redirect_uri": PUBLIC_URL + "/oauth/google/callback", "grant_type": "authorization_code",
                })
                token["expires_at"] = time.time() + int(token.get("expires_in", 3600))
                write_json(TOKEN_PATH, token)
                self.send_response(HTTPStatus.FOUND)
                self.send_header("Location", "/")
                self.end_headers()
            elif parsed.path == "/api/smartthings/devices":
                self.send_json(smartthings("/devices"))
            elif parsed.path.startswith("/api/smartthings/status/"):
                device_id = quote(parsed.path.rsplit("/", 1)[-1], safe="")
                self.send_json(smartthings(f"/devices/{device_id}/status"))
            elif parsed.path.startswith("/api/"):
                self.send_json({"error": "Endpoint não encontrado"}, HTTPStatus.NOT_FOUND)
            else:
                self.serve_static(parsed.path)
        except (ValueError, KeyError, PermissionError, FileNotFoundError, RuntimeError) as error:
            status = HTTPStatus.UNAUTHORIZED if isinstance(error, PermissionError) else HTTPStatus.BAD_GATEWAY
            self.send_json({"error": str(error)}, status)

    def do_POST(self) -> None:  # noqa: N802
        if self.require_auth():
            return
        parsed = urlparse(self.path)
        try:
            payload = self.body_json()
            if parsed.path == "/api/settings":
                settings = read_json(SETTINGS_PATH, {})
                for key in ("city", "calendar_ids", "tasklist_ids", "smartthings_device_id"):
                    if key in payload:
                        settings[key] = payload[key]
                write_json(SETTINGS_PATH, settings)
                self.send_json(settings)
            elif parsed.path == "/api/backup/sources":
                candidate = validate_backup_source(payload)
                sources = load_backup_sources()
                existing = next((source for source in sources if source["id"] == candidate["id"]), None)
                connection_changed = existing is None or backup_source_fingerprint(existing) != backup_source_fingerprint(candidate)
                activation = candidate["enabled"] and (existing is None or not existing["enabled"] or connection_changed)
                if activation and TESTED_BACKUP_SOURCES.get(candidate["id"]) != backup_source_fingerprint(candidate):
                    raise ValueError("Teste a conexão com sucesso antes de ativar esta origem")
                replaced = False
                for index, source in enumerate(sources):
                    if source["id"] == candidate["id"]:
                        sources[index] = candidate
                        replaced = True
                        break
                if not replaced:
                    sources.append(candidate)
                save_backup_sources(sources)
                self.send_json(candidate)
            elif parsed.path == "/api/backup/sources/test":
                candidate = validate_backup_source(payload)
                result = request_json(BACKUP_CONTROL_URL, method="POST", body=candidate)
                if result.get("ok"):
                    TESTED_BACKUP_SOURCES[candidate["id"]] = backup_source_fingerprint(candidate)
                self.send_json(result)
            elif parsed.path == "/api/backup/sources/delete":
                identifier = str(payload["id"])
                sources = load_backup_sources()
                target = next((source for source in sources if source["id"] == identifier), None)
                if target is None:
                    raise ValueError("Origem não encontrada")
                if target["enabled"]:
                    raise ValueError("Pause a origem antes de removê-la")
                remaining = [source for source in sources if source["id"] != identifier]
                if not remaining:
                    raise ValueError("Não é possível remover a única origem cadastrada")
                save_backup_sources(remaining)
                self.send_json({"removed": identifier})
            elif parsed.path == "/api/google/task/complete":
                list_id = quote(payload["tasklist_id"], safe="")
                task_id = quote(payload["task_id"], safe="")
                self.send_json(google_api(f"https://tasks.googleapis.com/tasks/v1/lists/{list_id}/tasks/{task_id}",
                                          method="PATCH", body={"status": "completed"}))
            elif parsed.path == "/api/smartthings/command":
                settings = read_json(SETTINGS_PATH, {})
                device_id = quote(settings["smartthings_device_id"], safe="")
                command = payload["command"]
                allowed = {
                    "on": {"component": "main", "capability": "switch", "command": "on"},
                    "off": {"component": "main", "capability": "switch", "command": "off"},
                    "cool": {"component": "main", "capability": "airConditionerMode", "command": "setAirConditionerMode", "arguments": ["cool"]},
                    "temperature": {"component": "main", "capability": "thermostatCoolingSetpoint", "command": "setCoolingSetpoint", "arguments": [int(payload["value"])]},
                }
                if command not in allowed:
                    raise ValueError("Comando não permitido")
                self.send_json(smartthings(f"/devices/{device_id}/commands", method="POST", body={"commands": [allowed[command]]}))
            else:
                self.send_json({"error": "Endpoint não encontrado"}, HTTPStatus.NOT_FOUND)
        except (ValueError, KeyError, PermissionError, RuntimeError) as error:
            status = HTTPStatus.UNAUTHORIZED if isinstance(error, PermissionError) else HTTPStatus.BAD_REQUEST
            self.send_json({"error": str(error)}, status)

    def serve_static(self, path: str) -> None:
        relative = "index.html" if path == "/" else path.lstrip("/")
        target = (STATIC_ROOT / relative).resolve()
        if STATIC_ROOT not in target.parents and target != STATIC_ROOT:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not target.is_file():
            target = STATIC_ROOT / "index.html"
        content = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main() -> None:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    HOST_METRICS.start()
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    print("ScreenDeck dashboard listening on 0.0.0.0:8080", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
