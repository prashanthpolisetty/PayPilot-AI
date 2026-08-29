from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Merchant, UserPreference, MerchantConfig
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterUserRequest(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "BUYER"

class RegisterMerchantRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    name: str

@router.post("/register/user", response_model=TokenResponse)
def register_user(req: RegisterUserRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(email=req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        external_ref=f"ext_{req.email.replace('@', '_')}",
        name=req.name,
        email=req.email,
        hashed_password=hash_password(req.password),
        role=req.role or "BUYER"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize default user preferences
    pref = UserPreference(user_id=user.id, preferred_categories=["Audio", "Laptops"])
    db.add(pref)
    db.commit()

    token = create_access_token({"sub": user.id, "role": user.role, "email": user.email})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        role=user.role,
        name=user.name
    )

@router.post("/register/merchant", response_model=TokenResponse)
def register_merchant(req: RegisterMerchantRequest, db: Session = Depends(get_db)):
    existing = db.query(Merchant).filter_by(email=req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Merchant email already registered")

    merchant = Merchant(
        name=req.name,
        email=req.email,
        hashed_password=hash_password(req.password),
        status="ACTIVE"
    )
    db.add(merchant)
    db.commit()
    db.refresh(merchant)

    # Initialize merchant default policy config
    config = MerchantConfig(
        merchant_id=merchant.id,
        max_transaction_limit_paise=10000000,
        max_daily_spend_paise=20000000,
        max_quantity_per_item=5,
        risk_scoring_enabled=True
    )
    db.add(config)
    db.commit()

    token = create_access_token({"sub": merchant.id, "role": "MERCHANT", "email": merchant.email})
    return TokenResponse(
        access_token=token,
        user_id=merchant.id,
        role="MERCHANT",
        name=merchant.name
    )

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    # Check User table first
    user = db.query(User).filter_by(email=req.email).first()
    if user and verify_password(req.password, user.hashed_password):
        token = create_access_token({"sub": user.id, "role": user.role, "email": user.email})
        return TokenResponse(
            access_token=token,
            user_id=user.id,
            role=user.role,
            name=user.name
        )

    # Check Merchant table
    merchant = db.query(Merchant).filter_by(email=req.email).first()
    if merchant and verify_password(req.password, merchant.hashed_password):
        token = create_access_token({"sub": merchant.id, "role": "MERCHANT", "email": merchant.email})
        return TokenResponse(
            access_token=token,
            user_id=merchant.id,
            role="MERCHANT",
            name=merchant.name
        )

    raise HTTPException(status_code=401, detail="Invalid email or password")
