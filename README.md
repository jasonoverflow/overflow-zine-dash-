# Ducks in a Row (Overflow Zine Dash Habit Tracker)

Ducks in a Row is a lightweight CLI and JSON API for tracking daily chores, skill practice, and wellbeing notes in a single JSON file—perfect for pairing with a mobile client or the built-in dashboard.

## Features
- **Chores & skills**: Log what you tackled each day.
- **Daily state**: Capture energy, mood tone, sleep quality, somatic shifts, movement, and creativity/clarity.
- **Reflection**: Celebrate victories, note struggles, set intentions, and record gratitude or extra notes.
- **Stats**: Quick averages, streaks, and a list of distinct chores/skills you track.
- **Correlation insights**: Average energy grouped by mood tone, chores, and skills.
- **Mobile-friendly API & dashboard**: A tiny Flask server exposes JSON endpoints and a `/dashboard` page for visualizing your log.

## Installation
The CLI only requires Python 3.8+. For the JSON API you'll also need Flask:

```bash
python -m venv .venv && source .venv/bin/activate
pip install Flask
```

```bash
python tracker.py --help
```

## Usage
Add a daily entry (fields are all optional except `--energy`):

```bash
python tracker.py add \
  --energy 7 \
  --mood-tone joyful \
  --sleep-quality "solid 8 hours" \
  --movement "short walk + stretching" \
  --creativity "light brainstorming" \
  --side-effects "mild headache" \
  --chore dishes --chore laundry \
  --skill guitar --skill writing \
  --victories "finished the weekly review" \
  --struggles "afternoon dip" \
  --intention "slow morning, hydrate" \
  --gratitude "sunny weather" \
  --notes "felt lighter after walk"
```

List recent entries (default: last 7 days; use `--count 0` for all):

```bash
python tracker.py list --count 7
```

View quick stats:

```bash
python tracker.py stats
```

## JSON API & Dashboard (for phone apps)
Run the Flask server to sync logs with a mobile client or to view the Ducks in a Row dashboard. By default it uses the same `data/entries.json` file as the CLI; override with `TRACKER_DATA_FILE` if needed.

```bash
export FLASK_APP=api_server.py
flask run --host 0.0.0.0 --port 5000
```

### Endpoints
- `GET /health` — simple readiness check.
- `GET /entries?count=7` — return the most recent entries (all if `count=0`).
- `POST /entries` — upsert a daily entry with a JSON body. Only `energy` (1–10) is required.
- `GET /stats` — returns averages, distinct chores/skills, best energy day, and current streak.
- `GET /streak` — returns the current streak in days.
- `GET /insights` — returns correlations showing average energy grouped by mood tone, chore, and skill.
- `GET /dashboard` — renders the Ducks in a Row dashboard that visualizes stats and correlations.

### Example mobile payload
Send JSON like this to `POST /entries`:

```json
{
  "date": "2024-08-05",
  "energy": 7,
  "mood_tone": "bright",
  "sleep_quality": "solid 8 hours",
  "movement": "walked 4k steps",
  "creativity": "drafted two ideas",
  "chores": ["dishes", "laundry"],
  "skills": ["guitar", "writing"],
  "victories": "shipped portfolio update",
  "struggles": "afternoon crash",
  "intention": "slow morning, hydrate",
  "gratitude": "sunny weather",
  "notes": "felt lighter after walk"
}
```

### Data storage
Entries are stored in `data/entries.json` by default. You can point to another file with `--data-file`.

### Tips for daily logging
- Keep inputs short so you can log quickly each evening.
- Use consistent wording for chores and skills to make stats more meaningful.
- Re-run `add` for the same date to update an entry.

