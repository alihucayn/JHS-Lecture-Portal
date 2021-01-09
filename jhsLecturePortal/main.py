from flask import Blueprint, render_template, redirect, url_for, flash, request
from .database import Lecture, Subject, Resource, Class
from flask_login import login_required, current_user

bp=Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template("main/home.html")

@bp.route('/lecture/<string:id>')
@login_required
def lecture(id):
    data=Lecture.query.filter_by(priv_id=id).first_or_404()
    if data:
        if (current_user.clas in data.subject.clases) or current_user.role!="Student":
            if current_user.verified:
                return render_template('main/lecture.html', data=data)
            else:
                flash("You didnt verify your email. Go to your email account and verify your email.", "warning")
                return redirect(url_for("auth.account"))
        else:
            flash("You can't have access to Lectures of other Classes", "warning")
            return redirect(url_for("main.subjects"))

@bp.route('/subjects')
def subjects():
    data=Subject.query.order_by(Subject.order)
    if current_user.is_authenticated:
        if current_user.role!="STUDENT":
            return render_template('main/subjects.html', data=data)
        subjects=[]
        for i in range(len(data.all())):
            if current_user.clas in data[i].clases:
                subjects.append(data[i])
        return render_template('main/subjects.html', data=subjects)
    return render_template('main/subjects.html', data=data)

@bp.route('/subjects/<int:id>/lectures')
@login_required
def subject_lectures(id):
    page=request.args.get("page", 1, type=int)
    subject=Subject.query.get_or_404(id)
    if (current_user.clas in subject.clases) or current_user.role!="STUDENT":
        if current_user.verified:
            if not subject.lectures.all():
                flash(f"There are currently no leactures available for the subject of {subject.name}", "info")
                return redirect(url_for("main.subjects"))
            lectures=Lecture.query.filter_by(subject_id=id).order_by(Lecture.date.desc()).paginate(page=page, per_page=10)
            return render_template('main/lectures.html', subject=subject, lectures=lectures)
        else:
            flash("You didnt verify your email. Click on Verify and Go to your email account and verify your email.", "warning")
            return redirect(url_for("auth.account"))
    else:
        flash("You cant have access to Lectures of other Classes", "warning")
        return redirect(url_for("main.subjects"))

@bp.route('/subjects/<int:id>/resources')
@login_required
def subject_resources(id):
    page=request.args.get("page", 1, type=int)
    subject=Subject.query.get(id)
    if subject:
        if current_user.clas in subject.clases:
            resources=Resource.query.filter_by(subject_id=id).order_by(Resource.date.desc()).paginate(page=page, per_page=10)
            return render_template('main/resources.html', subject=subject, resources=resources)
        else:
            flash("You cant have access to Resources of other Classes", "warning")
            return redirect(url_for("main.subjects"))
    else:
        flash("The requested page does not exist", "info")
        return redirect(url_for("main.subjects"))

    
@bp.route('/about')
def about():
    return render_template('main/about.html')