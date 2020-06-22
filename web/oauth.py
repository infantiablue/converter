import sys
import os
from flask import Flask, redirect, url_for, flash, render_template, Blueprint, request
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_login import login_user, current_user, LoginManager
from .models import db, User, Oauth
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound

login_manager = LoginManager()
fb_blueprint = make_facebook_blueprint(
    scope=['email'],
    storage=SQLAlchemyStorage(Oauth, db.session, user=current_user)
)
gg_blueprint = make_google_blueprint(
    scope=[
        'openid',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'],
    storage=SQLAlchemyStorage(Oauth, db.session, user=current_user),
)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# create/login local user on successful OAuth login
@oauth_authorized.connect_via(gg_blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash('Failed to log in.', category='error')
        return False

    resp = blueprint.session.get('/oauth2/v1/userinfo')
    if not resp.ok:
        msg = 'Failed to fetch user info.'
        flash(msg, category='error')
        return False

    info = resp.json()
    user_id = info['id']

    # Find this OAuth token in the database, or create it
    query = Oauth.query.filter_by(
        provider=blueprint.name, provider_user_id=user_id)
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = Oauth(
            token=token,
            provider=blueprint.name,
            provider_user_id=user_id
        )

    if oauth.user:
        login_user(oauth.user)
        #flash('Successfully signed in.')

    else:
        # Create a new local user account for this user
        new_user = User(email=info['email'],
                        fullname=info['name'])
        # Associate the new local user account with the OAuth token
        oauth.user = new_user
        # Save and commit our database models
        db.session.add_all([new_user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(new_user)
        #flash('Successfully signed in.')

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


@oauth_authorized.connect_via(fb_blueprint)
def facebook_logged_in(blueprint, token):
    if not token:
        flash('Failed to log in with facebook.', category='error')
        return False

    resp = blueprint.session.get('/me?fields=email,name')
    if not resp.ok:
        msg = 'Failed to fetch user info from facebook.'
        flash(msg, category='error')
        return False

    facebook_info = resp.json()
    facebook_user_id = facebook_info['id']
    # Find this OAuth token in the database, or create it
    query = Oauth.query.filter_by(
        provider=blueprint.name, provider_user_id=facebook_user_id)
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = Oauth(
            token=token,
            provider=blueprint.name,
            provider_user_id=facebook_user_id
        )

    if oauth.user:
        login_user(oauth.user)
    else:
        new_user = User(
            fullname=facebook_info['name'],
            email=facebook_info['email'],
        )
        oauth.user = new_user
        db.session.add_all([new_user, oauth])
        db.session.commit()

        # Log in the new local user account
        login_user(new_user)

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


@oauth_error.connect_via(fb_blueprint)
def facebook_error(blueprint, message, response):
    msg = ('OAuth error from {name}! ' 'message={message} response={response}').format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg, category='error')


# notify on OAuth provider error
@oauth_error.connect_via(gg_blueprint)
def google_error(blueprint, message, response):
    msg = ('OAuth error from {name}! ' 'message={message} response={response}').format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg, category='error')
