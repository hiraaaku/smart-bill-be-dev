# models.py
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    receipts = relationship("Receipt", back_populates="user")


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    image_url = Column(String)
    raw_ocr_result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="receipts")
    items = relationship("ReceiptItem", back_populates="receipt")
    participants = relationship("Participant", back_populates="receipt")
    splits = relationship("Split", back_populates="receipt")


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"))
    name = Column(String)
    price = Column(Numeric)
    editable = Column(Boolean, default=True)

    receipt = relationship("Receipt", back_populates="items")
    owners = relationship("ItemOwner", back_populates="item")


class Participant(Base):
    __tablename__ = "participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"))
    name = Column(String)

    receipt = relationship("Receipt", back_populates="participants")
    owned_items = relationship("ItemOwner", back_populates="participant")


class ItemOwner(Base):
    __tablename__ = "item_owners"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey("receipt_items.id"))
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id"))

    item = relationship("ReceiptItem", back_populates="owners")
    participant = relationship("Participant", back_populates="owned_items")


class Split(Base):
    __tablename__ = "splits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"))
    result = Column(JSON)  # {participant_id: total_amount}

    receipt = relationship("Receipt", back_populates="splits")
