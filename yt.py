import requests
import json
import os
import random
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

APP_PATH = os.path.dirname(os.path.realpath(__file__))
CACHE_FILE = APP_PATH + '/' + 'cache/popular_youtube.json'
YT_KEY = os.environ.get("YOUTUBE_API_KEY"),

# set up cache system
cache_opts = {
    'cache.type': 'dbm',
    'cache.data_dir': '/tmp/cache/data',
    'cache.lock_dir': '/tmp/cache/lock'
}
cache = CacheManager(**parse_cache_config_options(cache_opts))
tmpl_cache = cache.get_cache('template', type='dbm', expire=1800)


def get_popular_video_youtube(limit=30, random_videos=False, country='US'):
    payload = {
        'part': ['snippet', 'contentDetails', 'statistics'],
        'chart': 'mostPopular',
        'regionCode': country,
        'videoCategoryId': '10',
        'maxResults': str(limit),
        'key': YT_KEY
    }
    if not tmpl_cache.has_key(country):
        def cache_respond():
            res = requests.get(
                'https://www.googleapis.com/youtube/v3/videos', params=payload)
            if res.status_code != 200:
                payload['regionCode'] = 'US'
                res = requests.get(
                    'https://www.googleapis.com/youtube/v3/videos', params=payload)
            return res
        res = tmpl_cache.get(key=country, createfunc=cache_respond)
    else:
        # for debug print('Cached')
        res = tmpl_cache.get_value(key=country)
    data = res.json()

    result = []
    if random_videos:
        video_list = random.sample(range(0, int(limit)), int(limit))
    else:
        video_list = range(0, limit)

    for i in video_list:
        item = data['items'][i]
        if 'maxres' in item['snippet']['thumbnails']:
            thumbnail = item['snippet']['thumbnails']['maxres']['url']
        elif 'standard' in item['snippet']['thumbnails']:
            thumbnail = item['snippet']['thumbnails']['standard']['url']
        elif 'high' in item['snippet']['high']:
            thumbnail = item['snippet']['thumbnails']['high']['url']
        else:
            # customize by our own thumbnail
            thumbnail = item['snippet']['thumbnails']['default']['url']

        result.append({'id': item['id'],
                       'url': 'https://www.youtube.com/watch?v='+item['id'],
                       'title': item['snippet']['title'],
                       'thumb': thumbnail})
        i = i + 1
    return json.dumps(result)


@cache.cache('search_video_youtube', type='dbm', expire=3600)
def search_video_youtube(keyword='', limit=30):
    payload = {
        'part': ['snippet', 'contentDetails', 'statistics'],
        'q': str(keyword),
        'maxResults': str(limit),
        'type': 'video',
        'key': YT_KEY
    }
    res = requests.get(
        'https://www.googleapis.com/youtube/v3/search', params=payload)
    data = res.json()
    result = []
    if 'items' in data:
        for item in data['items']:
            if 'high' in item['snippet']['thumbnails']:
                thumbnail = item['snippet']['thumbnails']['high']['url']
            elif 'medium' in item['snippet']['thumbnails']:
                thumbnail = item['snippet']['thumbnails']['medium']['url']
            else:
                thumbnail = item['snippet']['thumbnails']['default']['url']

            result.append({'id': item['id']['videoId'],
                           'url': 'https://www.youtube.com/watch?v=' + item['id']['videoId'],
                           'title': item['snippet']['title'],
                           'thumb': thumbnail})
        return json.dumps(result)
    else:
        return json.dumps(data, indent=4)


if __name__ == '__main__':
    print(search_video_youtube('brazil'))
