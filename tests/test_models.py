
from models import User, JobApplication
from extensions import db


def test_password_is_hashed(app):
    with app.app_context():
        user = User(
            username="TestUser",
            email="test@example.com"
        )

        user.set_password("password123")

        assert user.password_hash != "password123"
        assert user.check_password("password123")
        assert not user.check_password("wrongpassword")


def test_create_job_application(app):
    with app.app_context():
        user = User(
            username="TestUser",
            email="test@example.com"
        )

        user.set_password("password123")

        db.session.add(user)
        db.session.commit()

        application = JobApplication(
            job_title="Python Developer",
            company="TCS",
            location="Pune",
            status="Applied",
            user_id=user.id
        )

        db.session.add(application)
        db.session.commit()

        saved_application = JobApplication.query.first()

        assert saved_application is not None
        assert saved_application.company == "TCS"
        assert saved_application.user.username == "TestUser"
