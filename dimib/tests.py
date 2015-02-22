import shutil
import string
import random
import json

from django.conf import settings
from django.test import Client
from django.core.urlresolvers import reverse
from unittest import TestCase
import gnupg

from dimib.models import Account, Post, Comment, Tag


USER1 = {
    'username': 'testuser1',
}
USER2 = {
    'username': 'testuser2',
}

HOMEDIR = '/tmp/dimib-test'

SIGNATURE_TEMPLATE = '''
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA1

{0}
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v1

{1}
-----END PGP SIGNATURE-----'''


client = Client()


class MainTest (TestCase):

    @classmethod
    def setUpClass (cls):
        settings.GPG_HOMEDIR = HOMEDIR
        settings.DEBUG = True
        cls.gpg = gnupg.GPG(gnupghome = HOMEDIR)

    @classmethod
    def tearDownClass (cls):
        shutil.rmtree(HOMEDIR)

    def getResponse (self, response):
        try:
            content = json.loads(response.content)
        except ValueError:
            content = None
        return {
            'status': response.status_code,
            'content': content
        }

    def sendGet(self, url):
        return self.getResponse(client.get(url))

    def sendPost(self, url, data):
        return self.getResponse(client.post(url, json.dumps(data), content_type='application/json'))

    def getFakeSig (self, data):
        return SIGNATURE_TEMPLATE.format(data, ''.join(random.choice(string.ascii_letters) for i in range(100)))

    def makeSignature (self, data, fingerprint):
        return str(self.gpg.sign(json.dumps(data), keyid=fingerprint))

    def login (self, username, signature):
        return self.sendPost(reverse('login'), {
            'data': username,
            'signature': signature
        })

    def test_1_registration (self):
        for user in (USER1, USER2):
            response = self.sendPost(reverse('registration'), user)
            self.assertIn('key', response['content'])
            user['fingerprint'] = self.gpg.list_keys().fingerprints[-1]

    def test_2_login (self):
        # failed
        response = self.login(USER1['username'], self.getFakeSig(USER1['username']))
        self.assertTrue('errors' in response['content'] and response['content']['errors'] == 'wrong signature')
        # success
        response = self.login(USER1['username'], self.makeSignature(USER1['username'], USER1['fingerprint']))
        self.assertTrue('success' in response['content'] and response['content']['success'])

    def test_3_add_post (self):
        post_data = {
            'message': 'Test post',
            'tags': ['tag1', 'tag2']
        }
        response = self.sendPost(reverse('posts'), {
            'data': post_data,
            'signature': self.makeSignature(post_data, USER1['fingerprint'])
        })
        self.assertTrue('success' in response['content'] and response['content']['success'])

    def test_4_add_comment (self):
        # comment for post
        response = self.sendGet(reverse('posts'))
        self.assertTrue('posts' in response['content'] and len(response['content']['posts']) == 1 and response['content']['posts'][0]['verified'])
        post_pk = response['content']['posts'][0]['pk']
        self.login(USER2['username'], self.makeSignature(USER2['username'], USER2['fingerprint']))
        comment_data = {'message': 'Test comment'}
        response = self.sendPost(reverse('comments', args=[post_pk]), {
            'data': comment_data,
            'signature': self.makeSignature(comment_data, USER2['fingerprint'])
        })
        self.assertTrue('success' in response['content'] and response['content']['success'])
        # comment for comment
        response = self.sendGet(reverse('comments', args=[post_pk]))
        self.assertTrue('comments' in response['content'] and len(response['content']['comments']) == 1 and response['content']['comments'][0]['verified'])
        comment_pk = response['content']['comments'][0]['pk']
        response = self.sendPost(reverse('comments', args=[post_pk]), {
            'data': {'message': 'Comment for comment'},
            'comment_id': comment_pk,
        })
        self.assertTrue('success' in response['content'] and response['content']['success'])
        response = self.sendGet(reverse('comments', args=[post_pk]))
        self.assertTrue('comments' in response['content'] and len(response['content']['comments']) == 2 and not response['content']['comments'][1]['verified'] and response['content']['comments'][1]['comment'] == comment_pk)



