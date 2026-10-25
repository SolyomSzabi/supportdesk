from io import StringIO

from django.core.management import call_command

from tickets import ai
from tickets.ai import TriageResult
from tickets.models import Reply

TICKETS_URL = "/api/tickets/"


def suggest_url(ticket):
    return f"{TICKETS_URL}{ticket.pk}/suggest-reply/"


def fake_triage(title, description):
    return TriageResult(category="technical", priority="medium", summary="Something broke.")


# --- AI reply suggestion -----------------------------------------------------


def test_customer_cannot_request_reply_suggestion(api_client, anna, make_ticket):
    ticket = make_ticket(anna)
    api_client.force_authenticate(anna)

    response = api_client.post(suggest_url(ticket))

    assert response.status_code == 403


def test_agent_gets_reply_draft(api_client, agent, anna, make_ticket, monkeypatch):
    ticket = make_ticket(anna)
    monkeypatch.setattr(ai, "suggest_reply", lambda ticket: "Hi Anna, we are looking into it.")
    api_client.force_authenticate(agent)

    response = api_client.post(suggest_url(ticket))

    assert response.status_code == 200
    assert response.data["draft"] == "Hi Anna, we are looking into it."


def test_reply_draft_is_not_saved(api_client, agent, anna, make_ticket, monkeypatch):
    ticket = make_ticket(anna)
    monkeypatch.setattr(ai, "suggest_reply", lambda ticket: "Draft text")
    api_client.force_authenticate(agent)

    api_client.post(suggest_url(ticket))

    assert Reply.objects.filter(ticket=ticket).count() == 0


def test_reply_suggestion_unavailable_returns_503(
    api_client, agent, anna, make_ticket, monkeypatch
):
    ticket = make_ticket(anna)
    monkeypatch.setattr(ai, "suggest_reply", lambda ticket: None)
    api_client.force_authenticate(agent)

    response = api_client.post(suggest_url(ticket))

    assert response.status_code == 503


# --- apply_triage and the backfill command ----------------------------------


def test_apply_triage_keeps_values_set_by_a_person(anna, make_ticket, monkeypatch):
    ticket = make_ticket(anna, priority="high")
    monkeypatch.setattr(ai, "triage_ticket", fake_triage)

    assert ai.apply_triage(ticket, keep_existing=True) is True

    ticket.refresh_from_db()
    assert ticket.priority == "high"  # kept
    assert ticket.category == "technical"  # was empty, filled in
    assert ticket.ai_summary == "Something broke."


def test_triage_command_fills_only_missing_summaries(anna, make_ticket, settings, monkeypatch):
    settings.GEMINI_API_KEY = "fake-key"
    monkeypatch.setattr(ai, "triage_ticket", fake_triage)
    new_ticket = make_ticket(anna)
    done_ticket = make_ticket(anna, ai_summary="Already summarised.")

    out = StringIO()
    call_command("triage_tickets", delay=0, stdout=out)

    new_ticket.refresh_from_db()
    done_ticket.refresh_from_db()
    assert new_ticket.ai_summary == "Something broke."
    assert done_ticket.ai_summary == "Already summarised."
    assert "1 triaged" in out.getvalue()
