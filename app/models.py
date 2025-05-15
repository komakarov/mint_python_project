from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(128))
    is_active = Column(Boolean, default=True)


    lots = relationship("Lot", back_populates="owner")
    bids = relationship("Bid", back_populates="user")


class Lot(Base):
    __tablename__ = "lots"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    start_price = Column(Numeric(10, 2), nullable=False)
    current_price = Column(Numeric(10, 2), nullable=False)
    bid_step = Column(Numeric(10, 2), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    end_time = Column(DateTime, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="lots")
    bids = relationship("Bid", back_populates="lot")


class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    lot_id = Column(Integer, ForeignKey("lots.id"))
    is_proxy = Column(Boolean, default=False)
    max_bid = Column(Numeric(10, 2))


    user = relationship("User", back_populates="bids")
    lot = relationship("Lot", back_populates="bids")
