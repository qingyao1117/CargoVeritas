import json
from db import supabase

with open("submission.json", "r", encoding="utf-8") as f:
    submission = json.load(f)

records_to_insert = []
for eid, item in submission.items():
    records_to_insert.append({
        "email_id": eid,
        "category": item.get("category"),
        "status": item.get("status"),
        "review_reason": item.get("review_reason"),
        "defect_fields": item.get("defect_fields", []),
        "operator_action": "PENDING" if item.get("status") in ["MISMATCH", "NEEDS_REVIEW"] else "AUTO_APPROVED"
    })

# Batch insert in chunks of 100
chunk_size = 100
for i in range(0, len(records_to_insert), chunk_size):
    chunk = records_to_insert[i:i + chunk_size]
    supabase.table("email_verifications").upsert(chunk).execute()
    print(f"Uploaded chunk {i} to {i + len(chunk)}...")

print("Database seeding complete!")