from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
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
    if current_user.approved:
        if (current_user.clas in data.subject.clases) or current_user.role!="Student":
            if current_user.verified:
                return render_template('main/lecture.html', data=data)
            else:
                flash("You didnt verify your email. Go to your email account and verify your email.", "warning")
                return redirect(url_for("auth.account"))
        else:
            abort(403)
    elif current_user.approved is None:
            flash("Account hasn't been approved yet. Check again in some time.", "info")

            return redirect(url_for("main.home"))
    elif not current_user.approved:
        flash("Your Account approval Request has been rejected", "danger")
        return redirect(url_for('main.home'))

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
    
    if current_user.verified:
        if current_user.approved:
            page=request.args.get("page", 1, type=int)
            subject=Subject.query.get_or_404(id)
            if (current_user.clas in subject.clases) or current_user.role!="STUDENT":
                if not subject.lectures.all():
                    flash(f"There are currently no leactures available for the subject of {subject.name}", "info")
                    return redirect(url_for("main.subjects"))
                lectures=Lecture.query.filter_by(subject_id=id).order_by(Lecture.date.desc()).paginate(page=page, per_page=10)
                return render_template('main/lectures.html', subject=subject, lectures=lectures)
            else:
                abort(403)
        elif current_user.approved is None:
            flash("Account hasn't been approved yet. Check again in some time.", "info")
            return redirect(url_for("main.home"))
        elif not current_user.approved:
            flash(f"Your Account approval Request has been rejected. Contact site admins at instagram handle", "danger")
            return redirect(url_for('main.home'))
    else:
        flash("You didnt verify your email. Click on Verify, Go to your email account and verify your email.", "warning")
        return redirect(url_for("auth.account"))

@bp.route('/subjects/<int:id>/resources')
@login_required
def subject_resources(id):
    if current_user.verified:
        if current_user.approved:
                page=request.args.get("page", 1, type=int)
                subject=Subject.query.get_or_404(id)
                if current_user.clas in subject.clases:
                    resources=Resource.query.filter_by(subject_id=id).order_by(Resource.date.desc()).paginate(page=page, per_page=10)
                    return render_template('main/resources.html', subject=subject, resources=resources)
                else:
                    abort(403)

        elif current_user.approved is None:
                flash("Account hasn't been approved yet. Check again in some time.", "info")
                return redirect(url_for("main.home"))
        elif not current_user.approved:
            flash(f"Your Account approval Request has been rejected. Contact site admins at instagram handle", "danger")
            return redirect(url_for('main.home'))
    else:
        flash("You didnt verify your email. Click on Verify, Go to your email account and verify your email.", "warning")
        return redirect(url_for("auth.account"))

    
@bp.route('/about')
def about():
    return render_template('main/about.html')