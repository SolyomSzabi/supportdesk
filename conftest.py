import pytest
from rest_framework.test import APIClient

from accounts.models import Company, User
from tickets.models import Ticket


@pytest.fixture(autouse=True)
def disable_real_ai(settings):
    """Tests must never call the real Gemini API; individual tests mock it when needed."""
    settings.GEMINI_API_KEY = ""


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def acme(db):
    return Company.objects.create(name="Acme Hotels")


@pytest.fixture
def sunrise(db):
    return Company.objects.create(name="Sunrise Travel")


@pytest.fixture
def anna(acme):
    return User.objects.create_user(username="anna", password="pass12345", company=acme)


@pytest.fixture
def lisa(sunrise):
    return User.objects.create_user(username="lisa", password="pass12345", company=sunrise)


@pytest.fixture
def agent(db):
    return User.objects.create_user(username="tom", password="pass12345", role=User.Role.AGENT)


@pytest.fixture
def make_ticket():
    """Factory: make_ticket(user, priority="high") creates a ticket for the user's company."""

    def _make(user, **kwargs):
        data = {"title": "Test ticket", "description": "Something is broken."}
        data.update(kwargs)
        return Ticket.objects.create(company=user.company, created_by=user, **data)

    return _make
