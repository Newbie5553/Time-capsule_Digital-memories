"""Sprint 4 acceptance checks: sharing, read permissions, search and upgrade."""
from contextlib import closing
from datetime import datetime, timezone
import io
import sqlite3
import unittest
import test_accounts
from app import create_app


class SharingSearchTests(unittest.TestCase):
    post = test_accounts.AccountTests.post
    register = test_accounts.AccountTests.register
    tearDown = test_accounts.AccountTests.tearDown

    def setUp(self):
        test_accounts.AccountTests.setUp(self)
        self.clock = 1900000000.0
        self.app.config['CLOCK'] = lambda: self.clock
        for name, email in [('Owner Name','owner@example.com'),('Recipient Name','recipient@example.com'),('Unrelated Person','stranger@example.com')]:
            self.register(name=name,email=email)
            self.post('/logout')
        self.login('owner@example.com')
        self.post('/capsules/new', {'title':'Graduation 100%_Memory','message':'PRIVATE_SHARED_MESSAGE','theme':'rose',
            'files':(io.BytesIO(b'\x89PNG\r\n\x1a\nfixture'),'memory.png')})

    def login(self,email):
        self.post('/logout')
        return self.post('/login',{'email':email,'password':'ExamplePass123'})

    def ready(self):
        self.post('/capsules/1/seal',{'confirm':'seal','unlock_at':datetime.fromtimestamp(self.clock+1,timezone.utc).isoformat()})
        self.clock += 1

    def share(self,email='recipient@example.com'):
        return self.post('/capsules/1/share',{'email':email})

    def share_count(self):
        with closing(sqlite3.connect(self.database)) as db:
            return db.execute('SELECT count(*) FROM capsule_shares').fetchone()[0]

    def test_only_opened_capsule_can_be_shared(self):
        self.assertEqual(self.share().status_code,403)
        self.ready();self.clock-=.001
        self.assertEqual(self.share().status_code,403)
        self.clock+=.001
        self.assertEqual(self.share().status_code,302)

    def test_email_normalization(self):
        self.ready()
        self.assertEqual(self.share(' RECIPIENT@EXAMPLE.COM ').status_code,302)
        self.assertEqual(self.share_count(),1)

    def test_invalid_unknown_self_duplicate(self):
        self.ready()
        for email in ['', 'bad', 'a'*255+'@x.com','missing@example.com','owner@example.com']:
            self.assertEqual(self.share(email).status_code,400)
        self.assertEqual(self.share_count(),0)
        self.share()
        self.assertEqual(self.share().status_code,400)
        self.assertEqual(self.share_count(),1)

    def test_recipient_content_file_and_author(self):
        self.ready();self.share();self.login('recipient@example.com')
        page=self.client.get('/capsules/1')
        self.assertEqual(page.status_code,200)
        self.assertIn(b'PRIVATE_SHARED_MESSAGE',page.data)
        self.assertIn(b'With love, Owner Name',page.data)
        self.assertIn(b'Read-only access',page.data)
        self.assertNotIn(b'Share this memory',page.data)
        with self.client.get('/attachments/1') as response:
            self.assertEqual(response.status_code,200)
            self.assertTrue(response.data.startswith(b'\x89PNG'))
        self.assertEqual(self.client.get('/capsules/1/status').json['state'],'ready')

    def test_shared_dashboard_separate_without_content(self):
        self.ready();self.share();self.login('recipient@example.com')
        self.assertNotIn(b'Graduation 100%',self.client.get('/dashboard').data)
        page=self.client.get('/shared').data
        self.assertIn(b'Graduation 100%',page)
        self.assertNotIn(b'PRIVATE_SHARED_MESSAGE',page)
        self.assertNotIn(b'memory.png',page)

    def test_recipient_cannot_mutate_or_reshare(self):
        self.ready();self.share();self.login('recipient@example.com')
        for path in ['/capsules/1/edit','/capsules/1/delete','/capsules/1/seal','/capsules/1/share']:
            self.assertEqual(self.client.get(path).status_code,404)
            self.assertEqual(self.post(path,{'email':'stranger@example.com'}).status_code,404)
        self.assertEqual(self.post('/capsules/1/shares/1/revoke',{'confirm':'revoke'}).status_code,404)

    def test_unrelated_user_denied(self):
        self.ready();self.share();self.login('stranger@example.com')
        for path in ['/capsules/1','/capsules/1/status','/attachments/1','/capsules/1/share']:
            self.assertEqual(self.client.get(path).status_code,404)
        self.assertNotIn(b'Graduation 100%',self.client.get('/shared').data)

    def test_anonymous_requires_login(self):
        self.ready();self.share();self.post('/logout')
        for path in ['/shared','/capsules/1','/attachments/1','/capsules/1/share']:
            self.assertEqual(self.client.get(path).status_code,302)

    def test_csrf_and_revoke_confirmation(self):
        self.ready();self.share()
        self.assertEqual(self.post('/capsules/1/shares/1/revoke').status_code,400)
        self.assertEqual(self.client.post('/capsules/1/shares/1/revoke',data={'confirm':'revoke'}).status_code,400)
        self.assertEqual(self.client.post('/capsules/1/share',data={'email':'stranger@example.com'}).status_code,400)
        self.assertEqual(self.share_count(),1)

    def test_revocation_existing_session_and_download(self):
        self.ready();self.share()
        recipient=self.app.test_client()
        with recipient.session_transaction() as session:session['user_id']=2
        self.assertEqual(recipient.get('/capsules/1').status_code,200)
        self.assertEqual(self.post('/capsules/1/shares/1/revoke',{'confirm':'revoke'}).status_code,302)
        for path in ['/capsules/1','/capsules/1/status','/attachments/1']:
            self.assertEqual(recipient.get(path).status_code,404)
        self.assertNotIn(b'Graduation 100%',recipient.get('/shared').data)
        self.assertEqual(self.client.get('/capsules/1').status_code,200)
        self.assertEqual(self.share().status_code,302)

    def test_unknown_share_and_wrong_capsule(self):
        self.ready();self.share()
        self.assertEqual(self.post('/capsules/1/shares/999/revoke',{'confirm':'revoke'}).status_code,404)
        self.assertEqual(self.post('/capsules/999/shares/1/revoke',{'confirm':'revoke'}).status_code,404)
        self.assertEqual(self.share_count(),1)

    def test_time_rechecked_for_shared_access(self):
        self.ready();self.share();self.clock-=1;self.login('recipient@example.com')
        for path in ['/capsules/1','/capsules/1/status','/attachments/1']:
            self.assertEqual(self.client.get(path).status_code,404)
        self.assertNotIn(b'Graduation 100%',self.client.get('/shared').data)

    def test_search_case_whitespace_empty_and_no_match(self):
        for q in ['graduation',' GRADUATION ','']:
            self.assertIn(b'Graduation 100%',self.client.get('/dashboard',query_string={'q':q}).data)
        page=self.client.get('/dashboard?q=nonexistent').data
        self.assertNotIn(b'Graduation 100%',page)
        self.assertIn(b'No memories found',page)

    def test_literal_wildcard_and_sql_input(self):
        self.assertIn(b'Graduation 100%',self.client.get('/dashboard',query_string={'q':'%_'}).data)
        self.assertNotIn(b'Graduation 100%',self.client.get('/dashboard',query_string={'q':"' OR 1=1 --"}).data)
        self.assertEqual(self.client.get('/dashboard',query_string={'q':'x'*101}).status_code,400)

    def test_search_does_not_leak_other_accounts(self):
        self.login('stranger@example.com')
        for path in ['/dashboard?q=Graduation','/shared?q=Graduation']:
            self.assertNotIn(b'Graduation 100%',self.client.get(path).data)

    def test_shared_search(self):
        self.ready();self.share();self.login('recipient@example.com')
        self.assertIn(b'Graduation 100%',self.client.get('/shared?q=graduation').data)
        self.assertNotIn(b'Graduation 100%',self.client.get('/shared?q=missing').data)
        self.assertEqual(self.client.get('/shared',query_string={'q':'x'*101}).status_code,400)

    def test_html_escaping(self):
        self.post('/capsules/1/edit',{'title':'<script>alert(1)</script>','message':'<script>bad()</script>','theme':'sky'})
        self.ready();self.share();self.login('recipient@example.com')
        for path in ['/shared','/capsules/1']:
            data=self.client.get(path).data
            self.assertNotIn(b'<script>alert',data)
            self.assertIn(b'&lt;script&gt;',data)

    def test_sprint_three_upgrade_and_restart(self):
        with closing(sqlite3.connect(self.database)) as db:
            db.execute('DROP TABLE capsule_shares');db.commit()
        config=dict(self.app.config)
        self.app=create_app(config);self.client=self.app.test_client()
        with closing(sqlite3.connect(self.database)) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM users').fetchone()[0],3)
            self.assertEqual(db.execute('SELECT message FROM capsules').fetchone()[0],'PRIVATE_SHARED_MESSAGE')
            self.assertEqual(db.execute('SELECT count(*) FROM attachments').fetchone()[0],1)
        self.login('owner@example.com');self.ready();self.share()
        again=create_app(dict(self.app.config));client=again.test_client()
        with client.session_transaction() as session:session['user_id']=2
        self.assertIn(b'PRIVATE_SHARED_MESSAGE',client.get('/capsules/1').data)
        with client.get('/attachments/1') as response:self.assertEqual(response.status_code,200)
        self.assertEqual(self.share_count(),1)

    def test_owner_cannot_change_sealed_content(self):
        self.ready();self.share()
        self.assertEqual(self.post('/capsules/1/edit',{'title':'Changed','message':'Changed','theme':'sky'}).status_code,403)
        self.assertEqual(self.post('/capsules/1/delete',{'confirm':'delete'}).status_code,403)

    def test_owner_only_recipient_list(self):
        self.ready();self.share()
        self.assertIn(b'recipient@example.com',self.client.get('/capsules/1/share').data)
        self.login('recipient@example.com')
        self.assertEqual(self.client.get('/capsules/1/share').status_code,404)
