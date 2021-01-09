from flask import Blueprint, render_template, flash, redirect, url_for, request
from .utils import generateChoicesList, username_generator
from .forms import RegistrationForm, LoginForm, UpdateAccountForm
from .database import Class, User
from . import db
from sqlalchemy import and_
from . import bcrypt, login_manager
from flask_login import login_user, login_required, logout_user, current_user

login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


bp=Blueprint('auth', __name__)


@bp.route('/signup', methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form=RegistrationForm()

    form.campus.choices=generateChoicesList("campus", Class)
    form.grade.choices=generateChoicesList("grade", Class)
    form.section.choices=generateChoicesList("section", Class)

    if form.validate_on_submit():

        clas_query=Class.query.filter(and_(Class.campus==form.campus.data, Class.grade==form.grade.data, Class.section==form.section.data)).first()
        if not clas_query:
            flash("Your Class data cannot be validated. Enter Real Class data", "danger")
            return render_template('auth/signup.html', form=form), 409

        user=User(username=username_generator(form), name=form.name.data,  email=form.email.data, password=bcrypt.generate_password_hash(form.password.data).decode("utf-8"), role="STUDENT", clas=clas_query)
        db.session.add(user)
        db.session.commit()
        flash(f"{form.name.data.split(' ')[0]}! Your Account has been created and is pending to be approved", "success")
        return redirect(url_for("auth.login"))
    
    return render_template('auth/signup.html', form=form)

@bp.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data) and user.approved:
            login_user(user, remember=form.remember.data)
            flash("Login Sucessful!", "success")
            
            next=request.args.get('next')

            return redirect(next) if next else redirect(url_for("main.home"))
        elif user.approved is None:
            flash("Account hasn't been approved yet. Check again in some time.", "info")

            return redirect(url_for("main.home"))
        elif not user.approved:
            flash("Your Account creation Request has been rejected", "danger")
        else:
            flash("Login Unsuccessful! Wrong Email address or Password Entered")
            
    return render_template('auth/login.html', form=form)

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@bp.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    form.campus.choices=generateChoicesList("campus", Class, empty_insert=False)
    form.grade.choices=generateChoicesList("grade", Class, empty_insert=False)
    form.section.choices=generateChoicesList("section", Class, empty_insert=False)

    if form.validate_on_submit():
        clas_query=Class.query.filter(and_(Class.campus==form.campus.data, Class.grade==form.grade.data, Class.section==form.section.data)).first()
        if not clas_query:
            flash("Your Class data cannot be validated. Enter Real Class data", "danger")
            return render_template('auth/account.html', form=form), 409
        
        current_user.name = form.name.data
        current_user.email = form.email.data
        if current_user.clas != clas_query:
            current_user.clas=clas_query
            current_user.approved=None
            db.session.commit()
            logout_user()
            flash("You have changed your Class data and it has to be approved by admin. Until then you won't be able to login.", "info")
            return redirect(url_for("main.home"))
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('auth.account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.campus.data = current_user.clas.campus
        form.grade.data = current_user.clas.grade
        form.section.data = current_user.clas.section
    return render_template('auth/account.html', form=form)