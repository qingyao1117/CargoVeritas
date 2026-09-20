"""CargoVeritas local SaaS dashboard. Run: python app.py"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import re
import secrets
import base64
import threading
import time
from datetime import datetime, timezone
from html import escape
from io import BytesIO
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse
from urllib.request import ProxyHandler, Request, build_opener, urlopen
from zipfile import ZIP_DEFLATED, ZipFile
from main import FIELDS, extract_text_from_bytes, process_email


PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CargoVeritas</title><style>
:root{--navy:#10243f;--blue:#1769e0;--green:#07836b;--amber:#aa6300;--line:#e1e8ef;--muted:#63758a}*{box-sizing:border-box}body{margin:0;background:#f5f7fa;color:var(--navy);font-family:"Times New Roman",Times,serif;font-size:16px}button{font:inherit;cursor:pointer}.shell{min-height:100vh;display:grid;grid-template-columns:238px 1fr}.side{background:var(--navy);color:#d6e2ef;padding:28px 16px;display:flex;flex-direction:column}.brand{font-size:23px;font-weight:bold;color:#fff;padding:0 12px 34px}.brand small{display:block;font-size:10px;letter-spacing:1.4px;color:#8fa7bd;margin-top:4px}.side label{color:#8fa7bd;font-size:10px;letter-spacing:1px;padding:0 12px 8px}nav{display:grid;gap:5px}nav button{border:0;border-radius:7px;background:none;color:#d6e2ef;text-align:left;padding:11px 12px}nav button:hover,nav button.active{background:#203d60;color:#fff}.profile{margin-top:auto;border-top:1px solid #324c68;padding:19px 12px 0}.profile small{color:#9bb0c5}.main{max-width:1500px;width:100%;margin:auto;padding:30px 38px}.top{display:flex;align-items:center;justify-content:space-between;gap:18px;margin-bottom:27px}h1{font-size:30px;margin:0 0 4px}h2{font-size:19px;margin:0}.sub,p{margin:0;color:var(--muted)}.actions{display:flex;gap:10px;align-items:center}.sync,.filter{background:#fff;border:1px solid var(--line);border-radius:7px;padding:9px 11px;font-size:13px}.sync:before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;background:#14a77f;margin-right:7px}.primary,.resolve{border:0;border-radius:7px;padding:10px 14px;background:var(--blue);color:#fff;font-weight:bold}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:23px}.card,.panel{background:#fff;border:1px solid var(--line);border-radius:11px}.card{padding:18px}.card small{color:var(--muted);font-size:12px}.card strong{display:block;font-size:31px;margin:12px 0 4px}.layout{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(300px,.75fr);gap:22px}.head{display:flex;align-items:center;justify-content:space-between;padding:18px 20px 13px}.link,.secondary{border:0;background:none;color:var(--blue);font-weight:bold}.secondary{border:1px solid var(--line);border-radius:6px;padding:8px 10px;color:#365d86;font-size:13px}table{width:100%;border-collapse:collapse}th{text-align:left;color:#75869a;font-size:11px;padding:0 18px 11px;letter-spacing:.6px}td{padding:13px 18px;border-top:1px solid var(--line);color:#4b6177;font-size:14px}td b{color:var(--navy)}.pill{display:inline-block;border-radius:99px;padding:5px 7px;font-size:11px;font-weight:bold}.ok{background:#e2f6ee;color:var(--green)}.review{background:#fff0d8;color:var(--amber)}.wait{background:#e8effe;color:#416cb8}.inbox{margin-top:22px}.mail{border-top:1px solid var(--line);display:flex;align-items:center;gap:11px;padding:12px 20px}.dot{width:8px;height:8px;border-radius:50%;background:#ce7900}.mail b,.mail small{display:block}.mail small{color:var(--muted);font-size:12px;margin-top:3px}.mail time{margin-left:auto;color:var(--muted);font-size:12px}.case{padding:20px;border-bottom:1px solid var(--line)}.eyebrow{color:var(--amber);font-weight:bold;font-size:11px;letter-spacing:.7px}.case h3{margin:10px 0 6px}.case p{line-height:1.45}.compare{border:1px solid var(--line);border-radius:8px;overflow:hidden;margin:15px 0}.compare div{display:grid;grid-template-columns:1.15fr 1fr 1fr;gap:7px;padding:8px 10px;border-top:1px solid var(--line);font-size:13px}.compare div:first-child{border-top:0;background:#f6f8fb;font-size:10px;font-weight:bold;color:#718195}.bad{color:#c24d57;font-weight:bold}.buttons{display:flex;gap:8px}.audit{padding:20px}.auditbox{background:#f4fbf9;border:1px solid #d6eee6;border-radius:8px;padding:12px;margin-top:13px}.auditbox p{font-size:13px;margin-top:5px}.modal{display:none;position:fixed;inset:0;place-items:center;padding:20px;background:rgba(10,29,50,.48);z-index:5}.modal.open{display:grid}.dialog{width:min(660px,100%);max-height:85vh;overflow:auto;background:#fff;border-radius:11px;padding:24px}.dialoghead{display:flex;justify-content:space-between;gap:12px;border-bottom:1px solid var(--line);padding-bottom:13px}.dialoghead p{margin-top:5px}.close{border:0;background:#edf2f7;border-radius:6px;width:30px;height:30px;font-size:20px}.item{display:flex;justify-content:space-between;align-items:center;gap:12px;border:1px solid var(--line);border-radius:8px;padding:12px;margin-top:10px}.item small{display:block;color:var(--muted);margin-top:3px}.toast{position:fixed;right:22px;bottom:20px;color:#fff;background:var(--navy);padding:12px 15px;border-radius:7px;opacity:0;z-index:10;transition:.2s}.toast.show{opacity:1}@media(max-width:950px){.cards{grid-template-columns:repeat(2,1fr)}.layout{grid-template-columns:1fr}}@media(max-width:680px){.shell{display:block}.side{display:none}.main{padding:21px 15px}.top{align-items:flex-start}.sync{display:none}.cards{gap:10px}.card{padding:14px}.scroll{overflow:auto}td,th{white-space:nowrap}.mail time{display:none}}
</style></head><body><div class="shell"><aside class="side"><div class="brand">⌁ CargoVeritas<small>CONTROL TOWER</small></div><label>WORKSPACE</label><nav><button class="active" data-view="Overview">▦ &nbsp; Overview</button><button data-view="Inbox intelligence">✉ &nbsp; Inbox intelligence</button><button data-view="Shipment operations">▱ &nbsp; Shipment operations</button><button data-view="Verification queue">✓ &nbsp; Verification queue</button><button data-view="Bill of Lading vault">▣ &nbsp; Bill of Lading vault</button><button data-view="Settlement calendar">◴ &nbsp; Settlement calendar</button></nav><div class="profile"><b>Avery Logistics</b><br><small>Operations team</small></div></aside><main class="main"><header class="top"><div><h1 id="title">Good morning, Avery team</h1><p class="sub" id="subtitle">Here is your shipping operation at a glance.</p></div><div class="actions"><span class="sync" id="sync">Inbox synced just now</span><button class="primary" id="connect">Connect mailbox</button></div></header><section class="cards"><article class="card"><small>ACTIVE SHIPMENTS</small><strong>24</strong><small>+4 since yesterday</small></article><article class="card"><small>EMAILS PROCESSED</small><strong>86</strong><small>96% automated</small></article><article class="card"><small>HUMAN REVIEW</small><strong id="count">5</strong><small>3 due today</small></article><article class="card"><small>SETTLEMENTS DUE</small><strong>9</strong><small>$184,260 this week</small></article></section><section class="layout"><div><section class="panel"><div class="head"><h2>Shipment workload</h2><button class="filter" id="filter">This week ▾</button></div><div class="scroll"><table><thead><tr><th>BOOKING</th><th>CUSTOMER</th><th>ROUTE</th><th>DEPARTURE</th><th>EQUIPMENT</th><th>DOCUMENT STATE</th></tr></thead><tbody><tr><td><b>BK-48291</b></td><td>Pacific Meridian</td><td>Port Klang to Rotterdam</td><td>24 Sep</td><td>3 x 40HC</td><td><span class="pill ok">Verified</span></td></tr><tr><td><b>BK-48307</b></td><td>Alpine Components</td><td>Singapore to Hamburg</td><td>24 Sep</td><td>2 x 20GP</td><td><span class="pill review">Review</span></td></tr><tr><td><b>BK-48318</b></td><td>Northstar Retail</td><td>Shanghai to Los Angeles</td><td>25 Sep</td><td>4 x 40HC</td><td><span class="pill ok">Verified</span></td></tr></tbody></table></div></section><section class="panel inbox"><div class="head"><h2>Incoming mail intelligence</h2><button class="link" id="inbox">View all emails →</button></div><div class="mail"><i class="dot"></i><div><b>BL draft for BK-48307</b><small>Alpine Components · BL comparison</small></div><time>2 min ago</time></div><div class="mail"><i class="dot" style="background:#0f9d85"></i><div><b>September freight invoice</b><small>Oceanic Lines · Invoice query</small></div><time>19 min ago</time></div></section></div><aside><section class="panel"><div class="case" id="case"><div class="eyebrow">HUMAN REVIEW NEEDED</div><h3>BL discrepancy - BK-48307</h3><p>The automated check found one value that needs confirmation before the BOL is released.</p><div class="compare"><div><span>FIELD</span><span>SHIPPING INSTRUCTION</span><span>DRAFT BOL</span></div><div><b>Container count</b><span>2 x 20GP</span><span class="bad">3 x 20GP</span></div><div><b>Gross weight</b><span>18,450 kg</span><span>18,450 kg</span></div></div><div class="buttons"><button class="secondary" id="evidence">View evidence</button><button class="resolve" id="review">Review case</button></div></div><div class="audit"><div class="head" style="padding:0"><h2>Audited BOL vault</h2><button class="link" id="vault">Open vault →</button></div><div class="auditbox"><b>BL-2026-0918-8821 · Verified</b><p>Every field, source email, reviewer decision, and timestamp is retained.</p></div></div></section></aside></section></main></div><div class="modal" id="modal"><div class="dialog"><div class="dialoghead"><div><h2 id="mtitle">Details</h2><p id="mcopy"></p></div><button class="close" id="close">×</button></div><div id="mbody"></div></div></div><div class="toast" id="toast"></div><script>
var modal=document.getElementById("modal"),body=document.getElementById("mbody");function toast(x){var t=document.getElementById("toast");t.textContent=x;t.classList.add("show");setTimeout(function(){t.classList.remove("show")},2600)}function openModal(a,b,c){document.getElementById("mtitle").textContent=a;document.getElementById("mcopy").textContent=b;body.innerHTML=c;modal.classList.add("open")}function closeModal(){modal.classList.remove("open")}document.getElementById("close").onclick=closeModal;modal.onclick=function(e){if(e.target===modal)closeModal()};document.addEventListener("click",function(e){var a=e.target.dataset.action;if(a==="open-review"){closeModal();document.getElementById("review").click()}if(a==="correction")resolveCase("Correction requested from carrier");if(a==="approve")resolveCase("Approved after manual verification");if(a==="record")toast("Audit record opened")});
document.getElementById("connect").onclick=function(){this.textContent="Mailbox connected";this.disabled=true;document.getElementById("sync").textContent="Secure mail connection active";toast("Mailbox connected. New mail will be classified automatically.")};document.getElementById("filter").onclick=function(){this.textContent=this.textContent.indexOf("This")>=0?"Next 7 days ▾":"This week ▾";toast("Shipment date range updated")};
document.getElementById("inbox").onclick=function(){openModal("Inbox intelligence","Classify, route, and act on incoming operational email.","<div class='item'><div><b>BL draft for BK-48307</b><small>Alpine Components · mismatch found</small></div><button class='secondary' data-action='open-review'>Open review</button></div><div class='item'><div><b>September freight invoice</b><small>Oceanic Lines · settlement recorded</small></div><span class='pill ok'>Settled</span></div><div class='item'><div><b>Special rates for Q4</b><small>Unknown sender · spam</small></div><span class='pill wait'>Filtered</span></div>")};
document.getElementById("evidence").onclick=function(){openModal("Source evidence","Documents and extraction results remain connected.","<div class='item'><div><b>Shipping Instruction.pdf</b><small>Received 09:41 · parsed successfully</small></div><span class='pill ok'>Parsed</span></div><div class='item'><div><b>Draft Bill of Lading.pdf</b><small>Container count differs</small></div><span class='pill review'>Mismatch</span></div><p><b>Audit event:</b> automated comparison completed at 09:42 and assigned this case to Avery Logistics.</p>")};
document.getElementById("review").onclick=function(){openModal("Resolve BL discrepancy","Record a human decision in the audit trail.","<p><b>Issue:</b> the SI says 2 x 20GP while the draft BOL says 3 x 20GP.</p><div class='buttons'><button class='resolve' data-action='correction'>Request correction</button><button class='secondary' data-action='approve'>Approve as correct</button></div>")};function resolveCase(x){document.getElementById("case").innerHTML="<div class='eyebrow' style='color:#07836b'>REVIEW COMPLETED</div><h3>BK-48307 decision recorded</h3><p>"+x+". The supporting documents and decision are now in the audit trail.</p><button class='secondary' onclick='location.reload()'>Reopen case</button>";document.getElementById("count").textContent="4";closeModal();toast(x)};
document.getElementById("vault").onclick=function(){openModal("Audited BOL vault","Verified BOLs preserve email sources, comparisons, and reviewer history.","<div class='item'><div><b>BL-2026-0918-8821</b><small>Pacific Meridian · Port Klang to Rotterdam</small></div><button class='secondary' data-action='record'>Open record</button></div><div class='item'><div><b>BL-2026-0918-8844</b><small>Northstar Retail · verified</small></div><span class='pill ok'>Verified</span></div>")};
document.querySelectorAll("nav button").forEach(function(b){b.onclick=function(){document.querySelector("nav .active").classList.remove("active");this.classList.add("active");var v=this.dataset.view;document.getElementById("title").textContent=v;document.getElementById("subtitle").textContent=v==="Overview"?"Here is your shipping operation at a glance.":"Working view: "+v;if(v==="Inbox intelligence")document.getElementById("inbox").click();if(v==="Verification queue")document.getElementById("review").click();if(v==="Bill of Lading vault")document.getElementById("vault").click();if(v==="Settlement calendar")openModal("Settlement calendar","Payments grouped by expected settlement date.","<div class='item'><div><b>24 Sep · Oceanic Lines</b><small>September freight invoice</small></div><b>$68,400</b></div><div class='item'><div><b>25 Sep · Harbour Link</b><small>Three completed shipments</small></div><b>$74,860</b></div>")}})</script></body></html>"""


OAUTH_STATES = set()
CONNECTED_ACCOUNTS = {}
PREFERENCES = {"language": "English", "theme": "Light mode"}
# The local development runtime has a placeholder localhost proxy.  Google OAuth
# must connect directly instead of inheriting that unusable proxy configuration.
GOOGLE_HTTP = build_opener(ProxyHandler({}))
SYNC_WORKER_STARTED = False
SYNC_WORKER_LOCK = threading.Lock()


def start_gmail_sync_worker():
    """Poll the connected inbox while this local demo server is running."""
    global SYNC_WORKER_STARTED
    with SYNC_WORKER_LOCK:
        if SYNC_WORKER_STARTED:
            return
        SYNC_WORKER_STARTED = True

    def worker():
        while True:
            time.sleep(max(30, int(os.getenv("GMAIL_SYNC_INTERVAL_SECONDS", "60"))))
            if not CONNECTED_ACCOUNTS or not os.getenv("SUPABASE_SECRET_KEY"):
                continue
            try:
                GOOGLE_HTTP.open(Request("http://127.0.0.1:8000/gmail/sync"), timeout=30).read()
            except Exception as error:
                print("Background Gmail sync skipped:", type(error).__name__)

    threading.Thread(target=worker, name="gmail-sync", daemon=True).start()


def load_local_env():
    """Load local development secrets without adding a dependency."""
    env_file = Path(".env")
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class App(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/auth/gmail":
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            if not client_id:
                self._html("<h1>Gmail is not configured</h1><p>Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to the server environment, then restart CargoVeritas.</p><p><a href='/settings'>Open settings</a></p>")
                return
            state = secrets.token_urlsafe(32)
            OAUTH_STATES.add(state)
            params = {
                "client_id": client_id,
                "redirect_uri": "http://127.0.0.1:8000/auth/gmail/callback",
                "response_type": "code",
                "scope": "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/userinfo.email",
                "access_type": "offline",
                "prompt": "consent",
                "state": state,
            }
            self.send_response(302)
            self.send_header("Location", "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params))
            self.end_headers()
            return
        if parsed.path == "/auth/gmail/callback":
            query = parse_qs(parsed.query)
            state, code = query.get("state", [""])[0], query.get("code", [""])[0]
            if state not in OAUTH_STATES or not code:
                self._html("<h1>Gmail connection could not be verified</h1><p>Please return to CargoVeritas and try again.</p>", 400)
                return
            OAUTH_STATES.discard(state)
            try:
                payload = urlencode({
                    "code": code,
                    "client_id": os.environ["GOOGLE_CLIENT_ID"],
                    "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
                    "redirect_uri": "http://127.0.0.1:8000/auth/gmail/callback",
                    "grant_type": "authorization_code",
                }).encode()
                token = json.load(GOOGLE_HTTP.open(Request("https://oauth2.googleapis.com/token", data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})))
                profile = json.load(GOOGLE_HTTP.open(Request("https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": "Bearer " + token["access_token"]})))
                CONNECTED_ACCOUNTS[profile["email"]] = token
                start_gmail_sync_worker()
                self._html("<h1>Gmail connected</h1><p><b>" + profile["email"] + "</b> is now connected with read-only Gmail access.</p><p><a href='/'>Return to CargoVeritas</a></p>")
            except Exception as error:
                # Keep OAuth secrets out of the browser while preserving a useful local diagnostic.
                print("Gmail OAuth callback failed:", type(error).__name__, str(error))
                self._html("<h1>Gmail connection failed</h1><p>Google approved the account, but CargoVeritas could not exchange the authorization with Google. Check the local server console for the safe diagnostic, then try a fresh connection.</p>", 502)
            return
        if parsed.path == "/logout":
            self._html("<main style='padding:80px;font-family:Times New Roman,serif'><h1>You have been logged out</h1><p>Your local CargoVeritas session has ended.</p><p><a href='/'>Return to dashboard</a></p></main>")
            return
        if parsed.path == "/settings/save":
            values = parse_qs(parsed.query)
            language = values.get("language", [PREFERENCES["language"]])[0]
            theme = values.get("theme", [PREFERENCES["theme"]])[0]
            if language in ("English", "Bahasa Melayu", "Chinese"):
                PREFERENCES["language"] = language
            if theme in ("Light mode", "Dark mode"):
                PREFERENCES["theme"] = theme
            self.send_response(302)
            self.send_header("Location", "/settings?saved=1")
            self.end_headers()
            return
        if parsed.path == "/gmail/sync":
            try:
                result = self._sync_gmail_to_supabase()
                self._html("<h1>Gmail sync complete</h1><p>Processed " + str(result["processed"]) + " recent messages from <b>" + escape(result["account"]) + "</b> and saved them to Supabase.</p><p><a href='/app/inbox-intelligence'>Open live inbox</a></p>")
            except RuntimeError as error:
                self._html("<h1>Gmail sync needs setup</h1><p>" + escape(str(error)) + "</p><p><a href='/settings'>Open settings</a></p>", 400)
            except Exception as error:
                print("Gmail sync failed:", type(error).__name__, str(error))
                self._html("<h1>Gmail sync failed</h1><p>The server could not retrieve or store mailbox messages. Check the local server console for the safe diagnostic.</p><p><a href='/app/inbox-intelligence'>Return to inbox</a></p>", 502)
            return
        if parsed.path == "/review/resolve":
            review_id = parse_qs(parsed.query).get("id", [""])[0]
            decision = parse_qs(parsed.query).get("decision", [""])[0]
            if not review_id or decision not in ("approved", "rejected_to_carrier", "amended_docs_requested"):
                self._html("<h1>Review action could not be recorded</h1><p>Select a valid verification decision.</p>", 400)
                return
            try:
                status = "RESOLVED" if decision == "approved" else "REJECTED_TO_CARRIER" if decision == "rejected_to_carrier" else "AMENDED_DOCS_REQUESTED"
                note = "Carrier discrepancy notice generated for dispatch." if decision == "rejected_to_carrier" else "Amended shipping documents requested." if decision == "amended_docs_requested" else "Discrepancy approved by reviewer."
                self._supabase_json("/rest/v1/gmail_messages?gmail_message_id=eq." + quote(review_id, safe=""), "PATCH", {"status": status, "processing_status": status, "operator_action": decision, "operator_notes": note})
                self._html("<h1>Verification decision recorded</h1><p>The audited Gmail record is now marked <b>" + escape(status.replace("_", " ")) + "</b>. " + escape(note) + "</p><p><a href='/app/verification-queue'>Return to verification queue</a></p>")
            except Exception as error:
                print("Review action failed:", type(error).__name__, str(error))
                self._html("<h1>Review action failed</h1><p>The decision could not be saved to Supabase.</p>", 502)
            return
        if parsed.path == "/bol/download":
            selected = parse_qs(parsed.query).get("bol", [])
            if not selected:
                self._html("<h1>No BOLs selected</h1><p>Select one or more documents in the BOL vault first.</p><p><a href='/app/bill-of-lading-vault'>Open BOL vault</a></p>", 400)
                return
            archive = BytesIO()
            with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
                for bol in selected:
                    safe_name = bol.replace("/", "").replace("\\", "")
                    record = self._bol_record(safe_name)
                    if record:
                        bundle.writestr(safe_name + ".pdf", self._build_bol_pdf(record, safe_name))
            data, content_type, attachment_name = archive.getvalue(), "application/zip", "CargoVeritas-BOLs.zip"
        elif parsed.path.startswith("/bol/") and parsed.path.endswith(".pdf"):
            bol_ref = unquote(parsed.path.rsplit("/", 1)[-1][:-4])
            record = self._bol_record(bol_ref)
            if not record:
                self.send_error(404, "Bill of Lading record not found")
                return
            data, content_type = self._build_bol_pdf(record, bol_ref), "application/pdf"
        elif parsed.path in ("/", "/index.html", "/settings") or parsed.path.startswith("/app/"):
            section = parsed.path.rsplit("/", 1)[-1].replace("-", " ").title()
            if parsed.path in ("/", "/index.html"):
                section = "Overview"
            page = self._workspace(section, parse_qs(parsed.query))
            data, content_type = page.encode(), "text/html; charset=utf-8"
        elif self.path == "/api/dashboard":
            data, content_type = b'{"status":"ready"}', "application/json"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        if 'attachment_name' in locals():
            self.send_header("Content-Disposition", "attachment; filename=" + attachment_name)
        self.end_headers()
        self.wfile.write(data)
    def _supabase_credentials(self):
        url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SECRET_KEY")
        if not url or not key:
            raise RuntimeError("Add SUPABASE_SECRET_KEY to .env. Use the Supabase secret/service-role key, not the publishable key.")
        return url.rstrip("/"), key

    def _supabase_json(self, path, method="GET", payload=None):
        url, key = self._supabase_credentials()
        headers = {"apikey": key, "Authorization": "Bearer " + key}
        data = None
        if payload is not None:
            data = json.dumps(payload).encode()
            headers["Content-Type"] = "application/json"
            headers["Prefer"] = "resolution=merge-duplicates,return=minimal"
        request = Request(url + path, data=data, headers=headers, method=method)
        response = GOOGLE_HTTP.open(request, timeout=20)
        raw = response.read()
        return json.loads(raw) if raw else []

    def _gmail_parts(self, payload):
        parts = [payload]
        for part in payload.get("parts", []):
            parts.extend(self._gmail_parts(part))
        return parts

    def _gmail_attachment_bytes(self, message_id, body, token):
        encoded = body.get("data")
        if not encoded and body.get("attachmentId"):
            data = json.load(GOOGLE_HTTP.open(Request(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages/" + message_id + "/attachments/" + body["attachmentId"],
                headers={"Authorization": "Bearer " + token["access_token"]}), timeout=20))
            encoded = data.get("data")
        if not encoded:
            return b""
        return base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))

    def _sync_gmail_to_supabase(self):
        if not CONNECTED_ACCOUNTS:
            raise RuntimeError("Connect a Gmail account first, then return here to sync it.")
        account, token = next(iter(CONNECTED_ACCOUNTS.items()))
        listing = json.load(GOOGLE_HTTP.open(Request(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=15&labelIds=INBOX",
            headers={"Authorization": "Bearer " + token["access_token"]}), timeout=20))
        records = []
        for item in listing.get("messages", []):
            message = json.load(GOOGLE_HTTP.open(Request(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages/" + item["id"] + "?format=full",
                headers={"Authorization": "Bearer " + token["access_token"]}), timeout=20))
            payload = message.get("payload", {})
            parts = self._gmail_parts(payload)
            headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
            subject = headers.get("subject", "(no subject)")
            received = datetime.fromtimestamp(int(message.get("internalDate", "0")) / 1000, tz=timezone.utc).isoformat()
            attachment_texts, attachment_summary, body_chunks = {}, [], []
            for part in parts:
                mime, filename = part.get("mimeType", ""), part.get("filename", "")
                if mime == "text/plain" and part.get("body", {}).get("data"):
                    body_chunks.append(self._gmail_attachment_bytes(message["id"], part["body"], token).decode("utf-8", errors="replace"))
                if filename:
                    raw = self._gmail_attachment_bytes(message["id"], part.get("body", {}), token)
                    text = extract_text_from_bytes(raw, filename)
                    attachment_texts[filename] = text
                    attachment_summary.append({"filename": filename, "mime_type": mime, "readable": bool(text.strip())})
            body = "\n".join(body_chunks) or message.get("snippet", "")
            processed = process_email({"subject": subject, "body": body}, attachment_texts)
            records.append({"gmail_message_id": message["id"], "gmail_thread_id": message.get("threadId"), "sender": headers.get("from", ""), "subject": subject, "snippet": message.get("snippet", ""), "body_snippet": body[:4000], "received_at": received, "classification": processed["category"], "processing_status": processed["status"], "category": processed["category"], "status": processed["status"], "review_reason": processed["review_reason"], "defect_fields": processed["defect_fields"], "si_data": processed["si_data"], "bl_data": processed["bl_data"], "attachment_summary": attachment_summary, "extraction": {"source": "gmail_documents", "category": processed["category"]}})
        if records:
            self._supabase_json("/rest/v1/gmail_messages?on_conflict=gmail_message_id", "POST", records)
        return {"account": account, "processed": len(records)}

    def _bol_record(self, bol_ref):
        """Resolve a BOL reference to its current structured Gmail record."""
        wanted = bol_ref.replace("BOL-", "")
        return next((row for row in self._recent_gmail_messages()
                     if (row.get("gmail_message_id") or "").endswith(wanted)
                     and row.get("category") == "BL_COMPARISON"), None)

    def _build_bol_pdf(self, record, bol_ref):
        """Build a styled, ASCII-safe verification certificate from live audit data."""
        def clean(value):
            if value in (None, ""):
                return "N/A"
            replacements = {"-": "-", "-": "-", "'": "'", "'": "'", '"': '"', '"': '"', "...": "...", "\u00a0": " "}
            text = str(value)
            for source, replacement in replacements.items():
                text = text.replace(source, replacement)
            return text.encode("ascii", "ignore").decode("ascii").strip() or "N/A"
        def literal(value):
            return clean(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        def text(cmds, x, y, value, size=9, color="0.06 0.09 0.16"):
            cmds.extend([color + " rg", f"/F1 {size} Tf", f"1 0 0 1 {x} {y} Tm (" + literal(value) + ") Tj"])
        def rect(cmds, x, y, width, height, color):
            cmds.append(color + f" rg {x} {y} {width} {height} re f")
        def clipped(value, length):
            value = clean(value)
            return value if len(value) <= length else value[: max(0, length - 3)] + "..."
        si, bl = record.get("si_data") or {}, record.get("bl_data") or {}
        defects = set(record.get("defect_fields") or [])
        labels = {"shipper": "Shipper", "consignee": "Consignee", "notify_party": "Notify Party", "port_of_loading": "Port of Loading (POL)", "port_of_discharge": "Port of Discharge (POD)", "container_count": "Container Count", "gross_weight_kg": "Gross Weight (kg)"}
        state_map = {"OK": ("PASSED / OK", "0.086 0.639 0.290"), "MISMATCH": ("DISCREPANCY DETECTED", "0.863 0.149 0.149"), "NEEDS_REVIEW": ("HUMAN REVIEW REQUIRED", "0.843 0.467 0.024")}
        state_text, state_color = state_map.get(record.get("status"), ("HUMAN REVIEW REQUIRED", "0.843 0.467 0.024"))
        commands = []
        rect(commands, 0, 700, 612, 142, "0.059 0.090 0.165")
        text(commands, 34, 802, "CARGOVERITAS AUDIT VERIFICATION CERTIFICATE", 18, "1 1 1")
        text(commands, 34, 778, "CargoVeritas - Audited Bill of Lading", 10, "0.85 0.90 0.97")
        text(commands, 34, 748, "Audit Reference: " + bol_ref, 9, "1 1 1")
        rect(commands, 334, 735, 238, 24, state_color)
        text(commands, 344, 744, state_text, 8, "1 1 1")
        text(commands, 34, 725, "Source Email: " + clipped(record.get("sender"), 69), 8, "0.85 0.90 0.97")
        text(commands, 34, 710, "Subject: " + clipped(record.get("subject"), 77), 8, "0.85 0.90 0.97")
        text(commands, 34, 692, "Timestamp (UTC): " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"), 8, "0.85 0.90 0.97")
        x, widths, y, row_height = 25, (125, 165, 165, 107), 648, 36
        rect(commands, x, y, sum(widths), 27, "0.118 0.161 0.231")
        headers = ("Field", "Shipping Instruction (SI)", "Draft Bill of Lading (BL)", "Audit Result")
        cursor = x
        for header, width in zip(headers, widths):
            text(commands, cursor + 6, y + 10, header, 8, "1 1 1")
            cursor += width
        for index, field in enumerate(FIELDS):
            row_y = y - (index + 1) * row_height
            rect(commands, x, row_y, sum(widths), row_height, "0.973 0.980 0.988" if index % 2 == 0 else "1 1 1")
            valid = si.get(field) not in (None, "") and bl.get(field) not in (None, "")
            outcome = "N/A" if not valid else "MISMATCH" if field in defects else "MATCH"
            if outcome == "MISMATCH":
                rect(commands, x + widths[0], row_y, widths[1] + widths[2], row_height, "0.996 0.922 0.922")
            cursor = x
            values = (labels[field], clipped(si.get(field), 27), clipped(bl.get(field), 27))
            for value, width in zip(values, widths[:3]):
                text(commands, cursor + 6, row_y + 13, value, 8)
                cursor += width
            if outcome == "MISMATCH":
                rect(commands, cursor + 6, row_y + 9, 92, 17, "0.937 0.267 0.267")
                text(commands, cursor + 12, row_y + 14, outcome, 7, "1 1 1")
            elif outcome == "MATCH":
                text(commands, cursor + 8, row_y + 13, outcome, 8, "0.086 0.639 0.290")
            else:
                text(commands, cursor + 8, row_y + 13, "N/A - UNEXTRACTED", 7, "0.392 0.455 0.545")
            cursor = x
            for width in widths:
                commands.append("0.80 0.84 0.89 RG 0.4 w " + f"{cursor} {row_y} m {cursor} {row_y + row_height} l S")
                cursor += width
        footer_y = y - len(FIELDS) * row_height - 35
        commands.append("0.75 0.80 0.86 RG 0.6 w 25 " + str(footer_y + 20) + " m 587 " + str(footer_y + 20) + " l S")
        text(commands, 25, footer_y, "CargoVeritas Control Tower | Automated Trade Document Verification Engine", 8, "0.23 0.29 0.38")
        text(commands, 25, footer_y - 14, "Verified against operational transport requirements. Generated automatically.", 8, "0.39 0.46 0.55")
        stream = ("BT\n" + "\n".join(commands) + "\nET").encode("ascii")
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
            b"<< /Title (CargoVeritas - Audited Bill of Lading) /Author (CargoVeritas) >>",
        ]
        pdf, offsets = bytearray(b"%PDF-1.4\n"), []
        for number, obj in enumerate(objects, 1):
            offsets.append(len(pdf))
            pdf.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
        xref = len(pdf)
        pdf.extend(b"xref\n0 7\n0000000000 65535 f \n")
        pdf.extend(b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets))
        pdf.extend(f"trailer\n<< /Size 7 /Root 1 0 R /Info 6 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
        return bytes(pdf)

    def _recent_gmail_messages(self):
        try:
            return self._supabase_json("/rest/v1/gmail_messages?select=gmail_message_id,sender,subject,snippet,body_snippet,category,status,defect_fields,si_data,bl_data,review_reason,attachment_summary,received_at&order=received_at.desc&limit=15")
        except Exception:
            return []
    def _workspace(self, section, query):
        slug = section.lower().replace(" ", "-")
        if section == "Settings":
            slug = "settings"
        inbox_rows = self._recent_gmail_messages()
        category_meta = {
            "BL_COMPARISON": ("Bill of Lading Comparison", "Sent to 7-Field Audit", "cat-bl"),
            "SI_REQUEST": ("Shipping Instruction Request", "Forwarded to Booking", "cat-si"),
            "INVOICE_QUERY": ("Invoice Query", "Routed to Finance", "cat-invoice"),
            "GENERAL": ("General Update", "Operations Updates", "cat-general"),
            "SPAM": ("Spam", "Filtered & Quarantined", "cat-spam"),
        }
        field_labels = {"shipper": "Shipper", "consignee": "Consignee", "notify_party": "Notify Party", "port_of_loading": "Port of Loading", "port_of_discharge": "Port of Discharge", "container_count": "Container Count", "gross_weight_kg": "Gross Weight (kg)"}
        reason_labels = {"missing_attachment": "Missing Attachment", "unreadable_document": "Unreadable Document"}
        status_labels = {"AUTO_RESOLVED": "Auto Resolved", "CLASSIFIED": "Classified", "NEEDS_REVIEW": "Needs Review", "MISMATCH": "Mismatch", "OK": "Straight-Through Processed", "RESOLVED": "Resolved"}
        def category_for(row):
            return row.get("category") if row.get("category") in category_meta else "GENERAL"
        def status_label(status):
            return status_labels.get(status, (status or "Pending").replace("_", " ").title())
        def category_badge(row):
            label, subtitle, css = category_meta[category_for(row)]
            return "<span class='category-badge " + css + "'>" + label + "</span><small class='category-routing'>" + subtitle + "</small>"
        selected_category = query.get("category", ["ALL"])[0]
        if selected_category not in category_meta:
            selected_category = "ALL"
        search = query.get("q", [""])[0].strip().lower()
        filtered_rows = [row for row in inbox_rows if (selected_category == "ALL" or category_for(row) == selected_category) and (not search or search in " ".join(str(row.get(key) or "") for key in ("sender", "subject", "snippet")).lower())]
        def routing_reason(row):
            return {"BL_COMPARISON": "Detected shipping-document content and routed it to the 7-field audit.", "SI_REQUEST": "Detected a shipping-instruction request and forwarded it to booking.", "INVOICE_QUERY": "Detected an invoice question and routed it to finance.", "GENERAL": "Detected an operational update that does not require document verification.", "SPAM": "Detected unsolicited promotional or irrelevant content and filtered it to quarantine."}[category_for(row)]
        def inbox_row(row):
            item_id = quote(row.get("gmail_message_id") or "", safe="")
            href = "/app/inbox-intelligence?category=" + quote(selected_category) + "&email=" + item_id
            return "<tr class='clickable-row' onclick=\"location.href='" + href + "'\"><td>" + escape(row.get("sender") or "Unknown sender") + "</td><td><b>" + escape(row.get("subject") or "(no subject)") + "</b></td><td>" + category_badge(row) + "</td><td>" + escape(status_label(row.get("status"))) + "</td><td>" + escape((row.get("received_at") or "")[:16].replace("T", " ")) + "</td></tr>"
        live_messages = "<table><tr><th>FROM</th><th>SUBJECT</th><th>CATEGORY</th><th>ROUTING STATUS</th><th>RECEIVED</th></tr>" + "".join(inbox_row(row) for row in filtered_rows) + "</table>" if filtered_rows else "<p>No emails match this filter.</p>"
        shipping_rows = [row for row in inbox_rows if category_for(row) == "BL_COMPARISON"]
        review_rows = [row for row in inbox_rows if row.get("status") in ("MISMATCH", "NEEDS_REVIEW")]
        def shipment_row(row):
            data = row.get("si_data") or {} if category_for(row) == "BL_COMPARISON" else {}
            reference = "BOL-" + (row.get("gmail_message_id") or "")[-8:] if data else "—"
            value = lambda key: escape(str(data.get(key))) if data.get(key) not in (None, "") else "—"
            return "<tr><td>" + escape(reference) + "</td><td>" + value("shipper") + "</td><td>" + value("consignee") + "</td><td>" + value("port_of_loading") + "</td><td>" + value("port_of_discharge") + "</td><td>" + value("container_count") + "</td><td>" + value("gross_weight_kg") + "</td><td>" + escape(status_label(row.get("status"))) + "</td></tr>"
        shipment_table = "".join(shipment_row(row) for row in inbox_rows) or "<tr><td colspan='8'>No processed email records have been synced yet.</td></tr>"
        bol_table = "".join("<tr><td><input type='checkbox' name='bol' value='BOL-" + escape((row.get("gmail_message_id") or "")[-8:]) + "'></td><td>BOL-" + escape((row.get("gmail_message_id") or "")[-8:]) + "</td><td>" + escape(row.get("subject") or "BL comparison") + "</td><td>" + escape(status_label(row.get("status"))) + "</td><td><a href='/bol/BOL-" + escape((row.get("gmail_message_id") or "")[-8:]) + ".pdf' download>Download PDF</a></td></tr>" for row in shipping_rows) or "<tr><td colspan='5'>No BL comparison records have been synced yet.</td></tr>"
        category_counts = {category: sum(1 for row in inbox_rows if category_for(row) == category) for category in category_meta}
        comparisons = [row for row in inbox_rows if category_for(row) == "BL_COMPARISON"]
        straight_through = sum(1 for row in comparisons if row.get("status") == "OK")
        stp_rate = round((straight_through / len(comparisons) * 100) if comparisons else 0)
        overview_cards = "<div class='grid cards'><article><small>ACTIVE SHIPMENTS</small><b>" + str(len(shipping_rows)) + "</b><small>Bill of Lading comparisons</small></article><article><small>EMAILS PROCESSED</small><b>" + str(len(inbox_rows)) + "</b><small>matches category breakdown</small></article><article><small>HUMAN REVIEW</small><b>" + str(len(review_rows)) + "</b><small>documents awaiting a decision</small></article><article><small>STRAIGHT-THROUGH RATE</small><b>" + str(straight_through) + " / " + str(len(comparisons)) + "</b><small>" + str(stp_rate) + "% passed all 7 fields</small></article></div>"
        category_breakdown = "<section><h2>Email Classification Breakdown</h2><div class='category-grid'>" + "".join("<a class='category-card " + category_meta[category][2] + "' href='/app/inbox-intelligence?category=" + category + "'><span class='category-badge " + category_meta[category][2] + "'>" + category_meta[category][0] + "</span><small>" + category_meta[category][1] + "</small><b>" + str(count) + "</b></a>" for category, count in category_counts.items()) + "</div></section>"
        def review_card(row):
            item_id = quote(row.get("gmail_message_id") or "", safe="")
            actions = "<p><a class='button' href='/review/resolve?id=" + item_id + "&decision=approved'>Approve Discrepancy</a> <a class='button muted' href='/review/resolve?id=" + item_id + "&decision=rejected_to_carrier'>Reject to Carrier</a> <a class='button muted' href='/review/resolve?id=" + item_id + "&decision=amended_docs_requested'>Request Amended Docs</a></p>"
            if row.get("status") == "NEEDS_REVIEW":
                reason = reason_labels.get(row.get("review_reason"), (row.get("review_reason") or "Document Could Not Be Verified").replace("_", " ").title())
                return "<div class='email'><h3>" + escape(row.get("subject") or "Document review") + "</h3><div class='warning-banner'><b>Escalation Reason: " + escape(reason) + "</b></div><p>" + escape(row.get("body_snippet") or row.get("snippet") or "No email body available.") + "</p>" + actions + "</div>"
            rows = "".join("<tr" + (" class='alert'" if field in (row.get("defect_fields") or []) else "") + "><td>" + field_labels[field] + "</td><td>" + escape(str((row.get("si_data") or {}).get(field) or "—")) + "</td><td>" + escape(str((row.get("bl_data") or {}).get(field) or "—")) + "</td><td>" + ("<span class='discrepancy-badge'>Discrepancy Detected</span>" if field in (row.get("defect_fields") or []) else "<span class='match-badge'>Match</span>") + "</td></tr>" for field in FIELDS)
            return "<div class='email'><h3>" + escape(row.get("subject") or "BL comparison") + "</h3><table><tr><th>Field Name</th><th>Shipping Instruction (SI)</th><th>Draft Bill of Lading (BL)</th><th>Status</th></tr>" + rows + "</table>" + actions + "</div>"
        review_cards = "".join(review_card(row) for row in review_rows) or "<p>No MISMATCH or NEEDS_REVIEW records are awaiting action.</p>"
        tab_specs = [("ALL", "All")] + [(category, category_meta[category][0]) for category in category_meta]
        filter_tabs = "<div class='filter-tabs'>" + "".join("<a class='filter-pill" + (" active" if selected_category == key else "") + "' href='/app/inbox-intelligence?category=" + key + "'>" + label + " (" + str(len(inbox_rows) if key == "ALL" else category_counts[key]) + ")</a>" for key, label in tab_specs) + "</div>"
        selected_email = query.get("email", [""])[0]
        inspected = next((row for row in inbox_rows if row.get("gmail_message_id") == selected_email), None)
        email_drawer = ""
        if inspected:
            close_url = "/app/inbox-intelligence?category=" + quote(selected_category)
            email_drawer = "<div class='drawer-backdrop'><aside class='email-drawer'><a class='drawer-close' href='" + close_url + "'>×</a><h2>Email inspection</h2><p><b>From:</b> " + escape(inspected.get("sender") or "Unknown sender") + "</p><p><b>Subject:</b> " + escape(inspected.get("subject") or "(no subject)") + "</p><p><b>Timestamp:</b> " + escape((inspected.get("received_at") or "").replace("T", " ")) + "</p><p>" + category_badge(inspected) + "</p><div class='routing-explainer'><b>Automated routing rationale</b><br>" + routing_reason(inspected) + "</div><h3>Full email body</h3><pre>" + escape(inspected.get("body_snippet") or inspected.get("snippet") or "No body content was available.") + "</pre></aside></div>"
        language_options = "".join("<option" + (" selected" if PREFERENCES["language"] == value else "") + ">" + value + "</option>" for value in ("English", "Bahasa Melayu", "Chinese"))
        theme_options = "".join("<option" + (" selected" if PREFERENCES["theme"] == value else "") + ">" + value + "</option>" for value in ("Light mode", "Dark mode"))
        save_confirmation = "<p class='notice'>Preferences saved. Language: " + escape(PREFERENCES["language"]) + "; appearance: " + escape(PREFERENCES["theme"]) + ".</p>" if query.get("saved") else ""
        pages = {
            "overview": overview_cards + category_breakdown + "<div class='grid two'><section><h2>Live shipping workload</h2><table><tr><th>BOOKING / BL REF</th><th>SHIPPER</th><th>CONSIGNEE</th><th>PORT OF LOADING</th><th>PORT OF DISCHARGE</th><th>CONTAINERS</th><th>GROSS WT (KG)</th><th>AUDIT STATE</th></tr>" + shipment_table + "</table><p><a class='button' href='/app/shipment-operations'>Open shipment operations</a></p></section><section><h2>Live processing</h2><p>Records refresh after Gmail sync. Use Inbox intelligence to run an immediate sync.</p><a class='button' href='/app/inbox-intelligence'>Open inbox</a></section></div>",
            "inbox-intelligence": """<section><h2>Incoming email</h2><p>Classified Gmail messages. Select a category or click a row to inspect the original email and automated routing rationale.</p><p><a class='button' href='/gmail/sync'>Sync Gmail now</a></p><form method='get' action='/app/inbox-intelligence' class='search'><input type='hidden' name='category' value='""" + selected_category + """'><input name='q' value='""" + escape(query.get("q", [""])[0]) + """' placeholder='Search sender, booking number, or subject'><button>Search inbox</button></form></section><section><h2>Live mailbox messages</h2>""" + filter_tabs + live_messages + "</section>" + email_drawer,
            "shipment-operations": "<section><h2>Shipment operations</h2><p>Extracted shipping parameters from processed Gmail messages. Non-comparison messages intentionally show an em dash.</p><table><tr><th>BOOKING / BL REF</th><th>SHIPPER</th><th>CONSIGNEE</th><th>PORT OF LOADING</th><th>PORT OF DISCHARGE</th><th>CONTAINERS</th><th>GROSS WT (KG)</th><th>AUDIT STATE</th></tr>" + shipment_table + "</table></section>",
            "verification-queue": "<section><h2>Verification queue</h2><p>Live shipping documents awaiting a human decision. A decision is written back to Supabase and removed from this queue.</p>" + review_cards + "</section>",
            "bill-of-lading-vault": "<section><h2>Audited BOL vault</h2><p>Generated from synced shipping emails. Select one or more BOL records to download.</p><form method='get' action='/bol/download'><table><tr><th>Select</th><th>BOL</th><th>Shipment email</th><th>Audit state</th><th>Individual PDF</th></tr>" + bol_table + "</table><p><button>Download selected BOLs</button></p></form></section>",
            "settings": """<section><h2>Company profile</h2>""" + save_confirmation + """<form method='get' action='/settings/save'><div class='formgrid'><label>Company name<input name='company' value='Avery Logistics'></label><label>Administrator email<input name='email' value='avery@averylogistics.com'></label><label>Preferred language<select name='language'>""" + language_options + """</select></label><label>Appearance<select name='theme'>""" + theme_options + """</select></label></div><p><button>Save preferences</button></p></form></section><section><h2>Mailbox connection</h2><p>Gmail read-only access is """ + ("ready to connect." if os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET") else "not configured on this server.") + "</p><a class='button' href='/auth/gmail'>Connect Gmail account</a></section><section><h2>Account</h2><p>Role: Operations Administrator</p><p><a href='/logout'>Log out of CargoVeritas</a></p></section>""",
        }
        content = pages.get(slug, pages["overview"])
        locale = {"Bahasa Melayu": {"Overview": "Gambaran Keseluruhan", "Inbox intelligence": "Kecerdasan Peti Masuk", "Shipment operations": "Operasi Penghantaran", "Verification queue": "Barisan Pengesahan", "Bill Of Lading Vault": "Arkib Bil Muatan", "Settings": "Tetapan"}, "Chinese": {"Overview": "概览", "Inbox intelligence": "收件箱智能", "Shipment operations": "运输作业", "Verification queue": "核验队列", "Bill Of Lading Vault": "提单档案库", "Settings": "设置"}}.get(PREFERENCES["language"], {})
        display_section = locale.get(section, section)
        nav = [("overview", "▦ " + locale.get("Overview", "Overview")), ("inbox-intelligence", "✉ " + locale.get("Inbox intelligence", "Inbox intelligence")), ("shipment-operations", "▱ " + locale.get("Shipment operations", "Shipment operations")), ("verification-queue", "✓ " + locale.get("Verification queue", "Verification queue")), ("bill-of-lading-vault", "▣ " + locale.get("Bill Of Lading Vault", "Bill of Lading vault"))]
        nav_html = "".join("<a class='active' href='/app/" + key + "'>" + label + "</a>" if key == slug else "<a href='/app/" + key + "'>" + label + "</a>" for key, label in nav)
        dark_css = "body{background:#101827;color:#e5edf7}.main{background:#101827}.cards article,section{background:#182335;border-color:#334155}.top p,p,.cards small,th,.category-card small{color:#a9bbcf}td{border-color:#334155;color:#d5deea}.email{border-color:#334155}.search input,.formgrid input,.formgrid select{background:#0f1725;color:#e5edf7;border-color:#475569}.drawer-backdrop{background:rgba(0,0,0,.6)}" if PREFERENCES["theme"] == "Dark mode" else ""
        return """<!doctype html><html><head><meta charset='utf-8'><meta http-equiv='refresh' content='60'><title>CargoVeritas — """ + display_section + """</title><style>*{box-sizing:border-box}body{margin:0;background:#f5f7fa;color:#10243f;font-family:'Times New Roman',Times,serif}.shell{display:grid;grid-template-columns:260px 1fr;min-height:100vh}.side{background:#10243f;color:#d6e2ef;padding:30px 20px}.brand{color:#fff;font-size:26px;font-weight:bold;margin:0 12px 38px}.brand small{display:block;color:#99b0c7;font-size:11px;letter-spacing:1px;margin-top:5px}.side label{display:block;color:#99b0c7;font-size:11px;letter-spacing:1px;padding:0 12px 9px}nav a{display:block;color:#d6e2ef;padding:12px;text-decoration:none;border-radius:8px;margin:3px 0}nav a:hover,nav a.active{background:#204b7c;color:#fff}.navbottom{border-top:1px solid #36506c;margin-top:20px;padding-top:14px}.main{max-width:1280px;width:100%;padding:34px 46px}.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:28px}.top h1{margin:0;font-size:32px}.top p{color:#657891}.button,button{display:inline-block;background:#1769e0;color:#fff;border:0;border-radius:7px;padding:10px 14px;text-decoration:none;font:inherit;cursor:pointer}.muted{background:#e8eef5;color:#254968}.grid{display:grid;gap:20px}.cards{grid-template-columns:repeat(4,1fr);margin-bottom:22px}.cards article,section{background:#fff;border:1px solid #e1e8ef;border-radius:12px;padding:22px}.cards small{display:block;color:#657891}.cards b{display:block;font-size:34px;margin:13px 0}.two{grid-template-columns:1.4fr .8fr}section{margin-bottom:20px}h2{margin-top:0}h3{margin-bottom:8px}p{color:#556b82;line-height:1.45}table{width:100%;border-collapse:collapse;margin:15px 0;font-size:14px}th,td{text-align:left;padding:12px;border-bottom:1px solid #e1e8ef}th{font-size:12px;color:#63758a}.clickable-row{cursor:pointer}.clickable-row:hover td{background:#f1f5f9}.email{border-top:1px solid #e1e8ef;padding:17px 0}.email:first-of-type{border-top:0}.search{display:flex;gap:10px}.search input,.formgrid input,.formgrid select{padding:10px;border:1px solid #cfd9e4;border-radius:6px;font:inherit}.search input{flex:1}.formgrid{display:grid;grid-template-columns:1fr 1fr;gap:15px}.formgrid label{display:grid;gap:6px}.category-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}.category-card{border:1px solid #e1e8ef;border-radius:9px;padding:14px;text-decoration:none}.category-card small{display:block;margin-top:9px;color:#63758a;min-height:32px}.category-card b{display:block;font-size:28px;margin-top:7px}.category-badge{display:inline-block;padding:5px 8px;border:1px solid;border-radius:12px;font-size:12px;font-weight:bold}.category-routing{display:inline-block;margin:0 14px 0 7px;color:#63758a}.cat-bl{background:#eff6ff;color:#1d4ed8;border-color:#bfdbfe}.cat-si{background:#f5f3ff;color:#6d28d9;border-color:#ddd6fe}.cat-invoice{background:#fffbeb;color:#b45309;border-color:#fde68a}.cat-general{background:#f1f5f9;color:#475569;border-color:#cbd5e1}.cat-spam{background:#fef2f2;color:#b91c1c;border-color:#fecaca}.filter-tabs{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}.filter-pill{border:1px solid #cbd5e1;border-radius:16px;padding:7px 10px;text-decoration:none;color:#475569;font-size:13px}.filter-pill.active{background:#1769e0;color:#fff;border-color:#1769e0}.alert td{background:#fef2f2;color:#b91c1c;font-weight:bold}.discrepancy-badge,.match-badge{display:inline-block;padding:4px 7px;border-radius:11px;font-size:12px}.discrepancy-badge{background:#fee2e2;color:#b91c1c;border:1px solid #fecaca}.match-badge{background:#e2f6ee;color:#08745f;border:1px solid #b7e4d6}.warning-banner{background:#fffbeb;border:1px solid #fde68a;color:#92400e;border-radius:7px;padding:11px;margin:10px 0}.pill,.notice{display:inline-block;padding:5px 8px;background:#fff0d8;color:#9a5a00;border-radius:12px}.notice{background:#e2f6ee;color:#08745f}.drawer-backdrop{position:fixed;inset:0;background:rgba(16,36,63,.45);z-index:10}.email-drawer{position:absolute;right:0;top:0;width:min(520px,94vw);height:100%;overflow:auto;background:#fff;padding:30px;box-shadow:-8px 0 30px rgba(0,0,0,.2)}.drawer-close{float:right;font-size:28px;text-decoration:none;color:#10243f}.routing-explainer{background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:12px;line-height:1.45}.email-drawer pre{white-space:pre-wrap;font:inherit;line-height:1.5;background:#f8fafc;border:1px solid #e1e8ef;padding:12px;border-radius:8px}""" + dark_css + """@media(max-width:1000px){.category-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:850px){.shell{display:block}.side{padding:20px}.main{padding:24px 16px;overflow-x:auto}.cards,.two,.formgrid{grid-template-columns:1fr}.top{align-items:flex-start;gap:12px;flex-direction:column}.category-grid{grid-template-columns:1fr}}</style></head><body><div class='shell'><aside class='side'><div class='brand'>⌁ CargoVeritas<small>CONTROL TOWER</small></div><label>WORKSPACE</label><nav>""" + nav_html + """<div class='navbottom'><a href='/settings'>⚙ Settings</a><a href='/logout'>⇥ Log out</a></div></nav></aside><main class='main'><header class='top'><div><h1>""" + display_section + """</h1><p>Company shipping workspace · Avery Logistics</p></div><a class='button' href='/auth/gmail'>Connect mailbox</a></header>""" + content + "</main></div></body></html>"
    def _html(self, message, status=200):
        page = ("<!doctype html><title>CargoVeritas</title>"
                "<body style='font-family:Times New Roman,serif;padding:64px;max-width:720px'>"
                + message + "</body>")
        data = page.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def log_message(self, *_): pass


if __name__ == "__main__":
    load_local_env()
    print("CargoVeritas running at http://127.0.0.1:8000")
    ThreadingHTTPServer(("127.0.0.1", 8000), App).serve_forever()

