from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_test_user():
    """
    Creates a unique user for testing and returns
    the authentication token.
    """

    unique_id = uuid4().hex[:8]

    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"
    password = "Test@12345"

    register_response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "role": "user"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


# --------------------------------------------------
# ROOT
# --------------------------------------------------

def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "Incident Management API"
    assert data["status"] == "running"


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "healthy"


# --------------------------------------------------
# DATABASE HEALTH
# --------------------------------------------------

def test_database_health():
    response = client.get("/db-health")

    assert response.status_code == 200

    assert response.json()["database"] == "connected"


# --------------------------------------------------
# USER REGISTRATION + LOGIN
# --------------------------------------------------

def test_authentication():
    token = create_test_user()

    assert token is not None
    assert len(token) > 20


# --------------------------------------------------
# CREATE INCIDENT
# --------------------------------------------------

def test_create_incident():
    token = create_test_user()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.post(
        "/incidents/",
        headers=headers,
        json={
            "title": "Test Payment Failure",
            "description": "Automated test incident",
            "severity": "P1",
            "assigned_to": "test-user"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Test Payment Failure"
    assert data["severity"] == "P1"
    assert data["status"] == "open"


# --------------------------------------------------
# GET INCIDENTS
# --------------------------------------------------

def test_get_incidents():
    token = create_test_user()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.get(
        "/incidents/",
        headers=headers
    )

    assert response.status_code == 200

    assert isinstance(response.json(), list)


# --------------------------------------------------
# INCIDENT FILTER
# --------------------------------------------------

def test_incident_filter():
    token = create_test_user()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    client.post(
        "/incidents/",
        headers=headers,
        json={
            "title": "Critical API Failure",
            "description": "P1 test incident",
            "severity": "P1",
            "assigned_to": "devops"
        }
    )

    response = client.get(
        "/incidents/?severity=P1",
        headers=headers
    )

    assert response.status_code == 200

    incidents = response.json()

    assert isinstance(incidents, list)

    for incident in incidents:
        assert incident["severity"] == "P1"


# --------------------------------------------------
# INCIDENT STATISTICS
# --------------------------------------------------

def test_incident_stats():
    token = create_test_user()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.get(
        "/incidents/stats",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert "total" in data
    assert "open" in data
    assert "investigating" in data
    assert "resolved" in data
    assert "closed" in data
    assert "critical" in data


# --------------------------------------------------
# UNAUTHORIZED ACCESS
# --------------------------------------------------

def test_unauthorized_access():
    response = client.get("/incidents/")

    assert response.status_code == 401