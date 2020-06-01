import os
from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
from .home import home_page
from .page import static_page, contact_page
from .fb_bot import fb_bot
from .profile import profile_page, login_manager, blueprint


def create_app():
    # load config files
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.config.from_object('config')
    os.environ['LANG'] = 'en_US.UTF-8'
    os.environ['FLASK_ENV'] = app.config['ENV']

    # load modules
    app.register_blueprint(home_page)
    app.register_blueprint(static_page)
    app.register_blueprint(contact_page)
    app.register_blueprint(fb_bot)
    app.register_blueprint(profile_page)
    app.register_blueprint(blueprint, url_prefix='/login')
    login_manager.init_app(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
