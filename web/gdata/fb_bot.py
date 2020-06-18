from flask import Blueprint, request
import os
import json
import requests
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from utils.yt import get_popular_video_youtube, search_video_youtube

# set up cache system
cache_opts = {
    'cache.type': 'dbm',
    'cache.data_dir': '/tmp/cache/data',
    'cache.lock_dir': '/tmp/cache/lock'
}
cache = CacheManager(**parse_cache_config_options(cache_opts))
tmpl_cache = cache.get_cache('facebook_bot_cache', type='dbm', expire=1800)

# setup encoding and absolute root path
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.'))

fb_bot = Blueprint('fb_bot', __name__, None)
fb_bot.config = {}


@fb_bot.record
def get_fb_config(setup_state):

    global FB_GRAPH_API, FB_MSG_API_URL, VERIFY_TOKEN, PAGE_ACCESS_TOKEN
    app = setup_state.app
    fb_bot.config = dict([(key, value) for (key, value) in app.config.items()])
    # FB App settings
    FB_GRAPH_API = fb_bot.config['FB_GRAPH_API']
    FB_MSG_API_URL = fb_bot.config['FB_MSG_API_URL']
    VERIFY_TOKEN = fb_bot.config['FB_VERIFY_TOKEN']
    PAGE_ACCESS_TOKEN = fb_bot.config['FB_PAGE_ACCESS_TOKEN']


def verify_webhook(req):
    if req.args.get('hub.verify_token') == VERIFY_TOKEN:
        return req.args.get('hub.challenge')
    else:
        return 'incorrect'


def respond_search_youtube(sender, keyword):
    videos = json.loads(search_video_youtube(limit=5, keyword=keyword))
    list_video = []
    for video in videos:
        el = {
            'title': video['title'],
            'image_url': video['thumb'],
            'default_action': {
                'type': 'web_url',
                'url': video['url'],
                'webview_height_ratio': 'COMPACT'
            },
            'buttons': [
                {
                    'type': 'postback',
                    'title': 'Convert2 MP3',
                    'payload': video['url']
                }
            ]
        }
        list_video.append(el)
    payload = {
        'message': {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'generic',
                    'elements': list_video
                }
            }
        },
        'recipient': {
            'id': sender
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }
    response = requests.post(
        FB_MSG_API_URL,
        headers={'Content-Type': 'application/json'},
        params=auth,
        json=payload
    )
    return response.json()


def respond_popular(sender, country='US'):
    videos = json.loads(get_popular_video_youtube(
        limit=5, random_videos=True, country=country_code))
    list_video = []
    for video in videos:
        el = {
            'title': video['title'],
            'image_url': video['thumb'],
            'default_action': {
                'type': 'web_url',
                'url': video['url'],
                'webview_height_ratio': 'COMPACT'
            },
            'buttons': [
                {
                    'type': 'postback',
                    'title': 'Convert2 MP3',
                    'payload': video['url']
                }
            ]
        }
        list_video.append(el)
    payload = {
        'message': {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'generic',
                    'elements': list_video
                }
            }
        },
        'recipient': {
            'id': sender
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }
    response = requests.post(
        FB_MSG_API_URL,
        headers={'Content-Type': 'application/json'},
        params=auth,
        json=payload
    )
    return response.json()


def respond_download(sender, message):
    LOCK_FILE_PATH = ROOT_PATH + '/cache/locked_senders/' + sender + '.lock'
    if not os.path.exists(LOCK_FILE_PATH):
        with open(LOCK_FILE_PATH, 'w') as f_lock:
            json.dump({'url': message}, f_lock)
        send_message(sender, 'Your request is being processed. Please wait ⏳')
        result = json.loads(
            download([message], audio_quality='192', action_from='fb_bot'))
        root_url = current_app.config['ROOT_URL']
        if result['status']:
            # send_message(sender, 'Here you go, click on the link below to download 📦: {} '.format(result['data']['title']))
            url_to_download = root_url + '/file/' + \
                result['data']['path'] + result['data']['extenstion']
            payload = {
                'message': {
                    'attachment': {
                        'type': 'template',
                        'payload': {
                            'template_type': 'generic',
                            'elements': [{
                                'title': result['data']['title'],
                                'image_url': 'https://i.ytimg.com/vi/' + result['data']['id'] + '/sddefault.jpg',
                                'buttons':[
                                    {
                                        'type': 'web_url',
                                        'title': 'Download',
                                        'url': url_to_download
                                    }
                                ]
                            }]
                        }
                    }
                },
                'recipient': {
                    'id': sender
                },
                'notification_type': 'regular'
            }
            auth = {
                'access_token': PAGE_ACCESS_TOKEN
            }
            response = requests.post(
                FB_MSG_API_URL,
                headers={'Content-Type': 'application/json'},
                params=auth,
                json=payload
            )
            os.unlink(LOCK_FILE_PATH)
            return response.json()
        else:
            os.unlink(LOCK_FILE_PATH)
            response = result['error']
            send_message(sender, response)
    else:
        with open(LOCK_FILE_PATH, 'r') as f_lock:
            f_name = json.load(f_lock)
        send_message(
            sender, 'You have requested to convert from this url {}, I can only handle one for now. Please wait for your previous request finished ⏳'.format(f_name['url']))


def is_user_message(message):
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get('is_echo'))


def send_message(recipient_id, text):
    payload = {
        'message': {
            'text': text
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }
    response = requests.post(
        FB_MSG_API_URL,
        headers={'Content-Type': 'application/json'},
        params=auth,
        json=payload
    )
    return response.json()


def get_fb_fullname(sender_id):
    response = requests.get(
        FB_GRAPH_API+str(sender_id),
        headers={'Content-Type': 'application/json'},
        params={
            'access_token': PAGE_ACCESS_TOKEN
        }
    )
    return response.json()


@fb_bot.route('/webhook', methods=['GET', 'POST'])
def listen():
    ''' This is the main function flask uses to
    listen at the `/webhook` endpoint '''
    if request.method == 'GET':
        return verify_webhook(request)

    if request.method == 'POST':
        if 'FLASK_ENV' not in os.environ or os.environ['FLASK_ENV'] == 'development':
            country_code = 'VN'
        else:
            client_info = json.loads(get_client_ip(request))
            country_code = client_info['country_code']
        payload = request.json
        event = payload['entry'][0]['messaging']
        for x in event:
            sender_id = x['sender']['id']
            if is_user_message(x):
                if x['message'] and x['message']['text']:
                    msg_id = event[0]['message']['mid']
                    text = x['message']['text'].lower()
                    nlp_entities = event[0]['message']['nlp']['entities']
                    if 'greetings' in nlp_entities:
                        fb_user = get_fb_fullname(sender_id)
                        send_message(
                            sender_id, 'Hi ' + fb_user['first_name'] + ', may I help you 🤖')
                    elif text.lstrip().rstrip() == 'popular':
                        respond_popular(sender_id, country=country_code)
                    elif text.startswith('search') or text.startswith('text') or text.startswith('get me'):
                        kw = text.split(
                            'search')[-1].split('find')[-1].split('get me')[-1]
                        respond_search_youtube(sender_id, kw)
                    elif 'url' in nlp_entities:
                        white_list = ['youtube.com', 'youtu.be']
                        if len(nlp_entities['url']) > 1:
                            send_message(
                                sender_id, 'Sorry, I can only handle 1 link at once for now 😔')
                        else:
                            if nlp_entities['url'][0]['domain'] in white_list:
                                # check if the msg was cached
                                if not tmpl_cache.has_key(msg_id):
                                    def cache_respond(): respond_download(
                                        sender_id, nlp_entities['url'][0]['value'])
                                    tmpl_cache.get(
                                        key=msg_id, createfunc=cache_respond)
                                else:
                                    print('Cached')
                            else:
                                send_message(
                                    sender_id, 'At the moment, I can only process video from YouTube 😔')
                    elif text.lstrip().rstrip() == 'help':
                        send_message(
                            sender_id, 'You may type "popular" or "search [keywords]"')
                    else:
                        send_message(
                            sender_id, 'You may type "help" for more instructions.')
            elif 'postback' in x:
                if not tmpl_cache.has_key(str(x['timestamp'])):
                    def cache_respond(): respond_download(
                        sender_id, x['postback']['payload'])
                    tmpl_cache.get(
                        key=str(x['timestamp']), createfunc=cache_respond)
                else:
                    print('Cached')
            return 'ok'
