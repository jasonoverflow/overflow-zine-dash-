"""Minimal JSON API for the daily habit tracker.

Designed for a lightweight mobile client to sync entries, fetch stats,
and stay updated with streak information.
"""
from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request

import tracker

DATA_FILE = Path(os.getenv("TRACKER_DATA_FILE", tracker.DATA_PATH))

app = Flask(__name__)


class BadRequest(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@app.errorhandler(BadRequest)
@app.errorhandler(400)
@app.errorhandler(ValueError)
@app.errorhandler(argparse.ArgumentTypeError)
def handle_bad_request(error: Exception):  # type: ignore[override]
    message = getattr(error, "message", str(error))
    return jsonify({"error": message}), 400


@app.route("/health", methods=["GET"])
def health() -> Any:
    return {"status": "ok"}


@app.route("/entries", methods=["GET"])
def list_entries() -> Any:
    count = request.args.get("count", default=7, type=int)
    entries = tracker.load_entries(DATA_FILE)
    if count > 0:
        entries = entries[-count:]
    return jsonify([tracker.asdict(entry) for entry in entries])


@app.route("/entries", methods=["POST"])
def add_entry() -> Any:
    payload = parse_payload(request.get_json(silent=True) or {})
    entries = tracker.load_entries(DATA_FILE)
    entries = tracker.upsert_entry(entries, payload)
    tracker.save_entries(entries, DATA_FILE)
    return jsonify({"saved": payload.date}), 201


@app.route("/stats", methods=["GET"])
def stats() -> Any:
    entries = tracker.load_entries(DATA_FILE)
    return jsonify(tracker.build_stats(entries))


@app.route("/streak", methods=["GET"])
def streak() -> Any:
    entries = tracker.load_entries(DATA_FILE)
    return jsonify({"streak_days": tracker.compute_streak(entries)})


@app.route("/insights", methods=["GET"])
def insights() -> Any:
    entries = tracker.load_entries(DATA_FILE)
    return jsonify(tracker.correlation_insights(entries))


@app.route("/dashboard", methods=["GET"])
def dashboard() -> Any:
    entries = tracker.load_entries(DATA_FILE)
    stats_payload = tracker.build_stats(entries)
    insight_payload = tracker.correlation_insights(entries)
    return render_template(
        "dashboard.html",
        stats=stats_payload,
        insights=insight_payload,
    )


# ---------- helpers ----------


def parse_payload(payload: Dict[str, Any]) -> tracker.DailyEntry:
    if not payload:
        raise BadRequest("Missing JSON body")

    energy = payload.get("energy")
    if not isinstance(energy, int) or not (1 <= energy <= 10):
        raise BadRequest("`energy` must be an integer between 1 and 10")

    raw_date = payload.get("date")
    if raw_date:
        parsed_date = tracker.parse_date(raw_date)
    else:
        parsed_date = date.today()

    def _text(key: str) -> str:
        value = payload.get(key, "")
        return value if isinstance(value, str) else str(value)

    return tracker.DailyEntry(
        date=parsed_date.isoformat(),
        energy=energy,
        mood_tone=_text("mood_tone"),
        sleep_quality=_text("sleep_quality"),
        side_effects=_text("side_effects"),
        movement=_text("movement"),
        creativity=_text("creativity"),
        chores=_ensure_list(payload.get("chores")),
        skills=_ensure_list(payload.get("skills")),
        victories=_text("victories"),
        struggles=_text("struggles"),
        intention=_text("intention"),
        gratitude=_text("gratitude"),
        notes=_text("notes"),
    )


def _ensure_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
