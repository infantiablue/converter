import click
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, flash
from flask_login import current_user
from flask_admin import AdminIndexView, BaseView, expose
from flask_admin.form import rules
from flask_admin.contrib.sqla import ModelView
from wtforms import PasswordField

admin_bp = Blueprint('admin_bp', __name__,
                     template_folder='templates/admin')


# CLI command to create admin user
@admin_bp.cli.command('promote')
@click.argument('email')
def promote_admin(email):
    from .models import db, User
    user = User.query.filter_by(email=email).one()
    if user.admin == True:
        print('The user with email {} is admin already'.format(email))
    else:
        user.admin = True
        db.session.commit()


class AdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()


class UserAdminView(ModelView):
    column_searchable_list = ('username', 'email')
    column_sortable_list = ('username', 'admin')
    column_exclude_list = ('pwdhash',)
    form_excluded_columns = ('pwdhash',)
    form_edit_rules = (
        'username', 'admin',
        rules.Header('Reset Password'),
        'new_password', 'confirm'
    )
    form_create_rules = (
        'username', 'fullname', 'email', 'admin', 'password'
    )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def scaffold_form(self):
        form_class = super(UserAdminView, self).scaffold_form()
        form_class.password = PasswordField('Password')
        form_class.new_password = PasswordField('New Password')
        form_class.confirm = PasswordField('Confirm New Password')
        return form_class

    def create_model(self, form):
        model = self.model(
            username=form.username.data,
            pwdhash=generate_password_hash(form.password.data),
            admin=form.admin.data,
            email=form.email.data,
            fullname=form.fullname.data
        )
        form.populate_obj(model)
        self.session.add(model)
        self._on_model_change(form, model, True)
        self.session.commit()
        flash('Created new user successfully', category='success')

    def update_model(self, form, model):
        form.populate_obj(model)
        if form.new_password.data:
            if form.new_password.data != form.confirm.data:
                flash('Passwords must match')
                return
            model.pwdhash = generate_password_hash(form.new_password.data)
        self.session.add(model)
        self._on_model_change(form, model, False)
        self.session.commit()
        flash('Updated password successfully', category='success')
