import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from datetime import datetime

db=SQLAlchemy()
login_manager=LoginManager()
bcrypt=Bcrypt()
admin=Admin(name="Admin Dashboard", template_mode="bootstrap4", subdomain="admin", url="")


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'dev.db')}",
        SERVER_NAME="localhost:5000",
        FLASK_ADMIN_SWATCH="litera",
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)


    @app.context_processor
    def define():
        return {'now': datetime.utcnow()}

    # Initialisations
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    admin.init_app(app)

    from .database import init_db
    init_db(app)

    from .main import bp
    app.register_blueprint(bp)

    from .auth import bp
    app.register_blueprint(bp)


    from .database import User, Class, Subject, Lecture, Resource
    from .administrator import UserView
    admin.add_view(UserView(User, db.session))
    admin.add_view(ModelView(Class, db.session))
    admin.add_view(ModelView(Subject, db.session))
    admin.add_view(ModelView(Lecture, db.session))
    admin.add_view(ModelView(Resource, db.session))
    path = os.path.join(os.path.dirname(__file__), 'static')
    admin.add_view(FileAdmin(path, '/static/', name='Static Files'))
    
    return app