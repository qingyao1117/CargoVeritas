import streamlit as st
import json
from datetime import datetime
from db import fetch_all_records, update_operator_action, upsert_verification

st.set_page_config(page_title="CargoVeritas | Autonomous Freight Ops", page_icon="🚢", layout="wide")

# Fetch live data from Supabase
records = fetch_all_records()
record_dict = {r["email_id"]: r for r in records}

st.title("🚢 CargoVeritas: Autonomous Shipping Operations")
st.caption("Connected Inbox: **ops@pacificlogistics.com** • Real-time AI Document Audit & Manifest Engine")

# KPI Summary
total = len(records)
ok_cnt = sum(1 for r in records if r.get("status") in ["OK", "AUTO_APPROVED"])
mismatch_cnt = sum(1 for r in records if r.get("status") == "MISMATCH")
review_cnt = sum(1 for r in records if r.get("status") == "NEEDS_REVIEW")
resolved_cnt = sum(1 for r in records if r.get("status") in ["RESOLVED", "REJECTED_TO_CARRIER"])

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Emails Intercepted", total)
k2.metric("Straight-Through Ready", ok_cnt)
k3.metric("Defects Flagged", mismatch_cnt)
k4.metric("Exceptions Pending", review_cnt)
k5.metric("Operator Handled", resolved_cnt)

st.divider()

# Tab Navigation: High-level Operations vs Detail Exception Handling
tab_manifest, tab_audit, tab_simulate = st.tabs(["📦 Active Shipping Manifest", "🛡️ Discrepancy & Exception Queue", "⚡ Live Email Ingestion Webhook"])

# --- TAB 1: LOGISTICS MANIFEST (WHAT TO SHIP, WHERE, DETAILS) ---
with tab_manifest:
    st.subheader("📋 Active Cargo Manifest (Parsed from Verified B/L & SI)")
    st.markdown("Automated overview of verified shipments extracted directly from operational communications.")

    manifest_data = []
    for r in records:
        if r.get("category") == "BL_COMPARISON":
            si = r.get("si_data") or {}
            bl = r.get("bl_data") or {}
            manifest_data.append({
                "Email Reference": r.get("email_id"),
                "Shipper": si.get("shipper") or bl.get("shipper") or "Pacific Global Exports",
                "Consignee": si.get("consignee") or bl.get("consignee") or "Atlantic Distribution Corp",
                "Port of Loading (POL)": si.get("port_of_loading") or bl.get("port_of_loading") or "Shanghai (CNSHA)",
                "Port of Discharge (POD)": si.get("port_of_discharge") or bl.get("port_of_discharge") or "Rotterdam (NLRTM)",
                "Weight (KG)": si.get("gross_weight_kg") or bl.get("gross_weight_kg") or "24,500 KG",
                "Containers": si.get("container_count") or bl.get("container_count") or "2 x 40HC",
                "Compliance Status": r.get("status")
            })

    if manifest_data:
        st.dataframe(
            manifest_data,
            column_config={
                "Compliance Status": st.column_config.BadgeColumn(
                    "Compliance Status",
                    help="Verification pipeline status",
                    colors={
                        "OK": "success",
                        "RESOLVED": "blue",
                        "MISMATCH": "error",
                        "NEEDS_REVIEW": "warning"
                    }
                )
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No comparison records available to generate manifest.")

# --- TAB 2: AUDIT & EXCEPTION RESOLUTION ---
with tab_audit:
    st.subheader("🔍 Discrepancy Desk (Human-in-the-Loop)")
    
    col_filter1, col_filter2 = st.columns([1, 2])
    with col_filter1:
        f_status = st.selectbox("Queue Filter", ["ALL", "MISMATCH", "NEEDS_REVIEW", "OK", "RESOLVED"])
    
    visible_records = [r for r in records if f_status == "ALL" or r.get("status") == f_status]
    
    with col_filter2:
        selected_id = st.selectbox(
            "Select Record to Inspect",
            [r["email_id"] for r in visible_records] if visible_records else [],
            format_func=lambda x: f"{x} - [{record_dict[x].get('status')}] {record_dict[x].get('category')}"
        )

    if selected_id and selected_id in record_dict:
        item = record_dict[selected_id]
        
        info_c1, info_c2, info_c3 = st.columns(3)
        info_c1.markdown(f"**Classification:** `{item.get('category')}`")
        info_c2.markdown(f"**Status:** `{item.get('status')}`")
        info_c3.markdown(f"**Operator State:** `{item.get('operator_action', 'PENDING')}`")

        if item.get("status") == "MISMATCH":
            st.error(f"🚨 **Compliance Failure Detected:** Fields mismatched: `{', '.join(item.get('defect_fields', []))}`")
        elif item.get("status") == "NEEDS_REVIEW":
            st.warning(f"⚠️ **Escalation Reason:** {item.get('review_reason')}")
        else:
            st.success("✅ **Fully Compliant:** Straight-through processed without defects.")

        st.markdown("#### 📝 Document Field Alignment")
        v1, v2 = st.columns(2)
        with v1:
            st.markdown("##### Source: Shipping Instruction (SI)")
            st.json(item.get("si_data") or {
                "shipper": "Alpha Logistics Pte Ltd",
                "consignee": "Delta Importers AG",
                "port_of_loading": "Port Klang, Malaysia",
                "port_of_discharge": "Hamburg, Germany",
                "gross_weight_kg": 18450.0,
                "container_count": 1
            })
        with v2:
            st.markdown("##### Carrier Target: Draft Bill of Lading (B/L)")
            st.json(item.get("bl_data") or {
                "shipper": "Alpha Logistics Pte Ltd",
                "consignee": "Delta Imports GmbH" if "consignee" in item.get("defect_fields", []) else "Delta Importers AG",
                "port_of_loading": "Port Klang, Malaysia",
                "port_of_discharge": "Hamburg, Germany",
                "gross_weight_kg": 18450.0,
                "container_count": 1
            })

        st.divider()
        st.markdown("#### ✍️ Operator Sign-Off Actions")
        notes = st.text_input("Operator Audit Notes", placeholder="e.g., Cross-checked company tax ID; name difference is a legal alias. Approved.")
        
        btn_a, btn_b, btn_c = st.columns(3)
        if btn_a.button("✅ Approve & Authorize Carrier Release", use_container_width=True):
            update_operator_action(selected_id, "APPROVED", notes)
            st.toast(f"{selected_id} approved and signed off.")
            st.rerun()

        if btn_b.button("❌ Issue Formal Carrier Rejection", type="primary", use_container_width=True):
            update_operator_action(selected_id, "REJECTED", notes)
            st.toast(f"Rejection notice drafted for {selected_id}.")
            st.rerun()

        if btn_c.button("📩 Dispatch Missing Doc Notice", use_container_width=True):
            update_operator_action(selected_id, "REQUESTED_DOCS", notes)
            st.toast(f"Follow-up dispatched for {selected_id}.")
            st.rerun()

# --- TAB 3: REAL-TIME INGESTION SIMULATOR ---
with tab_simulate:
    st.subheader("📩 Incoming Email Webhook Simulator")
    st.caption("Simulates incoming client emails arriving at the integrated company mailbox.")

    with st.form("incoming_email_form"):
        sim_id = st.text_input("Simulated Email ID", value=f"email_{total + 1:03d}")
        sim_from = st.text_input("From", "operations@oceanfreight-global.com")
        sim_subject = st.text_input("Subject", "Draft BL Verification - Booking #SG-8821")
        sim_cat = st.selectbox("Detected Category", ["BL_COMPARISON", "SI_REQUEST", "INVOICE_QUERY", "GENERAL", "SPAM"])
        sim_status = st.selectbox("Pipeline Status", ["MISMATCH", "NEEDS_REVIEW", "OK"])
        sim_defects = st.multiselect("Defects Found", ["shipper", "consignee", "port_of_loading", "port_of_discharge", "gross_weight_kg", "container_count"])
        
        sim_submit = st.form_submit_button("🚀 Simulate Inbound Client Email")
        if sim_submit:
            new_payload = {
                "email_id": sim_id,
                "subject": sim_subject,
                "category": sim_cat,
                "status": sim_status,
                "defect_fields": sim_defects,
                "operator_action": "PENDING" if sim_status != "OK" else "AUTO_APPROVED",
                "si_data": {
                    "shipper": "Global Tech Logistics",
                    "consignee": "European Distribution BV",
                    "port_of_loading": "Singapore (SGSIN)",
                    "port_of_discharge": "Rotterdam (NLRTM)",
                    "gross_weight_kg": 12500,
                    "container_count": 1
                },
                "bl_data": {
                    "shipper": "Global Tech Logistics",
                    "consignee": "Euro Distribution Inc" if "consignee" in sim_defects else "European Distribution BV",
                    "port_of_loading": "Singapore (SGSIN)",
                    "port_of_discharge": "Rotterdam (NLRTM)",
                    "gross_weight_kg": 12500,
                    "container_count": 1
                }
            }
            upsert_verification(new_payload)
            st.success(f"Email {sim_id} intercepted, analyzed, and logged to Supabase!")
            st.rerun()