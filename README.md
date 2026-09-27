AIVOA.AI — AI-Powered Customer Complaint Management System

Created by Tanvi Sakhale

An AI-powered Customer Complaint Management System developed as part of the
AIVOA.AI Round 1 — AI Product Engineer (Fresher) assignment.

The system helps pharmaceutical quality teams capture, analyze, assess, and
manage customer complaints using an AI-assisted workflow.

🚀 Live Demo

🌐 Live Application

https://aivoa-complaint-system-plum.vercel.app/

📚 API Documentation

https://aivoa-complaint-system-08ca.onrender.com/docs

💻 GitHub Repository

https://github.com/tanvisakhale/aivoa-complaint-system

🎥 Demo Video

Coming Soon

📌 Project Overview

AIVOA.AI is an AI-assisted Customer Complaint Management System designed for
pharmaceutical manufacturing environments.

The application allows a reviewer to submit a complaint through uploaded
documents or pasted complaint text. The system uses an AI workflow to extract
structured information, analyze the complaint, classify risk, identify
potential duplicates, recommend possible root causes and CAPA actions, and
generate a complaint summary.

The reviewer can review and edit AI-generated information before saving the
complaint to the database.

🎯 Problem Statement

Pharmaceutical companies receive customer complaints through different
channels such as emails, documents, and written reports.

Manually processing these complaints can require significant effort to:

Read and understand complaint information

Extract important product and batch details

Check whether required information is available

Assess complaint risk

Identify possible duplicate complaints

Suggest potential root causes

Recommend CAPA actions

Prepare complaint summaries

AIVOA.AI provides an AI-assisted workflow to help organize and accelerate
these activities while keeping the reviewer in control of the final complaint.

✨ Key Features

1. AI Complaint Intake

Users can provide complaint information by uploading a complaint document or
pasting complaint text/email.

Supported formats:

PDF

DOCX

TXT

EML

2. AI-Powered Complaint Extraction

The AI extracts relevant complaint information and populates the complaint
form automatically, including customer, product, batch/lot, dates, quantity,
complaint details, assessment, and priority.

3. Complaint Completeness Checker

Checks complaint information and provides a completeness assessment.

4. AI Risk Classification

Provides AI-assisted risk classification based on complaint information.

5. Duplicate Complaint Detection

Identifies potential similar or repeated complaints.

6. Root Cause Recommendation

Provides possible root-cause suggestions.

7. CAPA Recommendation

Generates AI-assisted Corrective Action and Preventive Action recommendations.

8. Complaint Summary

Generates a concise complaint summary.

9. AI Assistant

Allows reviewers to ask follow-up questions about the complaint.

Example:

Summarize this complaint.

10. Complaint Management

Supports creating, viewing, updating, and deleting complaints. Data is
persisted in PostgreSQL.

🧠 AI Workflow

Complaint Input
      ↓
Document Parsing / Text Input
      ↓
AI Field Extraction
      ↓
Completeness Check
      ↓
Risk Classification
      ↓
Duplicate Detection
      ↓
Root Cause Recommendation
      ↓
CAPA Recommendation
      ↓
Complaint Summary
      ↓
Structured Complaint Form
      ↓
Reviewer Review / Edit
      ↓
PostgreSQL

🏗️ System Architecture

┌──────────────────────────────┐
│      React + Redux           │
│        Frontend              │
└──────────────┬───────────────┘
               │ Axios / REST API
               ↓
┌──────────────────────────────┐
│       Python FastAPI         │
│          Backend             │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       ↓                ↓
┌──────────────┐  ┌──────────────┐
│  LangGraph   │  │ PostgreSQL   │
│  AI Workflow │  │   Database   │
└──────┬───────┘  └──────────────┘
       ↓
┌──────────────┐
│   Groq LLM   │
└──────────────┘

🛠️ Technology Stack

Layer

Technology

Frontend

React

State Management

Redux Toolkit

Build Tool

Vite

Backend

Python + FastAPI

AI Agent Framework

LangGraph

LLM Provider

Groq

AI Model

qwen/qwen3.8-27b

Database

PostgreSQL

ORM

SQLAlchemy

API Client

Axios

Styling

CSS

Font

Google Inter

Frontend Deployment

Vercel

Backend Deployment

Render

📂 Project Structure

aivoa-complaint-system/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── langgraph_workflow.py
│   │   ├── groq_client.py
│   │   ├── document_parser.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── database.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ComplaintForm.jsx
│   │   │   └── AICopilot.jsx
│   │   ├── store/
│   │   └── api/
│   │       └── api.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
└── README.md

🔌 API Endpoints

Method

Endpoint

Description

GET

/

Backend health/root endpoint

POST

/api/extract

Extract complaint information

GET

/api/complaints

Get all complaints

POST

/api/complaints

Create a complaint

GET

/api/complaints/{complaint_id}

Get a specific complaint

PUT

/api/complaints/{complaint_id}

Update a complaint

DELETE

/api/complaints/{complaint_id}

Delete a complaint

POST

/api/chat

AI assistant

Swagger: https://aivoa-complaint-system-08ca.onrender.com/docs

🧪 Demo Test Data

From: qa.reviewer@pharmaclient.com

Subject: Product Complaint - Batch B4521

We received a complaint from a customer regarding Metformin HCl 500mg
Tablets, Batch/Lot B4521, manufactured 2025-11-02, expiring 2027-10-31.

The customer (Ramesh Distributors) reported visible black specks in
12 tablets out of a 100-tablet strip received on 2026-06-18.

This is being reported as a critical quality complaint requiring urgent
investigation.

Expected Demo Flow

Paste Complaint
      ↓
Click Extract
      ↓
AI Processes Complaint
      ↓
Complaint Fields Populated
      ↓
AI Analysis Displayed
      ↓
Review / Edit Information
      ↓
Save Complaint
      ↓
Complaint Stored in PostgreSQL
      ↓
Ask AI Assistant Questions

💻 Local Setup

Prerequisites

Python 3.12+

Node.js

npm

PostgreSQL

Backend

cd backend
python -m venv venv

Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Create .env from .env.example:

GROQ_API_KEY=your_groq_api_key
DATABASE_URL=your_database_url

Start the backend:

uvicorn app.main:app --reload --port 8000

Backend: http://localhost:8000

Swagger: http://localhost:8000/docs

Frontend

cd frontend
npm install
npm run dev

Open: http://localhost:5173

☁️ Deployment

Frontend — Vercel

https://aivoa-complaint-system-plum.vercel.app/

Backend — Render

https://aivoa-complaint-system-08ca.onrender.com/

API Documentation

https://aivoa-complaint-system-08ca.onrender.com/docs

Database

PostgreSQL with SQLAlchemy is used for persistent complaint storage.

🔐 Environment Variables

Sensitive credentials are not stored in the GitHub repository.

GROQ_API_KEY=
DATABASE_URL=

Never commit .env files, API keys, or database passwords to GitHub.

🎥 Demo Video

The demo video should demonstrate:

Project introduction

Opening the live application

Submitting a pharmaceutical complaint

AI extraction

AI analysis

Reviewing and editing the complaint

Saving the complaint

Viewing the saved complaint

Using the AI assistant

Brief technical architecture explanation

Technical flow:

React + Redux
      ↓
FastAPI
      ↓
LangGraph
      ↓
Groq LLM
      ↓
PostgreSQL

📋 Assignment Requirements Covered

React frontend

Redux Toolkit

FastAPI backend

LangGraph workflow

Groq LLM integration

Complaint document upload

Complaint text input

AI field extraction

Complaint completeness analysis

AI risk classification

Duplicate complaint detection

Root-cause recommendations

CAPA recommendations

Complaint summary

AI assistant

Complaint CRUD operations

PostgreSQL database

REST APIs

Swagger API documentation

Vercel deployment

Render deployment

⚠️ Notes

Production-grade OCR is not implemented.

Text-based PDF, DOCX, EML, and TXT documents are supported.

AI-generated results are intended to assist the reviewer and should be
reviewed before final submission.

This project was developed as part of the AIVOA.AI Round 1 AI Product
Engineer assignment.

👩‍💻 Author

Tanvi Sakhale

B.Sc. Computer Science Graduate

GitHub:
https://github.com/tanvisakhale

Live Project:
https://aivoa-complaint-system-plum.vercel.app/

⭐ AIVOA.AI

AI-Powered Customer Complaint Management System

Built with React, FastAPI, LangGraph, Groq, and PostgreSQL.
