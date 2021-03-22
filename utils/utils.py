import arrow
import platform
import sys
import os
import time
import psutil
import shutil
import datetime
import pytz
import requests
import json
APP_PATH = os.environ.get('APP_PWD')

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


def generate_secret_key(size):
    import binascii
    return binascii.hexlify(os.urandom(size))


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


def send_simple_message(sender_name, body_msg):
    return requests.post(
        "https://api.mailgun.net/v3/mail.convertca.com/messages",
        auth=("api", os.environ.get("MAILGUN_KEY")),
        data={"from": "Convertca <no-reply@mail.convertca.com>",
              "to": ["dangtruong@gmail.com"],
              "subject": "Message from Convertca",
              "text": f"Message from {sender_name} \n--\n {body_msg}"})


def get_client_ip(req):
    client_info = requests.get(
        'https://geoip-db.com/json/' + req.environ['REMOTE_ADDR'])
    result = client_info.json()
    return json.dumps({
        'country_code': result['country_code'],
        'country_name': result['country_name']
    })


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def remove_expired_dirs():
    files_path = APP_PATH+'/web/files/'
    list_dir = [dI for dI in os.listdir(
        files_path) if os.path.isdir(os.path.join(files_path, dI))]
    if list_dir:
        for d in list_dir:
            fd = files_path+d
            ts = arrow.get(creation_date(fd))
            cts = arrow.utcnow()
            exp_ts = cts.timestamp-ts.timestamp
            if (exp_ts/3600) >= 1:
                # print('{} is expired.'.format(d))
                shutil.rmtree(fd)
