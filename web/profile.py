from flask import Flask, redirect, url_for, flash, render_template, Blueprint, current_app, request
from wtforms import Form, validators, StringField
from flask_login import current_user, login_required
from .user import User

profile_page = Blueprint('profile_page', __name__, None)


class ProfileForm(Form):
    username = StringField('Username:', validators=[
                           validators.DataRequired(), validators.Length(min=4)])


@profile_page.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if hasattr(current_user, 'user_id'):
        user = User(user_id=current_user.user_id)
    form = ProfileForm(request.form)
    if request.method == 'GET':
        if not hasattr(current_user, 'username'):
            # flash message, with category following bootstrap CSS info class convenience
            flash('You have not set your username yet', category='danger')
        else:
            form.username.data = current_user.username
    if request.method == 'POST' and form.validate():
        user.set_username(request.form['username'])
        flash('You updated your username succesfully', category='success')
        return redirect('/profile')
    return render_template('profile.html', title='Profile', form=form)


@profile_page.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
