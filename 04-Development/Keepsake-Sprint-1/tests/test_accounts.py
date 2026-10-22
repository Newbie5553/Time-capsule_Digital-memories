"""Account acceptance checks for Sprint 1."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from app import create_app


class AccountTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = str(Path(self.temp.name) / 'test.db')
        self.app = create_app({
            'TESTING': True,
            'DATABASE': self.database,
            'SECRET_KEY': 'test-only-key',
        })
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def post(self, path, data=None):
        with self.client.session_transaction() as session:
            session['csrf'] = 'test-token'
        return self.client.post(path, data={'csrf': 'test-token', **(data or {})})

    def register(self, **overrides):
        return self.post('/register', {
            'name': 'Amina',
            'email': 'amina@example.com',
            'password': 'ExamplePass123',
            **overrides,
        })

    def test_public_pages_render(self):
        for path in ('/', '/login', '/register'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'<html', response.data)

    def test_dashboard_requires_login(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/login'))

    def test_registration_and_personal_dashboard(self):
        self.assertEqual(self.register().status_code, 302)
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Amina', response.data)
        self.assertIn(b'amina@example.com', response.data)

    def test_duplicate_email_rejected(self):
        self.register()
        self.post('/logout')
        response = self.register(email='AMINA@example.com')
        self.assertIn(b'already has an account', response.data)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM users').fetchone()[0], 1)

    def test_invalid_registration(self):
        for values in ({'name': ''}, {'email': 'wrong'}, {'password': 'short'}):
            response = self.register(**values)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'flash error', response.data)
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM users').fetchone()[0], 0)

    def test_password_hash_and_login(self):
        self.register()
        with sqlite3.connect(self.database) as db:
            stored = db.execute('SELECT password FROM users').fetchone()[0]
            self.assertNotEqual(stored, 'ExamplePass123')
        self.post('/logout')
        self.assertIn(b'incorrect', self.post('/login', {
            'email': 'amina@example.com', 'password': 'wrong',
        }).data)
        self.assertEqual(self.post('/login', {
            'email': 'amina@example.com', 'password': 'ExamplePass123',
        }).status_code, 302)

    def test_logout_blocks_dashboard(self):
        self.register()
        self.post('/logout')
        self.assertEqual(self.client.get('/dashboard').status_code, 302)

    def test_csrf_required(self):
        response = self.client.post('/register', data={'name': 'Amina'})
        self.assertEqual(response.status_code, 400)

    def test_user_text_escaped(self):
        self.register(name='<script>alert(1)</script>')
        response = self.client.get('/dashboard')
        self.assertNotIn(b'<script>alert(1)</script>', response.data)
        self.assertIn(b'&lt;script&gt;', response.data)

    def test_future_routes_not_in_sprint_one(self):
        self.register()
        self.assertEqual(self.client.get('/capsules/new').status_code, 404)


if __name__ == '__main__':
    unittest.main()
