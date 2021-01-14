import os
from flask import Flask, send_from_directory, url_for, abort, Markup
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_mail import Mail
from datetime import datetime

db=SQLAlchemy()
login_manager=LoginManager()
bcrypt=Bcrypt()
mail=Mail()
from .administration import HomeView
admin=Admin(name='Admin Dashboard', template_mode='bootstrap4', index_view=HomeView())


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, static_url_path='/files', template_folder=os.environ.get('TEMPLATE_FOLDER'), static_folder=os.environ.get('STATIC_FOLDER'))
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        FLASK_ADMIN_SWATCH='litera',
        MAIL_SERVER = 'smtp.googlemail.com',
        MAIL_PORT = 587,
        MAIL_USE_TLS = True,
        SITE_NAME = 'Qura Time',
        MAIL_USERNAME = 'alifed2005@gmail.com',
        MAIL_PASSWORD = 'geqmlpbrjotljids',
        INSTAGRAM_PROFILE='qura.time',
        MAINTENANCE=False,
    )

    if test_config is None:
        app.config.from_pyfile(os.environ.get('CONFIG'), silent=True)
    else:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
        app.config.from_mapping(test_config)

    try:
        os.makedirs(os.path.join(os.environ.get('DATA_FOLDER'), 'pdfs'))
    except OSError:
        pass

    try:
        os.makedirs(os.path.join(os.environ.get('DATA_FOLDER'), 'audios'))
    except OSError:
        pass

    # Initialisations
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    admin.init_app(app)
    mail.init_app(app)


    @app.context_processor
    def define():
        return {'now': datetime.utcnow(),
                'site_name': app.config['SITE_NAME'],
                'current_app': app,}

    @login_required
    @app.route('/data/<path:file>')
    def data(file):
        if current_user.is_authenticated:
            if current_user.approved and current_user.verified:
                return send_from_directory(os.environ.get('DATA_FOLDER'), file)
        return abort(403)

    @app.before_request
    def check_for_maintenance():
        if app.config['MAINTENANCE']:
            return Markup('<h1 style="padding: 0% 25%;">Sorry, But we are off due Maintenance Activities.</h1>'), 503


    from .database import init_db
    init_db(app)

    from .main import bp
    app.register_blueprint(bp)

    from .auth import bp
    app.register_blueprint(bp)


    from .database import User, Class, Subject, Lecture, Resource
    from .administration import UserView, SubjectView, ClassView, LectureView, ResourceView, FileView
    admin.add_views(UserView(User, db.session), SubjectView(Subject, db.session), ClassView(Class, db.session), LectureView(Lecture, db.session), ResourceView(Resource, db.session), FileView(os.environ.get('DATA_FOLDER'), name='Data'))
    return app