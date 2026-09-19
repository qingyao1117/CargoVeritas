import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

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