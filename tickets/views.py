from django.db.models import Case, IntegerField, Value, When
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User

from . import ai
from .models import Ticket
from .permissions import IsAgent
from .serializers import ReplySerializer, TicketSerializer

# Priority is stored as text, so ordering by it would be alphabetical.
# This maps each priority to a number so the database can sort by severity.
PRIORITY_RANK = Case(
    When(priority=Ticket.Priority.URGENT, then=Value(4)),
    When(priority=Ticket.Priority.HIGH, then=Value(3)),
    When(priority=Ticket.Priority.MEDIUM, then=Value(2)),
    When(priority=Ticket.Priority.LOW, then=Value(1)),
    default=Value(0),
    output_field=IntegerField(),
)


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    filterset_fields = ["status", "priority", "category", "assigned_to"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "priority_rank"]

    def get_queryset(self):
        qs = (
            Ticket.objects.annotate(priority_rank=PRIORITY_RANK)
            .select_related("company", "created_by", "assigned_to")
            .prefetch_related("replies__author")
        )
        user = self.request.user
        if user.is_staff or user.role == User.Role.AGENT:
            return qs
        return qs.filter(company=user.company)

    def perform_create(self, serializer):
        user = self.request.user
        if user.company is None:
            raise serializers.ValidationError("Only customer accounts can create tickets.")
        ticket = serializer.save(created_by=user, company=user.company)
        ai.apply_triage(ticket)

    @action(detail=True, methods=["post"])
    def reply(self, request, pk=None):
        ticket = self.get_object()
        serializer = ReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ticket=ticket, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["post"],
        url_path="suggest-reply",
        permission_classes=[IsAuthenticated, IsAgent],
    )
    def suggest_reply(self, request, pk=None):
        """Return an AI-written draft. It is NOT saved: the agent edits and sends it."""
        ticket = self.get_object()
        draft = ai.suggest_reply(ticket)
        if draft is None:
            return Response(
                {"detail": "AI suggestions are currently unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({"draft": draft})
