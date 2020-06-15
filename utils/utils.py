from contextlib import contextmanager
import sys
import os
import psutil
import datetime
import pytz
import requests
import json


# Get timestamp by configured timezone
def get_timestamp(tz='Asia/Ho_Chi_Minh', time_format='%a %b %d %Y %H:%M:%S'):
    utc_naive = datetime.datetime.utcnow()
    utc = utc_naive.replace(tzinfo=pytz.utc)
    return utc.astimezone(pytz.timezone(tz)).strftime(time_format)


def clear_screen():
    if psutil.OSX:
        os.system('clear')
    else:
        os.system('cls')


def str_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError


def generate_secret_key():
    import binascii
    return binascii.hexlify(os.urandom(24))


def human_readable_size(size, decimal_places=2):
    for unit in ['', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f'{size:.{decimal_places}f}{unit}'


def send_email(recipients, sender_name, body_msg):
    import smtplib
    from email.mime.text import MIMEText

    smtp_ssl_host = 'smtp.gmail.com'
    smtp_ssl_port = 465
    username = os.environ.get('MAIL_USERNAME')
    password = os.environ.get('MAIL_PASSWORD')
    sender = os.environ.get('MAIL_SENDER')
    targets = recipients

    msg = MIMEText(body_msg)
    msg['Subject'] = 'Message from Converter'
    msg['From'] = sender_name
    msg['To'] = ', '.join(targets)

    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    server.login(username, password)
    server.sendmail(sender, targets, msg.as_string())
    server.quit()


def get_client_ip(req):
    client_info = requests.get(
        'https://geoip-db.com/json/' + req.environ['REMOTE_ADDR'])
    result = client_info.json()
    return json.dumps({
        'country_code': result['country_code'],
        'country_name': result['country_name']
    })
