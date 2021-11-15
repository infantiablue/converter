import os
import sys
import json
import datetime
from flask import Flask, g, render_template, send_from_directory, request, redirect, url_for, jsonify, Blueprint, session
from utils.process import download
import requests
import urllib.parse as urlparse
from urllib.parse import parse_qs
from sqlalchemy.orm.exc import NoResultFound
from utils.yt import get_popular_video_youtube
from utils.utils import get_client_ip
from flask_login import current_user
from .models import db, Video
from utils.logger import app_logger

# setup encoding and absolute root path
APP_PATH = os.path.dirname(os.path.realpath(__file__))
# setup directory path
static_file_dir = os.path.join(APP_PATH, 'files')

home_bp = Blueprint('home_bp', __name__)


# autoversioning feature to avoid cached static files
@home_bp.app_template_filter('autoversion')
def autoversion_filter(filename):
    # determining fullpath might be project specific
    fullpath = os.path.join('web/', filename[1:])
    try:
        timestamp = str(os.path.getmtime(fullpath))
    except OSError:
        return filename
    newfilename = "{0}?v={1}".format(filename, timestamp)
    return newfilename


@home_bp.before_request
def detect_user_language():
    if not 'country_code' in session:
        try:
            client_info = json.loads(get_client_ip(request))
            session['country_code'] = client_info['country_code']
        except:
            session['country_code'] = 'US'


@home_bp.before_request
def get_current_user():
    g.user = current_user


@home_bp.route('/')
def index():
    return render_template('index.html')


@home_bp.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@home_bp.route('/file/<path>.<file_ext>', methods=['GET'])
def serve_file_in_dir(path, file_ext):
    if not os.path.isdir(os.path.join(static_file_dir, path)):
        return redirect(url_for('index'))

    dir_path = os.path.join(static_file_dir, path)
    dir_list = os.listdir(dir_path)
    filename = None
    for file in dir_list:
        if file.endswith('.' + file_ext):
            filename = file
    path = os.path.join(path, filename)
    return send_from_directory(static_file_dir, path, as_attachment=True)


@home_bp.route('/img/<path:path>')
def send_img(path):
    return send_from_directory(static_file_dir, path)


@home_bp.route('/convert', methods=['POST'])
def convert():
    if request.method == 'POST':
        data = request.get_data()
        # google task handling data
        if not isinstance(data, dict):
            data = data.decode('utf-8')
            data = json.loads(data.replace("'", "\""))

        if 'audio_format' in data:
            audio_format = data['audio_format']
        else:
            audio_format = 'mp3'
        audio_quality = data['audio_quality']

        url = request.json['urls']
        r = requests.get(url)
        url = r.url
        # parse url to get video ID
        parsed = urlparse.urlparse(url)
        # strip wwww
        provider = str(parsed.netloc).replace('www.', '')
        if provider == 'youtube.com':
            try:
                result = download([url], audio_format,
                                  audio_quality, target=data['name'])

                if not current_user.is_anonymous:
                    video_id = parse_qs(parsed.query)['v'][0]
                    try:
                        # check if url existed
                        video = Video.query.filter_by(user_id=int(
                            current_user.id), video_id=video_id, provider=provider).one()
                        video.created_at = datetime.datetime.utcnow()
                        db.session.commit()

                    except NoResultFound:
                        new_video = Video(
                            url=url,
                            user_id=current_user.id,
                            video_id=video_id,
                            provider=provider
                        )
                        db.session.add(new_video)
                        db.session.commit()
                        Video.limit_history_videos(user_id=current_user.id)
                return jsonify(result), 200
            except Exception as e:
                app_logger.error('Error at %s', 'division', exc_info=e)
                return jsonify(json.dumps({
                    'status': False,
                    'code': 'error',
                    'error': 'Something goes wrong.'
                })), 403

        else:
            return jsonify(json.dumps({
                'status': False,
                'code': 'unsupported_provider',
                'error': 'This service provider is not supported yet.'
            })), 403


@home_bp.route('/popular', methods=['GET'])
def popular():
    if 'FLASK_ENV' not in os.environ or os.environ['FLASK_ENV'] == 'development':
        country_code = 'VN'
    else:
        if 'country_code' in session:
            country_code = session['country_code']
        else:
            country_code = 'US'
    if request.method == 'GET':
        if 'limit' in request.args:
            limit = request.args.get('limit')
        else:
            limit = 30
        return jsonify(get_popular_video_youtube(limit=limit, random_videos=True, country=country_code)), 200


@home_bp.route('/get_duration', methods=['POST'])
def get_duration():
    if request.method == 'POST':
        from utils.yt import get_yt_video_time
        yt_video_url = request.json['yt_video_url']
        return get_yt_video_time(yt_video_url), 200
