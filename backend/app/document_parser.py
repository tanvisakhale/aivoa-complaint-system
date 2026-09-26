"""
Lightweight document text extraction (PDF, DOCX, TXT, EML, plain text).
Production-grade OCR is explicitly not required per the assignment brief,
so this favors simplicity: get plain text out, then let the LLM do the
structured extraction.

Created by Tanvi Sakhale
"""
import email
from io import BytesIO

from pypdf import PdfReader
import docx2txt


def extract_text_from_upload(filename: str, content: bytes) -> str:
    lower = filename.lower()

    if lower.endswith(".pdf"):
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if lower.endswith(".docx"):
        # docx2txt needs a path-like or file-like object
        return docx2txt.process(BytesIO(content))

    if lower.endswith(".eml"):
        msg = email.message_from_bytes(content)
        parts = []
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    parts.append(part.get_payload(decode=True).decode(errors="ignore"))
        else:
            parts.append(msg.get_payload(decode=True).decode(errors="ignore"))
        subject = msg.get("Subject", "")
        sender = msg.get("From", "")
        return f"From: {sender}\nSubject: {subject}\n\n" + "\n".join(parts)

    # .txt or anything else: assume plain text
    return content.decode(errors="ignore")
