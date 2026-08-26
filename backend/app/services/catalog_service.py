from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import Product

class CatalogService:
    @staticmethod
    def search_products(
        db: Session,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_price_minor: Optional[int] = None,
        min_price_minor: Optional[int] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> List[Product]:
        q = db.query(Product).filter(Product.active == True)

        if category:
            q = q.filter(Product.category.ilike(f"%{category}%"))
        
        if max_price_minor is not None:
            q = q.filter(Product.price_minor <= max_price_minor)
            
        if min_price_minor is not None:
            q = q.filter(Product.price_minor >= min_price_minor)

        if query and query.strip():
            terms = [t.strip() for t in query.split() if len(t.strip()) > 1]
            from sqlalchemy import or_
            filters = []
            # Exact phrase match
            filters.append(Product.name.ilike(f"%{query}%"))
            filters.append(Product.description.ilike(f"%{query}%"))
            filters.append(Product.category.ilike(f"%{query}%"))
            # Individual token matches
            for t in terms:
                filters.append(Product.name.ilike(f"%{t}%"))
                filters.append(Product.description.ilike(f"%{t}%"))
            q = q.filter(or_(*filters))

        products = q.all()

        # Attribute-level filtering if specified (e.g. ANC=True)
        if attributes:
            filtered = []
            for prod in products:
                prod_attrs = prod.attributes_json or {}
                matches = True
                for k, v in attributes.items():
                    if k in prod_attrs:
                        if isinstance(v, str) and isinstance(prod_attrs[k], str):
                            if v.lower() != prod_attrs[k].lower():
                                matches = False
                        elif prod_attrs[k] != v:
                            matches = False
                if matches:
                    filtered.append(prod)
            return filtered

        return products

    @staticmethod
    def get_product(db: Session, product_id_or_sku: str) -> Optional[Product]:
        prod = db.query(Product).filter(
            (Product.id == product_id_or_sku) | (Product.sku == product_id_or_sku)
        ).first()
        return prod

    @staticmethod
    def check_inventory(db: Session, product_id: str, quantity: int) -> bool:
        prod = db.query(Product).get(product_id)
        if not prod or not prod.active:
            return False
        return prod.inventory_qty >= quantity

    @staticmethod
    def get_upsells(db: Session, product_id: str) -> List[Product]:
        prod = db.query(Product).get(product_id)
        if not prod or not prod.upsell_product_ids_json:
            return []
        
        upsell_ids = prod.upsell_product_ids_json
        return db.query(Product).filter(Product.id.in_(upsell_ids), Product.active == True).all()
