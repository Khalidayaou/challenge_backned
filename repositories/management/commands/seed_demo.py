from django.core.management.base import BaseCommand

from repositories.models import FileType, Repository, RepositoryFile


class Command(BaseCommand):
    help = "Charge un jeu de données de démonstration."

    def handle(self, *args, **options):
        repo, _ = Repository.objects.get_or_create(
            name="billing-api",
            defaults={
                "description": "API de facturation",
                "owner": "ops",
            },
        )
        samples = [
            {
                "name": "views.py",
                "path": "billing/views.py",
                "file_type": FileType.SOURCE,
                "language": "python",
                "size_bytes": 2400,
                "description": "Vues REST de facturation",
            },
            {
                "name": ".env",
                "path": "billing/.env",
                "file_type": FileType.CONFIG,
                "language": "",
                "size_bytes": 320,
                "description": "",
            },
            {
                "name": "id_rsa",
                "path": "deploy/id_rsa",
                "file_type": FileType.SECURITY,
                "language": "",
                "size_bytes": 1700,
                "description": "Clé de déploiement — à ne pas commiter",
            },
            {
                "name": "dump.sql",
                "path": "data/dump.sql",
                "file_type": FileType.OTHER,
                "language": "sql",
                "size_bytes": 250000,
                "description": "Export de base",
            },
        ]
        created = 0
        for sample in samples:
            _, was_created = RepositoryFile.objects.get_or_create(
                repository=repo,
                path=sample["path"],
                defaults=sample,
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Démo prête (fichiers créés: {created})."))
