import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from .home import home_page, page_not_found
from .page import static_page, contact_page
from .profile import profile_page
from .oauth import fb_blueprint, login_manager
from .ext import db


def create_app():
    # load config files
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.config.from_object('config')
    db.init_app(app)
    # load modules
    app.register_error_handler(404, page_not_found)
    app.register_blueprint(home_page)
    app.register_blueprint(static_page)
    app.register_blueprint(contact_page)
    # app.register_blueprint(fb_bot)
    app.register_blueprint(profile_page)
    app.register_blueprint(fb_blueprint, url_prefix='/login')
    # setup login manager

    login_manager.init_app(app)
    login_manager.login_view = 'facebook.login'

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
