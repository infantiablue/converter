import os
import sys
import json
import datetime
from google.cloud import datastore
from flask_dance.consumer.storage import BaseStorage
from flask_login import UserMixin, current_user

APP_PATH = os.environ.get('APP_PWD')


def query_handling(function):
    def wrapper(*args, **kwargs):
        try:
            function(*args, **kwargs)
            return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            f_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            error_msg = str(exc_type) + ' | ' + f_name + ' :: ' + \
                str(exc_tb.tb_lineno) + ' | ' + str(e)
            print(error_msg)
            return None
    return wrapper


class OathUser(UserMixin):
    client = datastore.Client.from_service_account_json(
        APP_PATH+'/config/gcloud.json')
    __acceptable_keys_list = ['oauth_id', 'provider',
                              'provider_user_id', 'user_id', 'token']

    def __init__(self, **kwargs):
        [self.__setattr__(key, kwargs.get(key))
         for key in self.__acceptable_keys_list]
        if not self.token and not self.user_id:
            oauth = self.get(provider=self.provider,
                             provider_user_id=self.provider_user_id)
            if not oauth:
                raise ValueError('Oauth Not Found')
            else:
                self.oauth_id = oauth.key.id
                self.provider = oauth['provider']
                self.provider_user_id = oauth['provider_user_id']
                self.token = oauth['token']
                self.user_id = oauth['user_id']
                self.created_at = oauth['created_at']
        elif self.token and self.user_id and self.provider_user_id and self.provider:
            ouath_key = self.client.key('Oauth')
            oauth = datastore.Entity(key=ouath_key)
            oauth['provider'] = self.provider
            oauth['token'] = self.token
            oauth['provider_user_id'] = self.provider_user_id
            oauth['user_id'] = self.user_id
            oauth['created_at'] = datetime.datetime.utcnow()
            self.client.put(oauth)
            self.oauth_id = oauth.key.id

    @staticmethod
    def get(provider, provider_user_id):
        query = OathUser.client.query(kind='Oauth')
        query.add_filter('provider', '=', provider)
        query.add_filter('provider_user_id', '=', provider_user_id)
        try:
            results = list(query.fetch())
            return results[0]
        except IndexError:
            return None

    def get_id(self):
        return self.oauth_id

    @query_handling
    def delete(self):
        key = self.client.key('Oauth', int(self.oauth_id))
        self.client.delete(key)


class User(UserMixin):
    client = datastore.Client.from_service_account_json(
        APP_PATH+'/config/gcloud.json')
    __acceptable_keys_list = ['fullname', 'email', 'username', 'user_id']

    def __init__(self, **kwargs):
        [self.__setattr__(key, kwargs.get(key))
         for key in self.__acceptable_keys_list]
        if not self.user_id:
            user_key = self.client.key('Users')
            user = datastore.Entity(key=user_key)
            user['fullname'] = self.fullname
            user['email'] = self.email
            user['username'] = self.username
            user['created_at'] = datetime.datetime.utcnow()
            self.client.put(user)
            self.user_id = user.key.id
        else:
            user = self.get(self.user_id)
            self.user_id = user.key.id
            if user['username']:
                self.username = user['username']
            self.fullname = user['fullname']
            self.email = user['email']
            self.created_at = user['created_at']

    def get_id(self):
        return self.user_id

    def set_username(self, username):
        updated_user = User.get(self.user_id)
        updated_user['username'] = username
        User.client.put(updated_user)

    @staticmethod
    def get(user_id):
        key = User.client.key('Users', int(user_id))
        user = User.client.get(key)
        return user

    @query_handling
    def delete(self):
        key = self.client.key('Users', int(self.user_id))
        self.client.delete(key)

    @staticmethod
    def list(limit=50):
        query = User.client.query(kind='Users')
        users = list(query.fetch(limit=limit))
        return users


class GoogleDatastoreBackend(BaseStorage):

    def __init__(self):
        super(GoogleDatastoreBackend, self).__init__()
        self.client = datastore.Client.from_service_account_json(
            APP_PATH+'/config/gcloud.json')

    @query_handling
    def get(self, provider, provider_user_id):
        query = self.client.query(kind='Oauth')
        query.add_filter('provider', '=', provider)
        query.add_filter('provider_user_id', '=', provider_user_id)
        results = list(query.fetch())
        return results[0]

    def set(self, oauth_props):
        ouath_key = self.client.key('Oauth')
        oauth = datastore.Entity(key=ouath_key)
        oauth['provider'] = oauth_props['provider']
        oauth['token'] = oauth_props['token']
        oauth['provider_user_id'] = oauth_props['provider_user_id']
        oauth['user_id'] = oauth_props['user_id']
        oauth['created_at'] = datetime.datetime.utcnow()
        self.client.put(oauth)
        return oauth.key

    def delete(self, provider, provider_user_id):
        query = self.client.query(kind='Oauth')
        query.add_filter('provider', '=', provider)
        query.add_filter('provider_user_id', '=', provider_user_id)
        results = list(query.fetch())
        self.client.delete(results[0].key)


if __name__ == '__main__':
    pass
