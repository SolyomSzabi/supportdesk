from tickets.models import Ticket

TICKETS_URL = "/api/tickets/"


def ticket_url(ticket):
    return f"{TICKETS_URL}{ticket.pk}/"


# --- Authentication -------------------------------------------------------


def test_unauthenticated_request_is_rejected(api_client, db):
    response = api_client.get(TICKETS_URL)

    assert response.status_code == 401


def test_jwt_login_returns_tokens_that_work(api_client, anna):
    response = api_client.post(
        "/api/auth/token/", {"username": "anna", "password": "pass12345"}, format="json"
    )
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    assert api_client.get(TICKETS_URL).status_code == 200


# --- Company scoping -------------------------------------------------------


def test_customer_sees_only_own_company_tickets(api_client, anna, lisa, make_ticket):
    make_ticket(anna, title="Acme ticket")
    make_ticket(lisa, title="Sunrise ticket")
    api_client.force_authenticate(anna)

    response = api_client.get(TICKETS_URL)

    titles = [t["title"] for t in response.data["results"]]
    assert titles == ["Acme ticket"]


def test_customer_gets_404_for_other_company_ticket(api_client, anna, lisa, make_ticket):
    other = make_ticket(lisa)
    api_client.force_authenticate(anna)

    response = api_client.get(ticket_url(other))

    assert response.status_code == 404


def test_customer_cannot_reply_to_other_company_ticket(api_client, anna, lisa, make_ticket):
    other = make_ticket(lisa)
    api_client.force_authenticate(anna)

    response = api_client.post(f"{ticket_url(other)}reply/", {"body": "Hi"}, format="json")

    assert response.status_code == 404


def test_agent_sees_all_tickets(api_client, agent, anna, lisa, make_ticket):
    make_ticket(anna)
    make_ticket(lisa)
    api_client.force_authenticate(agent)

    response = api_client.get(TICKETS_URL)

    assert response.data["count"] == 2


# --- Creating tickets and replies -----------------------------------------


def test_create_ticket_sets_company_and_author(api_client, anna, sunrise):
    api_client.force_authenticate(anna)

    response = api_client.post(
        TICKETS_URL,
        # The client tries to set another company - it must be ignored.
        {"title": "Printer offline", "description": "It does not print.", "company": sunrise.pk},
        format="json",
    )

    assert response.status_code == 201
    ticket = Ticket.objects.get(pk=response.data["id"])
    assert ticket.company == anna.company
    assert ticket.created_by == anna


def test_title_too_short_is_rejected(api_client, anna):
    api_client.force_authenticate(anna)

    response = api_client.post(
        TICKETS_URL, {"title": "Hi", "description": "Too short title."}, format="json"
    )

    assert response.status_code == 400
    assert "title" in response.data


def test_user_without_company_cannot_create_ticket(api_client, agent):
    api_client.force_authenticate(agent)

    response = api_client.post(
        TICKETS_URL, {"title": "Agent ticket", "description": "Should fail."}, format="json"
    )

    assert response.status_code == 400


def test_reply_author_is_the_logged_in_user(api_client, anna, make_ticket):
    ticket = make_ticket(anna)
    api_client.force_authenticate(anna)

    response = api_client.post(f"{ticket_url(ticket)}reply/", {"body": "Any update?"}, format="json")

    assert response.status_code == 201
    assert response.data["author"] == "anna"


# --- Ordering ---------------------------------------------------------------


def test_ordering_by_priority_rank_uses_severity_not_alphabet(api_client, agent, anna, make_ticket):
    make_ticket(anna, priority=Ticket.Priority.LOW)
    make_ticket(anna, priority=Ticket.Priority.URGENT)
    make_ticket(anna, priority=Ticket.Priority.HIGH)
    make_ticket(anna, priority=Ticket.Priority.MEDIUM)
    api_client.force_authenticate(agent)

    response = api_client.get(TICKETS_URL, {"ordering": "-priority_rank"})

    priorities = [t["priority"] for t in response.data["results"]]
    assert priorities == ["urgent", "high", "medium", "low"]