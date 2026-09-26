"""
Pydantic schemas.
Created by Tanvi Sakhale
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel


class ComplaintBase(BaseModel):
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength_grade: Optional[str] = None
    batch_lot_number: Optional[str] = None
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    quantity_affected: Optional[str] = None
    complaint_type: Optional[str] = None
    complaint_date: Optional[date] = None
    detailed_complaint_description: Optional[str] = None
    initial_severity: Optional[str] = None
    priority: Optional[str] = None


class ComplaintCreate(ComplaintBase):
    pass


class ComplaintOut(ComplaintBase):
    id: str
    status: str
    ai_completeness_score: Optional[float] = None
    ai_missing_fields: Optional[List[str]] = None
    ai_risk_classification: Optional[str] = None
    ai_root_cause_suggestions: Optional[List[str]] = None
    ai_capa_suggestions: Optional[List[str]] = None
    ai_summary: Optional[str] = None
    ai_duplicate_of: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExtractionResult(BaseModel):
    """What the LangGraph pipeline returns to populate the form."""
    fields: ComplaintBase
    completeness_score: float
    missing_fields: List[str]
    risk_classification: str
    root_cause_suggestions: List[str]
    capa_suggestions: List[str]
    summary: str
    duplicate_of: Optional[str] = None
    duplicate_confidence: Optional[float] = None


class ChatRequest(BaseModel):
    complaint_id: Optional[str] = None
    context_text: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    reply: str
    extraction: Optional[ExtractionResult] = None
