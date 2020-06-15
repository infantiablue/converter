import unittest
import datetime
from google.cloud import datastore
from web.user import OauthUser, User
from web.db import gclient, limit_history


class DbTestCase(unittest.TestCase):
    def test_model_user(self):
        query = gclient.query(kind='Users')
        query.add_filter('email', '=', 'test@test.local')
        result = list(query.fetch())
        if result:
            gclient.delete(result[0].key)

        new_user = User(
            fullname='Tasty Tester',
            email='test@test.local',
            username='testa',
            created_at=datetime.datetime.utcnow()
        )
        assert new_user.fullname == 'Tasty Tester'

    def test_model_oauth_user(self):
        query = gclient.query(kind='Oauth')
        query.add_filter('provider_id', '=', 'Facebook_2020')
        result = list(query.fetch())
        if result:
            gclient.delete(result[0].key)

        new_oauth_user = OauthUser(
            provider='Facebook_Test',
            provider_user_id='Facebook_2020',
            user_id='12345',
            token='54321',
            created_at=datetime.datetime.utcnow()
        )
        assert new_oauth_user.provider == 'Facebook_Test'

    def test_limit_history(self):
        # setup database
        query = gclient.query(kind='Users')
        query.add_filter('email', '=', 'test@test.local')
        result = list(query.fetch())
        test_user_id = result[0].key.id
        items = []
        for i in range(51):
            item = datastore.Entity(gclient.key('History'))
            item.update({
                'provider': 'youtube.com',
                'url': str('http://testurl/'),
                'videoid': i,
                'userid': test_user_id,
                'created_at': datetime.datetime.utcnow()
            })
            items.append(item)
        gclient.put_multi(items)
        check = limit_history(test_user_id)
        # cleanup
        keys = []
        for i in items:
            keys.append(i.key)
        gclient.delete_multi(keys)
        assert check.id == items[0].key.id
