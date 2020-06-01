import sys
import os
from flask import Flask, redirect, url_for, flash, render_template, Blueprint, current_app
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_login import (
    LoginManager, UserMixin, current_user,
    login_required, login_user, logout_user
)
from google.cloud import datastore
from werkzeug.contrib.fixers import ProxyFix
from .user import User, GoogleDatastoreBackend, OathUser

profile_page = Blueprint('profile_page', __name__, None)
profile_page.config = {}

blueprint = make_facebook_blueprint(
    client_id=os.environ.get("FACEBOOK_OAUTH_CLIENT_ID"),
    client_secret=os.environ.get("FACEBOOK_OAUTH_CLIENT_SECRET"),
    scope=['email'],
)

# setup SQLAlchemy backend with Google Data Store https://console.cloud.google.com/datastore
blueprint.backend = GoogleDatastoreBackend()
# setup login manager
login_manager = LoginManager()
login_manager.login_view = 'facebook.login'


@login_manager.user_loader
def load_user(user_id):
    return User(user_id=user_id)

# create/login local user on successful OAuth login


@oauth_authorized.connect_via(blueprint)
def facebook_logged_in(blueprint, token):
    if not token:
        # flash("Failed to log in with facebook.", category="error")
        return False

    resp = blueprint.session.get('/me?fields=email,name')
    if not resp.ok:
        msg = 'Failed to fetch user info from facebook.'
        # flash(msg, category='error')
        return False

    facebook_info = resp.json()
    facebook_user_id = str(facebook_info['id'])
    # Find this OAuth token in the database, or create it
    try:
        oauth_user = OathUser(
            provider=blueprint.name,
            provider_user_id=facebook_user_id,
        )
    except ValueError:
        oauth_user = False

    if oauth_user:
        print(oauth_user.user_id)
        login_user(User(user_id=oauth_user.user_id))
        # flash('Successfully signed in with facebook.')
    else:
        new_user = User(
            fullname=facebook_info['name'],
            email=facebook_info['email'],
            username=None
        )
        OathUser(
            token=token,
            user_id=new_user.user_id,
            provider=blueprint.name,
            provider_user_id=facebook_user_id
        )
        # Log in the new local user account
        login_user(new_user)
        # flash('Successfully signed in with facebook.')

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def facebook_error(blueprint, error, error_description=None, error_uri=None):
    msg = (
        'OAuth error from {name}!'
        'error={error} description={description} uri={uri}'
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    # flash(msg, category='error')


@profile_page.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@profile_page.route('/profile')
def profile():
    return render_template('profile.html')
