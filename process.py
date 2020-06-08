from __future__ import unicode_literals
import json
import sys
import hashlib
import datetime
import os
import logging
import youtube_dl
import unidecode
import glog
import uuid
from utils import print_progress_bar, get_timestamp

DURATION_LIMIT = 1800
APP_PATH = os.path.dirname(os.path.realpath(__file__))
st = get_timestamp(time_format='%Y-%m-%d_%H-%M')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler(APP_PATH+'/logs/download.log'),
    ])
download_logger = logging.getLogger('download')


class BasicLogger(object):
    def __init__(self, urls):
        self.urls = urls

    def debug(self, msg):
        download_logger.debug(msg)

    def warning(self, msg):
        download_logger.warning(msg)
        glog.write_log('download', json.dumps({
            'url': self.urls[0],
            'msg': msg
        }), 'WARNING')

    def error(self, msg):
        download_logger.error(msg)
        glog.write_log('download', json.dumps({
            'url': self.urls[0],
            'status': 'error',
            'msg': msg
        }), 'ERROR')


def progress_hook(d):
    try:
        tb = int(d['total_bytes'])
    except KeyError:
        tb = int(d['total_bytes_estimate'])
    if d['status'] == 'downloading':
        print_progress_bar(int(d['downloaded_bytes']), tb,
                           prefix='Progress:', suffix='Complete', length=50)
    elif d['status'] == 'finished':
        print('Done downloading, now converting ...')


def download(urls, audio_format='mp3', audio_quality='128', action_from='web'):
    # generate random dir name
    dir_name = uuid.uuid4().hex
    dir_path = os.path.join(APP_PATH+'/web/files/', dir_name)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    ydl_opts = {
        'forceurl': True,
        'writethumbnail': True,
        'writeinfojson': True,
        'noplaylist': True,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': audio_quality,
        }],
        'logger': BasicLogger(urls=urls),
        'outtmpl': dir_path + '/%(title)s.%(ext)s'
    }

    # add print out downloading process for debug
    if 'FLASK_ENV' not in os.environ or os.environ['FLASK_ENV'] == 'development':
        ydl_opts['progress_hooks'] = [progress_hook]

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(urls[0], download=False)
    if 'is_live' in info:
        if info['is_live']:
            return json.dumps({
                'status': False,
                'code': 'live_video',
                'error': 'Your requested URL is a LIVE video, and can not be downloaded.'
            })
    if int(info['duration']) < DURATION_LIMIT:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(urls)
        dir_list = os.listdir(dir_path)
        thumb = None
        filename = None
        title = False
        video_id = None
        for f_name in dir_list:
            # remove accents from file name for accented language and etc ...
            if not title:
                base = os.path.basename(f_name)
                title = os.path.splitext(base)[0]
            new_file = unidecode.unidecode(f_name)
            # then rename it
            os.rename(dir_path + '/' + f_name, dir_path + '/' + new_file)
            if new_file.endswith('.' + audio_format):
                filename = new_file
                file_size = os.path.getsize(dir_path + '/' + new_file)
            if new_file.endswith('.jpg'):
                thumb = new_file
            if new_file.endswith('.json'):
                with open(dir_path + '/' + new_file) as f:
                    data = json.load(f)
                video_id = data['id']
        json_result = json.dumps({
            'status': True,
            'data': {
                'id': video_id,
                'title': title,
                'path': dir_name,
                'filename': filename,
                'thumb': thumb,
                'extenstion': '.' + audio_format
            }
        })

        return json_result
    else:
        glog.write_log('download', json.dumps({
            'url': urls[0],
            'status': 'exceed_filesize',
            'source': action_from
        }), 'WARNING')
        return json.dumps({
            'status': False,
            'code': 'exceed_filesize',
            'error': 'At the moment, I can only handle content with {} minutes long.'.format(int(DURATION_LIMIT/60))
        })


def run_command(command):
    import subprocess
    import shlex
    import re

    _DURATION_RX = re.compile("Duration: (\d{2}):(\d{2}):(\d{2})\.\d{2}")
    _PROGRESS_RX = re.compile("time=(\d{2}):(\d{2}):(\d{2})\.\d{2}")
    _SOURCE_RX = re.compile("from '(.*)':")

    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            search = _DURATION_RX.search(output)

    rc = process.poll()
    return rc


if __name__ == '__main__':
    print(download(['https://youtube.com/watch?v=_aghWPzkB7M']))
