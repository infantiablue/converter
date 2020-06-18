import os
import sys
import json
import datetime
from google.cloud import datastore
from flask_login import UserMixin, current_user
from .firestore import query_handling, gclient


class OauthUser(UserMixin):
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
            ouath_key = gclient.key('Oauth')
            oauth = datastore.Entity(key=ouath_key)
            oauth['provider'] = self.provider
            oauth['token'] = self.token
            oauth['provider_user_id'] = self.provider_user_id
            oauth['user_id'] = self.user_id
            oauth['created_at'] = datetime.datetime.utcnow()
            gclient.put(oauth)
            self.oauth_id = oauth.key.id

    @staticmethod
    def get(provider, provider_user_id):
        query = gclient.query(kind='Oauth')
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
        key = gclient.key('Oauth', int(self.oauth_id))
        gclient.delete(key)


class User(UserMixin):
    __acceptable_keys_list = ['fullname', 'email', 'username', 'user_id']

    def __init__(self, **kwargs):
        [self.__setattr__(key, kwargs.get(key))
         for key in self.__acceptable_keys_list]
        if not self.user_id:
            user_key = gclient.key('Users')
            user = datastore.Entity(key=user_key)
            user['fullname'] = self.fullname
            user['email'] = self.email
            user['username'] = self.username
            user['created_at'] = datetime.datetime.utcnow()
            gclient.put(user)
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
        query = gclient.query(kind='Users')
        query.add_filter('username', '=', username)
        result = list(query.fetch())
        if not result:
            updated_user = User.get(self.user_id)
            updated_user['username'] = username
            gclient.put(updated_user)
            return True
        return False

    @staticmethod
    def get(user_id):
        key = gclient.key('Users', int(user_id))
        user = gclient.get(key)
        return user

    @query_handling
    def delete(self):
        key = gclient.key('Users', int(self.user_id))
        gclient.delete(key)

    @staticmethod
    def list(limit=50):
        query = gclient.query(kind='Users')
        users = list(query.fetch(limit=limit))
        return users


if __name__ == '__main__':
    pass
