import os
import unittest
from werkzeug.security import generate_password_hash
from web import create_app
from flask import url_for
from utils.utils import generate_secret_key
from web.models import db
from web.models import Video, User
app = create_app()
app.config['WTF_CSRF_ENABLED'] = False

user_test = 'tester'
user_pwd = '235tqk'
tester_email = 'test@local.{}'.format(
    generate_secret_key(4).decode())


class ProfileTestCase(unittest.TestCase):

    def __init__(self, *args):
        super().__init__(*args)
        self.client = app.test_client()
        self.login(user_test, user_pwd)

    @classmethod
    def setup_class(cls):
        with app.app_context():
            old_videos = Video.query.filter_by(provider='techika.com').all()
            for i in old_videos:
                db.session.delete(i)
            db.session.commit()
            tester = User(
                username='tester',
                email=tester_email,
                fullname='Testy Testa',
                pwdhash=generate_password_hash('235tqk')
            )
            db.session.add(tester)
            db.session.commit()

    @classmethod
    def teardown_class(cls):
        with app.app_context():
            tester = User.query.filter_by(email=tester_email).first()
            db.session.delete(tester)
            db.session.commit()

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout')

    def test_login(self):
        r = self.client.post(
            '/login', data=dict(username=user_test,
                                password=user_pwd), follow_redirects=True)
        assert r.status_code == 200
        assert b'Log out' in r.data

    '''
    def test_login_with_mrblue(self):
        r = self.client.post(
            '/login', data=dict(username='mrblue',
                                password='235tqk'))
        assert r.status_code == 200
    '''

    def test_history_with_auth(self):
        r = self.client.get('/history')
        assert r.status_code == 200
        assert b'History' in r.data

    def test_history_with_50_items(self):
        with app.app_context():
            tester = User.query.filter_by(email=tester_email).first()
            videos = []
            for i in range(51):
                new_video = Video(
                    url='http://test.video_{}.url'.format(i),
                    user_id=tester.id,
                    video_id=generate_secret_key(10).decode(),
                    provider='techika.com'
                )
                db.session.add(new_video)
                videos.append(new_video)
            db.session.commit()
            check = Video.limit_history_videos(user_id=tester.id)
            assert check == videos[0].id
            del videos[0]
            for i in videos:
                db.session.delete(i)
            db.session.commit()

    def test_profile_with_auth(self):
        r = self.client.get('/profile')
        assert r.status_code == 200
        assert b'Your details' in r.data
        assert b'tester' in r.data

    def test_profile_update(self):
        new_test_username = generate_secret_key(8).decode()
        self.login(user_test, user_pwd)
        r = self.client.post(
            '/profile', data=dict(username=new_test_username),  follow_redirects=True)
        self.client.post('/profile', data=dict(username=user_test))
        assert r.status_code == 200
        assert b'Your details' in r.data
        assert bytes(new_test_username, 'utf-8') in r.data

    def test_profile_without_auth(self):
        self.logout()
        r = self.client.get('/profile', follow_redirects=True)
        assert r.status_code == 200
        assert b'Please log in to access this page.' in r.data

    def test_history_without_auth(self):
        self.logout()
        r = self.client.get('/profile', follow_redirects=True)
        assert r.status_code == 200
        assert b'Please log in to access this page.' in r.data
