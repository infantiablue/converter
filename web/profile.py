from flask import Flask, redirect, url_for, flash, render_template, request, Blueprint, jsonify
from wtforms import Form, validators, StringField
from flask_login import current_user, login_required, logout_user
from flask_dance.contrib.facebook import facebook
from .user import User
from .db import gclient

profile_page = Blueprint('profile_page', __name__, None)


class ProfileForm(Form):
    username = StringField('Username:', validators=[
                           validators.DataRequired(), validators.Length(min=4)])


@profile_page.app_template_filter('timeago')
def timeago_filter(timestamp):
    import arrow
    ts = arrow.get(timestamp)
    return ts.humanize()


@profile_page.route('/profile', methods=['GET', 'POST'])
# @login_required
def profile():
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))
    if hasattr(current_user, 'user_id'):
        user = User(user_id=current_user.user_id)
    form = ProfileForm(request.form)
    if request.method == 'GET':
        if not current_user.username:
            # flash message, with category following bootstrap CSS info class convenience
            flash('You have not set your username yet.', category='danger')
        else:
            form.username.data = current_user.username
    if request.method == 'POST' and form.validate():
        if user.set_username(request.form['username']):
            flash('You updated your username succesfully.', category='success')
        else:
            flash('The username you input is duplicated.', category='danger')
        return redirect('/profile')
    return render_template('profile.html', title='Profile', form=form)


@profile_page.route('/history', methods=['GET'])
@login_required
def profile_history():
    query = gclient.query(kind='History')
    query.add_filter('userid', '=', current_user.user_id)
    # need to create index for Datastore to process
    query.order = ['-created_at']
    items = list(query.fetch())
    return render_template('history.html', items=items)


@profile_page.route('/history/remove', methods=['POST'])
@login_required
def profile_history_remove():
    if request.method == 'POST':
        item_id = int(request.json['id'])
        key = gclient.key('History', item_id)
        item = gclient.get(key)
        if(item['userid'] == current_user.user_id):
            try:
                gclient.delete(key)
                return jsonify({'success': True}), 200
            except:
                return jsonify({'success': False}), 400
        else:
            return jsonify({'success': False}), 401


@ profile_page.route('/logout')
@ login_required
def logout():
    logout_user()
    return redirect('/')
