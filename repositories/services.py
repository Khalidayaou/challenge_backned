"""Rules used to flag files that operations should review first."""

from django.conf import settings

from repositories.models import FileType, RepositoryFile

CONFIG_NAME_HINTS = (
    ".env",
    "settings",
    "config",
    "docker-compose",
    "nginx",
    "yaml",
    "yml",
    "ini",
    "toml",
)

SECURITY_NAME_HINTS = (
    "secret",
    "credential",
    "password",
    "passwd",
    "token",
    "id_rsa",
    ".pem",
    ".key",
    "auth",
    "certificate",
)


def assess_file(file: RepositoryFile) -> dict:
    """Return whether a file is critical and the human-readable reasons."""
    reasons = []
    threshold = getattr(settings, "CRITICAL_FILE_SIZE_BYTES", 100_000)
    name_and_path = f"{file.name} {file.path}".lower()

    if file.size_bytes >= threshold:
        reasons.append(f"taille élevée (>= {threshold} octets)")

    if file.file_type == FileType.CONFIG:
        reasons.append("fichier de configuration")
    elif any(hint in name_and_path for hint in CONFIG_NAME_HINTS):
        reasons.append("nom ou chemin typique d'un fichier de configuration")

    if file.file_type == FileType.SECURITY:
        reasons.append("fichier de sécurité")
    elif any(hint in name_and_path for hint in SECURITY_NAME_HINTS):
        reasons.append("nom ou chemin typique d'un fichier de sécurité")

    if not file.description.strip():
        reasons.append("absence de description")

    return {
        "is_critical": bool(reasons),
        "critical_reasons": reasons,
    }


def is_critical(file: RepositoryFile) -> bool:
    return assess_file(file)["is_critical"]
