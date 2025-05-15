import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.main import app
from app.database import Base, get_db, get_password_hash
from app.models import User, Lot, Bid

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    hashed_password = get_password_hash("password123")
    test_user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(test_user)

    hashed_password2 = get_password_hash("password456")
    test_user2 = User(
        username="testuser2",
        email="test2@example.com",
        hashed_password=hashed_password2,
        is_active=True
    )
    db.add(test_user2)

    end_time = datetime.now() + timedelta(days=7)
    test_lot = Lot(
        title="Test Lot",
        description="Test Description",
        start_price=100.0,
        bid_step=10.0,
        current_price=100.0,
        created_at=datetime.now(),
        end_time=end_time,
        owner_id=1
    )
    db.add(test_lot)

    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


def test_register_user():
    response = client.post(
        "/users/",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",

        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data


def test_register_user_duplicate():
    response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "password123",
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_login_user():
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "password123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_user_invalid_credentials():
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "wrongpassword"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert "invalid username or password" in response.json()["detail"].lower()


def get_auth_token(username="testuser", password="password123"):
    response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]


def test_create_lot():
    token = get_auth_token()
    end_time = (datetime.now() + timedelta(days=7)).isoformat()
    response = client.post(
        "/lots/",
        json={
            "title": "New Lot",
            "description": "New lot description",
            "start_price": 200.0,
            "bid_step": 20.0,
            "end_time": end_time
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Lot"
    assert data["start_price"] == 200.0
    assert data["current_price"] == 200.0
    assert "id" in data


def test_create_lot_unauthorized():
    end_time = (datetime.now() + timedelta(days=7)).isoformat()
    response = client.post(
        "/lots/",
        json={
            "title": "New Lot",
            "description": "New lot description",
            "start_price": 200.0,
            "bid_step": 20.0,
            "end_time": end_time
        }
    )
    assert response.status_code == 401


def test_get_lots():
    response = client.get("/lots/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["title"] == "Test Lot"


def test_get_lot_by_id():
    response = client.get("/lots/1")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Lot"
    assert data["id"] == 1


def test_get_lot_by_id_not_found():
    response = client.get("/lots/999")
    assert response.status_code == 404


def test_update_lot():
    token = get_auth_token()
    response = client.patch(
        "/lots/1",
        json={
            "title": "Updated Lot Title",
            "description": "Updated description",
            "start_price": 100.0,
            "bid_step": 10.0,
            "end_time": (datetime.now() + timedelta(days=7)).isoformat()
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Lot Title"


def test_update_lot_unauthorized():
    response = client.patch(
        "/lots/1",
        json={
            "title": "Updated Lot Title"
        }
    )
    assert response.status_code == 401


def test_update_lot_not_owner():
    token = get_auth_token(username="testuser2", password="password456")
    response = client.patch(
        "/lots/1",
        json={
            "title": "Updated by non-owner",
            "description": "Updated description",
            "start_price": 100.0,
            "bid_step": 10.0,
            "end_time": (datetime.now() + timedelta(days=7)).isoformat()
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


def test_delete_lot():
    token = get_auth_token()
    response = client.delete(
        "/lots/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204


def test_delete_lot_unauthorized():
    response = client.delete("/lots/1")
    assert response.status_code == 401


def test_create_bid():
    token = get_auth_token(username="testuser2", password="password456")
    end_time = (datetime.now() + timedelta(days=7)).isoformat()
    lot_response = client.post(
        "/lots/",
        json={
            "title": "Auction Lot",
            "description": "For bidding tests",
            "start_price": 100.0,
            "bid_step": 10.0,
            "end_time": end_time
        },
        headers={"Authorization": f"Bearer {get_auth_token()}"}
    )
    lot_id = lot_response.json()["id"]

    response = client.post(
        "/bids/",
        json={
            "lot_id": lot_id,
            "amount": 110.0,
            "is_proxy": False
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 110.0
    assert data["lot_id"] == lot_id


def test_create_proxy_bid():
    token = get_auth_token(username="testuser2", password="password456")
    end_time = (datetime.now() + timedelta(days=7)).isoformat()
    lot_response = client.post(
        "/lots/",
        json={
            "title": "Proxy Auction Lot",
            "description": "For proxy bidding tests",
            "start_price": 100.0,
            "bid_step": 10.0,
            "end_time": end_time
        },
        headers={"Authorization": f"Bearer {get_auth_token()}"}
    )
    lot_id = lot_response.json()["id"]

    response = client.post(
        "/bids/",
        json={
            "lot_id": lot_id,
            "amount": 110.0,
            "is_proxy": True,
            "max_bid": 200.0
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 110.0
    assert data["is_proxy"] == True
    assert data["max_bid"] == 200.0


def test_get_bids_for_lot():
    token = get_auth_token()
    lots_response = client.get("/lots/")
    lot_id = lots_response.json()[0]["id"]

    response = client.get(
        f"/lots/{lot_id}/bids",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "bids" in data
    assert isinstance(data["bids"], list)
    assert "count" in data


def test_get_bids_unauthorized():
    lots_response = client.get("/lots/")
    lot_id = lots_response.json()[0]["id"]

    response = client.get(f"/lots/{lot_id}/bids")
    assert response.status_code == 401