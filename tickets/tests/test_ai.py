from types import SimpleNamespace

from tickets import ai
from tickets.ai import TriageResult
from tickets.models import Ticket

TICKETS_URL = "/api/tickets/"
NEW_TICKET = {
    "title": "Charged twice this month",
    "description": "We see two identical payments for the October invoice.",
}


def fake_client_returning(text):
    """A stand-in for the Gemini client whose model always answers with `text`."""

    def generate_content(**kwargs):
        return SimpleNamespace(text=text)

    return SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))


# --- Triage on ticket creation ---------------------------------------------


def test_new_ticket_gets_ai_triage(api_client, anna, monkeypatch):
    monkeypatch.setattr(
        ai,
        "triage_ticket",
        lambda title, description: TriageResult(
            category="billing", priority="high", summary="Customer was charged twice."
        ),
    )
    api_client.force_authenticate(anna)

    response = api_client.post(TICKETS_URL, NEW_TICKET, format="json")

    assert response.status_code == 201
    assert response.data["category"] == "billing"
    assert response.data["priority"] == "high"
    ticket = Ticket.objects.get(pk=response.data["id"])
    assert ticket.ai_summary == "Customer was charged twice."


def test_ticket_is_created_when_ai_is_unavailable(api_client, anna, monkeypatch):
    monkeypatch.setattr(ai, "triage_ticket", lambda title, description: None)
    api_client.force_authenticate(anna)

    response = api_client.post(TICKETS_URL, NEW_TICKET, format="json")

    assert response.status_code == 201
    ticket = Ticket.objects.get(pk=response.data["id"])
    assert ticket.ai_summary == ""
    assert ticket.category == ""


# --- The AI service itself ---------------------------------------------------


def test_triage_is_skipped_without_api_key(settings):
    settings.GEMINI_API_KEY = ""

    assert ai.triage_ticket("Title", "Description") is None


def test_triage_returns_none_when_api_fails(settings, monkeypatch):
    settings.GEMINI_API_KEY = "fake-key"

    def broken_client():
        raise RuntimeError("API is down")

    monkeypatch.setattr(ai, "_client", broken_client)

    assert ai.triage_ticket("Title", "Description") is None


def test_triage_parses_valid_model_output(settings, monkeypatch):
    settings.GEMINI_API_KEY = "fake-key"
    answer = '{"category": "technical", "priority": "urgent", "summary": "Sync is down."}'
    monkeypatch.setattr(ai, "_client", lambda: fake_client_returning(answer))

    result = ai.triage_ticket("Sync stopped", "Reservations are not syncing.")

    assert result == TriageResult(category="technical", priority="urgent", summary="Sync is down.")


def test_triage_rejects_invalid_model_output(settings, monkeypatch):
    settings.GEMINI_API_KEY = "fake-key"
    # "food" is not an allowed category, so validation must fail.
    answer = '{"category": "food", "priority": "high", "summary": "Lunch order."}'
    monkeypatch.setattr(ai, "_client", lambda: fake_client_returning(answer))

    assert ai.triage_ticket("Lunch", "Where is my pizza?") is None
