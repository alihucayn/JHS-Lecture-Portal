import string
import random
import os
from . import mail
from flask_mail import Message
from flask import current_app, url_for

# gnerating list of choices
# def generateChoicesList(of, model, campus=None, grade=None):
#     list=[]
#     if of=="campus":
#         for entry in model.query:
#             if entry.campus not in list:
#                 list.append((entry.value, entry.value))
#         return list
#     elif of=="class":
#         for entry in model.query.filter_by(campus=campus):
#             value=getattr(entry, of)
#             if value not in list:
#                 list.append((value, value))
#         return list
#     elif of=="section":
#         for entry in model.query.filter(_or,campus=campus, grade=grade):
#             value=getattr(entry, of)
#             if value not in list:
#                 list.append((value, value))
#         return list

def generateChoicesList(of, model, empty_insert=True):
    list=[]
    for entry in model.query:
        value=getattr(entry, of)
        if (value, value) not in list:
            list.append((value, value))
    if empty_insert:
        list.insert(0,("",of.capitalize()))
    return list


def username_generator(form):
    return form.name.data.replace(" ", "-").lower()+"-"+form.grade.data.lower()


def token_generator(length=12):
    return ''.join( random.choice(string.ascii_letters) for i in range(length) )


def filename_generator(obj, file_data):
    ext=os.path.splitext(file_data.filename)[1]
    name=token_generator(10)
    
    return name+ext

def send_reset_email(user):
    token = user.get_token()
    msg = Message('Password Reset',
                  sender=(current_app.config['SITE_NAME'], current_app.config["MAIL_USERNAME"]),
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link: {url_for('auth.reset_token', token=token, _external=True)}\nIf you did not make this request then simply ignore this email and no changes will be made. '''
    mail.send(msg)

def send_verification_email(user):
    token = user.get_token()
    msg = Message('Email Verification',
                  sender=(current_app.config['SITE_NAME'], current_app.config["MAIL_USERNAME"]),
                  recipients=[user.email])
    msg.body = f'''Hi {user.name}! Welcome to Qura Time\n\tTo verify your email, visit the following link: {url_for('auth.verify_email', token=token, _external=True)}\n\tYour Approval request is being reviewed and so you will be approved very soon.\n\nNote: This is auto generated email.'''
    mail.send(msg)
