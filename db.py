import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("db.py requires SUPABASE_URL and server-only SUPABASE_SECRET_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upsert_verification(record: dict):
    """Insert or update an email verification record."""
    response = supabase.table("email_verifications").upsert(record).execute()
    return response

def fetch_all_records():
    """Retrieve all verification records ordered by creation."""
    response = supabase.table("email_verifications").select("*").order("created_at", desc=True).execute()
    return response.data or []

def update_operator_action(email_id: str, action: str, notes: str = ""):
    """Record human sign-off or escalation in the database."""
    response = supabase.table("email_verifications").update({
        "operator_action": action,
        "operator_notes": notes,
        "status": "RESOLVED" if action == "APPROVED" else "REJECTED_TO_CARRIER"
    }).eq("email_id", email_id).execute()
    return response

def upsert_gmail_verification(record: dict):
    """Persist the structured Gmail pipeline result, never raw OAuth credentials."""
    return supabase.table("gmail_messages").upsert(record, on_conflict="gmail_message_id").execute()

