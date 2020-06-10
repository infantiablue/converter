import requests
import json
import os
import random
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

APP_PATH = os.environ.get('APP_PWD')
CACHE_FILE = APP_PATH + '/cache/popular_youtube.json'
YT_KEY = str(os.environ.get('YOUTUBE_API_KEY'))
YT_API_ENDPOINT = 'https://www.googleapis.com/youtube/v3/'
# set up cache system
cache_opts = {
    'cache.type': 'dbm',
    'cache.data_dir': APP_PATH + '/cache/data',
    'cache.lock_dir': APP_PATH + '/cache/lock'
}
cache = CacheManager(**parse_cache_config_options(cache_opts))
tmpl_cache = cache.get_cache('template', type='dbm', expire=1800)


def get_popular_video_youtube(limit=30, random_videos=False, country='US'):
    '''
    Get a number of popular youtube video by country

    Args:

        limit (int, optional): The number of video to receive. Defaults to 30.
        random_videos (bool, optional): Random or not. Defaults to False.
        country (str, optional): Defaults to 'US'.

    Returns:

        json: a list with: id, url, title, thumb
    '''
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
            res = requests.get(YT_API_ENDPOINT+'videos', params=payload)
            if res.status_code != 200:
                payload['regionCode'] = 'US'
                res = requests.get(YT_API_ENDPOINT+'videos', params=payload)
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
        if 'items' in data and data['items'][i]:
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
def search_video_youtube(keyword, limit=30):
    '''
    Search for YouTube video

    Args:

        keyword (str): keyword to search.
        limit (int, optional): Defaults to 30.

    Returns:

        json: a list with: id, url, title, thumb
    '''
    payload = {
        'part': ['snippet', 'contentDetails', 'statistics'],
        'q': str(keyword),
        'maxResults': str(limit),
        'type': 'video',
        'key': YT_KEY
    }
    res = requests.get(
        YT_API_ENDPOINT+'search', params=payload)
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


def get_yt_video_time(url):
    '''
    Get the duration (seconds) of a Youtube video

    Args:

        url (str): a valid Youtube URL

    Returns:

        int: seconds of the video
    '''
    import isodate
    import requests
    import urllib.parse as urlparse
    from urllib.parse import parse_qs
    r = requests.get(url)
    url = r.url
    # parse url to get video ID
    parsed = urlparse.urlparse(url)
    yt_video_id = parse_qs(parsed.query)['v'][0]
    # make api request
    res = requests.get(
        YT_API_ENDPOINT+'videos?id='+yt_video_id+'&part=contentDetails&key='+YT_KEY)
    data = res.json()
    # convert time to seconds
    t = isodate.parse_duration(data['items'][0]['contentDetails']['duration'])
    return str(int(t.total_seconds()))


if __name__ == '__main__':
    print(get_popular_video_youtube(limit=15))
