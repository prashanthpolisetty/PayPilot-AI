from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import Cart, CartItem, Product, Approval, Order, MerchantConfig
from app.services.risk_service import RiskService

class PolicyCheckResult:
    def __init__(self, allowed: bool, reason_codes: List[str], details: Dict[str, Any]):
        self.allowed = allowed
        self.reason_codes = reason_codes
        self.details = details

    def to_dict(self):
        return {
            "allowed": self.allowed,
            "reason_codes": self.reason_codes,
            "details": self.details
        }

class PolicyEngine:
    @staticmethod
    def evaluate_cart_policy(db: Session, cart_id: str, user_id: str) -> PolicyCheckResult:
        reason_codes = []
        details = {}
        allowed = True

        cart = db.query(Cart).get(cart_id)
        if not cart:
            return PolicyCheckResult(False, ["CART_NOT_FOUND"], {"error": "Cart not found"})

        items = db.query(CartItem).filter_by(cart_id=cart_id).all()
        if not items:
            return PolicyCheckResult(False, ["CART_EMPTY"], {"error": "Cart is empty"})

        # Load dynamic merchant configuration if available
        merchant_config = db.query(MerchantConfig).filter_by(merchant_id=cart.merchant_id).first()
        max_tx_paise = merchant_config.max_transaction_limit_paise if merchant_config else settings.MAX_TRANSACTION_LIMIT_PAISE
        max_daily_paise = merchant_config.max_daily_spend_paise if merchant_config else settings.MAX_DAILY_SPEND_PAISE
        max_qty_item = merchant_config.max_quantity_per_item if merchant_config else settings.MAX_QUANTITY_PER_ITEM

        # Check 1: Server-side total calculation revalidation
        computed_total_minor = sum(item.line_total_minor for item in items)
        if computed_total_minor != cart.total_minor:
            cart.total_minor = computed_total_minor
            db.commit()
        
        details["cart_total_rupees"] = cart.total_minor / 100.0
        details["currency"] = cart.currency

        # Check 2: Max transaction limit check
        if cart.total_minor > max_tx_paise:
            allowed = False
            reason_codes.append("EXCEEDS_MAX_TRANSACTION_LIMIT")
            details["max_transaction_limit_rupees"] = max_tx_paise / 100.0
            details["violation"] = f"Cart total INR {cart.total_minor/100:.2f} exceeds max allowed INR {max_tx_paise/100:.2f}"

        # Check 3: Max item quantity check
        for item in items:
            if item.quantity > max_qty_item:
                allowed = False
                reason_codes.append("EXCEEDS_MAX_ITEM_QUANTITY")
                details["max_quantity_per_item"] = max_qty_item

        # Check 4: Stock availability and price revalidation
        for item in items:
            prod = db.query(Product).get(item.product_id)
            if not prod or not prod.active:
                allowed = False
                reason_codes.append("PRODUCT_INACTIVE_OR_DELETED")
            elif prod.inventory_qty < item.quantity:
                allowed = False
                reason_codes.append("INSUFFICIENT_STOCK")
                details["out_of_stock_product"] = prod.name
            elif prod.price_minor != item.unit_price_minor:
                allowed = False
                reason_codes.append("PRICE_CHANGED_REVALIDATION_REQUIRED")
                details["product_price_changed"] = prod.name

        # Check 5: Daily spend limit check (sum of past paid orders today in UTC)
        import datetime
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        start_of_today = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_today_naive = start_of_today.replace(tzinfo=None)
        
        paid_orders = db.query(Order).filter(
            Order.user_id == user_id,
            Order.status == "PAID",
            Order.created_at >= start_of_today_naive
        ).all()
        daily_spent_minor = sum(o.total_minor for o in paid_orders)
        if (daily_spent_minor + cart.total_minor) > max_daily_paise:
            allowed = False
            reason_codes.append("EXCEEDS_MAX_DAILY_SPEND_LIMIT")
            details["daily_spent_rupees"] = daily_spent_minor / 100.0
            details["max_daily_spend_rupees"] = max_daily_paise / 100.0

        # Check 6: Fraud Risk Scoring
        risk_res = RiskService.evaluate_cart_risk(db, cart_id, user_id)
        details["risk_assessment"] = risk_res.to_dict()
        if risk_res.risk_level == "CRITICAL":
            allowed = False
            reason_codes.append("BLOCKED_BY_RISK_ENGINE")

        if allowed:
            reason_codes.append("POLICY_PASSED")

        return PolicyCheckResult(allowed, reason_codes, details)

    @staticmethod
    def verify_user_approval(db: Session, cart_id: str, user_id: str) -> bool:
        cart = db.query(Cart).get(cart_id)
        if not cart:
            return False

        approval = db.query(Approval).filter(
            Approval.cart_id == cart_id,
            Approval.cart_version == cart.version,
            Approval.approved_by == user_id,
            Approval.status == "APPROVED"
        ).first()

        return approval is not None
