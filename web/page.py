import os
from flask import Blueprint, render_template, abort, current_app, request, flash, url_for, redirect
from jinja2 import TemplateNotFound
from utils.utils import send_simple_message
from wtforms import Form, TextAreaField, validators, StringField

APP_PATH = os.path.dirname(os.path.realpath(__file__))
PAGE_DIR = os.path.join(APP_PATH, 'pages')

static_page = Blueprint('static_page', __name__)
contact_page = Blueprint('contact_page', __name__)


class ContactForm(Form):
    name = StringField('Name:', validators=[
                       validators.DataRequired(), validators.Length(min=1)])
    email = StringField('Email:', validators=[validators.DataRequired(
    ), validators.Length(min=6, max=35), validators.Email()])
    message = TextAreaField('Message:', validators=[
                            validators.DataRequired(), validators.Length(min=10, max=200)])


@contact_page.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm(request.form)
    if request.method == 'POST':
        name = request.form['name']
        message = request.form['message']
        email = request.form['email']

        if form.validate():
            send_simple_message(name, email, message)
            flash('Thanks for your message, ' + name, category='success')
            return redirect('/contact')
        else:
            flash('Error happened, your message is not sent yet.', category='danger')

    return render_template('contact.html', title='Contact Us', form=form)


@static_page.route('/page/<page_name>')
def page(page_name):
    import markdown
    import codecs
    from flask import Markup
    md = markdown.Markdown(extensions=['markdown.extensions.meta'])
    try:
        input_file = codecs.open(
            PAGE_DIR + '/' + page_name + '.md', mode='r', encoding='utf-8')
    except FileNotFoundError:
        abort(404)
    text = input_file.read()
    html = Markup(md.convert(text))
    return render_template('page.html', page_content=html, title=md.Meta['title'][0], active_menu=page_name)
