# Convert2.Cloud

The idea is to practice some modern web technologies such as *Flask, VueJS, Webpack, Bootstrap* ... to develop a web application then deploy it to *Google Compute Engine (GCE)*, with *Google DataStore* in robust ways. The main function of the app is to convert an online video from youtube or other services to MP3 with some addtional features:

* Facebook authorization
* Save the converted file to DropBox

## Requirements

* Python 3 and packages in `requirements.txt`
* Node, npm and packages in `web/static/package.json`
* Nginx for reserve proxy server
* Google Cloud account

## Set Up

1. Create an VM instance on Google Compute Engine
2. Git clone
3. Create virtual environment (inside the app directory) `python -m venv env`
4. Install and configure 'direnv` with the current shell, follow [this instruction](https://direnv.net/docs/hook.html).
5. Create `.envrc' file

    ```bash
    source env/bin/activate
    export FLASK_APP="web"
    export FLASK_ENV="production"
    export FACEBOOK_OAUTH_CLIENT_ID="[your-fb-app-id]"
    export FACEBOOK_OAUTH_CLIENT_SECRET="[your-fb-app-secret]"
    export YOUTUBE_API_KEY="[your-youtube-api-key]"
    export GOOGLE_APPLICATION_CREDENTIALS="gcloud.json"
    export MAIL_USERNAME="[your-email-address]"
    export MAIL_PASSWORD="[your-email-password]"
    export MAIL_SENDER="Converter"
    gcloud config set project [yourproject-id]
    ```

6. Install Python dependencies 'pip install -r requirements.txt`
7. Go to `web/static` to install Node dependencies `npm install`
8. Install nginx `sudo apt install nginx`

## Congiguration

* Start server with `gunicorn "app:create_app()"`
* [Create Google cloud service account key](https://console.cloud.google.com/apis/credentials/serviceaccountkey)
* Enable [logging service](https://console.developers.google.com/apis/api/logging.googleapis.com/overview?project=528683999125)
* [Create Datastore entity](https://console.cloud.google.com/datastore/welcome)
* Generate app *SECRET_KEY* by this command `python -c 'import os; print(os.urandom(16))` then input to `config.py`
