"""Existing installation survives the project database rename."""
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import app as application


class DatabaseRenameTests(unittest.TestCase):
    def test_existing_database_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            previous = root / "previous.db"
            with closing(sqlite3.connect(previous)) as db:
                db.execute("CREATE TABLE migration_check (value TEXT)")
                db.execute("INSERT INTO migration_check VALUES ('preserved')")
                db.commit()
            original_flask = application.Flask

            def isolated_flask(*args, **kwargs):
                kwargs["instance_path"] = directory
                return original_flask(*args, **kwargs)

            with patch.object(application, "Flask", isolated_flask):
                app = application.create_app({"TESTING": True, "SECRET_KEY": "test"})
                target = Path(app.config["DATABASE"])
                self.assertEqual(target.name, "time_capsule_digital_memories.db")
                self.assertFalse(previous.exists())
                with closing(sqlite3.connect(target)) as db:
                    self.assertEqual(db.execute("SELECT value FROM migration_check").fetchone()[0], "preserved")
                self.assertEqual(app.test_client().get("/").status_code, 200)
                application.create_app({"TESTING": True, "SECRET_KEY": "test"})
