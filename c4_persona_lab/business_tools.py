"""Small, validated tools. The dispatcher is deliberately written by hand."""
from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone

CATALOGUE = [
    {"id": "birthday", "name": "Birthday Mystery Nights", "min_guests": 6, "max_guests": 20, "duration_minutes": 120, "starting_price_usd": 240, "description": "A hosted mystery celebration where friends become the suspects, sleuths and stars."},
    {"id": "city", "name": "City Quests", "min_guests": 2, "max_guests": 12, "duration_minutes": 90, "starting_price_usd": 90, "description": "An exploratory city adventure with collaborative clues and playful discoveries."},
    {"id": "corporate", "name": "Corporate Missions", "min_guests": 10, "max_guests": 60, "duration_minutes": 150, "starting_price_usd": 650, "description": "A shared mission built around communication, puzzle solving and team participation."},
    {"id": "custom", "name": "Custom Story Adventures", "min_guests": None, "max_guests": None, "duration_minutes": None, "starting_price_usd": None, "description": "A bespoke story designed around the guests; scope, capacity, duration and price require a quote."},
]
PRICE_NOTE = "Fictional indicative USD starting prices per group; final scope and quote require the team. This is not a booking or availability check."

TOOL_DESCRIPTIONS = """Available actions (exact names and argument keys):
search_experiences(query: string, guests: integer or null): search the fictional catalogue and optionally filter supported group sizes. Returns matches and facts. A custom option always requires a quote.
estimate_event(experience_id: string, guests: integer): check known capacity and return the indicative group starting price; never confirms booking, availability or final quote.
record_customer_interest(email: string, name: string, message: string): save a local enquiry using customer-provided contact details. Requires a clear request/consent to save or follow up. It does not email anyone.
record_feedback(question: string): save the user's feedback or an unanswered question locally for the team. Use for unsupported questions instead of inventing an answer.
"""

def clean_text(value, field, limit=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{field} must be nonempty text of at most {limit} characters")
    return value.strip()

class RecordStore:
    def __init__(self, path=None):
        self.path = Path(path) if path else Path(__file__).parent / "data" / "plottwist.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, session_id TEXT NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE(session_id, kind, payload))")

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            # sqlite3's transaction context alone does not close Windows handles.
            conn.close()

    def save(self, session_id, kind, payload):
        session_id = clean_text(session_id, "session_id", 128)
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        with self._connect() as conn:
            cursor = conn.execute("INSERT OR IGNORE INTO records(session_id,kind,payload,created_at) VALUES (?,?,?,?)", (session_id, kind, encoded, datetime.now(timezone.utc).isoformat()))
            row = conn.execute("SELECT id FROM records WHERE session_id=? AND kind=? AND payload=?", (session_id, kind, encoded)).fetchone()
            return {"ok": True, "record_id": row["id"], "duplicate": cursor.rowcount == 0, "saved_locally": True, "message_sent": False, "kind": kind}

    def records(self, session_id):
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM records WHERE session_id=? ORDER BY id", (session_id,)).fetchall()
            return [{**dict(row), "payload": json.loads(row["payload"])} for row in rows]

    def clear_session(self, session_id):
        with self._connect() as conn:
            conn.execute("DELETE FROM records WHERE session_id=?", (session_id,))

def search_experiences(query, guests=None):
    query = clean_text(query, "query", 500).lower()
    if guests is not None and (isinstance(guests, bool) or not isinstance(guests, int) or not 1 <= guests <= 10000):
        raise ValueError("guests must be an integer between 1 and 10000")
    aliases = {"birthday": ("birthday", "party", "celebration"), "city": ("city", "quest", "outdoor", "couple"), "corporate": ("corporate", "team", "work", "office"), "custom": ("custom", "bespoke", "personal", "story")}
    specific = {key for key, words in aliases.items() if any(word in query for word in words)}
    matches = []
    for item in CATALOGUE:
        if specific and item["id"] not in specific:
            continue
        if guests is not None and item["min_guests"] is not None and not item["min_guests"] <= guests <= item["max_guests"]:
            continue
        matches.append(dict(item))
    return {"ok": True, "matches": matches, "note": PRICE_NOTE, "no_match_help": "Try a different group size or ask the team for a Custom Story Adventures quote." if not matches else ""}

def estimate_event(experience_id, guests):
    if isinstance(guests, bool) or not isinstance(guests, int) or not 1 <= guests <= 10000:
        raise ValueError("guests must be an integer between 1 and 10000")
    item = next((x for x in CATALOGUE if x["id"] == experience_id), None)
    if item is None:
        raise ValueError("Unknown experience_id; use birthday, city, corporate, or custom")
    if item["min_guests"] is None:
        return {"ok": True, "experience": item["name"], "guests": guests, "requires_quote": True, "starting_price_usd": None, "note": PRICE_NOTE}
    fits = item["min_guests"] <= guests <= item["max_guests"]
    return {"ok": True, "experience": item["name"], "guests": guests, "fits_capacity": fits, "capacity": f"{item['min_guests']}-{item['max_guests']}", "duration_minutes": item["duration_minutes"], "starting_price_usd": item["starting_price_usd"] if fits else None, "indicative_floor_per_guest_usd": round(item["starting_price_usd"] / guests, 2) if fits else None, "note": PRICE_NOTE}

class ToolRegistry:
    def __init__(self, store):
        self.store = store

    def record_customer_interest(self, email, name, message, *, session_id):
        email = clean_text(email, "email", 254).lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ValueError("Please supply a valid email address")
        return self.store.save(session_id, "customer_interest", {"email": email, "name": clean_text(name, "name", 120), "message": clean_text(message, "message")})

    def record_feedback(self, question, *, session_id):
        return self.store.save(session_id, "feedback", {"question": clean_text(question, "question")})

    def execute(self, name, arguments, *, session_id, user_context=""):
        """An allowlist and argument checks prevent arbitrary functions/code execution."""
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be a JSON object")
        if name == "search_experiences":
            return search_experiences(**arguments)
        if name == "estimate_event":
            return estimate_event(**arguments)
        if name == "record_customer_interest":
            email = clean_text(arguments.get("email", ""), "email", 254)
            person = clean_text(arguments.get("name", ""), "name", 120)
            if not email or email.casefold() not in user_context.casefold() or not person or person.casefold() not in user_context.casefold():
                raise ValueError("Use only the name and email the customer actually supplied")
            if re.search(r"\b(?:don't|do not|never)\s+(?:save|record|contact|store)\b", user_context, re.I):
                raise ValueError("The conversation contains a request not to save/contact; clarify consent before saving")
            if not re.search(r"\b(save|record|contact|follow\s?up|follow up|reach|enquir\w*|inquir\w*|interested)\b", user_context, re.I):
                raise ValueError("Ask whether the customer wants their contact details saved for an enquiry")
            return self.record_customer_interest(**arguments, session_id=session_id)
        if name == "record_feedback":
            return self.record_feedback(**arguments, session_id=session_id)
        raise ValueError(f"Unknown tool: {name}")
