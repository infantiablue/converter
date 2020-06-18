import sys
import os
from flask import Flask, redirect, url_for, flash, render_template, Blueprint, request
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_login import login_user, current_user, LoginManager
from .models import User, Oauth
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from .ext import db

login_manager = LoginManager()
fb_blueprint = make_facebook_blueprint(
    client_id=os.environ.get("FACEBOOK_OAUTH_CLIENT_ID"),
    client_secret=os.environ.get("FACEBOOK_OAUTH_CLIENT_SECRET"),
    scope=['email'],
    storage=SQLAlchemyStorage(Oauth, db.session, user=current_user)
)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@oauth_authorized.connect_via(fb_blueprint)
def facebook_logged_in(blueprint, token):
    if not token:
        flash('Failed to log in with facebook.', category='error')
        return False

    resp = blueprint.session.get('/me?fields=email,name')
    if not resp.ok:
        msg = 'Failed to fetch user info from facebook.'
        return False

    facebook_info = resp.json()
    facebook_user_id = facebook_info['id']
    # Find this OAuth token in the database, or create it
    try:
        oauth_user = Oauth.query.filter_by(
            provider=blueprint.name, provider_user_id=facebook_user_id).first()
    except:
        oauth_user = False

    if oauth_user:
        login_user(User.query.get(int(oauth_user.user_id)))
    else:
        new_user = User(
            fullname=facebook_info['name'],
            email=facebook_info['email'],
            username=None,
        )
        db.session.add(new_user)
        db.session.commit()
        new_oauth = Oauth(
            token=str(token),
            user_id=new_user.id,
            provider=blueprint.name,
            provider_user_id=facebook_user_id
        )
        db.session.add(new_oauth)
        db.session.commit()
        # Log in the new local user account
        login_user(new_user)

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


@oauth_error.connect_via(fb_blueprint)
def facebook_error(blueprint, error, error_description=None, error_uri=None):
    msg = (
        'OAuth error from {name}!'
        'error={error} description={description} uri={uri}'
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri
    )
    flash(msg, category='error')
