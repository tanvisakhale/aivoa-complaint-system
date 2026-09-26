# AIVOA.AI — AI-Powered Customer Complaint Management System

**Created by Tanvi Sakhale**

Round 1 assignment submission for AIVOA.AI — AI Product Engineer (Fresher).
An AI-assisted Customer Complaint Management module for a pharmaceutical
Quality Management System (QMS), covering API and Finished Dosage Form (FDF)
complaints.

## What it does

1. A reviewer drags & drops a complaint document (PDF/DOCX/TXT/EML) or pastes
   complaint text/email into the **AI Complaint Intake Assistant** panel.
2. The backend runs a **LangGraph** agent pipeline (`extract_fields →
   completeness_check → risk_classification → duplicate_check →
   root_cause_and_capa → summarize`) using **Groq** (`gemma2-9b-it` for fast
   structured extraction, `llama-3.3-70b-versatile` for reasoning steps).
3. The extracted fields auto-populate the **Log Customer Complaint** form
   (Origin & Customer, Product & Batch, Complaint Details, Initial Assessment
   & Priority).
4. The AI panel also surfaces the bonus features: completeness score,
   AI risk classification, duplicate complaint detection, root cause
   suggestions, CAPA recommendations, and a complaint summary — plus a
   chat box to ask follow-up questions about the complaint.
5. The reviewer can edit any field and click **Save Complaint** to persist it.

## Tech stack (per assignment spec)

| Layer            | Choice                                   |
|-------------------|-------------------------------------------|
| Frontend          | React + Redux Toolkit (Vite)             |
| Backend           | Python + FastAPI                          |
| AI agent framework| LangGraph                                 |
| LLMs              | Groq — `gemma2-9b-it`, `llama-3.3-70b-versatile` |
| Database          | PostgreSQL or MySQL (SQLAlchemy)          |
| Font              | Google Inter                              |

## Project structure

```
aivoa-complaint-system/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI routes
│   │   ├── langgraph_workflow.py # LangGraph AI agent pipeline
│   │   ├── groq_client.py        # Groq API wrapper
│   │   ├── document_parser.py    # PDF/DOCX/EML/TXT text extraction
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── schemas.py            # Pydantic schemas
│   │   └── database.py           # DB session setup
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   │   ├── ComplaintForm.jsx  # Left panel — the complaint form
    │   │   └── AICopilot.jsx      # Right panel — AI intake assistant
    │   ├── store/                # Redux Toolkit slice + store
    │   └── api/api.js            # Axios API client
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## Setup

### 1. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # then fill in GROQ_API_KEY and DATABASE_URL
uvicorn app.main:app --reload --port 8000
```

Get a free Groq API key at https://console.groq.com.
Create a Postgres or MySQL database matching your `DATABASE_URL` before
starting the server — tables are auto-created on first run.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173. Vite proxies `/api` calls to the backend on
port 8000 (see `vite.config.js`).

## Demo data

Create a realistic pharma complaint email/PDF like:

```
From: qa.reviewer@pharmaclient.com
Subject: Product Complaint - Batch B4521

We received a complaint from a customer regarding Metformin HCl 500mg
Tablets, Batch/Lot B4521, manufactured 2025-11-02, expiring 2027-10-31.
The customer (Ramesh Distributors) reported visible black specks in
12 tablets out of a 100-tablet strip received on 2026-06-18. This is
being reported as a critical quality complaint requiring urgent
investigation.
```

Paste this into the AI Assistant panel to see the full extraction →
completeness → risk classification → root cause/CAPA → summary pipeline
run end-to-end.

## Notes

- Production-grade OCR is not implemented per the assignment brief —
  text-based PDFs/DOCX/EML/TXT are supported, which covers the demonstrated
  workflow.
- Bonus AI features implemented: Complaint Completeness Checker, Root Cause
  Recommendation, Duplicate Complaint Detection, CAPA Recommendation,
  Complaint Summary, and AI Risk Classification.
