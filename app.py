"""CargoVeritas local SaaS dashboard. Run: python app.py"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import secrets
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen


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
                token = json.load(urlopen(Request("https://oauth2.googleapis.com/token", data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})))
                profile = json.load(urlopen(Request("https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": "Bearer " + token["access_token"]})))
                CONNECTED_ACCOUNTS[profile["email"]] = token
                self._html("<h1>Gmail connected</h1><p><b>" + profile["email"] + "</b> is now connected with read-only Gmail access.</p><p><a href='/'>Return to CargoVeritas</a></p>")
            except Exception:
                self._html("<h1>Gmail connection failed</h1><p>Check the OAuth redirect URI, Gmail API, and server credentials, then try again.</p>", 502)
            return
        if parsed.path == "/logout":
            self._html("<main style='padding:80px;font-family:Times New Roman,serif'><h1>You have been logged out</h1><p>Your local CargoVeritas session has ended.</p><p><a href='/'>Return to dashboard</a></p></main>")
            return
        if parsed.path == "/settings":
            configured = bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"))
            gmail_status = "Ready to connect" if configured else "Needs server configuration"
            self._html("<main style='max-width:760px;margin:60px auto;padding:32px;font-family:Times New Roman,serif;color:#09284b'><p><a href='/app/overview'>← Back to dashboard</a></p><h1>Workspace settings</h1><p>Manage your company mailbox connection and account preferences.</p><section style='border:1px solid #dce5ef;border-radius:14px;padding:24px;margin-top:24px'><h2>Gmail connection</h2><p><b>Status:</b> " + gmail_status + "</p><p>CargoVeritas requests read-only access and never displays your client secret in the browser.</p><p><a href='/auth/gmail' style='display:inline-block;background:#0d6efd;color:white;padding:11px 16px;border-radius:8px;text-decoration:none'>Connect Gmail account</a></p></section><section style='border:1px solid #dce5ef;border-radius:14px;padding:24px;margin-top:18px'><h2>Account</h2><p>Avery Logistics · Operations Administrator</p><p><a href='/logout'>Log out</a></p></section></main>")
            return
        if parsed.path == "/bol/BL-2026-0918-8821.pdf":
            data, content_type = Path("BL-2026-0918-8821.pdf").read_bytes(), "application/pdf"
        elif parsed.path in ("/", "/index.html") or parsed.path.startswith("/app/"):
            section = parsed.path.rsplit("/", 1)[-1].replace("-", " ").title()
            if parsed.path in ("/", "/index.html"):
                section = "Overview"
            enhancement = """<script>
document.body.innerHTML=document.body.innerHTML.replaceAll("$","RM ");
var nav=document.querySelector("nav");
var settings=document.createElement("button");settings.textContent="⚙  Settings";settings.onclick=function(){location.href="/settings"};nav.appendChild(settings);
var logout=document.createElement("button");logout.textContent="⇥  Log out";logout.onclick=function(){document.body.innerHTML="<main style='padding:80px;font-family:Times New Roman,serif'><h1>You have been logged out</h1><p>Sign in again to access your CargoVeritas workspace.</p><a href='/' style='font-size:18px'>Return to sign in</a></main>"};nav.appendChild(logout);
document.getElementById("connect").onclick=function(){openModal("Connect Gmail mailbox","Authorize a company Gmail inbox so CargoVeritas can read, classify, and verify shipping email.","<p>CargoVeritas uses Google OAuth with the Gmail read-only scope. You will select the company Gmail account on Google's consent screen.</p><a class='primary' href='/auth/gmail' style='display:inline-block;text-decoration:none'>Continue with Google</a>")};
document.querySelectorAll("nav button[data-view]").forEach(function(b){b.onclick=function(){location.href="/app/"+b.dataset.view.toLowerCase().replaceAll(" ","-")}});
var title=document.getElementById("title");if(title)title.textContent=""" + repr(section) + """;
</script>"""
            links = {
                '<button class="active" data-view="Overview">▦ &nbsp; Overview</button>': '<a href="/app/overview" style="display:block;color:#fff;padding:11px 12px;text-decoration:none;background:#204b7c;border-radius:8px">▦ &nbsp; Overview</a>',
                '<button data-view="Inbox intelligence">✉ &nbsp; Inbox intelligence</button>': '<a href="/app/inbox-intelligence" style="display:block;color:#d6e2ef;padding:11px 12px;text-decoration:none">✉ &nbsp; Inbox intelligence</a>',
                '<button data-view="Shipment operations">▱ &nbsp; Shipment operations</button>': '<a href="/app/shipment-operations" style="display:block;color:#d6e2ef;padding:11px 12px;text-decoration:none">▱ &nbsp; Shipment operations</a>',
                '<button data-view="Verification queue">✓ &nbsp; Verification queue</button>': '<a href="/app/verification-queue" style="display:block;color:#d6e2ef;padding:11px 12px;text-decoration:none">✓ &nbsp; Verification queue</a>',
                '<button data-view="Bill of Lading vault">▣ &nbsp; Bill of Lading vault</button>': '<a href="/app/bill-of-lading-vault" style="display:block;color:#d6e2ef;padding:11px 12px;text-decoration:none">▣ &nbsp; Bill of Lading vault</a>',
                '<button data-view="Settlement calendar">◴ &nbsp; Settlement calendar</button>': '<a href="/app/settlement-calendar" style="display:block;color:#d6e2ef;padding:11px 12px;text-decoration:none">◴ &nbsp; Settlement calendar</a>',
                '<button class="filter" id="filter">This week ▾</button>': '<a class="filter" href="/app/shipment-operations?range=this-week" style="text-decoration:none">This week ▾</a>',
                '<button class="link" id="inbox">View all emails →</button>': '<a class="link" href="/app/inbox-intelligence" style="text-decoration:none">View all emails →</a>',
                '<button class="secondary" id="evidence">View evidence</button>': '<a class="secondary" href="/app/verification-queue" style="text-decoration:none">View evidence</a>',
                '<button class="resolve" id="review">Review case</button>': '<a class="resolve" href="/app/verification-queue" style="text-decoration:none">Review case</a>',
                '<button class="link" id="vault">Open vault →</button>': '<a class="link" href="/app/bill-of-lading-vault" style="text-decoration:none">Open vault →</a>',
            }
            page = PAGE.replace("<button class='secondary' data-action='record'>Open record</button>", "<a class='secondary' href='/bol/BL-2026-0918-8821.pdf' target='_blank' download>Open &amp; download PDF</a>").replace("<button class=\"primary\" id=\"connect\">Connect mailbox</button>", "<a class=\"primary\" href=\"/auth/gmail\" style=\"display:inline-block;text-decoration:none\">Connect mailbox</a>")
            for source, target in links.items():
                page = page.replace(source, target)
            page = page.replace("</nav>", '<a href="/settings" style="display:block;color:#d6e2ef;padding:11px 12px;text-decoration:none">⚙ &nbsp; Settings</a><a href="/logout" style="display:block;color:#d6e2ef;padding:11px 12px;text-decoration:none">⇥ &nbsp; Log out</a></nav>')
            page = page.replace("</body>", enhancement + "</body>")
            data, content_type = page.encode(), "text/html; charset=utf-8"
        elif self.path == "/api/dashboard":
            data, content_type = b'{"status":"ready"}', "application/json"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
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

