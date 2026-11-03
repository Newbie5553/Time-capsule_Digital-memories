"""Sprint 5 tests: run with python -m unittest discover -s tests -v."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from app import create_app

class Sprint5Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = str(Path(self.temp.name) / 'data.db')
        self.app = create_app({'TESTING': True, 'DATABASE': self.database, 'SECRET_KEY': 'test-only', 'UPLOAD_FOLDER': str(Path(self.temp.name) / 'uploads')})
        self.client = self.app.test_client()

    def tearDown(self): self.temp.cleanup()

    def post(self, path, **data):
        with self.client.session_transaction() as sess: sess['csrf'] = 'test'
        return self.client.post(path, data={'csrf':'test', **data})

    def register(self, name, email):
        return self.post('/register', name=name, email=email, password='SecurePass1234')

    def login(self, email):
        return self.post('/login', email=email, password='SecurePass1234')

    def create_locked(self):
        self.post('/capsules/new', title='Future message', message='TOP SECRET', theme='sky')
        with sqlite3.connect(self.database) as db:
            cid = db.execute('SELECT id FROM capsules ORDER BY id DESC LIMIT 1').fetchone()[0]
            db.execute('UPDATE capsules SET locked=1, unlock_at=9999999999 WHERE id=?', (cid,))
        return cid

    def test_locked_sharing_and_protected_content(self):
        self.register('Owner', 'owner@example.com')
        cid = self.create_locked()
        self.post('/logout')
        self.register('Friend', 'friend@example.com')
        self.post('/logout')
        self.login('owner@example.com')
        response = self.post(f'/capsules/{cid}/share', email='friend@example.com')
        self.assertEqual(response.status_code, 302)
        self.post('/logout')
        self.login('friend@example.com')
        self.assertIn(b'Future message', self.client.get('/shared').data)
        self.assertNotIn(b'TOP SECRET', self.client.get('/shared').data)
        response = self.client.get(f'/capsules/{cid}')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'TOP SECRET', response.data)
        with sqlite3.connect(self.database) as db:
            kinds = {r[0] for r in db.execute('SELECT kind FROM email_notifications')}
        self.assertEqual(kinds, {'invitation', 'unlocked'})

    def test_admin_authorization_and_disable(self):
        self.register('Owner', 'owner@example.com')
        self.assertEqual(self.client.get('/admin').status_code, 403)
        self.post('/logout')
        self.register('Admin', 'admin@example.com')
        with sqlite3.connect(self.database) as db:
            db.execute("UPDATE users SET role='admin' WHERE email='admin@example.com'")
            owner_id = db.execute("SELECT id FROM users WHERE email='owner@example.com'").fetchone()[0]
        self.assertEqual(self.client.get('/admin').status_code, 200)
        self.assertEqual(self.post(f'/admin/users/{owner_id}/toggle', confirm='yes').status_code, 302)
        self.post('/logout')
        self.assertIn(b'incorrect', self.login('owner@example.com').data)
