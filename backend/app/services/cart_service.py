from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import Cart, CartItem, Product
from app.services.catalog_service import CatalogService

class CartService:
    @staticmethod
    def create_cart(db: Session, user_id: str, merchant_id: str) -> Cart:
        cart = Cart(
            user_id=user_id,
            merchant_id=merchant_id,
            status="ACTIVE",
            currency="INR",
            total_minor=0,
            version=1
        )
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart

    @staticmethod
    def add_to_cart(db: Session, cart_id: str, product_id: str, quantity: int = 1) -> Cart:
        cart = db.query(Cart).get(cart_id)
        if not cart:
            raise ValueError(f"Cart {cart_id} not found")

        product = db.query(Product).get(product_id)
        if not product or not product.active:
            raise ValueError(f"Product {product_id} is not available")

        if not CatalogService.check_inventory(db, product_id, quantity):
            raise ValueError(f"Insufficient stock for product '{product.name}'. Available: {product.inventory_qty}")

        # Check if item already in cart
        existing_item = db.query(CartItem).filter_by(cart_id=cart_id, product_id=product_id).first()
        if existing_item:
            new_qty = existing_item.quantity + quantity
            if not CatalogService.check_inventory(db, product_id, new_qty):
                raise ValueError(f"Cannot add {quantity} more. Stock limit reached.")
            existing_item.quantity = new_qty
            existing_item.line_total_minor = existing_item.quantity * product.price_minor
        else:
            item = CartItem(
                cart_id=cart_id,
                product_id=product_id,
                quantity=quantity,
                unit_price_minor=product.price_minor,
                line_total_minor=quantity * product.price_minor
            )
            db.add(item)

        # Recalculate total & increment version
        cart.version += 1
        CartService._invalidate_approvals(db, cart_id)
        db.commit()
        CartService.recalculate_total(db, cart_id)
        db.refresh(cart)
        return cart

    @staticmethod
    def update_cart_item(db: Session, cart_id: str, item_id: str, quantity: int) -> Cart:
        cart = db.query(Cart).get(cart_id)
        if not cart:
            raise ValueError(f"Cart {cart_id} not found")

        item = db.query(CartItem).filter_by(id=item_id, cart_id=cart_id).first()
        if not item:
            raise ValueError(f"Cart item {item_id} not found")

        if quantity <= 0:
            db.delete(item)
        else:
            product = db.query(Product).get(item.product_id)
            if not CatalogService.check_inventory(db, item.product_id, quantity):
                raise ValueError(f"Insufficient stock for product '{product.name}'")
            item.quantity = quantity
            item.line_total_minor = quantity * item.unit_price_minor

        cart.version += 1
        CartService._invalidate_approvals(db, cart_id)
        db.commit()
        CartService.recalculate_total(db, cart_id)
        db.refresh(cart)
        return cart

    @staticmethod
    def remove_from_cart(db: Session, cart_id: str, item_id: str) -> Cart:
        return CartService.update_cart_item(db, cart_id, item_id, 0)

    @staticmethod
    def _invalidate_approvals(db: Session, cart_id: str):
        """Invalidates all previous approvals when cart content changes."""
        from app.db.models import Approval
        approvals = db.query(Approval).filter_by(cart_id=cart_id, status="APPROVED").all()
        for a in approvals:
            a.status = "EXPIRED"

    @staticmethod
    def recalculate_total(db: Session, cart_id: str) -> int:
        cart = db.query(Cart).get(cart_id)
        if not cart:
            return 0

        items = db.query(CartItem).filter_by(cart_id=cart_id).all()
        total_minor = sum(item.line_total_minor for item in items)
        cart.total_minor = total_minor
        db.commit()
        return total_minor

    @staticmethod
    def get_cart(db: Session, cart_id: str) -> Optional[Cart]:
        return db.query(Cart).get(cart_id)

