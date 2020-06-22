from flask import Flask, redirect, url_for, flash, render_template, request, Blueprint, jsonify
from flask_login import current_user, login_required, logout_user, login_user
from werkzeug.security import generate_password_hash
from .models import db, Video, User
from .forms import ProfileForm, LoginForm
profile_bp = Blueprint('profile_bp', __name__, None)


@profile_bp.app_template_filter('timeago')
def timeago_filter(timestamp):
    import arrow
    ts = arrow.get(timestamp)
    return ts.humanize()


@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(current_user.id)
    form = ProfileForm(request.form)
    form.fullname.data = user.fullname
    form.email.data = user.email
    if request.method == 'GET':
        print('debugging GET')
        if not current_user.username:
            # flash message, with category following bootstrap CSS info class convenience
            flash('You have not set your username yet.', category='danger')
        else:
            form.username.data = current_user.username
    if request.method == 'POST' and form.validate():
        try:
            user.username = request.form['username']
            db.session.commit()
            flash('You updated your username succesfully.', category='success')
        except IntegrityError:
            # for test: https://stackoverflow.com/questions/58740043/how-do-i-catch-a-psycopg2-errors-uniqueviolation-error-in-a-python-flask-app
            flash('The username you input is duplicated.', category='danger')
        return redirect('/profile')
    return render_template('profile.html', title='Profile', form=form)


@profile_bp.route('/history', methods=['GET'])
@login_required
def profile_history():
    '''
    user = User.query.get(current_user.id)
    user.pwdhash = generate_password_hash('235tqk')
    db.session.commit()
    '''
    videos = Video.query.filter_by(user_id=current_user.id).order_by(
        Video.created_at.desc()).all()
    return render_template('history.html', items=videos)


@profile_bp.route('/history/remove', methods=['POST'])
@login_required
def profile_history_remove():
    if request.method == 'POST':
        video = Video.query.get(int(request.json['id']))
        if(int(video.user_id) == int(current_user.id)):
            try:
                db.session.delete(video)
                db.session.commit()
                return jsonify({'success': True}), 200
            except:
                return jsonify({'success': False}), 400
        else:
            return jsonify({'success': False}), 401


@profile_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('home_bp.index'))
    if request.method == 'POST' and form.validate():
        print('debugging')
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = User.query.filter_by(username=username).first()

        if not (existing_user and existing_user.check_password(password)):
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('login.html', form=form)

        login_user(existing_user)
        #flash('You have successfully logged in.', 'success')
        return redirect(url_for('home_bp.index'))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('login.html', form=form)


@profile_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
