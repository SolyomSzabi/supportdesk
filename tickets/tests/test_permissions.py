TICKETS_URL = "/api/tickets/"


def test_customer_cannot_change_own_ticket(api_client, anna, make_ticket):
    ticket = make_ticket(anna, priority="low")
    api_client.force_authenticate(anna)

    response = api_client.patch(f"{TICKETS_URL}{ticket.pk}/", {"priority": "urgent"}, format="json")

    assert response.status_code == 403
    ticket.refresh_from_db()
    assert ticket.priority == "low"


def test_customer_cannot_delete_ticket(api_client, anna, make_ticket):
    ticket = make_ticket(anna)
    api_client.force_authenticate(anna)

    assert api_client.delete(f"{TICKETS_URL}{ticket.pk}/").status_code == 403


def test_agent_can_change_status(api_client, agent, anna, make_ticket):
    ticket = make_ticket(anna)
    api_client.force_authenticate(agent)

    response = api_client.patch(f"{TICKETS_URL}{ticket.pk}/", {"status": "resolved"}, format="json")

    assert response.status_code == 200
    ticket.refresh_from_db()
    assert ticket.status == "resolved"
