import uuid
import pytest
from fastapi.testclient import TestClient
from main import app
from app.db.database import init_db
from app.db.seed import seed_database

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    seed_database()

def test_user_registration_and_login():
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    # 1. Register User
    reg_res = client.post("/api/v1/auth/register/user", json={
        "name": "Test Buyer",
        "email": unique_email,
        "password": "Password123!",
        "role": "BUYER"
    })
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["role"] == "BUYER"

    # 2. Login User
    login_res = client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    assert login_data["name"] == "Test Buyer"

def test_merchant_config_and_coupon_flow():
    merchant_id = "merchant_test_cfg_001"
    
    # 1. Get Merchant Config
    cfg_res = client.get(f"/api/v1/merchant/config/{merchant_id}")
    assert cfg_res.status_code == 200
    assert cfg_res.json()["merchant_id"] == merchant_id

    # 2. Update Merchant Config
    update_res = client.put(f"/api/v1/merchant/config/{merchant_id}", json={
        "max_transaction_limit_rupees": 150000,
        "risk_scoring_enabled": True
    })
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "SUCCESS"

    # 3. Create Coupon Code
    unique_code = f"PROMO_{uuid.uuid4().hex[:4].upper()}"
    cpn_res = client.post("/api/v1/merchant/coupons", json={
        "merchant_id": merchant_id,
        "code": unique_code,
        "discount_type": "PERCENTAGE",
        "discount_value": 15,
        "min_cart_rupees": 500
    })
    assert cpn_res.status_code == 200
    assert cpn_res.json()["code"] == unique_code

    # 4. List Coupons
    list_res = client.get(f"/api/v1/merchant/coupons/{merchant_id}")
    assert list_res.status_code == 200
    codes = [c["code"] for c in list_res.json()]
    assert unique_code in codes
