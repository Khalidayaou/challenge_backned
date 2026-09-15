from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from repositories.models import FileType, Repository, RepositoryFile


class RepositoryApiTests(APITestCase):
    def test_create_and_list_repositories(self):
        create_url = reverse("repository-list")
        response = self.client.post(
            create_url,
            {"name": "billing-api", "description": "API facturation", "owner": "ops"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        listing = self.client.get(create_url)
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(listing.data["count"], 1)
        self.assertEqual(listing.data["results"][0]["name"], "billing-api")

    def test_repository_detail_includes_files(self):
        repo = Repository.objects.create(name="core", owner="ops")
        RepositoryFile.objects.create(
            repository=repo,
            name="models.py",
            path="core/models.py",
            file_type=FileType.SOURCE,
            language="python",
            size_bytes=800,
            description="modèles",
        )
        url = reverse("repository-detail", args=[repo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["files_count"], 1)
        self.assertEqual(len(response.data["files"]), 1)

    def test_add_file_to_repository(self):
        repo = Repository.objects.create(name="webhooks", owner="ops")
        url = reverse("repository-files", args=[repo.id])
        response = self.client.post(
            url,
            {
                "name": ".env",
                "path": "webhooks/.env",
                "file_type": "config",
                "language": "",
                "size_bytes": 120,
                "description": "",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["is_critical"])
        self.assertEqual(repo.files.count(), 1)


class FileSearchAndCriticalApiTests(APITestCase):
    def setUp(self):
        self.repo = Repository.objects.create(name="platform", owner="ops")
        RepositoryFile.objects.create(
            repository=self.repo,
            name="app.py",
            path="src/app.py",
            file_type=FileType.SOURCE,
            language="python",
            size_bytes=400,
            description="entrée applicative",
        )
        RepositoryFile.objects.create(
            repository=self.repo,
            name="settings.yaml",
            path="config/settings.yaml",
            file_type=FileType.CONFIG,
            language="yaml",
            size_bytes=900,
            description="",
        )

    def test_search_by_name_language_and_type(self):
        by_name = self.client.get(reverse("file-list"), {"name": "app"})
        self.assertEqual(by_name.data["count"], 1)

        by_language = self.client.get(reverse("file-list"), {"language": "python"})
        self.assertEqual(by_language.data["count"], 1)

        by_type = self.client.get(reverse("file-list"), {"type": "config"})
        self.assertEqual(by_type.data["count"], 1)

    def test_critical_endpoint_returns_flagged_files(self):
        response = self.client.get(reverse("file-critical"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data["results"]]
        self.assertIn("settings.yaml", names)
        self.assertNotIn("app.py", names)
