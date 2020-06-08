from web.profile import blueprint as fb_bp
import os
from web import create_app
from flask_dance.consumer.storage import MemoryStorage
import unittest
from _pytest.monkeypatch import MonkeyPatch
app = create_app()
BASE_URL = os.environ.get('FLASK_ROOT_URL')


class ProfileTestCase(unittest.TestCase):

    def __init__(self, *args):
        super().__init__(*args)
        # create monkeypatch directly
        self.monkeypatch = MonkeyPatch()
        self.tester = app.test_client(self)

    def test_profile_unauthorized(self):
        storage = MemoryStorage()
        self.monkeypatch.setattr(fb_bp, 'storage', storage)

        with app.test_client() as client:
            response = self.tester.get(
                '/profile', base_url=BASE_URL)
        response = self.tester.get('/profile', content_type='html/text')
        assert response.status_code == 302
        assert response.headers['Location'] == BASE_URL+'/login/facebook'

    def test_profile_authorized(self):
        storage = MemoryStorage({'access_token': 'fake-token'})
        self.monkeypatch.setattr(fb_bp, 'storage', storage)

        with app.test_client() as client:
            response = client.get('/profile', base_url=BASE_URL)

        assert response.status_code == 200
