"""
LangGraph AI Agent workflow for the Customer Complaint Intake Assistant.

Pipeline:
  extract_fields -> completeness_check -> classify_risk ->
  duplicate_check -> root_cause_and_capa -> summarize -> END

Each node calls Groq (gemma2-9b-it for fast/structured steps,
llama-3.3-70b-versatile for reasoning-heavy steps) and updates a
shared state dict that is threaded through the graph.

Created by Tanvi Sakhale
"""
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END

from app.groq_client import call_groq_json, FAST_MODEL, REASONING_MODEL

REQUIRED_FIELDS = [
    "complaint_source", "customer_name", "product_name", "product_strength_grade",
    "batch_lot_number", "manufacturing_date", "expiry_date", "quantity_affected",
    "complaint_type", "complaint_date", "detailed_complaint_description",
    "initial_severity", "priority",
]


class ComplaintState(TypedDict, total=False):
    raw_text: str
    existing_complaints: List[dict]   # for duplicate detection, passed in by caller
    fields: dict
    completeness_score: float
    missing_fields: List[str]
    risk_classification: str
    root_cause_suggestions: List[str]
    capa_suggestions: List[str]
    summary: str
    duplicate_of: Optional[str]
    duplicate_confidence: Optional[float]


# ---------------------------------------------------------------------------
# Node 1: Extract structured fields from raw complaint text
# ---------------------------------------------------------------------------
def extract_fields(state: ComplaintState) -> ComplaintState:
    system = (
        "You are an AI assistant for a pharmaceutical Quality Management System (QMS). "
        "Extract structured customer-complaint data from the given text. "
        "Respond ONLY with a JSON object with these exact keys (use null if not found): "
        "complaint_source, customer_name, product_name, product_strength_grade, "
        "batch_lot_number, manufacturing_date (YYYY-MM-DD), expiry_date (YYYY-MM-DD), "
        "quantity_affected, complaint_type, complaint_date (YYYY-MM-DD), "
        "detailed_complaint_description, initial_severity (Low/Medium/High/Critical), "
        "priority (Low/Medium/High/Urgent)."
    )
    data = call_groq_json(system, state["raw_text"], model=FAST_MODEL)
    fields = {k: data.get(k) for k in REQUIRED_FIELDS}
    return {"fields": fields}


# ---------------------------------------------------------------------------
# Node 2: Complaint Completeness Checker (bonus feature)
# ---------------------------------------------------------------------------
def completeness_check(state: ComplaintState) -> ComplaintState:
    fields = state["fields"]
    missing = [f for f in REQUIRED_FIELDS if not fields.get(f)]
    score = round((len(REQUIRED_FIELDS) - len(missing)) / len(REQUIRED_FIELDS) * 100, 1)
    return {"completeness_score": score, "missing_fields": missing}


# ---------------------------------------------------------------------------
# Node 3: AI Risk Classification (bonus feature)
# ---------------------------------------------------------------------------
def risk_classification(state: ComplaintState) -> ComplaintState:
    system = (
        "You are a pharma QMS risk assessor. Given complaint details, classify the "
        "overall product risk. Respond ONLY with JSON: "
        '{"risk_classification": "Critical|Major|Minor"}'
    )
    user = str(state["fields"])
    data = call_groq_json(system, user, model=FAST_MODEL)
    return {"risk_classification": data.get("risk_classification", "Minor")}


# ---------------------------------------------------------------------------
# Node 4: Duplicate Complaint Detection (bonus feature)
# ---------------------------------------------------------------------------
def duplicate_check(state: ComplaintState) -> ComplaintState:
    existing = state.get("existing_complaints") or []
    if not existing:
        return {"duplicate_of": None, "duplicate_confidence": None}

    system = (
        "You detect duplicate pharmaceutical complaints. Given a NEW complaint and a "
        "list of EXISTING complaints (each with an id), decide if the new one is a "
        "likely duplicate of any existing one (same product/batch/issue). "
        'Respond ONLY with JSON: {"duplicate_of": "<id or null>", "confidence": 0.0}'
    )
    user = f"NEW COMPLAINT:\n{state['fields']}\n\nEXISTING COMPLAINTS:\n{existing}"
    data = call_groq_json(system, user, model=FAST_MODEL)
    return {
        "duplicate_of": data.get("duplicate_of"),
        "duplicate_confidence": data.get("confidence"),
    }


# ---------------------------------------------------------------------------
# Node 5: Root Cause Recommendation + CAPA Recommendation (bonus features)
# ---------------------------------------------------------------------------
def root_cause_and_capa(state: ComplaintState) -> ComplaintState:
    system = (
        "You are a pharmaceutical quality engineer. Given complaint details, suggest "
        "likely root causes and CAPA (Corrective and Preventive Action) recommendations. "
        'Respond ONLY with JSON: {"root_causes": ["...", "..."], "capa": ["...", "..."]}'
    )
    user = str(state["fields"])
    data = call_groq_json(system, user, model=REASONING_MODEL, reasoning_effort="default")
    return {
        "root_cause_suggestions": data.get("root_causes", []),
        "capa_suggestions": data.get("capa", []),
    }


# ---------------------------------------------------------------------------
# Node 6: Complaint Summary (bonus feature)
# ---------------------------------------------------------------------------
def summarize(state: ComplaintState) -> ComplaintState:
    system = (
        "Summarize the pharmaceutical customer complaint in 2-3 concise sentences "
        'for a QA reviewer. Respond ONLY with JSON: {"summary": "..."}'
    )
    user = str(state["fields"])
    data = call_groq_json(system, user, model=REASONING_MODEL)
    return {"summary": data.get("summary", "")}


def build_graph():
    graph = StateGraph(ComplaintState)
    graph.add_node("extract_fields", extract_fields)
    graph.add_node("completeness_check", completeness_check)
    graph.add_node("classify_risk", risk_classification)
    graph.add_node("duplicate_check", duplicate_check)
    graph.add_node("root_cause_and_capa", root_cause_and_capa)
    graph.add_node("summarize", summarize)

    graph.set_entry_point("extract_fields")
    graph.add_edge("extract_fields", "completeness_check")
    graph.add_edge("completeness_check", "classify_risk")
    graph.add_edge("classify_risk", "duplicate_check")
    graph.add_edge("duplicate_check", "root_cause_and_capa")
    graph.add_edge("root_cause_and_capa", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()


complaint_graph = build_graph()


def run_complaint_pipeline(raw_text: str, existing_complaints: Optional[List[dict]] = None) -> dict:
    """Entry point used by the FastAPI route."""
    initial_state: ComplaintState = {
        "raw_text": raw_text,
        "existing_complaints": existing_complaints or [],
    }
    result = complaint_graph.invoke(initial_state)
    return result
