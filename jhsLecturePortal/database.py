from . import db
from . import login_manager
from flask_login import UserMixin
from flask_admin import form
from flask.cli import with_appcontext
import click
from datetime import date
from .utils import token_generator
import os
from sqlalchemy.event import listens_for
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

sbjcts=db.Table("sbjcts",
        db.Column("clas_id", db.ForeignKey("clases.id")),
        db.Column("subject_id", db.ForeignKey("subjects.id")))

class Class(db.Model):
    
    __tablename__="clases"

    id=db.Column(db.Integer, primary_key=True)
    campus=db.Column(db.String(15), nullable=False)
    grade=db.Column(db.String(5), nullable=False)
    section=db.Column(db.String(1), nullable=False)
    clas_incharge=db.Column(db.String(46))
    students=db.relationship("User", backref=db.backref("clas", lazy=True), lazy="dynamic")
    subjects=db.relationship("Subject", secondary=sbjcts, lazy=True, backref=db.backref("clases", lazy=True))

    def __repr__(self):
        return f"{self.grade} - {self.section} - {self.campus}"


class User(db.Model, UserMixin):

    __tablename__="users"

    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20), nullable=False)
    name=db.Column(db.String(48), nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    password=db.Column(db.String(70), nullable=False)
    role=db.Column(db.String(10), nullable=False, default="STUDENT")
    approved=db.Column(db.Boolean)
    verified=db.Column(db.Boolean, nullable=False, default=False)
    clas_id=db.Column(db.Integer, db.ForeignKey("clases.id"))

    def get_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    

    def __repr__(self):
        return f'{self.name} - {self.role}'
   

class Lecture(db.Model):

    __tablename__="lectures"

    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(56), nullable=False)
    priv_id=db.Column(db.String(12), unique=True, nullable=False, default=token_generator(12))
    src=db.Column(db.String(14), unique=True)
    audio_src=db.Column(db.String(14), unique=True)
    frmt=db.Column(db.String(5), nullable=False, default="VIDEO")
    date=db.Column(db.Date(), nullable=False, default=date.today)
    subject_id=db.Column(db.Integer, db.ForeignKey("subjects.id"))
    resources=db.relationship("Resource", backref=db.backref("lecture", lazy=True), lazy="dynamic")

    def __repr__(self):
        return f"{self.name} - {self.subject} - {self.date}"

class Resource(db.Model):

    __tablename__="resources"

    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(80), nullable=False)
    type=db.Column(db.String(36), nullable=False)
    src=db.Column(db.String(14))
    date=db.Column(db.Date(), nullable=False, default=date.today)
    subject_id=db.Column(db.Integer, db.ForeignKey("subjects.id"))
    lecture_id=db.Column(db.Integer, db.ForeignKey("lectures.id"))

    def __repr__(self):
        return f"{self.name} - {self.type} - {self.date}"

class Subject(db.Model):

    __tablename__="subjects"

    id=db.Column(db.Integer, primary_key=True)
    order=db.Column(db.Integer, unique=True, default=0)
    name=db.Column(db.String(20), nullable=False)
    description=db.Column(db.String(80), nullable=False)
    cover_pic=db.Column(db.String(15), nullable=False, default="cover_default.jpg")
    teacher_name=db.Column(db.String(46), nullable=False)
    teacher_pic=db.Column(db.String(15), nullable=False, default="teacher_default.jpg")
    lectures=db.relationship("Lecture", backref=db.backref("subject", lazy=True), lazy="dynamic")
    resources=db.relationship("Resource", backref=db.backref("subject", lazy=True), lazy="dynamic")

    def __repr__(self):
        
        clases=[clas.grade+'-'+clas.campus for clas in self.clases]
        return f"{self.name} - {clases}"

static_path=os.environ.get('STATIC_FOLDER')

@listens_for(Subject, 'after_delete')
def del_image(mapper, connection, target):
    if target.cover_pic:
        # Delete image
        try:
            os.remove(os.path.join(static_path, 'images/cover-pics', target.cover_pic))
        except OSError:
            pass

        # Delete thumbnail
        try:
            os.remove(os.path.join(static_path, 'images/cover-pics', form.thumbgen_filename(target.cover_pic)))
        except OSError:
            pass
    
    if target.teacher_pic:
        # Delete image
        try:
            os.remove(os.path.join(static_path, 'images/teacher-pics', target.teacher_pic))
        except OSError:
            pass

        # Delete thumbnail
        try:
            os.remove(os.path.join(static_path, 'images/teacher-pics', form.thumbgen_filename(target.teacher_pic)))
        except OSError:
            pass


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo("Initiated the Database.")

def init_db(app):
    app.cli.add_command(init_db_command)