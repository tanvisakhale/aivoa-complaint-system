"""
AIVOA.AI — AI-Powered Customer Complaint Management System (Pharma QMS)
FastAPI backend.

Created by Tanvi Sakhale
"""
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app import models, schemas
from app.document_parser import extract_text_from_upload
from app.langgraph_workflow import run_complaint_pipeline
from app.groq_client import call_groq, REASONING_MODEL, classify_chat_intent

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AIVOA.AI Customer Complaint Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "AIVOA.AI Complaint Management System",
            "created_by": "Tanvi Sakhale"}


def _get_recent_complaints_for_duplicate_check(db: Session) -> list:
    return [
        {"id": c.id, "product_name": c.product_name, "batch_lot_number": c.batch_lot_number,
         "detailed_complaint_description": c.detailed_complaint_description}
        for c in db.query(models.Complaint).order_by(models.Complaint.created_at.desc()).limit(50)
    ]


def _build_extraction_result(result: dict) -> schemas.ExtractionResult:
    """Shared by /api/extract and the auto-fill-from-chat bonus feature in /api/chat."""
    return schemas.ExtractionResult(
        fields=schemas.ComplaintBase(**result.get("fields", {})),
        completeness_score=result.get("completeness_score", 0),
        missing_fields=result.get("missing_fields", []),
        risk_classification=result.get("risk_classification", "Minor"),
        root_cause_suggestions=result.get("root_cause_suggestions", []),
        capa_suggestions=result.get("capa_suggestions", []),
        summary=result.get("summary", ""),
        duplicate_of=result.get("duplicate_of"),
        duplicate_confidence=result.get("duplicate_confidence"),
    )


# ---------------------------------------------------------------------------
# AI Complaint Intake Assistant: upload a document or paste text -> extract
# ---------------------------------------------------------------------------
@app.post("/api/extract", response_model=schemas.ExtractionResult)
async def extract_complaint(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    if not file and not text:
        raise HTTPException(400, "Provide either a file or pasted text.")

    if file:
        content = await file.read()
        raw_text = extract_text_from_upload(file.filename, content)
    else:
        raw_text = text

    if not raw_text or not raw_text.strip():
        raise HTTPException(422, "Could not extract any text from the input.")

    existing = _get_recent_complaints_for_duplicate_check(db)
    result = run_complaint_pipeline(raw_text, existing_complaints=existing)
    return _build_extraction_result(result)


# ---------------------------------------------------------------------------
# CRUD for the "Log Customer Complaint" form (left panel -> Save Complaint)
# ---------------------------------------------------------------------------
@app.post("/api/complaints", response_model=schemas.ComplaintOut)
def create_complaint(payload: schemas.ComplaintCreate, db: Session = Depends(get_db)):
    complaint = models.Complaint(**payload.model_dump())
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@app.get("/api/complaints", response_model=List[schemas.ComplaintOut])
def list_complaints(db: Session = Depends(get_db)):
    return db.query(models.Complaint).order_by(models.Complaint.created_at.desc()).all()


@app.get("/api/complaints/{complaint_id}", response_model=schemas.ComplaintOut)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    return complaint


@app.put("/api/complaints/{complaint_id}", response_model=schemas.ComplaintOut)
def update_complaint(complaint_id: str, payload: schemas.ComplaintCreate, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    for k, v in payload.model_dump().items():
        setattr(complaint, k, v)
    complaint.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(complaint)
    return complaint


@app.delete("/api/complaints/{complaint_id}")
def delete_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    db.delete(complaint)
    db.commit()
    return {"deleted": True}


# ---------------------------------------------------------------------------
# AI Assistant chat ("Ask me anything about this complaint...")
#
# Bonus feature: auto-fill-from-chat. If the message itself looks like new
# complaint data (rather than a question), it's routed through the same
# extraction pipeline as /api/extract, and the result is returned alongside
# the reply so the frontend can populate the form -- letting a reviewer
# paste or type a complaint directly into the chat box, not just the
# dedicated upload/paste panel.
# ---------------------------------------------------------------------------
@app.post("/api/chat", response_model=schemas.ChatResponse)
def chat(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    if classify_chat_intent(payload.message):
        existing = _get_recent_complaints_for_duplicate_check(db)
        result = run_complaint_pipeline(payload.message, existing_complaints=existing)
        extraction = _build_extraction_result(result)
        reply = (
            f"Got it — I've extracted the complaint details from your message and "
            f"updated the form (completeness {extraction.completeness_score}%, risk "
            f"classified as {extraction.risk_classification}). Please review and edit "
            f"before saving."
        )
        return schemas.ChatResponse(reply=reply, extraction=extraction)

    context = payload.context_text or ""
    if payload.complaint_id:
        complaint = db.query(models.Complaint).filter(models.Complaint.id == payload.complaint_id).first()
        if complaint:
            context = str(complaint.__dict__)

    system = (
        "You are the AI Complaint Intake Assistant inside a pharmaceutical QMS "
        "Customer Complaint Management System. Answer the user's question about "
        "the current complaint clearly and concisely, using the provided context. "
        "If information isn't in the context, say so rather than guessing."
    )
    user_prompt = f"COMPLAINT CONTEXT:\n{context}\n\nQUESTION:\n{payload.message}"
    reply = call_groq(
        system, user_prompt, model=REASONING_MODEL, json_mode=False,
        temperature=0.4, reasoning_effort="none",
    )
    return schemas.ChatResponse(reply=reply.strip())
