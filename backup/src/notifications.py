"""Failure notification contracts and an SMTP adapter."""

from dataclasses import dataclass
from email.message import EmailMessage
import smtplib
from typing import Callable, Protocol

from .reporting import RunReport


@dataclass(frozen=True)
class SMTPSettings:
    host: str
    port: int
    username: str
    password: str
    sender: str
    recipient: str
    starttls: bool = True


class FailureNotifier(Protocol):
    def notify(self, report: RunReport) -> None: ...


class NotificationError(RuntimeError):
    """Sanitized error safe for operational status files."""


def failure_message(report: RunReport) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = f"[ScreenDeck] Falha no backup de {report.source}"
    message.set_content(
        "\n".join(
            [
                f"Origem: {report.source}",
                f"Execução: {report.run_id}",
                f"Data/hora: {report.finished_at}",
                f"Status: {report.status}",
                f"Resumo sanitizado: {report.error or 'sem detalhe'}",
                "Consulte o relatório local para detalhes.",
            ]
        )
    )
    return message


class SMTPNotifier:
    def __init__(
        self,
        settings: SMTPSettings,
        smtp_factory: Callable[..., smtplib.SMTP] = smtplib.SMTP,
    ):
        self.settings = settings
        self.smtp_factory = smtp_factory

    def notify(self, report: RunReport) -> None:
        message = failure_message(report)
        message["From"] = self.settings.sender
        message["To"] = self.settings.recipient
        try:
            with self.smtp_factory(self.settings.host, self.settings.port, timeout=30) as client:
                if self.settings.starttls:
                    client.starttls()
                if self.settings.username:
                    client.login(self.settings.username, self.settings.password)
                client.send_message(message)
        except Exception as error:
            raise NotificationError(
                f"SMTP notification failed ({type(error).__name__})"
            ) from error
