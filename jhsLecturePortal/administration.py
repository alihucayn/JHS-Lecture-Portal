import os
from flask_admin.form import SecureForm, rules, ImageUploadField, FileUploadField
from flask_admin import form, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from .database import Class
from .utils import filename_generator
from jinja2 import Markup
from flask import url_for
from sqlalchemy import and_
from .database import User
from flask_login import current_user
from flask import redirect, request, url_for, flash
data_path=os.environ.get('DATA_FOLDER')

class Authentication(ModelView):
    def is_accessible(self):
        
        if current_user.is_authenticated and current_user.role=='ADMIN' and current_user.verified and current_user.approved:
            return True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash('You dont have the priveliges to access Admin Dashboard', 'danger')
        return redirect(url_for('auth.login', next=request.url))

class HomeView(AdminIndexView):
    def is_accessible(self):
        
        if current_user.is_authenticated and (current_user.role=='ADMIN' or current_user.role=='EDITOR') and current_user.verified and current_user.approved:
            return True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash('You dont have the priveliges to access Admin Dashboard', 'danger')
        return redirect(url_for('auth.login', next=request.url))



class UserView(Authentication):

    form_base_class = SecureForm
    can_export = True
    column_display_pk=True
    column_exclude_list=['username', 'password',]
    column_searchable_list = ['name', 'email',]
    column_filters=['role', 'approved', 'verified','clas']
    column_editable_list = ['role', 'approved', 'clas']
    form_choices={
        'role':[
            ('ADMIN', 'Administrator'),
            ('EDITOR', 'Editor'),
            # ('MODERATOR', 'Moderator'),
            ('STUDENT', 'Student')
        ]
    }
    form_excluded_columns=['username', 'password', 'verified']
    form_rules=[
        rules.FieldSet(('name', 'email', 'role', 'clas', 'approved'), 'Add User'),
    ]


class SubjectView(Authentication):

    column_list=['order', 'name', 'description', 'cover_pic', 'teacher_pic', 'teacher_name','clases']
    
    can_export = True
    column_searchable_list = ['name', 'teacher_name',]
    column_editable_list = ['clases']

    def _list_thumbnail(view, context, model, name):
        if not getattr(model, name):
            return ''

        folder='images/'+name.replace('_','-')+'s/'

        return Markup('<img src="%s" width="50">'% url_for('static', filename=folder+form.thumbgen_filename(getattr(model, name))))

    column_formatters = {
        'cover_pic': _list_thumbnail,
        'teacher_pic': _list_thumbnail,
    }
    
    form_base_class = SecureForm
    form_rules=[
        rules.FieldSet(('order', 'name', 'description', 'teacher_name', 'cover_pic', 'teacher_pic', 'clases'), 'Add Subject'),
    ]
    form_extra_fields = {
        'teacher_pic': ImageUploadField('Teacher Pic', base_path=os.path.join(data_path, 'teacher-pics'), namegen=filename_generator, thumbnail_size=(200, 200, True), max_size=(512, 512, True), url_relative_path='files/teacher-pics/'),
        'cover_pic': ImageUploadField('Cover Pic', base_path=os.path.join(data_path, 'cover-pics'), namegen=filename_generator, thumbnail_size=(200, 133, True), max_size=(516, 344, True), url_relative_path='files/cover-pics/'),
    }
    form_choices={
        'order':[(i,str(i)) for i in range(1, 11)]
    }
    form_excluded_columns=['lectures', 'resources']

class ClassView(Authentication):
    

    # def list_student_count(view, context, model, name):
    #     query=User.clas.query.filter(and_(campus=form.campus.data, grade=form.campus.grade, section=form.section.data)).all()
    #     return Markup('<span>%s</span>'%str(len(query)))
    
    # column_formatters={
    #     'students':list_student_count
    # }

    column_list=['campus', 'grade', 'section', 'clas_incharge', 'subjects' ]
    column_editable_list=['subjects']
    
    form_base_class = SecureForm
    form_excluded_columns=['students', 'subjects']

class LectureView(ModelView):

    def is_accessible(self):
        
        if current_user.is_authenticated and (current_user.role=='ADMIN' or current_user.role=='EDITOR') and current_user.verified and current_user.approved:
            return True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))
    
    can_export = True
    column_display_pk=True
    column_exclude_list=['priv_id', 'src']
    column_searchable_list = ['name','date']
    column_editable_list=['name','frmt', 'date', 'subject']
    
    form_base_class = SecureForm
    form_choices={
        'frmt':[
            ('VIDEO', 'Video'),
            ('AUDIO', 'Audio')
        ]
    }
    form_extra_fields={
            'audio_src':FileUploadField('Audio File (MP3)', base_path=os.path.join(data_path, 'audios'), allowed_extensions=['mp3'], namegen=filename_generator)
    }

class ResourceView(ModelView):

    def is_accessible(self):
        
        if current_user.is_authenticated and (current_user.role=='ADMIN' or current_user.role=='EDITOR') and current_user.verified:
            return True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))


    can_export=True
    column_display_pk=True
    column_editable_list=['name', 'type', 'lecture', 'subject']
    column_exclude_list=['src']

    form_choices={
        'type':[
            ('PAST PAPER', 'Past Paper'),
            ('NOTES', 'Notes'),
        ]
    }

    form_extra_fields={
        'src':FileUploadField('PDF File', base_path=os.path.join(data_path, 'pdfs'), allowed_extensions=['pdf'], namegen=filename_generator)
    }

class FileView(FileAdmin):

    def is_accessible(self):
        
        if current_user.is_authenticated and (current_user.role=='ADMIN') and current_user.verified:
            return True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))