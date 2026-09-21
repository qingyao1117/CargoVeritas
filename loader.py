#!/usr/bin/env python3
"""
loader.py — one-import access to the SDOC hackathon inbox (participants).

Works two ways with the same API:

  # A) local files (static bundle):
  from loader import Inbox
  inbox = Inbox("data")                 # folder with inbox/ + attachments/
  for email in inbox:
      print(email["email_id"], email["subject"])
      for path in email["attachments"]:
          text = inbox.read_text(path)  # SI/BL .txt content

  # B) the HTTP server (docker):
  inbox = Inbox("http://localhost:8080")
  ...                                    # identical loop

No third-party dependencies for the plain-text path (only stdlib). Reading
PDF/DOCX/XLSX attachments is up to your pipeline — see read_bytes().

You do NOT have ground truth. Produce a submission dict shaped like
sample_submission.json and either score it with score_cli.py (if organizers
gave you a ground_truth.json) or POST it to the server's /submit.
"""
import json
import os
import re
import urllib.request
from pathlib import Path


GROSS_WEIGHT_PATTERN = re.compile(
    r'(?:Gross\s*We|G\.?W\.?|Berat\s*Kasar|\u6bdb\u91cd)[^\d\n]*?[:=]?\s*'
    r'([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)', re.I)


def extract_two_column_fields(text):
    """Read shortened English/Malay/Chinese labels from any tabular document text."""
    prefixes = (
        ("shipper", ("shipper", "pengirim", "\u53d1\u8d27")),
        ("consignee", ("consignee", "to the order of", "penerima", "\u6536\u8d27")),
        ("notify_party", ("notify", "pihak dimaklumkan", "\u901a\u77e5")),
        ("port_of_loading", ("load", "port of lo", "pol", "pelabuhan memuat", "\u88c5\u8d27")),
        ("port_of_discharge", ("discharge", "port of dis", "pod", "pelabuhan memunggah", "\u5378\u8d27")),
        ("container_count", ("no. of c", "no of c", "container", "kontena", "\u7bb1\u6570")),
        ("gross_weight_kg", ("gross w", "g.w", "gw", "berat kasar", "\u6bdb\u91cd")),
    )
    values = {}
    for line in text.splitlines():
        cells = [cell.strip() for cell in re.split(r"\s*\|\s*|\t+", line)]
        if len(cells) < 2:
            match = re.match(r"^\s*(.+?)(?:\s{2,})(.+?)\s*$", line)
            cells = [match.group(1).strip(), match.group(2).strip()] if match else cells
        if len(cells) < 2 or not cells[1]:
            continue
        key = re.sub(r"[\s\.:;|\-]+$", "", cells[0].lower())
        for field, aliases in prefixes:
            if key.startswith(aliases):
                value = " | ".join(cell for cell in cells[1:] if cell)
                if field in ("container_count", "gross_weight_kg") and not re.search(r"\d", value):
                    continue
                values[field] = value
                break
    return values


class Inbox:
    def __init__(self, source):
        self.source = source.rstrip("/")
        self.is_http = self.source.startswith("http://") or self.source.startswith("https://")

    # -- listing ---------------------------------------------------------
    def emails(self):
        """Return the list of email records (dicts)."""
        if self.is_http:
            return self._get_json("/emails")
        inbox_dir = Path(self.source) / "inbox"
        return [json.loads(p.read_text())
                for p in sorted(inbox_dir.glob("email_*.json"))]

    def __iter__(self):
        return iter(self.emails())

    def get(self, email_id):
        if self.is_http:
            return self._get_json(f"/emails/{email_id}")
        return json.loads((Path(self.source) / "inbox" / f"{email_id}.json").read_text())

    # -- attachments -----------------------------------------------------
    def read_bytes(self, att_path):
        """Raw bytes of an attachment. att_path is the string exactly as it
        appears in email['attachments'] (e.g. 'attachments/email_004_SI.txt')."""
        if self.is_http:
            return self._get_bytes("/" + att_path.lstrip("/"))
        return (Path(self.source) / att_path).read_bytes()

    def read_text(self, att_path, encoding="utf-8"):
        return self.read_bytes(att_path).decode(encoding, errors="replace")

    # -- submission ------------------------------------------------------
    def submit(self, submission):
        """POST a submission to the server and return the scoreboard. HTTP only."""
        if not self.is_http:
            raise RuntimeError("submit() needs an HTTP source; run the docker server")
        data = json.dumps(submission).encode()
        req = urllib.request.Request(self.source + "/submit", data=data,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())

    def sample_submission(self):
        if self.is_http:
            return self._get_json("/sample_submission")
        return json.loads((Path(self.source) / "sample_submission.json").read_text())

    # -- http helpers ----------------------------------------------------
    def _get_json(self, path):
        with urllib.request.urlopen(self.source + path) as r:
            return json.loads(r.read())

    def _get_bytes(self, path):
        with urllib.request.urlopen(self.source + path) as r:
            return r.read()


if __name__ == "__main__":
    # tiny smoke test / demo against a local bundle
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else "data"
    inbox = Inbox(src)
    ems = inbox.emails()
    print(f"{len(ems)} emails from {src}")
    docs = [e for e in ems if e["attachments"]]
    print(f"{len(docs)} have attachments; example: {docs[0]['email_id']}")
    for a in docs[0]["attachments"]:
        head = inbox.read_text(a)[:60].replace("\n", " ") if a.endswith(".txt") else "(binary)"
        print(f"  {a}: {head}")
