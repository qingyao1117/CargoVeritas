"""CargoVeritas local SaaS dashboard. Run: python app.py"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import re
import secrets
import threading
import time
from datetime import datetime, timezone
from html import escape
from io import BytesIO
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import ProxyHandler, Request, build_opener, urlopen
from zipfile import ZIP_DEFLATED, ZipFile


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
        if parsed.path == "/bol/download":
            selected = parse_qs(parsed.query).get("bol", [])
            if not selected:
                self._html("<h1>No BOLs selected</h1><p>Select one or more documents in the BOL vault first.</p><p><a href='/app/bill-of-lading-vault'>Open BOL vault</a></p>", 400)
                return
            source = Path("BL-2026-0918-8821.pdf").read_bytes()
            archive = BytesIO()
            with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
                for bol in selected:
                    safe_name = bol.replace("/", "").replace("\\", "")
                    bundle.writestr(safe_name + ".pdf", source)
            data, content_type, attachment_name = archive.getvalue(), "application/zip", "CargoVeritas-BOLs.zip"
        elif parsed.path.startswith("/bol/") and parsed.path.endswith(".pdf"):
            data, content_type = Path("BL-2026-0918-8821.pdf").read_bytes(), "application/pdf"
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

    def _sync_gmail_to_supabase(self):
        if not CONNECTED_ACCOUNTS:
            raise RuntimeError("Connect a Gmail account first, then return here to sync it.")
        account, token = next(iter(CONNECTED_ACCOUNTS.items()))
        listing = json.load(GOOGLE_HTTP.open(Request(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=10&labelIds=INBOX",
            headers={"Authorization": "Bearer " + token["access_token"]}), timeout=20))
        records = []
        for item in listing.get("messages", []):
            message = json.load(GOOGLE_HTTP.open(Request(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages/" + item["id"] + "?format=metadata&metadataHeaders=From&metadataHeaders=Subject",
                headers={"Authorization": "Bearer " + token["access_token"]}), timeout=20))
            headers = {h["name"].lower(): h["value"] for h in message.get("payload", {}).get("headers", [])}
            subject = headers.get("subject", "(no subject)")
            words = (subject + " " + message.get("snippet", "")).lower()
            category = "settlement" if any(w in words for w in ("invoice", "payment", "settlement")) else "shipping" if any(w in words for w in ("bol", "bill of lading", "shipping", "container", "booking")) else "other"
            received = datetime.fromtimestamp(int(message.get("internalDate", "0")) / 1000, tz=timezone.utc).isoformat()
            amount = re.search(r"(?:RM|MYR)\s*([\d,]+(?:\.\d{2})?)", subject + " " + message.get("snippet", ""), re.I)
            status = "review" if category == "shipping" and any(w in words for w in ("bol", "bill of lading", "draft")) else "processed"
            records.append({"gmail_message_id": message["id"], "gmail_thread_id": message.get("threadId"), "sender": headers.get("from", ""), "subject": subject, "snippet": message.get("snippet", ""), "received_at": received, "classification": category, "processing_status": status, "extraction": {"source": "gmail_metadata", "category": category, "amount_rm": amount.group(1) if amount else None}})
        if records:
            self._supabase_json("/rest/v1/gmail_messages?on_conflict=gmail_message_id", "POST", records)
        return {"account": account, "processed": len(records)}

    def _recent_gmail_messages(self):
        try:
            return self._supabase_json("/rest/v1/gmail_messages?select=gmail_message_id,sender,subject,snippet,classification,processing_status,received_at,extraction&order=received_at.desc&limit=50")
        except Exception:
            return []
    def _workspace(self, section, query):
        slug = section.lower().replace(" ", "-")
        if section == "Settings":
            slug = "settings"
        inbox_rows = self._recent_gmail_messages()
        live_messages = "".join("<div class='email'><b>From:</b> " + escape(row.get("sender") or "Unknown sender") + "<br><b>Subject:</b> " + escape(row.get("subject") or "(no subject)") + "<p>" + escape(row.get("snippet") or "No preview available.") + "</p><span class='pill'>" + escape(row.get("classification") or "other") + "</span></div>" for row in inbox_rows) or "<p>No synced Gmail messages yet. Connect Gmail, then select <b>Sync Gmail now</b>.</p>"
        shipping_rows = [row for row in inbox_rows if row.get("classification") == "shipping"]
        settlement_rows = [row for row in inbox_rows if row.get("classification") == "settlement"]
        review_rows = [row for row in shipping_rows if row.get("processing_status") == "review"]
        shipment_table = "".join("<tr><td>GM-" + escape((row.get("gmail_message_id") or "")[-8:]) + "</td><td>" + escape(row.get("sender") or "Gmail sender") + "</td><td>" + escape(row.get("subject") or "Shipping email") + "</td><td>" + escape(row.get("received_at") or "")[:10] + "</td><td>" + escape(row.get("processing_status") or "processed") + "</td></tr>" for row in shipping_rows) or "<tr><td colspan='5'>No shipping emails have been synced yet.</td></tr>"
        settlement_table = "".join("<tr><td>" + escape(row.get("received_at") or "")[:10] + "</td><td>" + escape(row.get("sender") or "Gmail sender") + "</td><td>" + escape(row.get("subject") or "Settlement email") + "</td><td>RM " + escape(str((row.get("extraction") or {}).get("amount_rm") or "pending extraction")) + "</td><td>Imported</td></tr>" for row in settlement_rows) or "<tr><td colspan='5'>No settlement emails have been synced yet.</td></tr>"
        bol_table = "".join("<tr><td><input type='checkbox' name='bol' value='BOL-" + escape((row.get("gmail_message_id") or "")[-8:]) + "'></td><td>BOL-" + escape((row.get("gmail_message_id") or "")[-8:]) + "</td><td>" + escape(row.get("subject") or "Shipping email") + "</td><td>" + escape(row.get("processing_status") or "processed") + "</td><td><a href='/bol/BOL-" + escape((row.get("gmail_message_id") or "")[-8:]) + ".pdf' download>Download PDF</a></td></tr>" for row in shipping_rows) or "<tr><td colspan='5'>No BOL-related shipping emails have been synced yet.</td></tr>"
        overview_cards = "<div class='grid cards'><article><small>ACTIVE SHIPMENTS</small><b>" + str(len(shipping_rows)) + "</b><small>from synced Gmail</small></article><article><small>EMAILS PROCESSED</small><b>" + str(len(inbox_rows)) + "</b><small>stored in Supabase</small></article><article><small>HUMAN REVIEW</small><b>" + str(len(review_rows)) + "</b><small>BOL drafts needing attention</small></article><article><small>SETTLEMENTS DUE</small><b>" + str(len(settlement_rows)) + "</b><small>settlement emails detected</small></article></div>"
        pages = {
            "overview": overview_cards + "<div class='grid two'><section><h2>Live shipping workload</h2><table><tr><th>BOOKING</th><th>SENDER</th><th>EMAIL SUBJECT</th><th>RECEIVED</th><th>STATE</th></tr>" + shipment_table + "</table><p><a class='button' href='/app/shipment-operations'>Open shipment operations</a></p></section><section><h2>Live processing</h2><p>Records refresh after Gmail sync. Use Inbox intelligence to run an immediate sync.</p><a class='button' href='/app/inbox-intelligence'>Open inbox</a></section></div>",
            "inbox-intelligence": """<section><h2>Incoming email</h2><p>Connect Gmail once, then use Sync Gmail now to bring the latest inbox metadata into Supabase for classification.</p><p><a class='button' href='/gmail/sync'>Sync Gmail now</a></p><form method='get' action='/app/inbox-intelligence' class='search'><input name='q' placeholder='Search sender, booking number, or subject'><button>Search inbox</button></form></section><section><h2>Live mailbox messages</h2>""" + live_messages + "</section>",
            "shipment-operations": "<section><h2>Shipment operations</h2><p>Live shipping records detected from synced Gmail messages.</p><table><tr><th>BOOKING</th><th>CUSTOMER / SENDER</th><th>EMAIL SUBJECT</th><th>RECEIVED</th><th>STATE</th></tr>" + shipment_table + "</table></section>",
            "verification-queue": """<section><h2>Verification queue</h2><p>Human review protects the audit trail when extracted shipping fields disagree.</p><div class='email'><h3>BK-48307 — Container count mismatch</h3><table><tr><th>FIELD</th><th>SHIPPING INSTRUCTION</th><th>DRAFT BOL</th></tr><tr><td>Container count</td><td>2 × 20GP</td><td class='alert'>3 × 20GP</td></tr><tr><td>Gross weight</td><td>18,450 kg</td><td>18,450 kg</td></tr></table><p><a class='button' href='/app/verification-queue?decision=correction'>Request carrier correction</a> <a class='button muted' href='/app/verification-queue?decision=approved'>Approve after review</a></p>""" + ("<p class='notice'>Decision recorded: " + ("carrier correction requested." if query.get("decision") == ["correction"] else "approved after manual verification.") + "</p>" if query.get("decision") else "") + "</div></section>",
            "bill-of-lading-vault": "<section><h2>Audited BOL vault</h2><p>Generated from synced shipping emails. Select one or more BOL records to download.</p><form method='get' action='/bol/download'><table><tr><th>Select</th><th>BOL</th><th>Shipment email</th><th>Audit state</th><th>Individual PDF</th></tr>" + bol_table + "</table><p><button>Download selected BOLs</button></p></form></section>",
            "settlement-calendar": "<section><h2>Settlement calendar</h2><p>Live settlement emails detected from Gmail. Amounts appear when the email contains RM or MYR.</p><table><tr><th>RECEIVED</th><th>SENDER</th><th>EMAIL SUBJECT</th><th>AMOUNT</th><th>STATUS</th></tr>" + settlement_table + "</table></section>",
            "settings": """<section><h2>Company profile</h2><form method='get' action='/settings'><div class='formgrid'><label>Company name<input name='company' value='Avery Logistics'></label><label>Administrator email<input name='email' value='avery@averylogistics.com'></label><label>Preferred language<select name='language'><option>English</option><option>Bahasa Melayu</option><option>Chinese</option></select></label><label>Appearance<select name='theme'><option>Light mode</option><option>Dark mode</option></select></label></div><p><button>Save preferences</button></p></form></section><section><h2>Mailbox connection</h2><p>Gmail read-only access is """ + ("ready to connect." if os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET") else "not configured on this server.") + "</p><a class='button' href='/auth/gmail'>Connect Gmail account</a></section><section><h2>Account</h2><p>Role: Operations Administrator</p><p><a href='/logout'>Log out of CargoVeritas</a></p></section>""",
        }
        content = pages.get(slug, pages["overview"])
        nav = [("overview", "▦ Overview"), ("inbox-intelligence", "✉ Inbox intelligence"), ("shipment-operations", "▱ Shipment operations"), ("verification-queue", "✓ Verification queue"), ("bill-of-lading-vault", "▣ Bill of Lading vault"), ("settlement-calendar", "◴ Settlement calendar")]
        nav_html = "".join("<a class='active' href='/app/" + key + "'>" + label + "</a>" if key == slug else "<a href='/app/" + key + "'>" + label + "</a>" for key, label in nav)
        return """<!doctype html><html><head><meta charset='utf-8'><title>CargoVeritas — """ + section + """</title><style>*{box-sizing:border-box}body{margin:0;background:#f5f7fa;color:#10243f;font-family:'Times New Roman',Times,serif}.shell{display:grid;grid-template-columns:260px 1fr;min-height:100vh}.side{background:#10243f;color:#d6e2ef;padding:30px 20px}.brand{color:#fff;font-size:26px;font-weight:bold;margin:0 12px 38px}.brand small{display:block;color:#99b0c7;font-size:11px;letter-spacing:1px;margin-top:5px}.side label{display:block;color:#99b0c7;font-size:11px;letter-spacing:1px;padding:0 12px 9px}nav a{display:block;color:#d6e2ef;padding:12px;text-decoration:none;border-radius:8px;margin:3px 0}nav a:hover,nav a.active{background:#204b7c;color:#fff}.navbottom{border-top:1px solid #36506c;margin-top:20px;padding-top:14px}.main{max-width:1280px;width:100%;padding:34px 46px}.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:28px}.top h1{margin:0;font-size:32px}.top p{color:#657891}.button,button{display:inline-block;background:#1769e0;color:#fff;border:0;border-radius:7px;padding:10px 14px;text-decoration:none;font:inherit;cursor:pointer}.muted{background:#e8eef5;color:#254968}.grid{display:grid;gap:20px}.cards{grid-template-columns:repeat(4,1fr);margin-bottom:22px}.cards article,section{background:#fff;border:1px solid #e1e8ef;border-radius:12px;padding:22px}.cards small{display:block;color:#657891}.cards b{display:block;font-size:34px;margin:13px 0}.two{grid-template-columns:1.4fr .8fr}section{margin-bottom:20px}h2{margin-top:0}h3{margin-bottom:8px}p{color:#556b82;line-height:1.45}table{width:100%;border-collapse:collapse;margin:15px 0}th,td{text-align:left;padding:12px;border-bottom:1px solid #e1e8ef}th{font-size:12px;color:#63758a}.alert{color:#b4444d;font-weight:bold}.email{border-top:1px solid #e1e8ef;padding:17px 0}.email:first-of-type{border-top:0}.search{display:flex;gap:10px}.search input,.formgrid input,.formgrid select{padding:10px;border:1px solid #cfd9e4;border-radius:6px;font:inherit}.search input{flex:1}.formgrid{display:grid;grid-template-columns:1fr 1fr;gap:15px}.formgrid label{display:grid;gap:6px}.pill,.notice{display:inline-block;padding:5px 8px;background:#fff0d8;color:#9a5a00;border-radius:12px}.notice{background:#e2f6ee;color:#08745f}@media(max-width:850px){.shell{display:block}.side{padding:20px}.main{padding:24px 16px}.cards,.two,.formgrid{grid-template-columns:1fr}.top{align-items:flex-start;gap:12px;flex-direction:column}}</style></head><body><div class='shell'><aside class='side'><div class='brand'>⌁ CargoVeritas<small>CONTROL TOWER</small></div><label>WORKSPACE</label><nav>""" + nav_html + """<div class='navbottom'><a href='/settings'>⚙ Settings</a><a href='/logout'>⇥ Log out</a></div></nav></aside><main class='main'><header class='top'><div><h1>""" + section + """</h1><p>Company shipping workspace · Avery Logistics</p></div><a class='button' href='/auth/gmail'>Connect mailbox</a></header>""" + content + "</main></div></body></html>"
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

