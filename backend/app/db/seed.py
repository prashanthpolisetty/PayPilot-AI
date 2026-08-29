import json
from pathlib import Path
from app.db.database import SessionLocal, init_db
from app.db.models import Merchant, User, Product

def seed_database():
    init_db()
    db = SessionLocal()

    try:
        # Seed Merchant if not exists
        merchant = db.query(Merchant).filter_by(name="Razorpay Tech Merchant Store").first()
        if not merchant:
            merchant = Merchant(
                id="merchant_demo_001",
                name="Razorpay Tech Merchant Store",
                status="ACTIVE"
            )
            db.add(merchant)
            db.commit()
            db.refresh(merchant)
            print(f"[Seed] Created Merchant: {merchant.name} ({merchant.id})")

        # Seed MerchantConfig if not exists or reset to default ₹1,00,000
        from app.db.models import MerchantConfig
        m_cfg = db.query(MerchantConfig).filter_by(merchant_id=merchant.id).first()
        if not m_cfg:
            m_cfg = MerchantConfig(merchant_id=merchant.id, max_transaction_limit_paise=10000000, max_daily_spend_paise=20000000)
            db.add(m_cfg)
            db.commit()
        else:
            m_cfg.max_transaction_limit_paise = 10000000
            m_cfg.max_daily_spend_paise = 20000000
            db.commit()

        # Seed User if not exists
        user = db.query(User).filter_by(external_ref="user_demo_001").first()
        if not user:
            user = User(
                id="user_demo_001",
                external_ref="user_demo_001",
                name="Demo AI Buyer",
                email="buyer@example.com"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"[Seed] Created User: {user.name} ({user.id})")

        # Seed Products from products.json
        products_json_path = Path(__file__).resolve().parent.parent.parent / "data" / "products.json"
        with open(products_json_path, "r", encoding="utf-8") as f:
            products_data = json.load(f)

        sku_to_id_map = {}

        # First pass: Insert or update products
        for prod_item in products_data:
            existing = db.query(Product).filter_by(sku=prod_item["sku"]).first()
            if not existing:
                product = Product(
                    id=f"prod_{prod_item['sku'].lower().replace('-', '_')}",
                    merchant_id=merchant.id,
                    sku=prod_item["sku"],
                    name=prod_item["name"],
                    category=prod_item["category"],
                    description=prod_item["description"],
                    price_minor=prod_item["price_minor"],
                    currency=prod_item["currency"],
                    inventory_qty=prod_item["inventory_qty"],
                    attributes_json=prod_item.get("attributes", {}),
                    active=True
                )
                db.add(product)
                db.commit()
                db.refresh(product)
                sku_to_id_map[prod_item["sku"]] = product.id
                print(f"[Seed] Added product: {product.name} (INR {product.price_minor/100:.2f})")
            else:
                sku_to_id_map[prod_item["sku"]] = existing.id

        # Second pass: Update upsell product IDs mapping
        for prod_item in products_data:
            product_id = sku_to_id_map.get(prod_item["sku"])
            upsell_skus = prod_item.get("upsell_skus", [])
            upsell_ids = [sku_to_id_map[s] for s in upsell_skus if s in sku_to_id_map]
            
            product = db.query(Product).get(product_id)
            if product:
                product.upsell_product_ids_json = upsell_ids
                db.commit()

        print("[Seed] Seeding completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"[Seed Error] {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
