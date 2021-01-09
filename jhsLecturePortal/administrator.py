from flask_admin.form import SecureForm
from flask_admin.contrib.sqla import ModelView
from .database import Class
class UserView(ModelView):
    form_base_class = SecureForm
    column_exclude_list=['username', 'password',]
    column_searchable_list = ['name', 'email',]
    column_filters=['role', 'approved', 'verified']
    column_editable_list = ['role', 'approved', 'clas']
    form_choices={
        'role':[
            ('ADMIN', 'Administrator'),
            ('EDITOR', 'Editor'),
            ('MODERATOR', 'Moderator'),
        ]
    }
