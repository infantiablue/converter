import os
import warnings
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask
from flask_admin import Admin
from .admin import admin_bp, AdminIndexView, UserAdminView
from .home import home_bp, page_not_found
from .page import static_page, contact_page
from .profile import profile_bp
from .oauth import fb_blueprint, gg_blueprint, login_manager
from .models import db, User


def create_app():
    # load config files
    app = Flask(__name__)
    # Add any other application configuration
    admin = Admin(app, index_view=AdminIndexView())
    # Other admin configuration as shown in last recipe
    with warnings.catch_warnings():
        warnings.filterwarnings(
            'ignore', 'Fields missing from ruleset', UserWarning)
        admin.add_view(UserAdminView(User, db.session))
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.config.from_object('config')
    db.init_app(app)
    # load modules
    app.register_error_handler(404, page_not_found)
    app.register_blueprint(admin_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(static_page)
    app.register_blueprint(contact_page)
    # app.register_blueprint(fb_bot)
    app.register_blueprint(profile_bp)
    app.register_blueprint(fb_blueprint, url_prefix='/login')
    app.register_blueprint(gg_blueprint, url_prefix='/login')
    # setup login manager

    login_manager.init_app(app)
    login_manager.login_view = 'profile_bp.login'

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
