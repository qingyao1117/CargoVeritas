import io
import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import docx
import openpyxl
from loader import Inbox

# Load secret key from .env file
load_dotenv()
client = OpenAI()

# ---------------------------------------------------------
# 1. Attachment Reader (Multi-format)
# ---------------------------------------------------------
def extract_file_content(inbox: Inbox, att_path: str) -> str:
    try:
        raw_bytes = inbox.read_bytes(att_path)
    except Exception:
        return ""

    ext = Path(att_path).suffix.lower()

    if ext == ".txt":
        return raw_bytes.decode("utf-8", errors="replace")

    elif ext == ".pdf":
        try:
            reader = PdfReader(io.BytesIO(raw_bytes))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            return ""

    elif ext == ".docx":
        try:
            doc = docx.Document(io.BytesIO(raw_bytes))
            paras = [p.text for p in doc.paragraphs]
            table_lines = []
            for table in doc.tables:
                for row in table.rows:
                    table_lines.append(" | ".join(cell.text.strip() for cell in row.cells))
            return "\n".join(paras + table_lines)
        except Exception:
            return ""

    elif ext == ".xlsx":
        try:
            wb = openpyxl.load_workbook(io.BytesIO(raw_bytes), data_only=True)
            lines = []
            for sheet in wb.worksheets:
                for row in sheet.iter_rows(values_only=True):
                    row_vals = [str(v).strip() for v in row if v is not None]
                    if row_vals:
                        lines.append(" | ".join(row_vals))
            return "\n".join(lines)
        except Exception:
            return ""

    return raw_bytes.decode("utf-8", errors="replace")

# ---------------------------------------------------------
# 2. Step 1: Email Classification
# ---------------------------------------------------------
def classify_email(subject: str, body: str) -> str:
    prompt = f"""You are an email triage assistant for a shipping company.
Classify this email into exactly ONE category:
- BL_COMPARISON: Requests to verify, compare, or check a draft Bill of Lading (BL) against a Shipping Instruction (SI).
- SI_REQUEST: Inquiries or requests to create, draft, submit, or amend a Shipping Instruction.
- INVOICE_QUERY: Questions or billing updates regarding rates, invoices, charges, or payments.
- GENERAL: General operational notices, greetings, schedule updates, logistics announcements.
- SPAM: Unsolicited marketing, junk, irrelevant offers.

Subject: {subject}
Body: {body}

Respond with valid JSON: {{"category": "<CATEGORY>"}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        data = json.loads(response.choices[0].message.content)
        cat = data.get("category", "GENERAL").upper().strip()
        valid = {"BL_COMPARISON", "SI_REQUEST", "INVOICE_QUERY", "GENERAL", "SPAM"}
        return cat if cat in valid else "GENERAL"
    except Exception:
        return "GENERAL"

# ---------------------------------------------------------
# 3. Document 7-Field Extractor (Refined)
# ---------------------------------------------------------
def extract_fields_from_doc(doc_text: str, doc_name: str) -> dict:
    prompt = f"""Extract the following 7 shipping fields from this {doc_name}.

Rules:
- For 'shipper', 'consignee', and 'notify_party': Extract ONLY the company or person name. Do NOT include addresses, phone numbers, emails, or postal codes.
- For 'port_of_loading' and 'port_of_discharge': Extract the primary port name or UN/LOCODE (e.g. 'PORT KLANG' or 'CALLAO').
- For 'container_count': Extract the integer number of containers (e.g. '1 x 40HC' -> 1, '2x20FT' -> 2).
- For 'gross_weight_kg': Extract the numeric weight in kilograms as a float (e.g. '21,577 KG' -> 21577.0).

Document Text:
{doc_text[:4000]}

Return valid JSON with exact keys:
{{
  "shipper": string or null,
  "consignee": string or null,
  "notify_party": string or null,
  "port_of_loading": string or null,
  "port_of_discharge": string or null,
  "container_count": integer or null,
  "gross_weight_kg": float or null
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {}

# ---------------------------------------------------------
# 4. Deterministic Field Comparator (Robust to Formatting)
# ---------------------------------------------------------
def normalize_text(val) -> str:
    if not val:
        return ""
    text = str(val).lower()
    text = re.sub(r"[,\.\-\/\\#\(\);:]", " ", text)
    text = re.sub(r"\b(sdn|bhd|ltd|limited|inc|corp|co|pte)\b", "", text)
    return " ".join(text.split())

def is_text_match(s1: str, s2: str) -> bool:
    n1 = normalize_text(s1)
    n2 = normalize_text(s2)
    
    if not n1 and not n2:
        return True
    if not n1 or not n2:
        return False
    if n1 == n2:
        return True

    # Token overlap check (Jaccard similarity)
    tokens1 = set(n1.split())
    tokens2 = set(n2.split())
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2

    jaccard = len(intersection) / len(union) if union else 0.0
    # Match if >= 75% overlap or one name contains the other
    return jaccard >= 0.75 or n1 in n2 or n2 in n1

def compare_fields(si_fields: dict, bl_fields: dict) -> list:
    defects = []
    
    # 1. Text comparisons
    str_fields = ["shipper", "consignee", "notify_party", "port_of_loading", "port_of_discharge"]
    for field in str_fields:
        si_val = si_fields.get(field)
        bl_val = bl_fields.get(field)
        if si_val and bl_val:
            if not is_text_match(si_val, bl_val):
                defects.append(field)

    # 2. Container count (numeric match)
    si_cnt = si_fields.get("container_count")
    bl_cnt = bl_fields.get("container_count")
    if si_cnt is not None and bl_cnt is not None:
        try:
            if int(si_cnt) != int(bl_cnt):
                defects.append("container_count")
        except (ValueError, TypeError):
            if str(si_cnt).strip() != str(bl_cnt).strip():
                defects.append("container_count")

    # 3. Gross weight (float within 1.0 kg tolerance)
    si_wt = si_fields.get("gross_weight_kg")
    bl_wt = bl_fields.get("gross_weight_kg")
    if si_wt is not None and bl_wt is not None:
        try:
            if abs(float(si_wt) - float(bl_wt)) > 1.0:
                defects.append("gross_weight_kg")
        except (ValueError, TypeError):
            if str(si_wt).strip() != str(bl_wt).strip():
                defects.append("gross_weight_kg")

    return defects

# ---------------------------------------------------------
# 5. Full Inspection Pipeline
# ---------------------------------------------------------
def inspect_email(email_record: dict, inbox: Inbox) -> dict:
    subject = email_record.get("subject", "")
    body = email_record.get("body", "")
    attachments = email_record.get("attachments", [])

    category = classify_email(subject, body)

    # Baseline for non-comparison emails
    result = {
        "category": category,
        "status": "OK",
        "review_reason": None,
        "defect_fields": [],
        "has_defect": False
    }

    if category != "BL_COMPARISON":
        return result

    # Identify SI and BL attachments
    si_att = next((a for a in attachments if "_SI" in a.upper()), None)
    bl_att = next((a for a in attachments if "_BL" in a.upper()), None)

    # Reliability: missing attachment
    if not si_att or not bl_att:
        result["status"] = "NEEDS_REVIEW"
        result["review_reason"] = "missing_attachment"
        return result

    si_text = extract_file_content(inbox, si_att)
    bl_text = extract_file_content(inbox, bl_att)

    # Reliability: unreadable attachment
    if not si_text.strip() or not bl_text.strip():
        result["status"] = "NEEDS_REVIEW"
        result["review_reason"] = "unreadable"
        return result

    # Extract 7 fields
    si_fields = extract_fields_from_doc(si_text, "Shipping Instruction")
    bl_fields = extract_fields_from_doc(bl_text, "Bill of Lading")

    # Reliability: missing critical values in documents
    critical_fields = ["shipper", "consignee", "port_of_loading", "port_of_discharge"]
    if any(not si_fields.get(f) or not bl_fields.get(f) for f in critical_fields):
        result["status"] = "NEEDS_REVIEW"
        result["review_reason"] = "missing_value"
        return result

    # Compare
    defects = compare_fields(si_fields, bl_fields)
    
    if len(defects) > 0:
        result["status"] = "MISMATCH"
        result["has_defect"] = True
        result["defect_fields"] = defects
    else:
        result["status"] = "OK"
        result["has_defect"] = False
        result["defect_fields"] = []

    return result

# ---------------------------------------------------------
# 6. Main Runner
# ---------------------------------------------------------
def main():
    inbox = Inbox(".")
    
    # Initialize with sample_submission.json so all 520 records remain present
    with open("sample_submission.json", "r", encoding="utf-8") as f:
        submission = json.load(f)

    # Test limit: Change to None when running the complete 520 inbox
    test_limit = None
    print(f"Starting inspection (limit={test_limit})...")

    for i, email in enumerate(inbox):
        if test_limit and i >= test_limit:
            break
        eid = email["email_id"]
        print(f"[{i+1}] Processing {eid}...")
        submission[eid] = inspect_email(email, inbox)

    with open("submission.json", "w", encoding="utf-8") as f:
        json.dump(submission, f, indent=2)

    print("Finished! Output saved to submission.json")

if __name__ == "__main__":
    main()