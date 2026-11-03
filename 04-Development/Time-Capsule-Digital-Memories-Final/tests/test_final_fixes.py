"""Regression checks for final presentation fixes."""
import tempfile
import unittest
from pathlib import Path
from app import create_app


class FinalFixTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app({'TESTING': True, 'DATABASE': str(Path(self.temp.name) / 'test.db'), 'UPLOAD_FOLDER': str(Path(self.temp.name) / 'uploads'), 'SECRET_KEY': 'unit-test-secret'})
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def post(self, url, values):
        with self.client.session_transaction() as sess:
            sess['csrf'] = 'csrf-test'
        return self.client.post(url, data={'csrf': 'csrf-test', **values})

    def test_recovery_navigation_and_home(self):
        self.assertIn(b'Forgot password?', self.client.get('/login').data)
        self.assertEqual(self.client.get('/forgot-password').status_code, 200)
        self.post('/register', {'name': 'Demo', 'email': 'demo@example.com', 'password': 'Pass12345'})
        self.assertIn(b'My capsules', self.client.get('/').data)
        self.assertIn(b'Shared with me', self.client.get('/').data)
        self.assertIn(b'Home', self.client.get('/dashboard').data)
        self.assertNotIn(b'Admin dashboard', self.client.get('/dashboard').data)
        self.assertEqual(self.client.get('/admin').status_code, 403)

    def test_recovery_response_does_not_reveal_account(self):
        unknown = self.post('/forgot-password', {'email': 'no@example.com'})
        self.assertEqual(unknown.status_code, 302)
        self.post('/register', {'name': 'Demo', 'email': 'demo@example.com', 'password': 'Pass12345'})
        known = self.post('/forgot-password', {'email': 'demo@example.com'})
        self.assertEqual(known.status_code, 302)
        self.assertEqual(unknown.location, known.location)


if __name__ == '__main__':
    unittest.main()
