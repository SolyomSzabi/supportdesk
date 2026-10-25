# SupportDesk AI

A B2B customer support portal where companies open tickets and support agents answer them, with an LLM that triages new tickets and drafts replies for agents.

I built it to learn Django, DRF and Vue, and to try LLM integration on a problem I know well: I handle 50+ support cases a day at Teleperformance (Booking.com customer support).

**Live demo:** https://supportdesk-547027748023.europe-west1.run.app
(first load can take a few seconds while the container starts)

| Role | Username | Password | What you can do |
| --- | --- | --- | --- |
| Customer (Acme Hotels) | `anna.acme` | `test12345` | See your company's tickets, open tickets, reply |
| Support agent | `tom.agent` | `test12345` | See all tickets, change status, get AI reply drafts |

## Features

- **Multi-tenant access control.** Customers only see their own company's tickets. Another company's ticket returns 404, not 403, so its existence isn't leaked. Only agents can change or delete tickets.
- **AI triage.** When a ticket is created, Gemini assigns a category, a priority and a one-sentence summary.
- **AI reply drafts.** Agents can ask for a draft based on the ticket and the conversation so far. The draft goes into the reply box for the agent to edit. It is never sent automatically.
- **Ticket list** with search, filters, pagination and ordering by severity.
- **Backfill command:** `python manage.py triage_tickets` triages older tickets, respecting the free-tier rate limit and keeping values a person already set.

## Stack

| Layer | Technology |
| --- | --- |
| Backend | Python 3.14, Django 6.1, Django REST Framework, JWT (SimpleJWT), django-filter |
| Database | PostgreSQL 16 (Docker locally, Neon in production) |
| AI | Google Gemini via the `google-genai` SDK, Pydantic for structured output |
| Frontend | Vue 3, TypeScript, Vue Router, Vite |
| Quality | pytest (26 tests), Ruff, GitHub Actions |
| Deploy | Docker multi-stage build, Gunicorn, WhiteNoise, Google Cloud Run |

## How the AI part works

All AI code lives in [`tickets/ai.py`](tickets/ai.py), separate from the views, so the provider can be swapped and the tests can replace it.

- **Structured output.** Triage asks for JSON matching a Pydantic model (`TriageResult`) with fixed category and priority values, then validates the response again. Invalid output is rejected, not saved.
- **AI is optional.** A missing key, a timeout, a rate limit or invalid output never blocks ticket creation: the ticket is saved without AI fields and the error is logged. The reply endpoint returns `503` when AI is unavailable.
- **Prompt injection.** Ticket text is customer input. It is passed separately from the instructions, wrapped in tags, and the model is told to treat it as data. The strict schema also limits what it can return.
- **Human in the loop.** Drafts are only suggestions.

Things I learned while testing it live:

- Mocked tests passed, but the first real call failed with `504 DEADLINE_EXCEEDED`. The SDK was forwarding my timeout to Google as a server-side deadline, which the "thinking" model exceeded. I switched to a client-side timeout only. Mocked tests can't catch this kind of integration problem, so external services also need a live test.
- An early reply draft said *"I have forwarded this to our billing team"*, an action nobody took. A "never claim X" rule didn't fix it. Rewriting it as a positive instruction with an example and a reason ("you are writing a draft before anything has happened, describe next steps in the future tense") did.
- Ordering by priority was alphabetical because the field is text. It now orders by a database-level `Case/When` rank, which still works with pagination. There is a test for it.

## Running locally

Requirements: Python 3.12+, Node 20+, Docker.

```bash
git clone https://github.com/SolyomSzabi/supportdesk.git
cd supportdesk
docker compose up -d                 # PostgreSQL

python -m venv .venv
source .venv/bin/activate            # Windows Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
SECRET_KEY=any-long-random-string-at-least-32-characters
DEBUG=True
DATABASE_URL=postgres://supportdesk:supportdesk@127.0.0.1:5432/supportdesk
GEMINI_API_KEY=            # optional; without it the app works, just without AI
GEMINI_MODEL=gemini-3.5-flash-lite
```

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver           # API on :8000

cd frontend
npm install
npm run dev                          # app on http://localhost:5173 (proxies /api to Django)
```

Tests and lint:

```bash
pytest
ruff check . && ruff format --check .
```

The tests never call the real Gemini API. It is mocked, so they are fast, free and don't depend on rate limits.

## API overview

| Method | Endpoint | Who |
| --- | --- | --- |
| POST | `/api/auth/token/`, `/api/auth/token/refresh/` | anyone |
| GET | `/api/me/` | logged in |
| GET, POST | `/api/tickets/` (`?status=`, `?priority=`, `?category=`, `?search=`, `?ordering=-priority_rank`) | logged in, scoped by company |
| GET | `/api/tickets/{id}/` | logged in, scoped by company |
| PATCH, DELETE | `/api/tickets/{id}/` | agents |
| POST | `/api/tickets/{id}/reply/` | logged in, scoped by company |
| POST | `/api/tickets/{id}/suggest-reply/` | agents |

## Deployment

One container serves everything: the Dockerfile builds the Vue app in a Node stage, then Django serves the API, the admin and the built frontend (via WhiteNoise) under Gunicorn. Cloud Run scales to zero when idle. Configuration comes from environment variables, so the same image runs in CI and production. CI runs lint, the tests against a real PostgreSQL service, the frontend type-check and build, and a Docker image build on every push.

## Known limitations and next steps

- Secrets are passed as Cloud Run environment variables. Next step: Secret Manager.
- Migrations run at container start, which is fine for one instance but should be a separate release job at scale.
- AI calls are synchronous (around 2 seconds on ticket creation). With more traffic they should move to a background queue (e.g. Celery or Cloud Tasks).
- The Gemini free tier may use inputs to improve Google's models, which is fine for demo data. Real customer data would need the paid tier.
- No email notifications or file attachments yet.

## How I used AI tools

I built this with Claude as a pair programmer: for planning, explaining Django and DRF concepts I hadn't used before, and drafting code. I ran, tested and debugged everything myself. The live issues above (the 504 timeout, the hallucinated "I have forwarded" draft, the alphabetical ordering) were found by testing the running app, not by the AI.