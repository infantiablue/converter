import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from .home import home_page, page_not_found
from .page import static_page, contact_page
from .fb_bot import fb_bot
from .profile import profile_page
from .oauth import fb_blueprint, login_manager


def create_app():
    # load config files
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.config.from_object('config')

    # load modules
    app.register_error_handler(404, page_not_found)
    app.register_blueprint(home_page)
    app.register_blueprint(static_page)
    app.register_blueprint(contact_page)
    # app.register_blueprint(fb_bot)
    app.register_blueprint(profile_page)
    app.register_blueprint(fb_blueprint, url_prefix='/login')
    login_manager.init_app(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
