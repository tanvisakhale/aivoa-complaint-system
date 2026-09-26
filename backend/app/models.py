"""
SQLAlchemy models for the Customer Complaint Management System.
Created by Tanvi Sakhale
"""
import uuid
from datetime import datetime, date

from sqlalchemy import Column, String, Text, Float, DateTime, Date, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=gen_uuid)

    # 1. Origin & Customer Details
    complaint_source = Column(String(255))
    customer_name = Column(String(255))

    # 2. Product & Batch Identification
    product_name = Column(String(255))
    product_strength_grade = Column(String(255))
    batch_lot_number = Column(String(255))
    manufacturing_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    quantity_affected = Column(String(64))

    # 3. Complaint Details
    complaint_type = Column(String(255))
    complaint_date = Column(Date, nullable=True)
    detailed_complaint_description = Column(Text)

    # 4. Initial Assessment & Priority
    initial_severity = Column(String(64))
    priority = Column(String(64))

    # AI Copilot outputs
    ai_completeness_score = Column(Float, nullable=True)
    ai_missing_fields = Column(JSON, nullable=True)
    ai_risk_classification = Column(String(64), nullable=True)
    ai_root_cause_suggestions = Column(JSON, nullable=True)
    ai_capa_suggestions = Column(JSON, nullable=True)
    ai_summary = Column(Text, nullable=True)
    ai_duplicate_of = Column(String(36), nullable=True)

    status = Column(String(32), default="Pending Triage")
    raw_source_text = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
