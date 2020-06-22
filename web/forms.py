from wtforms import Form, StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, InputRequired, Length


class AdminUserCreateForm(Form):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    admin = BooleanField('Is Admin ?')


class AdminUserUpdateForm(Form):
    username = StringField('Username', validators=[InputRequired()])
    admin = BooleanField('Is Admin ?')


class LoginForm(Form):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


class ProfileForm(Form):
    fullname = StringField('Full Name:', render_kw={'disabled': ''})
    email = StringField('Email:', render_kw={'disabled': ''})
    username = StringField('Username:', validators=[
                           DataRequired(), Length(min=4)])
