import os
import sys
import time
import json
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, jsonify, Blueprint, session, after_this_request, Response, current_app

from process import download
import requests
from yt import get_popular_video_youtube, search_video_youtube
from utils import get_client_ip
# setup encoding and absolute root path
# ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.'))
APP_PATH = os.path.dirname(os.path.realpath(__file__))
# setup directory path
static_file_dir = os.path.join(APP_PATH, 'files')

home_page = Blueprint('home_page', __name__)


@home_page.app_template_filter('autoversion')
def autoversion_filter(filename):
    # determining fullpath might be project specific
    fullpath = os.path.join('web/', filename[1:])
    try:
        timestamp = str(os.path.getmtime(fullpath))
    except OSError:
        return filename
    newfilename = "{0}?v={1}".format(filename, timestamp)
    return newfilename


@home_page.before_request
def detect_user_language():
    if not 'country_code' in session:
        client_info = json.loads(get_client_ip(request))
        session['country_code'] = client_info['country_code']


@home_page.route('/')
def index():
    return render_template('index.html')


@home_page.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@home_page.route('/file/<path>.<file_ext>', methods=['GET'])
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


@home_page.route('/img/<path:path>')
def send_img(path):
    return send_from_directory(static_file_dir, path)


@home_page.route('/test')
def test():
    return render_template('progress.html')


@home_page.route('/progress')
def progress():
    def generate():
        x = 0
        while x <= 100:
            yield "data:" + str(x) + "\n\n"
            x = x + 10
            time.sleep(0.5)

    return Response(generate(), mimetype='text/event-stream')


@home_page.route('/convert', methods=['POST'])
def convert():
    if request.method == 'POST':
        audio_format = 'mp3'
        audio_quality = request.json['audio_quality']
        result = jsonify(
            download([request.json['urls']], audio_format, audio_quality))
        return result, 200


@home_page.route('/popular', methods=['GET'])
def popular():
    if 'FLASK_ENV' not in os.environ or os.environ['FLASK_ENV'] == 'development':
        country_code = 'VN'
    else:
        if 'country_code' in session:
            country_code = session['country_code']
        else:
            country_code = 'US'
    if request.method == 'GET':
        limit = request.args.get('limit')
        return jsonify(get_popular_video_youtube(limit=limit, random_videos=True, country=country_code)), 200


@home_page.route('/get_duration', methods=['POST'])
def get_duration():
    if request.method == 'POST':
        from yt import get_yt_video_time
        yt_video_url = request.json['yt_video_url']
        return get_yt_video_time(yt_video_url), 200
