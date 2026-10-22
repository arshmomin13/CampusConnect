# CampusConnect

A student-built campus event aggregator MVP using FastAPI, SQLAlchemy, SQLite, Jinja2, HTML, CSS, and JavaScript.

## Features

- Browse events in a responsive event-card layout
- Search event titles, descriptions, and locations
- Filter events by category
- Add and delete events through a basic form
- CRUD JSON API for creating, reading, updating, and deleting events
- SQLite persistence
- Interactive API documentation at `/docs`

## Setup (macOS / zsh)

```bash
cd ~/projects/CampusConnect

# Install Python 3.12 if needed
uv python install 3.12

# Create and activate the virtual environment
uv venv --python 3.12
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Run the application server
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 for the site and http://127.0.0.1:8000/docs for API docs.

## Automated Tests

CampusConnect uses `pytest` and FastAPI's test client to verify backend behavior.

Run the test suite from the project root:

```bash
python -m pytest -v
```

The test suite covers:

- Health-check endpoint
- Creating, listing, retrieving, updating, and deleting events
- Handling requests for events that do not exist, including `404 Not Found` responses
- Searching events by title

Run the tests before committing changes to help catch regressions.

## API examples

- `GET /api/events`
- `GET /api/events?q=career`
- `GET /api/events?category=Career`
- `GET /api/events/{event_id}`
- `POST /api/events`
- `PUT /api/events/{event_id}`
- `DELETE /api/events/{event_id}`

Example JSON for `POST /api/events`:

```json
{
  "title": "Sample Tech Career Night",
  "description": "Meet recruiters and alumni.",
  "date": "2026-10-22T18:00:00",
  "location": "Student Union",
  "category": "Career",
  "source_url": "https://example.edu/events/career-night"
}
```

## Important MVP limitations

- The app has no authentication, so it is for local development/demo use only.
- Sample records should be clearly labeled and must not be presented as verified campus events.
- Event source URLs should point to the original listing when real events are added.
- The current SQLite database is created in the working directory as `campusconnect.db`.
