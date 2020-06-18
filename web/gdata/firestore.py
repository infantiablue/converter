import os
from flask_dance.consumer.storage import BaseStorage
from google.cloud import datastore

APP_PATH = os.environ.get('APP_PWD')
gclient = datastore.Client.from_service_account_json(
    APP_PATH+'/config/gcloud.json')


def limit_history(user_id):
    query = gclient.query(kind='History')
    query.add_filter('userid', '=', user_id)
    # need to create index for Datastore to process
    query.order = ['-created_at']
    items = list(query.fetch())
    if len(items) > 50:
        gclient.delete(items[-1].key)
        return items[-1].key
    else:
        return False


# decoration function to handle query
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


class GoogleDatastoreBackend(BaseStorage):

    def __init__(self):
        super(GoogleDatastoreBackend, self).__init__()

    @query_handling
    def get(self, provider, provider_user_id):
        query = gclient.query(kind='Oauth')
        query.add_filter('provider', '=', provider)
        query.add_filter('provider_user_id', '=', provider_user_id)
        results = list(query.fetch())
        return results[0]

    def set(self, oauth_props):
        ouath_key = gclient.key('Oauth')
        oauth = datastore.Entity(key=ouath_key)
        oauth['provider'] = oauth_props['provider']
        oauth['token'] = oauth_props['token']
        oauth['provider_user_id'] = oauth_props['provider_user_id']
        oauth['user_id'] = oauth_props['user_id']
        oauth['created_at'] = datetime.datetime.utcnow()
        gclient.put(oauth)
        return oauth.key

    def delete(self, provider, provider_user_id):
        query = gclient.query(kind='Oauth')
        query.add_filter('provider', '=', provider)
        query.add_filter('provider_user_id', '=', provider_user_id)
        results = list(query.fetch())
        gclient.delete(results[0].key)
