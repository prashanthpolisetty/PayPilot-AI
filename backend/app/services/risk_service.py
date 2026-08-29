from typing import Dict, Any, List
from sqlalchemy.orm import Session
import datetime
from app.db.models import Cart, CartItem, Order, Payment

class RiskScoreResult:
    def __init__(self, risk_score: float, risk_level: str, flags: List[str]):
        self.risk_score = risk_score        # 0.0 (low) to 1.0 (critical)
        self.risk_level = risk_level        # LOW, MEDIUM, HIGH, CRITICAL
        self.flags = flags

    def to_dict(self):
        return {
            "risk_score": round(self.risk_score, 2),
            "risk_level": self.risk_level,
            "flags": self.flags
        }

class RiskService:
    @staticmethod
    def evaluate_cart_risk(db: Session, cart_id: str, user_id: str) -> RiskScoreResult:
        flags = []
        score = 0.0

        cart = db.query(Cart).get(cart_id)
        if not cart:
            return RiskScoreResult(1.0, "CRITICAL", ["INVALID_CART"])

        items = db.query(CartItem).filter_by(cart_id=cart_id).all()
        if not items:
            return RiskScoreResult(0.0, "LOW", [])

        total_rupees = cart.total_minor / 100.0

        # Risk Rule 1: High Transaction Value (> ₹50,000)
        if total_rupees >= 50000:
            score += 0.35
            flags.append("HIGH_TRANSACTION_VALUE")

        # Risk Rule 2: High Quantity Items
        total_qty = sum(item.quantity for item in items)
        if total_qty >= 5:
            score += 0.2
            flags.append("BULK_QUANTITY_ATTEMPT")

        # Risk Rule 3: Velocity Check (Recent orders within last 1 hour)
        one_hour_ago = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - datetime.timedelta(hours=1)
        recent_orders_count = db.query(Order).filter(
            Order.user_id == user_id,
            Order.created_at >= one_hour_ago
        ).count()
        if recent_orders_count >= 3:
            score += 0.3
            flags.append("HIGH_ORDER_VELOCITY")

        # Risk Rule 4: Recent Failed Payment Attempts
        recent_failures = db.query(Payment).join(Order).filter(
            Order.user_id == user_id,
            Payment.status == "FAILED",
            Payment.created_at >= one_hour_ago
        ).count()
        if recent_failures >= 2:
            score += 0.25
            flags.append("MULTIPLE_PAYMENT_FAILURES")

        # Determine level
        score = min(score, 1.0)
        if score >= 0.7:
            level = "CRITICAL"
        elif score >= 0.4:
            level = "HIGH"
        elif score >= 0.2:
            level = "MEDIUM"
        else:
            level = "LOW"

        return RiskScoreResult(score, level, flags)
