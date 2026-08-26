import uuid
import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    external_ref = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=utc_now)

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime, default=utc_now)

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=generate_uuid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)
    sku = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price_minor = Column(Integer, nullable=False)  # Integer paise (e.g. ₹4,499 = 449900)
    currency = Column(String, default="INR")
    inventory_qty = Column(Integer, default=100)
    attributes_json = Column(JSON, nullable=True)  # e.g. {"ANC": True, "battery_hours": 35}
    upsell_product_ids_json = Column(JSON, nullable=True)  # Complementary item IDs
    active = Column(Boolean, default=True)

class Cart(Base):
    __tablename__ = "carts"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)
    status = Column(String, default="ACTIVE")  # ACTIVE, CHECKOUT, COMPLETED, ABANDONED
    currency = Column(String, default="INR")
    total_minor = Column(Integer, default=0)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    cart_id = Column(String, ForeignKey("carts.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price_minor = Column(Integer, nullable=False)
    line_total_minor = Column(Integer, nullable=False)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=generate_uuid)
    cart_id = Column(String, ForeignKey("carts.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="CREATED")  # CREATED, PAID, FAILED, PENDING_REVIEW
    total_minor = Column(Integer, nullable=False)
    currency = Column(String, default="INR")
    razorpay_order_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=generate_uuid)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    razorpay_payment_id = Column(String, nullable=True)
    razorpay_signature = Column(String, nullable=True)
    status = Column(String, default="INITIATED")  # INITIATED, SUCCESS, FAILED
    amount_minor = Column(Integer, nullable=False)
    method = Column(String, default="UPI")
    attempt_no = Column(Integer, default=1)
    error_code = Column(String, nullable=True)
    error_description = Column(String, nullable=True)
    created_at = Column(DateTime, default=utc_now)

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String, primary_key=True, default=generate_uuid)
    cart_id = Column(String, ForeignKey("carts.id"), nullable=False)
    cart_version = Column(Integer, nullable=False)
    approved_by = Column(String, nullable=False)  # User ID
    status = Column(String, default="PENDING")  # PENDING, APPROVED, REJECTED, EXPIRED
    approved_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, nullable=False)
    state = Column(String, default="RUNNING")
    model = Column(String, nullable=False)
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)

class AgentAction(Base):
    __tablename__ = "agent_actions"

    id = Column(String, primary_key=True, default=generate_uuid)
    agent_run_id = Column(String, ForeignKey("agent_runs.id"), nullable=False)
    tool_name = Column(String, nullable=False)
    input_hash = Column(String, nullable=True)
    input_json = Column(JSON, nullable=True)
    output_summary = Column(Text, nullable=True)
    status = Column(String, default="SUCCESS")
    latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    actor_type = Column(String, nullable=False)  # USER, AGENT, SYSTEM
    actor_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)  # CART, ORDER, PAYMENT, POLICY
    entity_id = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    event_id = Column(String, unique=True, nullable=False)
    event_type = Column(String, nullable=False)
    payload_json = Column(JSON, nullable=False)
    status = Column(String, default="PROCESSED")  # PROCESSED, IGNORED, FAILED
    processed_at = Column(DateTime, default=utc_now)
