"""PlotTwist C3 business agent: routing, memory, actual tools, and reflection.

Live: native Gemini function-calling loop. Demo: deterministic rehearsal
with real local SQLite writes, explicitly identified in every response object.
Official reference: https://ai.google.dev/gemini-api/docs/function-calling
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
import re
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any

from prompts import INSTRUCTIONS, PERSONA, REFLECTION_INSTRUCTIONS, TOOL_SCHEMAS

ROOT = Path(__file__).resolve().parent
LOGGER = logging.getLogger("plottwist.c3")
EMAIL_RE = re.compile(r"[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?(?:\.[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?)+", re.I)
FEEDBACK_RE = re.compile(r"\b(feedback|complaint|complain|disappointed|unhappy|frustrated|loved|enjoyed|confusing|too hard|too easy|too difficult)\b", re.I)
LEAD_RE = re.compile(r"\b(book|booking|reserve|reservation|quote|enquiry|inquiry)\b|\b(sign me up|contact me|interested in|plan (?:a|an|my|our)|get in touch)\b|\b(?:i|we) (?:want|need|would like) (?:a|an|our|my) (?:birthday|city|corporate|custom|mystery|event|party)\b", re.I)
UNKNOWN_RE = re.compile(r"\b(accessib\w*|wheelchair|rain|refund\w*|cancel\w*|discount\w*|available|availability|location|address|parking|allerg\w*|dietary|insurance|payment|pay|opening hours|dogs?|pets?|languages?|age limit|minimum age)\b", re.I)
GENERAL_RE = re.compile(r"\b(hi|hello|hey|thanks|thank|services?|offer|experiences?|price|pricing|cost|budget|birthday|city|quest|corporate|mission|custom|story|team|aseel|noah|jiso|felix|clue|plottwist|about|who|long|duration|people|guests|group|work|different)\b", re.I)


class ConfigurationError(RuntimeError):
    """The requested execution mode or knowledge sources are unavailable."""


def load_knowledge(directory: Path) -> dict[str, str]:
    """Read BOTH required course artefacts; missing/empty files fail clearly."""
    from pypdf import PdfReader

    summary_path = directory / "business_summary.txt"
    pdf_path = directory / "about_business.pdf"
    try:
        summary = summary_path.read_text(encoding="utf-8").strip()
        profile = "\n\n".join(page.extract_text() or "" for page in PdfReader(pdf_path).pages).strip()
    except Exception as exc:
        raise ConfigurationError("Cannot read me/business_summary.txt and me/about_business.pdf. Restore both knowledge files.") from exc
    if not summary or not profile:
        raise ConfigurationError("Both business knowledge files must contain extractable text.")
    return {"business_summary.txt": summary, "about_business.pdf": profile}


def _clean_text(value: Any, field: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string.")
    result = value.strip()
    if len(result) > maximum or "\x00" in result:
        raise ValueError(f"{field} must be at most {maximum} characters and contain no NUL.")
    return result


class EventStore:
    """Parameterized SQLite storage. Every read/write requires a session scope."""

    def __init__(self, path: str | Path):
        path = str(path)
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.lock = threading.RLock()
        self.connection = sqlite3.connect(path, check_same_thread=False, timeout=10)
        self.connection.row_factory = sqlite3.Row
        with self.connection:
            self.connection.execute("PRAGMA journal_mode=WAL")
            self.connection.execute("""CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL,
                kind TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL,
                fingerprint TEXT NOT NULL, UNIQUE(session_id, kind, fingerprint))""")
            self.connection.execute("""CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY, state TEXT NOT NULL)""")

    def append(self, session_id: str, kind: str, payload: dict) -> dict:
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        fingerprint = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        now = datetime.now(timezone.utc).isoformat()
        with self.lock, self.connection:
            cursor = self.connection.execute(
                "INSERT OR IGNORE INTO events(session_id,kind,payload,created_at,fingerprint) VALUES(?,?,?,?,?)",
                (session_id, kind, encoded, now, fingerprint),
            )
            inserted = cursor.rowcount == 1
            row = self.connection.execute(
                "SELECT id FROM events WHERE session_id=? AND kind=? AND fingerprint=?",
                (session_id, kind, fingerprint),
            ).fetchone()
        LOGGER.info("session tool record: kind=%s id=%s status=%s", kind, row["id"], "saved" if inserted else "duplicate")
        # Explicit console evidence for the coursework; contact details stay in the local store.
        print(f"[tool log] {kind}: record #{row['id']} ({'saved' if inserted else 'already_recorded'})")
        return {"ok": True, "id": row["id"], "kind": kind, "status": "saved" if inserted else "already_recorded"}

    def records(self, session_id: str) -> list[dict]:
        with self.lock:
            rows = self.connection.execute(
                "SELECT id,kind,payload,created_at FROM events WHERE session_id=? ORDER BY id", (session_id,)
            ).fetchall()
        return [{"id": row["id"], "kind": row["kind"], "data": json.loads(row["payload"]), "created_at": row["created_at"]} for row in rows]

    def state(self, session_id: str) -> dict:
        with self.lock:
            row = self.connection.execute("SELECT state FROM sessions WHERE session_id=?", (session_id,)).fetchone()
        return json.loads(row["state"]) if row else {"collecting_lead": False, "lead": {}}

    def save_state(self, session_id: str, state: dict) -> None:
        with self.lock, self.connection:
            self.connection.execute(
                "INSERT INTO sessions(session_id,state) VALUES(?,?) ON CONFLICT(session_id) DO UPDATE SET state=excluded.state",
                (session_id, json.dumps(state, ensure_ascii=False)),
            )

    def close(self) -> None:
        with self.lock:
            self.connection.close()


class SessionTools:
    """The required function signatures, with session binding outside model args."""

    def __init__(self, store: EventStore, session_id: str):
        self.store, self.session_id = store, session_id

    def record_customer_interest(self, email: str, name: str, message: str) -> dict:
        try:
            email = _clean_text(email, "email", 254)
            name = _clean_text(name, "name", 120)
            message = _clean_text(message, "message", 4000)
            if not EMAIL_RE.fullmatch(email):
                raise ValueError("email must be a valid email address, for example guest@example.com.")
            return self.store.append(self.session_id, "lead", {"email": email.lower(), "name": name, "message": message})
        except ValueError as exc:
            return {"ok": False, "error": str(exc), "kind": "validation_error"}
        except (sqlite3.Error, OSError):
            LOGGER.exception("Could not save customer enquiry")
            return {"ok": False, "error": "Local storage is unavailable. The enquiry was not saved.", "kind": "storage_error"}

    def record_feedback(self, question: str) -> dict:
        try:
            question = _clean_text(question, "question", 4000)
            return self.store.append(self.session_id, "feedback", {"question": question})
        except ValueError as exc:
            return {"ok": False, "error": str(exc), "kind": "validation_error"}
        except (sqlite3.Error, OSError):
            LOGGER.exception("Could not save customer feedback")
            return {"ok": False, "error": "Local storage is unavailable. The feedback was not saved.", "kind": "storage_error"}


def route_message(message: str, history: list[dict] | None = None, collecting_lead: bool = False) -> str:
    """Three explicit handling classes; word boundaries avoid 'Facebook' -> book."""
    if collecting_lead and re.search(r"\b(no thanks|never mind|nevermind|stop|cancel|do not save|don't save|skip)\b", message, re.I):
        return "lead_collection"
    if FEEDBACK_RE.search(message) or UNKNOWN_RE.search(message):
        return "feedback_unanswered"
    if LEAD_RE.search(message) or EMAIL_RE.search(message):
        return "lead_collection"
    if collecting_lead and not ("?" in message and GENERAL_RE.search(message)):
        return "lead_collection"
    # History makes short replies meaningful even when an API caller supplies no state.
    previous = next((item["content"] for item in reversed(history or []) if item.get("role") == "assistant" and isinstance(item.get("content"), str)), "")
    if re.search(r"(?:your|a) (?:name|email)|name and email", previous, re.I) and "?" not in message:
        return "lead_collection"
    if GENERAL_RE.search(message):
        return "general_question"
    return "feedback_unanswered"


def _history_messages(history: list[dict] | None) -> list[dict]:
    return [{"role": item["role"], "content": item["content"][:4000]}
            for item in (history or [])[-30:]
            if isinstance(item, dict) and item.get("role") in {"user", "assistant"} and isinstance(item.get("content"), str)]


def _extract_lead(message: str, history: list[dict], lead: dict) -> dict:
    """Demo-only conservative field extraction. Live mode can extract with its model."""
    lead = dict(lead)
    emails = EMAIL_RE.findall(message)
    if emails:
        lead["email"] = emails[-1]
    named = re.search(r"(?:my name is|name\s*[:=]|i am|i'm|this is|call me)\s+([A-Za-zÀ-ž][A-Za-zÀ-ž'’ -]{0,100})", message, re.I)
    if named:
        candidate = re.split(r"\b(?:and|email|interested|looking|planning|from|for)\b|[,.;!]", named.group(1), maxsplit=1, flags=re.I)[0].strip()
        if candidate and not re.search(r"\b(book|want|ready|interested|planning|looking|a|an)\b", candidate, re.I):
            lead["name"] = candidate
    previous = next((x["content"] for x in reversed(history) if x["role"] == "assistant"), "")
    if not lead.get("name") and re.search(r"your name|name and", previous, re.I):
        possible_name = EMAIL_RE.sub("", message).strip(" ,.;!\n")
        if re.fullmatch(r"[A-Za-zÀ-ž][A-Za-zÀ-ž'’ -]{0,79}", possible_name) and len(possible_name.split()) <= 5:
            lead["name"] = possible_name
    # Preserve concrete experience notes; an email/name-only reply isn't a request.
    if LEAD_RE.search(message) or re.search(r"\b(birthday|city quest|corporate|custom|guests|people|team of)\b", message, re.I):
        prior = lead.get("message", "")
        if message not in prior:
            lead["message"] = (prior + "\n" + message).strip()[:4000]
    elif lead.get("name") and lead.get("email") and "experience" in previous.lower() and not emails and not named:
        lead["message"] = message
    return lead


class PlotTwistAgent:
    def __init__(self, mode: str = "auto", db_path: str | Path | None = None, *, client: Any = None,
                 knowledge_dir: str | Path | None = None, model: str | None = None):
        if mode not in {"auto", "demo", "live"}:
            raise ConfigurationError("Mode must be auto, demo, or live.")
        try:
            from dotenv import load_dotenv
            load_dotenv(ROOT / ".env", override=False)
        except ImportError:
            pass  # Environment variables also work without python-dotenv.
        key = os.getenv("GEMINI_API_KEY", "").strip()
        if key.lower() in {"your_api_key_here", "your-gemini-api-key", "sk-your-key-here", "replace_me"}:
            key = ""
        self.mode = "live" if mode == "auto" and (key or client is not None) else ("demo" if mode == "auto" else mode)
        if self.mode == "live" and not key and client is None:
            raise ConfigurationError("Live mode requires GEMINI_API_KEY in your local .env or environment. Select demo for offline rehearsal.")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        self.client = client
        if self.mode == "live" and self.client is None:
            try:
                from gemini_client import GeminiClient
            except ImportError as exc:
                raise ConfigurationError("Install requirements.txt to use live mode.") from exc
            self.client = GeminiClient(api_key=key)
        self.knowledge = load_knowledge(Path(knowledge_dir) if knowledge_dir else ROOT / "me")
        self.system_prompt = f"PERSONA\n{PERSONA}\n\nINSTRUCTIONS\n{INSTRUCTIONS}\n\nBUSINESS KNOWLEDGE\n" + "\n\n".join(
            f"SOURCE: {name}\n<source_data>\n{content}\n</source_data>" for name, content in self.knowledge.items())
        self.store = EventStore(db_path or os.getenv("PLOTTWIST_DB", str(ROOT / "data" / "plottwist.sqlite3")))
        self._respond_lock = threading.RLock()

    def tools_for(self, session_id: str) -> SessionTools:
        return SessionTools(self.store, _clean_text(session_id, "session_id", 200))

    def records(self, session_id: str = "demo") -> list[dict]:
        return self.store.records(_clean_text(session_id, "session_id", 200))

    def stats(self, session_id: str = "demo") -> dict:
        records = self.records(session_id)
        return {"leads": sum(x["kind"] == "lead" for x in records), "feedback": sum(x["kind"] == "feedback" for x in records), "total": len(records)}

    def export_records(self, session_id: str, path: str | Path) -> str:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({"session_id": session_id, "records": self.records(session_id)}, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(target.resolve())

    def _call_tool(self, name: str, arguments: str | dict, session_id: str, trace: list, user_text: str) -> dict:
        args = None
        try:
            if isinstance(arguments, str):
                if len(arguments) > 12000:
                    raise ValueError("Tool arguments are too long.")
                args = json.loads(arguments)
            else:
                args = arguments
            expected = {"record_customer_interest": {"email", "name", "message"}, "record_feedback": {"question"}}
            if name not in expected:
                raise ValueError("Unknown tool name.")
            if not isinstance(args, dict) or set(args) != expected[name] or not all(isinstance(v, str) for v in args.values()):
                raise ValueError("Tool arguments do not match the required schema.")
            if name == "record_customer_interest":
                # Extra barrier against a model inventing contact details from the profile.
                if args["email"].casefold() not in user_text.casefold() or args["name"].casefold() not in user_text.casefold():
                    raise ValueError("Name and email must have been provided by this customer.")
            result = getattr(self.tools_for(session_id), name)(**args)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            result = {"ok": False, "kind": "validation_error", "error": str(exc)}
        trace.append({"stage": "tool", "tool": name, "arguments": args if isinstance(args, dict) else None, "result": result, "source": "model" if self.mode == "live" else "deterministic_demo"})
        return result

    def respond(self, message: str, history: list[dict] | None = None, session_id: str = "demo", settings: dict | None = None) -> dict:
        """Return text plus a factual audit trace; never silently switch live to demo."""
        trace: list[dict] = [{"stage": "mode", "mode": self.mode, "label": "Live Gemini" if self.mode == "live" else "Offline deterministic demo — no model call"}]
        try:
            message = _clean_text(message, "message", 4000)
            session_id = _clean_text(session_id, "session_id", 200)
        except ValueError as exc:
            return {"reply": str(exc), "route": "general_question", "trace": trace, "mode": self.mode}
        history = _history_messages(history)
        settings = settings or {}
        with self._respond_lock:
            try:
                state = self.store.state(session_id)
                route = route_message(message, history, state.get("collecting_lead", False))
                trace.append({"stage": "router", "route": route, "method": "three-way heuristic"})
                trace.append({"stage": "knowledge", "sources": list(self.knowledge), "loaded": True})
                if state.get("collecting_lead") and re.search(r"\b(no thanks|never mind|nevermind|stop|cancel|do not save|don't save|skip)\b", message, re.I):
                    state.update(collecting_lead=False, lead={})
                    self.store.save_state(session_id, state)
                    trace.append({"stage": "action", "action": "cancel_pending_enquiry", "source": "application_guard"})
                    return {"reply": "Of course. I have stopped this enquiry. You can still explore our adventures without leaving contact details.", "route": "lead_collection", "trace": trace, "mode": self.mode}
                if route == "lead_collection":
                    state["collecting_lead"] = True
                    # Replay user-only history for explicit contact details on cold starts.
                    if not state.get("lead"):
                        for i, item in enumerate(history):
                            if item["role"] == "user":
                                state["lead"] = _extract_lead(item["content"], history[:i], state.get("lead", {}))
                    state["lead"] = _extract_lead(message, history, state.get("lead", {}))
                if self.mode == "demo":
                    draft = self._demo_reply(message, history, session_id, route, state, trace)
                else:
                    draft = self._live_reply(message, history, session_id, route, state, trace)
                reply = draft
                if settings.get("reflection", True):
                    reply = self._reflect(draft, message, history, route, state, trace)
                self.store.save_state(session_id, state)
                return {"reply": reply, "route": route, "trace": trace, "mode": self.mode}
            except (sqlite3.Error, OSError):
                trace.append({"stage": "error", "kind": "storage_error", "detail": "Local storage unavailable"})
                return {"reply": "Local storage is unavailable. I cannot reliably save an enquiry or feedback right now. Please check the data folder and try again.", "route": "general_question", "trace": trace, "mode": self.mode}

    def _demo_reply(self, message: str, history: list[dict], session_id: str, route: str, state: dict, trace: list) -> str:
        user_text = "\n".join(x["content"] for x in history if x["role"] == "user") + "\n" + message
        if route == "lead_collection":
            if re.search(r"\b(no thanks|never mind|nevermind|stop|cancel|do not save|don't save|skip)\b", message, re.I):
                state.update(collecting_lead=False, lead={})
                return "Of course. I have stopped this enquiry. You can still explore our adventures without leaving contact details."
            lead = state.get("lead", {})
            missing = [field for field in ("name", "email", "message") if not lead.get(field)]
            if missing:
                labels = {"name": "your name", "email": "your email address", "message": "a short note about the experience you want"}
                ask = ", ".join(labels[field] for field in missing)
                invalid = "That email does not look complete. " if "@" in message and not EMAIL_RE.search(message) else ""
                return f"{invalid}Let's open your story file. Please share {ask}. I will save your enquiry locally in this classroom demo; it will not confirm a booking."
            # Include previously collected user-provided fields in provenance check.
            user_text += "\n" + lead["email"] + "\n" + lead["name"]
            result = self._call_tool("record_customer_interest", lead, session_id, trace, user_text)
            if result["ok"]:
                state.update(collecting_lead=False, lead={})
                return f"Your story file is open, {lead['name']}! Your enquiry has been saved locally (reference #{result['id']}). This is a fictional classroom enquiry, not a confirmed booking or a sent email."
            return "I couldn't save your enquiry. " + result["error"]
        if route == "feedback_unanswered":
            result = self._call_tool("record_feedback", {"question": message}, session_id, trace, user_text)
            is_feedback = bool(FEEDBACK_RE.search(message))
            opening = "Thank you for sharing that feedback." if is_feedback else "I don't have a confirmed answer in our business profile, so I won't guess."
            if result["ok"]:
                return f"{opening} I've saved it locally for review (reference #{result['id']}). This classroom demo does not send it to a real team."
            return opening + " I couldn't save it: " + result["error"]
        lower = message.lower()
        if re.search(r"\b(aseel|noah|jiso|felix|who|team members|your team)\b", lower):
            return "Meet the people behind the plot: **Aseel — Story Director**, **Noah — Puzzle Architect**, **Jiso — Experience Producer**, and **Felix — Guest Experience Lead**. I'm Clue, your virtual adventure concierge."
        if "custom" in lower:
            return "**Custom Story Adventures** turn your ideas into a personalized mystery. Pricing is **quote only**; the team needs your group size, occasion, preferred setting, and story preferences before proposing an experience. Want to open an enquiry?"
        if "birthday" in lower and not re.search(r"\b(all|services|offer|compare)\b", lower):
            return "**Birthday Mystery Nights** put the guest of honor inside the story: **6–20 people**, about **2 hours**, from **$240 per group**. This is an indicative fictional price in USD. I can help you prepare an enquiry with your preferred theme and group size."
        if "city" in lower and not re.search(r"\b(all|services|offer|compare)\b", lower):
            return "**City Quests** are clue-led adventures for **2–12 people**, about **90 minutes**, from **$90 per group**. This is an indicative fictional price in USD. Route and availability would need confirmation in a real enquiry."
        if re.search(r"\b(corporate|mission)\b", lower) and not re.search(r"\b(all|services|offer|compare)\b", lower):
            return "**Corporate Missions** turn collaboration into an adventure: **10–60 people**, about **2.5 hours**, from **$650 per group**. This is an indicative fictional price in USD. Tell me your team's size and the occasion to start shaping a brief."
        if re.search(r"\b(hi|hello|hey)\b", lower) and len(message.split()) < 5:
            return "Welcome to PlotTwist. I'm **Clue** — your next adventure starts with a good question. Explore a birthday mystery, a city quest, a corporate mission, or a story created around you. What are you imagining?"
        if re.fullmatch(r"(?:thanks|thank you)[.! ]*", lower):
            return "You're welcome. Every good story starts with a little curiosity."
        return ("**You bring the people. We bring the plot.** PlotTwist creates personalized mystery adventures.\n\n"
                "• **Birthday Mystery Nights:** 6–20 guests · 2 hours · from $240/group.\n"
                "• **City Quests:** 2–12 guests · 90 minutes · from $90/group.\n"
                "• **Corporate Missions:** 10–60 guests · 2.5 hours · from $650/group.\n"
                "• **Custom Story Adventures:** a tailored story · quote only.\n\n"
                "All prices are indicative fictional USD. Which adventure should we explore?")

    def _live_reply(self, message: str, history: list[dict], session_id: str, route: str, state: dict, trace: list) -> str:
        messages = [{"role": "system", "content": self.system_prompt},
                    {"role": "system", "content": f"CURRENT ROUTE: {route}.\nValidated short-term lead fields: {json.dumps(state.get('lead', {}))}"},
                    *history, {"role": "user", "content": message}]
        user_text = "\n".join(x["content"] for x in history if x["role"] == "user") + "\n" + message
        user_text += "\n" + "\n".join(state.get("lead", {}).get(key, "") for key in ("name", "email"))
        for turn in range(6):
            try:
                tool_choice: str | dict = "auto"
                if turn == 0 and route == "feedback_unanswered":
                    tool_choice = {"type": "function", "function": {"name": "record_feedback"}}
                elif turn == 0 and route == "lead_collection" and all(state.get("lead", {}).get(field) for field in ("email", "name", "message")):
                    tool_choice = {"type": "function", "function": {"name": "record_customer_interest"}}
                response = self.client.chat.completions.create(model=self.model, messages=messages,
                    tools=TOOL_SCHEMAS, tool_choice=tool_choice, parallel_tool_calls=False, temperature=0.35)
                reply = response.choices[0].message
                calls = reply.tool_calls or []
                trace.append({"stage": "model", "round": turn + 1, "model": self.model, "tool_calls": len(calls)})
                if not calls:
                    observations = [item["result"] for item in trace if item.get("stage") == "tool"]
                    if observations and not any(item.get("ok") for item in observations):
                        return "I couldn't save this record. " + observations[-1].get("error", "Please try again.") + "\n\n" + (reply.content or "Please check the details and try again.")
                    return reply.content or "I couldn't form a complete reply. Please try rephrasing your question."
                messages.append({"role": "assistant", "content": reply.content, "_native_content": getattr(reply, "native_content", None), "tool_calls": [
                    {"id": call.id, "type": "function", "function": {"name": call.function.name, "arguments": call.function.arguments}} for call in calls]})
                for call in calls:
                    result = self._call_tool(call.function.name, call.function.arguments, session_id, trace, user_text)
                    if call.function.name == "record_customer_interest" and result["ok"]:
                        state.update(collecting_lead=False, lead={})
                    messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
            except Exception as exc:
                # Avoid exposing API keys, endpoint details, or raw remote exceptions.
                trace.append({"stage": "error", "kind": "model_error", "exception_type": type(exc).__name__, "api_code": getattr(exc, "code", None)})
                saved = any(x.get("stage") == "tool" and x["result"].get("ok") for x in trace)
                suffix = " A tool record was already saved locally; its reference is in the activity trace." if saved else ""
                return "The live model request failed. Check your API key, model access, network, and quota, then retry. No offline answer was substituted." + suffix
        trace.append({"stage": "error", "kind": "tool_loop_limit", "max_rounds": 6})
        return "I reached the tool-call limit for this turn. Please review the activity trace before retrying; successful tool records are already saved locally."

    def _reflect(self, draft: str, message: str, history: list[dict], route: str, state: dict, trace: list) -> str:
        if any(item.get("stage") == "error" for item in trace):
            trace.append({"stage": "reflection", "status": "skipped_after_error", "draft": draft, "revised": draft})
            return draft
        if self.mode == "demo":
            revised = draft
            checks = ["No model call; deterministic guardrail audit."]
            if re.search(r"\$\d", draft) and "fictional" not in draft.lower():
                revised += " Prices are indicative fictional USD."
                checks.append("Added the price qualification.")
            else:
                checks.append("Price qualification present or no price quoted.")
            if route == "lead_collection" and state.get("collecting_lead") and not state.get("lead", {}).get("email") and "email" not in revised.lower():
                revised += " What email address should I attach to your local enquiry?"
                checks.append("Added the missing email request.")
            trace.append({"stage": "reflection", "status": "checked", "method": "deterministic_demo", "draft": draft, "revised": revised, "changed": draft != revised, "checks": checks})
            return revised
        try:
            result = self.client.chat.completions.create(model=self.model, temperature=0,
                response_format={"type": "json_object"}, messages=[
                    {"role": "system", "content": self.system_prompt + "\n\n" + REFLECTION_INSTRUCTIONS},
                    {"role": "user", "content": json.dumps({"request": message, "history": history[-8:], "route": route,
                        "lead_fields": state.get("lead", {}), "tool_results": [item for item in trace if item.get("stage") == "tool"], "candidate_reply": draft})}])
            audit = json.loads(result.choices[0].message.content)
            revised = _clean_text(audit.get("revised_reply"), "revised_reply", 8000)
            if not isinstance(audit.get("checks"), list) or not all(isinstance(x, str) for x in audit["checks"]):
                raise ValueError("Reflection checks must be a list of outcome summaries.")
            trace.append({"stage": "reflection", "status": "checked", "method": "model_review", "draft": draft, "revised": revised, "changed": revised != draft, "checks": audit["checks"]})
            return revised
        except Exception as exc:
            trace.append({"stage": "reflection", "status": "failed_draft_retained", "draft": draft, "revised": draft, "exception_type": type(exc).__name__, "api_code": getattr(exc, "code", None)})
            return draft


def build_agent(mode: str = "auto", db_path: str | Path | None = None) -> PlotTwistAgent:
    return PlotTwistAgent(mode=mode, db_path=db_path)
