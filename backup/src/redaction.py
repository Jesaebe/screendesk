"""Sanitize known secret values before persistence or notification."""


def redact(text: str, secrets: list[str]) -> str:
    result = text
    for secret in sorted((value for value in secrets if value), key=len, reverse=True):
        result = result.replace(secret, "[REDACTED]")
    return result
