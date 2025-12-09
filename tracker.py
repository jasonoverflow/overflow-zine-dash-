"""
Ducks in a Row: daily habit tracker for chores, skill practice, and mood/state logging.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from statistics import mean
from typing import Dict, List

DATA_PATH = Path("data/entries.json")


@dataclass
class DailyEntry:
    """Container for a daily log entry."""

    date: str
    energy: int
    mood_tone: str
    sleep_quality: str
    side_effects: str
    movement: str
    creativity: str
    chores: List[str]
    skills: List[str]
    victories: str
    struggles: str
    intention: str
    gratitude: str
    notes: str

    @staticmethod
    def from_args(args: argparse.Namespace) -> "DailyEntry":
        return DailyEntry(
            date=args.date.isoformat(),
            energy=args.energy,
            mood_tone=args.mood_tone,
            sleep_quality=args.sleep_quality,
            side_effects=args.side_effects,
            movement=args.movement,
            creativity=args.creativity,
            chores=args.chores or [],
            skills=args.skills or [],
            victories=args.victories,
            struggles=args.struggles,
            intention=args.intention,
            gratitude=args.gratitude,
            notes=args.notes,
        )


# ---------- Helpers ----------

def ensure_data_path(path: Path = DATA_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]\n", encoding="utf-8")


def load_entries(path: Path = DATA_PATH) -> List[DailyEntry]:
    ensure_data_path(path)
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return [DailyEntry(**entry) for entry in data]


def save_entries(entries: List[DailyEntry], path: Path = DATA_PATH) -> None:
    ensure_data_path(path)
    serialized = [asdict(entry) for entry in entries]
    with path.open("w", encoding="utf-8") as fh:
        json.dump(serialized, fh, indent=2)
        fh.write("\n")


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Dates must be in YYYY-MM-DD format") from exc


# ---------- Commands ----------

def upsert_entry(entries: List[DailyEntry], new_entry: DailyEntry) -> List[DailyEntry]:
    """Add or replace a daily entry, preserving date uniqueness and sort order."""

    existing_dates = {entry.date for entry in entries}
    if new_entry.date in existing_dates:
        entries = [entry for entry in entries if entry.date != new_entry.date]

    entries.append(new_entry)
    entries.sort(key=lambda entry: entry.date)
    return entries


def add_entry(args: argparse.Namespace) -> None:
    entries = load_entries(args.data_file)
    new_entry = DailyEntry.from_args(args)

    entries = upsert_entry(entries, new_entry)
    save_entries(entries, args.data_file)
    print(f"Saved daily entry for {new_entry.date}.")


def list_entries(args: argparse.Namespace) -> None:
    entries = load_entries(args.data_file)
    if args.count > 0:
        entries = entries[-args.count :]

    if not entries:
        print("No entries recorded yet. Use `add` to log your day.")
        return

    for entry in entries:
        print("-" * 60)
        print(f"Date: {entry.date}")
        print(f" Energy: {entry.energy}/10 | Mood tone: {entry.mood_tone}")
        print(f" Sleep: {entry.sleep_quality}")
        print(f" Movement: {entry.movement}")
        print(f" Creativity / Clarity: {entry.creativity}")
        print(f" Side effects or somatic shifts: {entry.side_effects}")
        if entry.chores:
            print(f" Chores: {', '.join(entry.chores)}")
        if entry.skills:
            print(f" Skills: {', '.join(entry.skills)}")
        if entry.victories:
            print(f" Small victories: {entry.victories}")
        if entry.struggles:
            print(f" Struggles: {entry.struggles}")
        if entry.intention:
            print(f" Tomorrow's intention: {entry.intention}")
        if entry.gratitude:
            print(f" Gratitude: {entry.gratitude}")
        if entry.notes:
            print(f" Notes: {entry.notes}")
    print("-" * 60)


def stats(args: argparse.Namespace) -> None:
    entries = load_entries(args.data_file)
    stats_payload = build_stats(entries)

    if not entries:
        print("No entries recorded yet. Stats will appear after your first log.")
        return

    print(f"Entries recorded: {stats_payload['entries']}")
    print(f"Average energy: {stats_payload['average_energy']:.2f}/10")
    print(
        "Distinct chores tracked: "
        f"{', '.join(stats_payload['distinct_chores']) if stats_payload['distinct_chores'] else 'None yet'}"
    )
    print(
        "Distinct skills tracked: "
        f"{', '.join(stats_payload['distinct_skills']) if stats_payload['distinct_skills'] else 'None yet'}"
    )
    print(f"Current streak: {stats_payload['streak_days']} day(s)")
    if stats_payload["high_energy_day"]:
        print(
            f"Best energy day: {stats_payload['high_energy_day']['date']} "
            f"({stats_payload['high_energy_day']['energy']}/10)"
        )


def build_stats(entries: List[DailyEntry]) -> dict:
    if not entries:
        return {
            "entries": 0,
            "average_energy": 0.0,
            "distinct_chores": [],
            "distinct_skills": [],
            "streak_days": 0,
            "high_energy_day": None,
        }

    avg_energy = mean(entry.energy for entry in entries)
    unique_chores = sorted({chore for entry in entries for chore in entry.chores})
    unique_skills = sorted({skill for entry in entries for skill in entry.skills})
    streak_days = compute_streak(entries)
    high_energy_day = max(entries, key=lambda entry: entry.energy)

    return {
        "entries": len(entries),
        "average_energy": avg_energy,
        "distinct_chores": unique_chores,
        "distinct_skills": unique_skills,
        "streak_days": streak_days,
        "high_energy_day": asdict(high_energy_day),
    }


def correlation_insights(entries: List[DailyEntry]) -> dict:
    """Summaries that relate energy to moods, chores, and skills."""

    def _aggregate(keys: List[str], label: str) -> list:
        totals: Dict[str, List[int]] = {}
        for entry in entries:
            for key in keys:
                value = getattr(entry, key)
                if isinstance(value, list):
                    for item in value:
                        totals.setdefault(item, []).append(entry.energy)
                elif value:
                    totals.setdefault(value, []).append(entry.energy)
        results = [
            {
                label: name or "unspecified",
                "average_energy": mean(values),
                "count": len(values),
            }
            for name, values in totals.items()
            if values
        ]
        return sorted(results, key=lambda row: row["average_energy"], reverse=True)

    return {
        "mood_energy": _aggregate(["mood_tone"], "mood"),
        "chore_energy": _aggregate(["chores"], "name"),
        "skill_energy": _aggregate(["skills"], "name"),
    }


def compute_streak(entries: List[DailyEntry]) -> int:
    if not entries:
        return 0

    sorted_entries = sorted(entries, key=lambda entry: entry.date, reverse=True)
    expected = datetime.strptime(sorted_entries[0].date, "%Y-%m-%d").date()
    streak = 0

    for entry in sorted_entries:
        entry_date = datetime.strptime(entry.date, "%Y-%m-%d").date()
        if entry_date == expected:
            streak += 1
            expected = expected.fromordinal(expected.toordinal() - 1)
        else:
            break
    return streak


# ---------- Parser ----------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Track chores, skills, and daily state in a lightweight JSON log.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=DATA_PATH,
        help="Path to the JSON file used for storing daily entries.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="Add or update a daily entry.")
    add.add_argument("--date", type=parse_date, default=date.today(), help="Date of the entry.")
    add.add_argument("--energy", type=int, required=True, choices=range(1, 11), help="Energy level (1-10).")
    add.add_argument("--mood-tone", default="neutral", help="Overall mood tone (joyful, heavy, neutral, etc.).")
    add.add_argument("--sleep-quality", default="", help="Sleep quality notes.")
    add.add_argument("--side-effects", default="", help="Any somatic shifts or medication side effects.")
    add.add_argument("--movement", default="", help="Movement or activity, even small wins.")
    add.add_argument("--creativity", default="", help="Creativity / clarity / overflow feelings.")
    add.add_argument("--chore", dest="chores", action="append", help="A chore you touched today.")
    add.add_argument("--skill", dest="skills", action="append", help="A skill you practiced.")
    add.add_argument("--victories", default="", help="Small victories worth celebrating.")
    add.add_argument("--struggles", default="", help="Struggles or friction points.")
    add.add_argument("--intention", default="", help="Set an intention for tomorrow.")
    add.add_argument("--gratitude", default="", help="Something you are grateful for.")
    add.add_argument("--notes", default="", help="Extra notes or feelings.")
    add.set_defaults(func=add_entry)

    list_cmd = subparsers.add_parser("list", help="Show recent entries.")
    list_cmd.add_argument("--count", type=int, default=7, help="Number of recent entries to display. Use 0 for all.")
    list_cmd.set_defaults(func=list_entries)

    stats_cmd = subparsers.add_parser("stats", help="Summarize your log so far.")
    stats_cmd.set_defaults(func=stats)

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
