"""Final release regressions: no phantom cards, in-app and outgoing email alerts."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app import create_app


class FakeSMTP:
    messages = []
    def __init__(self, *args, **kwargs): pass
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def ehlo(self): pass
    def starttls(self): pass
    def login(self, *args): pass
    def send_message(self, message): self.messages.append(message)


class FinalNotificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.clock = [1000.0]
        self.db = str(Path(self.temp.name) / 'db.sqlite')
        self.app = create_app({
            'TESTING': True, 'DATABASE': self.db, 'SECRET_KEY': 'test-secret',
            'UPLOAD_FOLDER': str(Path(self.temp.name) / 'uploads'),
            'CLOCK': lambda: self.clock[0],
            'SMTP_HOST': 'smtp.example.com', 'SMTP_PORT': 587,
            'SMTP_FROM': 'notify@example.com',
            'PUBLIC_BASE_URL': 'https://capsule.example.com',
        })
        self.client = self.app.test_client()
        FakeSMTP.messages = []

    def tearDown(self): self.temp.cleanup()

    def post(self, path, **data):
        with self.client.session_transaction() as sess: sess['csrf'] = 'test'
        return self.client.post(path, data={'csrf': 'test', **data})

    def user(self, name, email):
        self.assertEqual(self.post('/register', name=name, email=email,
                                   password='SecurePass1234').status_code, 302)

    def logout(self): self.post('/logout')
    def login(self, email):
        self.assertEqual(self.post('/login', email=email, password='SecurePass1234').status_code, 302)

    def create_sealed(self):
        self.assertEqual(self.post('/capsules/new', title='Future note', message='PRIVATE LETTER', theme='sky').status_code, 302)
        with sqlite3.connect(self.db) as db:
            cid = db.execute('SELECT id FROM capsules ORDER BY id DESC LIMIT 1').fetchone()[0]
            db.execute('UPDATE capsules SET locked=1, unlock_at=2000, sealed_at=1000 WHERE id=?', (cid,))
        return cid

    def test_grid_has_one_card_per_capsule_and_share_inside_capsule(self):
        self.user('Owner', 'owner@example.com')
        cid = self.create_sealed()
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.count(b'class="capsule-card"'), 1)
        self.assertNotIn(b'capsule-share-shortcut', response.data)
        self.assertIn(f'/capsules/{cid}/share'.encode(), self.client.get(f'/capsules/{cid}').data)
        self.assertIn(b'href="/"', response.data)

    def test_share_creates_inbox_and_sends_email_then_unlock_notifies_both(self):
        self.user('Owner', 'owner@example.com')
        cid = self.create_sealed()
        self.logout()
        self.user('Friend', 'friend@example.com')
        self.logout()
        self.login('owner@example.com')
        with patch('app.smtplib.SMTP', FakeSMTP):
            result = self.post(f'/capsules/{cid}/share', email='friend@example.com')
        self.assertEqual(result.status_code, 302)
        self.assertEqual(len(FakeSMTP.messages), 1)
        self.assertEqual(FakeSMTP.messages[0]['To'], 'friend@example.com')
        self.logout()
        self.login('friend@example.com')
        self.assertIn(b'A capsule was shared with you', self.client.get('/notifications').data)
        self.assertNotIn(b'PRIVATE LETTER', self.client.get(f'/capsules/{cid}').data)
        self.clock[0] = 2001.0
        self.assertIn(b'Your capsule is ready to open', self.client.get('/notifications').data)
        with self.app.app_context():
            # CLI must be able to handle an opening even without visiting the browser.
            with patch('app.smtplib.SMTP', FakeSMTP):
                runner = self.app.test_cli_runner().invoke(args=['send-notifications'])
            self.assertEqual(runner.exit_code, 0, runner.output)
        self.assertEqual(len(FakeSMTP.messages), 3)
        self.assertEqual({m['To'] for m in FakeSMTP.messages}, {'owner@example.com','friend@example.com'})
        self.client.get('/notifications')
        with self.app.app_context():
            with patch('app.smtplib.SMTP', FakeSMTP):
                runner = self.app.test_cli_runner().invoke(args=['send-notifications'])
            self.assertEqual(runner.exit_code, 0, runner.output)
        self.assertEqual(len(FakeSMTP.messages), 3)
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM app_notifications WHERE kind='unlocked'").fetchone()[0], 2)
        self.logout()
        self.login('owner@example.com')
        self.assertIn(b'Your capsule is ready to open', self.client.get('/notifications').data)

    def test_revoked_share_removes_notifications_and_permits_new_invitation(self):
        self.user('Owner', 'owner@example.com')
        cid = self.create_sealed()
        self.logout()
        self.user('Friend', 'friend@example.com')
        self.logout()
        self.login('owner@example.com')
        with patch('app.smtplib.SMTP', FakeSMTP):
            self.assertEqual(self.post(f'/capsules/{cid}/share', email='friend@example.com').status_code, 302)
        with sqlite3.connect(self.db) as db:
            share_id = db.execute('SELECT id FROM capsule_shares WHERE capsule_id=?', (cid,)).fetchone()[0]
        self.assertEqual(self.post(f'/capsules/{cid}/shares/{share_id}/revoke', confirm='revoke').status_code, 302)
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM app_notifications').fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT count(*) FROM email_notifications').fetchone()[0], 0)
        with patch('app.smtplib.SMTP', FakeSMTP):
            self.assertEqual(self.post(f'/capsules/{cid}/share', email='friend@example.com').status_code, 302)
        self.assertEqual(len(FakeSMTP.messages), 2)

    def test_notification_read_cannot_be_changed_by_another_user(self):
        self.user('Owner', 'owner@example.com')
        cid = self.create_sealed()
        self.logout()
        self.user('Friend', 'friend@example.com')
        self.logout()
        self.login('owner@example.com')
        with patch('app.smtplib.SMTP', FakeSMTP):
            self.post(f'/capsules/{cid}/share', email='friend@example.com')
        with sqlite3.connect(self.db) as db:
            nid = db.execute("SELECT id FROM app_notifications WHERE kind='invitation'").fetchone()[0]
        self.assertEqual(self.post(f'/notifications/{nid}/read').status_code, 404)
        self.logout()
        self.login('friend@example.com')
        self.assertEqual(self.post(f'/notifications/{nid}/read').status_code, 302)
        self.assertNotIn(' · New'.encode(), self.client.get('/notifications').data)

if __name__ == '__main__': unittest.main()
