"""Internal-only API for testing database connectivity without exposing secrets."""

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import time
from typing import Any

from .dump import Source, build_dump_environment
from .executor import CommandRunner


def _source(payload: dict[str, Any]) -> Source:
    engine = str(payload.get("engine", ""))
    if engine not in {"postgresql", "mysql", "mariadb"}:
        raise ValueError("unsupported engine")
    port = int(payload.get("port", 0))
    if not 1 <= port <= 65535:
        raise ValueError("invalid port")
    required = {key: str(payload.get(key, "")).strip() for key in ("id", "host", "database", "sslmode")}
    if not all(required.values()):
        raise ValueError("missing connection field")
    return Source(required["id"], required["id"], engine, "", required["host"], port,
                  required["database"], "cyriusBackup", "/run/secrets/maker-password",
                  required["sslmode"], ("00:00",), "America/Bahia", 0, False, "")


def test_connection(payload: dict[str, Any], password: str, runner: CommandRunner) -> dict[str, Any]:
    source = _source(payload)
    if source.engine == "postgresql":
        argv = ["psql", "-X", "--no-psqlrc", "--no-password", "--host", source.host, "--port",
                str(source.port), "--username", source.username, "--dbname", source.database,
                "--tuples-only", "--no-align", "--command", "SHOW server_version"]
        environment = {**build_dump_environment(source, password), "PGCONNECT_TIMEOUT": "10"}
    else:
        ssl = ["--skip-ssl"] if source.sslmode == "disabled" else ["--ssl"]
        if source.sslmode in {"verify-ca", "verify-identity"}:
            ssl.append("--ssl-verify-server-cert")
        argv = ["mariadb", "--connect-timeout=10", "--protocol=TCP", "--host", source.host,
                "--port", str(source.port), "--user", source.username, *ssl, "--batch",
                "--skip-column-names", "--execute", "SELECT VERSION()", source.database]
        environment = build_dump_environment(source, password)
    started = time.monotonic()
    result = runner.run(argv, environment)
    duration_ms = round((time.monotonic() - started) * 1000)
    if result.returncode == 0:
        return {"ok": True, "version": result.stdout.strip().splitlines()[0][:80], "latency_ms": duration_ms}
    error = result.stderr.casefold()
    if "password" in error or "access denied" in error or "authentication" in error:
        message = "Falha de autenticação"
    elif "does not exist" in error or "unknown database" in error:
        message = "Banco não encontrado"
    elif "ssl" in error or "certificate" in error:
        message = "Configuração SSL incompatível"
    elif "timed out" in error or "refused" in error or "could not connect" in error or "can't connect" in error:
        message = "Host ou porta inacessível"
    else:
        message = "Conexão rejeitada pelo servidor"
    return {"ok": False, "error": message, "latency_ms": duration_ms}


def start_control_server(password_file: Path, runner: CommandRunner, port: int = 8090) -> None:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, _format: str, *_args: Any) -> None:
            return

        def do_POST(self) -> None:  # noqa: N802
            try:
                length = min(int(self.headers.get("Content-Length", "0")), 16384)
                payload = json.loads(self.rfile.read(length) or b"{}")
                password = password_file.read_text(encoding="utf-8").rstrip("\r\n")
                response = test_connection(payload, password, runner)
            except (OSError, ValueError, KeyError, json.JSONDecodeError):
                response = {"ok": False, "error": "Dados de conexão inválidos", "latency_ms": 0}
            body = json.dumps(response, ensure_ascii=False).encode()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    threading.Thread(target=server.serve_forever, name="backup-control", daemon=True).start()
