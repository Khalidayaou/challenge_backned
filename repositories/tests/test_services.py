from django.test import TestCase

from repositories.models import FileType, Repository, RepositoryFile
from repositories.services import assess_file


class CriticalFileRulesTests(TestCase):
    def setUp(self):
        self.repo = Repository.objects.create(name="demo", owner="ops")

    def _file(self, **kwargs):
        defaults = {
            "repository": self.repo,
            "name": "app.py",
            "path": "src/app.py",
            "file_type": FileType.SOURCE,
            "language": "python",
            "size_bytes": 100,
            "description": "code applicatif",
        }
        defaults.update(kwargs)
        return RepositoryFile.objects.create(**defaults)

    def test_source_file_with_description_is_not_critical(self):
        file = self._file()
        result = assess_file(file)
        self.assertFalse(result["is_critical"])
        self.assertEqual(result["critical_reasons"], [])

    def test_large_file_is_critical(self):
        file = self._file(name="dump.sql", path="data/dump.sql", size_bytes=150_000, language="sql")
        result = assess_file(file)
        self.assertTrue(result["is_critical"])
        self.assertTrue(any("taille" in reason for reason in result["critical_reasons"]))

    def test_config_file_is_critical(self):
        file = self._file(
            name=".env",
            path=".env",
            file_type=FileType.CONFIG,
            language="",
            description="secrets locaux",
        )
        self.assertTrue(assess_file(file)["is_critical"])

    def test_security_file_is_critical(self):
        file = self._file(
            name="id_rsa",
            path="keys/id_rsa",
            file_type=FileType.SECURITY,
            language="",
            description="clé privée",
        )
        self.assertTrue(assess_file(file)["is_critical"])

    def test_missing_description_is_critical(self):
        file = self._file(description="")
        result = assess_file(file)
        self.assertTrue(result["is_critical"])
        self.assertIn("absence de description", result["critical_reasons"])
