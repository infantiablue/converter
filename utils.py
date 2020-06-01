from contextlib import contextmanager
import sys
import os
import psutil
import datetime
import pytz
import requests
import json

# SOURCE: https://stackoverflow.com/questions/287871/print-in-terminal-with-colors
CEND = '\033[0m'
CGREEN = '\33[32m'

# Progress Bar
# SOURCE: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(CGREEN+'\r%s |%s| %s%% %s' %
          (prefix, bar, percent, suffix), end='\r'+CEND)
    # Print New Line on Complete
    if iteration == total:
        print()


# Turn off output
# SOURCE: https://thesmithfam.org/blog/2012/10/25/temporarily-suppress-console-output-in-python/
@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


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
