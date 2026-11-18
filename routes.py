
from datetime import date, datetime

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, abort
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)

from extensions import db
from models import User, JobApplication, Interview

main = Blueprint("main", __name__)

APPLICATION_STATUSES = [
    "Applied",
    "Interview",
    "Selected",
    "Rejected",
    "Withdrawn"
]


# ---------------- HOME ----------------

@main.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTRATION ----------------

@main.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("main.register"))

        if "@" not in email:
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("main.register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return redirect(url_for("main.register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with this email already exists.", "error")
            return redirect(url_for("main.register"))

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Account created successfully!", "success")

        return redirect(url_for("main.dashboard"))

    return render_template("register.html")


# ---------------- LOGIN ----------------

@main.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("main.dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@main.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()
    flash("You have been logged out.", "success")

    return redirect(url_for("main.home"))


# ---------------- DASHBOARD ----------------

@main.route("/dashboard")
@login_required
def dashboard():

    all_applications = JobApplication.query.filter_by(
        user_id=current_user.id
    ).all()

    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()

    query = JobApplication.query.filter_by(
        user_id=current_user.id
    )

    if search:
        query = query.filter(
            db.or_(
                JobApplication.job_title.ilike(f"%{search}%"),
                JobApplication.company.ilike(f"%{search}%")
            )
        )

    if status_filter in APPLICATION_STATUSES:
        query = query.filter_by(status=status_filter)

    applications = query.order_by(
        JobApplication.created_at.desc()
    ).all()

    total = len(all_applications)
    interviews = sum(
        a.status == "Interview" for a in all_applications
    )
    selected = sum(
        a.status == "Selected" for a in all_applications
    )
    rejected = sum(
        a.status == "Rejected" for a in all_applications
    )

    return render_template(
        "dashboard.html",
        applications=applications,
        total=total,
        interviews=interviews,
        selected=selected,
        rejected=rejected,
        search=search,
        status_filter=status_filter,
        statuses=APPLICATION_STATUSES
    )


# ---------------- ADD APPLICATION ----------------

@main.route("/application/add", methods=["GET", "POST"])
@login_required
def add_application():

    if request.method == "POST":

        job_title = request.form.get("job_title", "").strip()
        company = request.form.get("company", "").strip()
        location = request.form.get("location", "").strip()
        status = request.form.get("status", "Applied")
        job_url = request.form.get("job_url", "").strip()
        description = request.form.get("description", "").strip()
        applied_date_value = request.form.get("applied_date", "")

        if not job_title or not company:
            flash("Job title and company are required.", "error")
            return render_template(
                "application_form.html",
                application=None,
                statuses=APPLICATION_STATUSES
            )

        if status not in APPLICATION_STATUSES:
            abort(400)

        try:
            applied_date = (
                date.fromisoformat(applied_date_value)
                if applied_date_value else None
            )
        except ValueError:
            flash("Please enter a valid application date.", "error")
            return render_template(
                "application_form.html",
                application=None,
                statuses=APPLICATION_STATUSES
            )

        application = JobApplication(
            job_title=job_title,
            company=company,
            location=location or None,
            status=status,
            job_url=job_url or None,
            description=description or None,
            applied_date=applied_date,
            user_id=current_user.id
        )

        db.session.add(application)
        db.session.commit()

        flash("Job application added successfully!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template(
        "application_form.html",
        application=None,
        statuses=APPLICATION_STATUSES
    )


# ---------------- EDIT APPLICATION ----------------

@main.route(
    "/application/<int:application_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_application(application_id):

    application = JobApplication.query.filter_by(
        id=application_id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        job_title = request.form.get("job_title", "").strip()
        company = request.form.get("company", "").strip()
        status = request.form.get("status", "")
        applied_date_value = request.form.get("applied_date", "")

        if not job_title or not company:
            flash("Job title and company are required.", "error")

        elif status not in APPLICATION_STATUSES:
            abort(400)

        else:
            try:
                applied_date = (
                    date.fromisoformat(applied_date_value)
                    if applied_date_value else None
                )

                application.job_title = job_title
                application.company = company
                application.location = (
                    request.form.get("location", "").strip() or None
                )
                application.status = status
                application.job_url = (
                    request.form.get("job_url", "").strip() or None
                )
                application.description = (
                    request.form.get("description", "").strip() or None
                )
                application.applied_date = applied_date

                db.session.commit()

                flash("Application updated successfully!", "success")
                return redirect(url_for("main.dashboard"))

            except ValueError:
                flash("Please enter a valid application date.", "error")

    return render_template(
        "application_form.html",
        application=application,
        statuses=APPLICATION_STATUSES
    )


# ---------------- DELETE APPLICATION ----------------

@main.route(
    "/application/<int:application_id>/delete",
    methods=["POST"]
)
@login_required
def delete_application(application_id):

    application = JobApplication.query.filter_by(
        id=application_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(application)
    db.session.commit()

    flash("Application deleted successfully.", "success")

    return redirect(url_for("main.dashboard"))


# ---------------- VIEW INTERVIEWS ----------------

@main.route("/interviews")
@login_required
def interviews():

    user_interviews = (
        Interview.query
        .join(JobApplication)
        .filter(JobApplication.user_id == current_user.id)
        .order_by(Interview.scheduled_at.asc())
        .all()
    )

    return render_template(
        "interviews.html",
        interviews=user_interviews
    )


# ---------------- ADD INTERVIEW ----------------

@main.route(
    "/applications/<int:application_id>/interviews/add",
    methods=["GET", "POST"]
)
@login_required
def add_interview(application_id):

    application = JobApplication.query.filter_by(
        id=application_id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        round_name = request.form.get("round_name", "").strip()
        interview_type = request.form.get(
            "interview_type", "Technical"
        )
        scheduled_at_value = request.form.get("scheduled_at", "")
        location = request.form.get("location", "").strip()
        notes = request.form.get("notes", "").strip()

        if not round_name or not scheduled_at_value:
            flash("Round name and interview date are required.", "error")
            return render_template(
                "interview_form.html",
                application=application
            )

        try:
            scheduled_at = datetime.strptime(
                scheduled_at_value,
                "%Y-%m-%dT%H:%M"
            )
        except ValueError:
            flash("Please enter a valid interview date and time.", "error")
            return render_template(
                "interview_form.html",
                application=application
            )

        interview = Interview(
            round_name=round_name,
            interview_type=interview_type,
            scheduled_at=scheduled_at,
            location=location or None,
            notes=notes or None,
            application_id=application.id
        )

        db.session.add(interview)
        db.session.commit()

        flash("Interview scheduled successfully!", "success")

        return redirect(url_for("main.interviews"))

    return render_template(
        "interview_form.html",
        application=application
    )


# ---------------- DELETE INTERVIEW ----------------

@main.route(
    "/interviews/<int:interview_id>/delete",
    methods=["POST"]
)
@login_required
def delete_interview(interview_id):

    interview = (
        Interview.query
        .join(JobApplication)
        .filter(
            Interview.id == interview_id,
            JobApplication.user_id == current_user.id
        )
        .first_or_404()
    )

    db.session.delete(interview)
    db.session.commit()

    flash("Interview deleted successfully.", "success")

    return redirect(url_for("main.interviews"))
