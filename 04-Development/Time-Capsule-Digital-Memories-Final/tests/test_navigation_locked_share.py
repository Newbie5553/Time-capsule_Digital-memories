"""Regression: sealed capsule owners see sharing; guests do not."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from app import create_app

class LockedSharingNavigationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / 'test.db')
        self.app = create_app({'TESTING': True, 'DATABASE': self.db, 'UPLOAD_FOLDER': str(Path(self.tmp.name) / 'uploads'), 'SECRET_KEY': 'testing'})
        self.client = self.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def post(self, route, **values):
        with self.client.session_transaction() as session:
            session['csrf'] = 'abc'
        return self.client.post(route, data={'csrf': 'abc', **values})

    def test_locked_owner_can_navigate_to_share_and_home_is_not_create(self):
        self.post('/register', name='Owner', email='owner@example.com', password='SafePass1234')
        self.post('/capsules/new', title='Sealed future', message='PRIVATE CONTENT', theme='sky')
        with sqlite3.connect(self.db) as db:
            cid = db.execute('SELECT id FROM capsules ORDER BY id DESC LIMIT 1').fetchone()[0]
            db.execute('UPDATE capsules SET locked=1, unlock_at=9999999999 WHERE id=?', (cid,))
        locked = self.client.get(f'/capsules/{cid}')
        self.assertEqual(locked.status_code, 200)
        self.assertIn(f'/capsules/{cid}/share'.encode(), locked.data)
        self.assertIn(b'Share this locked capsule', locked.data)
        dashboard = self.client.get('/dashboard')
        self.assertIn(b'Share locked capsule', dashboard.data)
        self.assertIn(b'href="/"', dashboard.data)
        home = self.client.get('/')
        self.assertIn(b'WELCOME TO TIME CAPSULE DIGITAL MEMORIES', home.data)
        self.assertNotIn(b'Create a capsule', home.data)
        self.assertEqual(self.client.get(f'/capsules/{cid}/share').status_code, 200)

if __name__ == '__main__': unittest.main()
