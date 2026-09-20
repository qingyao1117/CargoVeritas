"""CargoVeritas shipping-document verification pipeline."""
from __future__ import annotations

import io
import json
import re
from pathlib import Path

from loader import Inbox

FIELDS = ("shipper", "consignee", "notify_party", "port_of_loading", "port_of_discharge", "container_count", "gross_weight_kg")


def classify_email(subject: str, body: str, attachment_names=()) -> str:
    """Route every email before any document work is attempted."""
    text = f"{subject}\n{body}".lower()
    names = " ".join(attachment_names).lower()
    has_si = bool(re.search(r"(?:^|[^a-z])si(?:[^a-z]|$)", names)) or "shipping instruction" in names
    has_bl = bool(re.search(r"(?:^|[^a-z])bl(?:[^a-z]|$)", names)) or "bill of lading" in names or "draft bl" in names
    if (has_si and has_bl) or ("draft" in text and (" bill of lading" in text or " bl" in text) and any(w in text for w in ("compare", "check", "confirm"))):
        return "BL_COMPARISON"
    if any(word in text for word in ("unsubscribe", "limited offer", "buy now", "promotion", "marketing")):
        return "SPAM"
    if any(word in text for word in ("invoice", "payment", "billing", "charge", "freight rate")):
        return "INVOICE_QUERY"
    if any(word in text for word in ("shipping instruction", "submit si", "amend si", "prepare si")):
        return "SI_REQUEST"
    return "GENERAL"


def extract_text_from_bytes(raw: bytes, filename: str) -> str:
    """Read TXT/PDF/DOCX/XLSX attachments; return empty text when unreadable."""
    suffix = Path(filename).suffix.lower()
    try:
        if suffix in (".txt", ".csv"):
            return raw.decode("utf-8", errors="replace")
        if suffix == ".pdf":
            from pypdf import PdfReader
            return "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(raw)).pages)
        if suffix == ".docx":
            import docx
            doc = docx.Document(io.BytesIO(raw))
            return "\n".join([p.text for p in doc.paragraphs] + [" | ".join(c.text for c in row.cells) for table in doc.tables for row in table.rows])
        if suffix == ".xlsx":
            import openpyxl
            book = openpyxl.load_workbook(io.BytesIO(raw), data_only=True)
            return "\n".join(" | ".join(str(v) for v in row if v is not None) for sheet in book.worksheets for row in sheet.iter_rows(values_only=True))
    except Exception:
        return ""
    return ""


def _label_value(text: str, labels) -> str | None:
    for label in labels:
        match = re.search(r"(?im)^\s*" + label + r"\s*[:\-]\s*(.+?)\s*$", text)
        if match:
            return match.group(1).strip()
    return None


def extract_fields_from_doc(text: str) -> dict:
    """Extract exactly the seven mandatory values; unknown values remain null."""
    result = {field: None for field in FIELDS}
    result["shipper"] = _label_value(text, (r"shipper(?:/exporter)?",))
    result["consignee"] = _label_value(text, (r"consignee",))
    result["notify_party"] = _label_value(text, (r"notify(?:\s+party)?",))
    result["port_of_loading"] = _label_value(text, (r"port\s+of\s+loading(?:\s*\(pol\))?", r"load(?:ing)?\s+port", r"pol"))
    result["port_of_discharge"] = _label_value(text, (r"port\s+of\s+discharge", r"discharge\s+port", r"pod"))
    containers = _label_value(text, (r"(?:no\.\s+of\s+)?containers?(?:\s+or\s+packages)?", r"container\s+count"))
    weight = _label_value(text, (r"gross\s*(?:weight|wt)(?:\s*\(kgs?\))?",))
    if containers:
        number = re.search(r"\d+", containers.replace(",", ""))
        result["container_count"] = int(number.group()) if number else None
    if weight:
        number = re.search(r"\d[\d,]*(?:\.\d+)?", weight)
        result["gross_weight_kg"] = float(number.group().replace(",", "")) if number else None
    return result


def _normal_text(value) -> str:
    return " ".join(re.sub(r"[^a-z0-9]", " ", str(value or "").lower()).split())


def _normal_port(value) -> str:
    text = _normal_text(value)
    aliases = {"port klang": "mypkg", "pkg": "mypkg", "mypkg": "mypkg", "callao": "pecll", "pecll": "pecll"}
    return next((code for name, code in aliases.items() if name in text), text)


def compare_fields(si_data: dict, bl_data: dict) -> list[str]:
    """Compare all fields after normalizing harmless formatting differences."""
    defects = []
    for field in FIELDS:
        si, bl = si_data.get(field), bl_data.get(field)
        if field == "container_count":
            same = int(si) == int(bl)
        elif field == "gross_weight_kg":
            same = abs(float(si) - float(bl)) < 0.01
        elif field in ("port_of_loading", "port_of_discharge"):
            same = _normal_port(si) == _normal_port(bl)
        else:
            same = _normal_text(si) == _normal_text(bl)
        if not same:
            defects.append(field)
    return defects


def process_email(email: dict, attachment_texts: dict[str, str]) -> dict:
    """Return the structured category, extraction, comparison, and review record."""
    attachments = list(attachment_texts)
    category = classify_email(email.get("subject", ""), email.get("body", ""), attachments)
    result = {"category": category, "status": "AUTO_RESOLVED", "review_reason": None, "defect_fields": [], "si_data": {}, "bl_data": {}}
    if category != "BL_COMPARISON":
        return result
    si_name = next((name for name in attachments if re.search(r"(?:^|[^a-z])si(?:[^a-z]|$)", name.lower()) or "shipping instruction" in name.lower()), None)
    bl_name = next((name for name in attachments if re.search(r"(?:^|[^a-z])bl(?:[^a-z]|$)", name.lower()) or "bill of lading" in name.lower() or "draft bl" in name.lower()), None)
    if not si_name or not bl_name:
        result.update(status="NEEDS_REVIEW", review_reason="missing_attachment")
        return result
    if not attachment_texts[si_name].strip() or not attachment_texts[bl_name].strip():
        result.update(status="NEEDS_REVIEW", review_reason="unreadable_document")
        return result
    si_data, bl_data = extract_fields_from_doc(attachment_texts[si_name]), extract_fields_from_doc(attachment_texts[bl_name])
    result.update(si_data=si_data, bl_data=bl_data)
    if any(si_data[field] is None or bl_data[field] is None for field in FIELDS):
        result.update(status="NEEDS_REVIEW", review_reason="unreadable_document")
        return result
    defects = compare_fields(si_data, bl_data)
    result.update(status="MISMATCH" if defects else "OK", defect_fields=defects)
    return result


def inspect_email(email_record: dict, inbox: Inbox) -> dict:
    texts = {path: extract_text_from_bytes(inbox.read_bytes(path), path) for path in email_record.get("attachments", [])}
    return process_email(email_record, texts)


if __name__ == "__main__":
    inbox = Inbox(".")
    output = {email["email_id"]: inspect_email(email, inbox) for email in inbox}
    Path("submission.json").write_text(json.dumps(output, indent=2), encoding="utf-8")

