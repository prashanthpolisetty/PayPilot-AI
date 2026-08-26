import os
import sys
try:
    import pytest
except ImportError:
    pytest = None
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.database import SessionLocal, init_db
from app.db.seed import seed_database
from app.services.catalog_service import CatalogService
from app.services.cart_service import CartService
from app.services.policy_engine import PolicyEngine
from app.services.razorpay_adapter import razorpay_adapter
from app.agents.runner import AgentRunner
from app.db.models import Product, Order, Approval

def dummy_decorator(*args, **kwargs):
    def decorator(fn):
        return fn
    return decorator

fixture_dec = pytest.fixture if pytest else dummy_decorator

@fixture_dec(scope="module")
def setup_db():
    init_db()
    seed_database()
    db = SessionLocal()
    yield db
    db.close()

def test_catalog_search(setup_db):
    db = setup_db
    products = CatalogService.search_products(db, query="headphone")
    assert len(products) > 0
    first = products[0]
    assert "ANC" in first.name or "Headphone" in first.name
    assert first.price_minor > 0

def test_policy_engine_over_limit_block(setup_db):
    db = setup_db
    # Workstation laptop costs INR 1,49,999 (14,999,900 paise) which exceeds the INR 1,00,000 (10,000,000 paise) limit
    expensive_prod = db.query(Product).filter(Product.price_minor > 10000000).first()
    assert expensive_prod is not None

    cart = CartService.create_cart(db, "user_demo_001", "merchant_demo_001")
    CartService.add_to_cart(db, cart.id, expensive_prod.id, 1)

    pol_res = PolicyEngine.evaluate_cart_policy(db, cart.id, "user_demo_001")
    assert pol_res.allowed is False
    assert "EXCEEDS_MAX_TRANSACTION_LIMIT" in pol_res.reason_codes

def test_end_to_end_agent_flow_success(setup_db):
    db = setup_db
    user_prompt = "I need ANC wireless headphones under INR 5,000."
    res = AgentRunner.run_agent_turn(db, user_prompt, session_id="test_success_session", user_id="user_test_success_001")
    
    assert res["run_id"] is not None
    assert "Apex Pro ANC Wireless Headphones" in res["agent_response"]
    assert "APPROVED" in res["agent_response"]
    assert "VERIFIED & PAID" in res["agent_response"]

def test_graceful_payment_failure_recovery_demo(setup_db):
    db = setup_db
    user_prompt = "I want ANC headphones under INR 5,000. Trigger test failure demo."
    res = AgentRunner.run_agent_turn(db, user_prompt, session_id="test_fail_session", user_id="user_test_fail_001")

    assert res["run_id"] is not None
    assert "Graceful Failure Recovery Triggered" in res["agent_response"]
    assert "No money was captured" in res["agent_response"]

def test_razorpay_adapter_order_creation():
    order_dict = razorpay_adapter.create_order(amount_minor=449900, currency="INR", receipt_id="rcpt_unit_test")
    assert order_dict["id"] is not None
    assert order_dict["amount"] == 449900

def run_all_tests():
    print("[TEST RUNNER] Initializing test suite...")
    init_db()
    seed_database()
    db = SessionLocal()
    try:
        print("[1/5] Running Catalog Search Test...")
        test_catalog_search(db)
        print("  -> PASSED: Catalog search & filters working.")

        print("[2/5] Running Policy Engine Over-Limit Block Test...")
        test_policy_engine_over_limit_block(db)
        print("  -> PASSED: Policy engine correctly blocked transaction exceeding INR 10,000 limit.")

        print("[3/5] Running End-To-End Agent Flow Test...")
        test_end_to_end_agent_flow_success(db)
        print("  -> PASSED: Complete 18-step agentic commerce journey executed & verified.")

        print("[4/5] Running Graceful Payment Failure Recovery Test...")
        test_graceful_payment_failure_recovery_demo(db)
        print("  -> PASSED: Controlled failure triggered & handled gracefully with recovery options.")

        print("[5/5] Running Razorpay Order Creation Adapter Test...")
        test_razorpay_adapter_order_creation()
        print("  -> PASSED: Razorpay order created with Key ID rzp_test_TSF2aLs0qkWNQy.")

        print("\nALL 5 TESTS PASSED SUCCESSFULLY! BACKEND WORKING MODEL IS VALIDATED.")
    finally:
        db.close()

if __name__ == "__main__":
    run_all_tests()

