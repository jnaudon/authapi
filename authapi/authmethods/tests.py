from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

import json
from api.tests import JClient
from api.models import AuthEvent
from .m_email import Email
from .m_sms import Sms


class AuthMethodTestCase(TestCase):
    def setUp(self):
        ae = AuthEvent(pk=1, name='test', auth_method='email',
                auth_method_config=json.dumps(Email.TPL_CONFIG))
        ae.save()

    def test_method_custom_view(self):
        c = JClient()
        response = c.get('/api/authmethod/user-and-password/test/asdfdsf/', {})
        self.assertEqual(response.status_code, 200)
        r = json.loads(response.content.decode('utf-8'))
        self.assertEqual(r['status'], 'ok')

        response = c.get('/api/authmethod/user-and-password/test/asdfdsf/cxzvcx/', {})
        self.assertEqual(response.status_code, 404)

    def test_method_email(self):
        c = JClient()
        response = c.post('/api/authmethod/email/register/1/',
                {'email': 'test@test.com'})
        self.assertEqual(response.status_code, 200)
        r = json.loads(response.content.decode('utf-8'))
        self.assertEqual(r['status'], 'ok')

        body = mail.outbox[0].body
        for word in body.split():
            if word.startswith('http://'):
                user = word.split('/')[-2]
                code = word.split('/')[-1]
                break

        # valid code
        response = c.get('/api/authmethod/email/validate/%s/%s/' % (user, code), {})
        self.assertEqual(response.status_code, 200)
        r = json.loads(response.content.decode('utf-8'))
        self.assertEqual(r['status'], 'ok')

        # invalid code
        response = c.get('/api/authmethod/email/validate/%s/bad/' % (user), {})
        self.assertEqual(response.status_code, 200)
        r = json.loads(response.content.decode('utf-8'))
        self.assertEqual(r['status'], 'nok')


class AuthMethodSmsTestCase(TestCase):
    def setUp(self):
        ae = AuthEvent(pk=1, name='test', auth_method='sms-code',
                auth_method_config=json.dumps(Sms.TPL_CONFIG))
        ae.save()

        u = User(pk=1, username='test')
        u.save()
        u.userdata.event = ae
        u.userdata.metadata = json.dumps({
                'tlf': '+34666666666',
                'code': 'AAAAAAAA',
                'sms_verified': False
        })
        u.userdata.save()

    def test_method_sms_regiter(self):
        c = JClient()
        response = c.post('/api/authmethod/sms-code/register/1/',
                {'tlf': '+34666666666'})
        self.assertEqual(response.status_code, 200)
        r = json.loads(response.content.decode('utf-8'))
        self.assertEqual(r['status'], 'ok')

    def test_method_sms_valid_code(self):
        user = 1
        code = 'AAAAAAAA'

        c = JClient()
        response = c.get('/api/authmethod/sms-code/validate/%s/%s/' % (user, code), {})
        self.assertEqual(response.status_code, 200)
        r = json.loads(response.content.decode('utf-8'))
        self.assertEqual(r['status'], 'ok')

    def test_method_sms_invalid_code(self):
        user = 1
        code = 'BBBBBBBB'

        c = JClient()
        response = c.get('/api/authmethod/sms-code/validate/%s/bad/' % (user), {})
        self.assertEqual(response.status_code, 200)
        r = json.loads(response.content.decode('utf-8'))
        self.assertEqual(r['status'], 'nok')
