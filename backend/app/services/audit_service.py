from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import AuditLog

class AuditService:
    @staticmethod
    def write_audit_event(
        db: Session,
        actor_type: str,  # USER, AGENT, SYSTEM
        actor_id: str,
        action: str,  # SEARCH_PRODUCTS, CART_CREATED, POLICY_CHECK, PAYMENT_APPROVAL, ORDER_CREATED, PAYMENT_FAILED, PAYMENT_VERIFIED
        entity_type: str,  # PRODUCT, CART, ORDER, PAYMENT, POLICY
        entity_id: str,
        reason: Optional[str] = None,
        metadata_json: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        log_entry = AuditLog(
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            reason=reason,
            metadata_json=metadata_json or {}
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    def get_audit_trail(db: Session, entity_type: Optional[str] = None, entity_id: Optional[str] = None, limit: int = 50):
        q = db.query(AuditLog)
        if entity_type and entity_id:
            q = q.filter(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        elif entity_type:
            q = q.filter(AuditLog.entity_type == entity_type)
        
        return q.order_by(AuditLog.created_at.asc()).limit(limit).all()
