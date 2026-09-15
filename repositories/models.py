from django.db import models


class FileType(models.TextChoices):
    SOURCE = "source", "Source"
    CONFIG = "config", "Configuration"
    SECURITY = "security", "Sécurité"
    DOCUMENTATION = "documentation", "Documentation"
    OTHER = "other", "Autre"


class Repository(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    owner = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RepositoryFile(models.Model):
    repository = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
        related_name="files",
    )
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=500)
    file_type = models.CharField(max_length=32, choices=FileType.choices)
    language = models.CharField(max_length=64, blank=True)
    size_bytes = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["path"]
        constraints = [
            models.UniqueConstraint(
                fields=["repository", "path"],
                name="unique_file_path_per_repository",
            )
        ]

    def __str__(self):
        return f"{self.repository.name}:{self.path}"
