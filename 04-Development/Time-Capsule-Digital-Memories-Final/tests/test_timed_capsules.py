"""Check sealing, server-enforced time boundaries, and additive migration."""
import io
import sqlite3
import unittest
from datetime import datetime, timezone
from pathlib import Path
import test_accounts
from app import create_app


class TimedCapsuleTests(unittest.TestCase):
    post = test_accounts.AccountTests.post
    register = test_accounts.AccountTests.register
    tearDown = test_accounts.AccountTests.tearDown

    def setUp(self):
        test_accounts.AccountTests.setUp(self)
        self.clock = 1900000000.0
        self.app.config['CLOCK'] = lambda: self.clock
        self.register()
        self.post('/capsules/new', {
            'title': 'Future memory', 'message': 'SECRET CONTENT 8942', 'theme': 'sky',
            'files': (io.BytesIO(b'\x89PNG\r\n\x1a\nfixture'), 'private.png'),
        })

    def seal(self, **overrides):
        return self.post('/capsules/1/seal', {
            'confirm': 'seal',
            'unlock_at': datetime.fromtimestamp(self.clock + 120, timezone.utc).isoformat(),
            **overrides,
        })

    def test_confirmation_page_and_sealing(self):
        self.assertEqual(self.client.get('/capsules/1/seal').status_code, 200)
        self.assertIn(b'SECRET CONTENT', self.client.get('/capsules/1').data)
        self.assertEqual(self.seal().status_code, 302)
        self.assertEqual(self.client.get('/capsules/1/status').json['state'], 'sealed')

    def test_future_timezone_and_confirmation_validation(self):
        for timestamp in ('', 'bad', '2030-01-01T12:00', '2000-01-01T12:00:00Z'):
            self.assertEqual(self.seal(unlock_at=timestamp).status_code, 400)
        self.assertEqual(self.seal(confirm='').status_code, 400)
        self.assertEqual(self.client.get('/capsules/1/status').json['state'], 'draft')

    def test_offset_time_is_normalized(self):
        from datetime import timedelta
        selected = datetime.fromtimestamp(self.clock + 120, timezone(timedelta(hours=4)))
        self.seal(unlock_at=selected.isoformat())
        self.assertEqual(self.client.get('/capsules/1/status').json['unlock_at'], self.clock + 120)

    def test_no_early_content_or_file_leaks(self):
        self.seal()
        for route in ('/capsules/1', '/dashboard', '/capsules/1/status'):
            response = self.client.get(route)
            self.assertNotIn(b'SECRET CONTENT', response.data)
            self.assertNotIn(b'private.png', response.data)
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
        self.assertEqual(self.client.get('/attachments/1').status_code, 403)

    def test_immutable_even_after_opening(self):
        self.seal()
        for moment in (self.clock, self.clock + 121):
            self.clock = moment
            for route in ('/capsules/1/edit', '/capsules/1/delete', '/capsules/1/seal'):
                self.assertEqual(self.client.get(route).status_code, 403)
                self.assertEqual(self.post(route, {'title': 'Changed', 'message': 'Changed',
                                                  'theme': 'rose', 'confirm': 'delete'}).status_code, 403)

    def test_exact_opening_boundary(self):
        target = self.clock + 120
        self.seal()
        self.clock = target - 0.001
        self.assertEqual(self.client.get('/attachments/1').status_code, 403)
        self.clock = target
        self.assertEqual(self.client.get('/capsules/1/status').json['state'], 'ready')
        self.assertIn(b'SECRET CONTENT', self.client.get('/capsules/1').data)
        with self.client.get('/attachments/1') as response:
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.data.startswith(b'\x89PNG'))

    def test_other_account_cannot_open_or_query_status(self):
        self.seal()
        self.post('/logout')
        self.register(email='stranger@example.com')
        self.clock += 200
        for route in ('/capsules/1', '/capsules/1/status', '/capsules/1/seal', '/attachments/1'):
            self.assertEqual(self.client.get(route).status_code, 404)
        self.assertEqual(self.seal().status_code, 404)

    def test_csrf_and_duplicate_seal(self):
        self.assertEqual(self.client.post('/capsules/1/seal', data={'confirm': 'seal'}).status_code, 400)
        self.seal()
        self.assertEqual(self.seal().status_code, 403)

    def test_sprint_two_data_and_attachment_survive_migration(self):
        # Reconstruct the actual pre-Sprint-3 schema with an account and draft.
        old = str(Path(self.temp.name) / 'sprint-two.db')
        with sqlite3.connect(old) as db:
            db.executescript('''
                CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL);
                CREATE TABLE capsules(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), title TEXT NOT NULL, message TEXT NOT NULL, theme TEXT NOT NULL, created_at REAL NOT NULL, updated_at REAL NOT NULL);
                CREATE TABLE attachments(id INTEGER PRIMARY KEY, capsule_id INTEGER NOT NULL REFERENCES capsules(id) ON DELETE CASCADE, filename TEXT NOT NULL, stored TEXT NOT NULL UNIQUE, kind TEXT NOT NULL);
                INSERT INTO users VALUES(1,'Old user','old@example.com','hash');
                INSERT INTO capsules VALUES(1,1,'Old draft','Keep this memory','rose',1,1);
                INSERT INTO attachments VALUES(1,1,'old.png','old.png','image');
            ''')
        uploads = Path(self.temp.name) / 'old-files'
        uploads.mkdir()
        (uploads / 'old.png').write_bytes(b'old photo bytes')
        config = {'TESTING': True, 'SECRET_KEY': 'test', 'DATABASE': old, 'UPLOAD_FOLDER': str(uploads)}
        app = create_app(config)
        app = create_app(config)  # Migration must also be safe on a second start.
        client = app.test_client()
        with client.session_transaction() as session:
            session['user_id'] = 1
        self.assertIn(b'Keep this memory', client.get('/capsules/1').data)
        self.assertEqual(client.get('/capsules/1/status').json['state'], 'draft')
        with client.get('/attachments/1') as response:
            self.assertEqual(response.data, b'old photo bytes')
        with sqlite3.connect(old) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM users').fetchone()[0], 1)
