"""Sprint 2 acceptance tests use isolated temporary databases and uploads."""
import io
import sqlite3
import unittest
from pathlib import Path
from unittest.mock import patch
from werkzeug.security import generate_password_hash
from werkzeug.datastructures import FileStorage
import test_accounts
from app import create_app


class CapsuleTests(unittest.TestCase):
    # Reuse only fixtures/helpers, not the account test methods.
    tearDown = test_accounts.AccountTests.tearDown
    post = test_accounts.AccountTests.post
    register = test_accounts.AccountTests.register

    def setUp(self):
        test_accounts.AccountTests.setUp(self)
        self.register()

    def draft(self, **overrides):
        return self.post('/capsules/new', {
            'title': 'My first memory', 'message': 'A private letter.',
            'theme': 'rose', **overrides,
        })

    def png(self, name='photo.png'):
        return io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'header fixture'), name

    def test_create_edit_and_cover(self):
        self.assertEqual(self.draft().status_code, 302)
        self.assertIn(b'My first memory', self.client.get('/dashboard').data)
        self.assertIn(b'A private letter.', self.client.get('/capsules/1').data)
        self.assertEqual(self.client.get('/capsules/1/edit').status_code, 200)
        response = self.post('/capsules/1/edit', {
            'title': 'Updated title', 'message': 'New words.', 'theme': 'forest',
        })
        self.assertEqual(response.status_code, 302)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT title, theme FROM capsules').fetchone(),
                             ('Updated title', 'forest'))

    def test_upload_download_and_retain_on_edit(self):
        self.assertEqual(self.draft(files=self.png()).status_code, 302)
        with self.client.get('/attachments/1') as response:
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.data.startswith(b'\x89PNG'))
            self.assertIn('attachment;', response.headers['Content-Disposition'])
        self.post('/capsules/1/edit', {'title': 'New', 'message': 'Still here', 'theme': 'sky'})
        self.assertIn(b'photo.png', self.client.get('/capsules/1').data)

    def test_video_and_multiple_attachments(self):
        mp4 = (io.BytesIO(b'\x00\x00\x00\x20ftypisom' + b'video fixture'), 'video.mp4')
        self.assertEqual(self.draft(files=[self.png(), mp4]).status_code, 302)
        with sqlite3.connect(self.database) as db:
            self.assertEqual([r[0] for r in db.execute('SELECT kind FROM attachments ORDER BY id')],
                             ['image', 'video'])

    def test_owner_only_on_every_route(self):
        self.draft(files=self.png())
        self.post('/logout')
        self.register(email='other@example.com')
        for path in ('/capsules/1', '/capsules/1/edit', '/capsules/1/delete', '/attachments/1'):
            self.assertEqual(self.client.get(path).status_code, 404)
        self.assertEqual(self.post('/capsules/1/edit', {
            'title': 'Intrusion', 'message': 'Bad', 'theme': 'sky',
        }).status_code, 404)
        self.assertEqual(self.post('/capsules/1/delete', {'confirm': 'delete'}).status_code, 404)
        self.assertNotIn(b'My first memory', self.client.get('/dashboard').data)

    def test_delete_requires_confirmation_and_cleans_up(self):
        self.draft(files=self.png())
        self.assertEqual(self.client.get('/capsules/1/delete').status_code, 200)
        self.assertEqual(self.client.get('/capsules/1').status_code, 200)
        self.assertEqual(self.post('/capsules/1/delete').status_code, 400)
        self.assertEqual(self.post('/capsules/1/delete', {'confirm': 'delete'}).status_code, 302)
        self.assertEqual(self.client.get('/capsules/1').status_code, 404)
        self.assertEqual(self.client.get('/attachments/1').status_code, 404)
        self.assertEqual(list(Path(self.app.config['UPLOAD_FOLDER']).iterdir()), [])
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM attachments').fetchone()[0], 0)

    def test_bad_extension_and_disguised_file(self):
        for name in ('bad.html', 'disguised.png'):
            self.assertEqual(self.draft(files=(io.BytesIO(b'<script>bad</script>'), name)).status_code, 400)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM capsules').fetchone()[0], 0)

    def test_input_limits_and_theme_validation(self):
        for bad in ({'title': ''}, {'message': ''}, {'title': 'x'*101},
                    {'message': 'x'*20001}, {'theme': '<script>'}):
            self.assertEqual(self.draft(**bad).status_code, 400)

    def test_count_limit_includes_existing_files(self):
        self.draft(files=[self.png(f'{i}.png') for i in range(10)])
        response = self.post('/capsules/1/edit', {
            'title': 'Too many', 'message': 'Words', 'theme': 'sky', 'files': self.png(),
        })
        self.assertEqual(response.status_code, 400)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM attachments').fetchone()[0], 10)

    def test_request_size_limit(self):
        self.app.config['MAX_CONTENT_LENGTH'] = 100
        self.assertEqual(self.draft(message='x'*1000).status_code, 413)

    def test_csrf_blocks_draft_mutations(self):
        self.draft()
        self.assertEqual(self.client.post('/capsules/1/delete', data={'confirm': 'delete'}).status_code, 400)
        self.assertEqual(self.client.get('/capsules/1').status_code, 200)

    def test_markup_escaped_in_capsule(self):
        self.draft(title='<script>alert(1)</script>', message='<img src=x onerror=alert(1)>')
        response = self.client.get('/capsules/1')
        self.assertIn(b'&lt;script&gt;', response.data)
        self.assertNotIn(b'<img src=x', response.data)

    def test_failed_upload_rolls_back(self):
        def fail_save(upload, destination):
            Path(destination).write_bytes(b'partial')
            raise OSError('Simulated disk full')
        with patch.object(FileStorage, 'save', fail_save):
            self.assertEqual(self.draft(files=self.png()).status_code, 500)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM capsules').fetchone()[0], 0)
        self.assertEqual(list(Path(self.app.config['UPLOAD_FOLDER']).iterdir()), [])

    def test_sprint_one_database_upgrade(self):
        old_db = str(Path(self.temp.name) / 'sprint-one.db')
        with sqlite3.connect(old_db) as db:
            db.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL)')
            db.execute('INSERT INTO users VALUES (1, ?, ?, ?)', (
                'Existing user', 'old@example.com', generate_password_hash('ExistingPass123'),
            ))
        upgraded = create_app({'TESTING': True, 'SECRET_KEY': 'test-key', 'DATABASE': old_db,
                              'UPLOAD_FOLDER': str(Path(self.temp.name) / 'old-uploads')})
        client = upgraded.test_client()
        with client.session_transaction() as s:
            s['csrf'] = 'upgrade-token'
        self.assertEqual(client.post('/login', data={
            'csrf': 'upgrade-token', 'email': 'old@example.com', 'password': 'ExistingPass123',
        }).status_code, 302)
        self.assertIn(b'Existing user', client.get('/dashboard').data)
        with client.session_transaction() as s:
            token = s['csrf']
        self.assertEqual(client.post('/capsules/new', data={
            'csrf': token, 'title': 'After upgrade', 'message': 'Still works', 'theme': 'sky',
        }).status_code, 302)
        with sqlite3.connect(old_db) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM users').fetchone()[0], 1)
