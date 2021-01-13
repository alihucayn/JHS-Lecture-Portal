import os
from flask import Flask, send_from_directory, url_for, abort
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
data_path=os.path.join(os.path.dirname(__file__), 'data')
mail=Mail()
from .administration import HomeView
admin=Admin(name='Admin Dashboard', template_mode='bootstrap4', index_view=HomeView())


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, static_url_path='/files')
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{os.path.join(app.instance_path, "dev.db")}',
        FLASK_ADMIN_SWATCH='litera',
        DATA_FOLDER='D:\Coding\JHS-Lecture-Portal\jhsLecturePortal\data',
        MAIL_SERVER = 'smtp.googlemail.com',
        MAIL_PORT = 587,
        MAIL_USE_TLS = True,
        SITE_NAME = 'Qura Time',
        MAIL_USERNAME = 'alifed2005@gmail.com',
        MAIL_PASSWORD = 'geqmlpbrjotljids',
        INSTAGRAM_PROFILE='https://google.com',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
        app.config.from_mapping(test_config)


    # Initialisations
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    admin.init_app(app)
    mail.init_app(app)


    @app.context_processor
    def define():
        return {'now': datetime.utcnow()}

    @login_required
    @app.route('/data/<path:file>')
    def data(file):
        if current_user.is_authenticated:
            if current_user.approved and current_user.verified:
                return send_from_directory(app.config['DATA_FOLDER'], file)
        return abort(403)


    from .database import init_db
    init_db(app)

    from .main import bp
    app.register_blueprint(bp)

    from .auth import bp
    app.register_blueprint(bp)


    from .database import User, Class, Subject, Lecture, Resource
    from .administration import UserView, SubjectView, ClassView, LectureView, ResourceView, FileView
    admin.add_views(UserView(User, db.session), SubjectView(Subject, db.session), ClassView(Class, db.session), LectureView(Lecture, db.session), ResourceView(Resource, db.session), FileView(data_path, name='Data'))
    return app