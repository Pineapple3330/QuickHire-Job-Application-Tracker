
from models import User


def test_homepage_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"QuickHire" in response.data


def test_user_registration(client, app):
    response = client.post(
        "/register",
        data={
            "username": "TestUser",
            "email": "test@example.com",
            "password": "password123"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"TestUser" in response.data

    with app.app_context():
        user = User.query.filter_by(
            email="test@example.com"
        ).first()

        assert user is not None
        assert user.username == "TestUser"



def test_duplicate_registration(client):

    user_data = {
        "username": "TestUser",
        "email": "test@example.com",
        "password": "password123"
    }

    # Register the first user
    client.post("/register", data=user_data)

    # Log out because registration automatically logs the user in
    client.post("/logout")

    # Attempt to register with the same email
    response = client.post(
        "/register",
        data={
            "username": "AnotherUser",
            "email": "test@example.com",
            "password": "password123"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"already exists" in response.data



def test_user_login(client):
    client.post(
        "/register",
        data={
            "username": "TestUser",
            "email": "test@example.com",
            "password": "password123"
        }
    )

    client.post("/logout")

    response = client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "password123"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"TestUser" in response.data


def test_invalid_login(client):
    response = client.post(
        "/login",
        data={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        },
        follow_redirects=True
    )

    assert b"Invalid email or password" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
