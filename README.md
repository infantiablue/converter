# Convertca.com

The idea is to practice some modern web technologies such as _Flask, VueJS, Webpack, Bootstrap_ ... to develop a web application then deploy it to _Google Compute Engine (GCE)_, with _Google DataStore_ in robust ways. The main function of the app is to convert an online video from youtube or other services to MP3 with some addtional features:

- Facebook authorization
- Save the converted file to DropBox

## Requirements

- Python 3 and packages in `requirements.txt`
- Node, npm and packages in `web/static/package.json` (for development)
- Nginx for reserve proxy server
- Google Cloud account (*for experimenting with logging service*)
- Facebook Developer account

## Set Up

1. Create an VM instance on Google Compute Engine
    - [Use SSH for GitHub](https://help.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh)
    - [SSH to connect VM instance](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/create-ssh-keys-detailed)
2. Install required packages

        sudo apt install software-properties-common python3 python3-venv python-pip python3-pip python-pip python3-dev git nodejs npm openssl build-essential libssl-dev libffi-dev libpq-dev ffmpeg virtualenv direnv nginx

3. Git clone
4. Create virtual environment (inside the app directory) `python -m venv env`
5. Install and configure 'direnv` with the current shell, follow [this instruction](https://direnv.net/docs/hook.html).
6. Create `.envrc` file

        source env/bin/activate
        export LANG="en_US.UTF-8"
        export FLASK_APP="web"
        export FLASK_ENV="production"
        export FLASK_ROOT_URL="[your-web-url]"
        export SECRET_KEY="[your-secret-key]"      
        export SOCKET_URI="[your-websocket-uri]"        
        export FACEBOOK_OAUTH_CLIENT_ID="[your-fb-app-id]"
        export FACEBOOK_OAUTH_CLIENT_SECRET="[your-fb-app-secret]"
        export YOUTUBE_API_KEY="[your-youtube-api-key]"
        export GOOGLE_APPLICATION_CREDENTIALS="[path to google cloud json file]"
        export GOOGLE_OAUTH_CLIENT_ID="[...]"
        export GOOGLE_OAUTH_CLIENT_SECRET="[...]"
        export OAUTHLIB_RELAX_TOKEN_SCOPE="True"
        export OAUTHLIB_INSECURE_TRANSPORT="True"        
        export MAIL_USERNAME="[your-email-address]"
        export MAIL_PASSWORD="[https://support.google.com/mail/answer/185833?hl=en-GB]"
        export MAIL_SENDER="[...]"
        export APP_PWD="[your-app-root-directory]"       
        export DATABASE_URL="[your-postgresql-uri-with-password]"
        gcloud config set project [your-google-cloud-project-id]

7. Install Python dependencies 'pip install -r config/requirements.txt`
8. Create Postgres DB

        CREATE DATABASE converter;
        CREATE USER converter WITH ENCRYPTED PASSWORD 'password';
        GRANT ALL PRIVILEGES ON DATABASE converter TO converter;

## Congiguration For Production

- [ ] Run `gcloud init` to configure [Google Cloud SDK authentication](https://cloud.google.com/sdk/docs/authorizing)
- [ ] Create [Google cloud service account key](https://console.cloud.google.com/apis/credentials/serviceaccountkey) then fille the name to _GOOGLE_APPLICATION_CREDENTIALS_ | `.envrc`
- [ ] Enable [logging service](https://console.developers.google.com/apis/api/logging.googleapis.com/overview?project=528683999125)
- [ ] Get [YOUTUBE_API_KEY](https://developers.google.com/youtube/v3/getting-started) | `.envrc`
- [ ] Create [Datastore entity](https://console.cloud.google.com/datastore/welcome)
- [ ] Run command to create indexes `gcloud datastore indexes create config/index.yaml`
- [ ] Generate app _SECRET_KEY_ by this command `python -c 'import os; print(os.urandom(16))` | `config.py`
- [ ] Get [FACEBOOK_OAUTH_CLIENT_ID & FACEBOOK_OAUTH_CLIENT_SECRET](https://developers.facebook.com/) | `.envrc`
- [ ] Modify app root path & domain name then include the conf file `config/nginx.conf` into `/etc/nginx/nginx.conf`

        ...
        server_name  converter.techika.com;
        error_log    /home/truong/converter/logs/nginx_error.log;
        ...

        location /static/ {
            alias /home/truong/converter/web/static/;
        }
        location /files/ {
            alias /home/truong/converter/web/files;
        }

- [ ] Start gunicorn server `supervisord -c config/supervisor.conf`
- [ ] Configure SSL
        sudo apt install software-properties-common
        sudo apt install certbot python-certbot-nginx
        sudo certbot --nginx -d your_domain -d www.your_domain

- [ ] Set-up Mail Account then fill in _MAIL_USERNAME_,_MAIL_PASSWORD_,_MAIL_SENDER_, [Gmail will be used](https://support.google.com/mail/answer/185833?hl=en) in this case for the sake of expediency. | `.envrc`
- [ ] Run `deploy.sh` to migrate Postgresql DB

## Local Development

- `brew install ffmpeg`
- Run `gunicorn wsgi:app` (port 8000)
- Run `python server.py` (websocket server)
- Run Postgres DB instance.
  