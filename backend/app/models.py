"""Database models - Hardened with strict constraints and type safety."""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Integer, String, ForeignKey, DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Wallet(Base):
    __tablename__ = 'wallets'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal('0.00'), nullable=False)

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    kind: Mapped[str] = mapped_column(String(20), nullable=False) # e.g., 'deposit', 'withdrawal'
    status: Mapped[str] = mapped_column(String(20), default='pending', nullable=False)
    # Unique constraint prevents duplicate processing / replay attacks at the DB level
    reference: Mapped[str | None] = mapped_column(String(150), unique=True, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)