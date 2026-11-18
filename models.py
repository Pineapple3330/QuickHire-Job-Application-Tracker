
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    applications = db.relationship(
        "JobApplication",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    job_title = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150))

    status = db.Column(db.String(50), default="Applied")
    job_url = db.Column(db.String(500))
    description = db.Column(db.Text)

    applied_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    round_name = db.Column(db.String(100), nullable=False)
    interview_type = db.Column(db.String(50), default="Technical")

    scheduled_at = db.Column(db.DateTime, nullable=False)

    location = db.Column(db.String(200))
    notes = db.Column(db.Text)

    status = db.Column(db.String(50), default="Scheduled")

    application_id = db.Column(
        db.Integer,
        db.ForeignKey("job_application.id"),
        nullable=False
    )

    application = db.relationship(
        "JobApplication",
        backref=db.backref("interviews", lazy=True)
    )
