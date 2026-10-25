import time

from django.conf import settings
from django.core.management.base import BaseCommand

from tickets import ai
from tickets.models import Ticket


class Command(BaseCommand):
    help = "Run AI triage on tickets that do not have an AI summary yet."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=20, help="Maximum number of tickets to process."
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=6.0,
            help="Seconds to wait between requests, to stay within the free-tier rate limit.",
        )

    def handle(self, *args, **options):
        if not settings.GEMINI_API_KEY:
            self.stderr.write(self.style.ERROR("GEMINI_API_KEY is not set, nothing to do."))
            return

        tickets = list(
            Ticket.objects.filter(ai_summary="").order_by("created_at")[: options["limit"]]
        )
        if not tickets:
            self.stdout.write("All tickets already have an AI summary.")
            return

        succeeded = 0
        for index, ticket in enumerate(tickets):
            if index:
                time.sleep(options["delay"])
            # keep_existing: don't overwrite category/priority a person already set.
            if ai.apply_triage(ticket, keep_existing=True):
                succeeded += 1
                self.stdout.write(
                    f"#{ticket.pk} {ticket.title}: {ticket.priority}/{ticket.category}"
                )
            else:
                self.stdout.write(self.style.WARNING(f"#{ticket.pk} {ticket.title}: failed"))

        failed = len(tickets) - succeeded
        self.stdout.write(self.style.SUCCESS(f"Done: {succeeded} triaged, {failed} failed."))
