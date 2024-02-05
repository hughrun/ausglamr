"""check whether announcements need to be queued"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from blogs import models


class Command(BaseCommand):
    """the command"""

    # we could add arguments but we don't really need any

    def handle(self, *args, **options):
        """check whether we need to queue announcements and queue them"""

        events = models.Event.objects.filter(
            approved=True,
            announcements__lt=3,
            start_date__gte=timezone.now(),
        )
        calls = models.CallForPapers.objects.filter(
            announcements__lt=3,
            closing_date__gte=timezone.now(),
            event__approved=True,
        )

        for conf in events:
            delta = conf.start_date - timezone.now().date()

            if (
                conf.announcements < 1
                or (delta < timedelta(days=7))
                or (delta < timedelta(days=90) and conf.announcements < 2)
            ):
                conf.announce()

        for cfp in calls:
            delta_one = timezone.now().date() - cfp.opening_date
            delta_two = cfp.closing_date - timezone.now().date()

            if (
                cfp.announcements < 1
                or (delta_one > delta_two and cfp.announcements < 2)
                or (delta_two < timedelta(days=7))
            ):
                cfp.announce()
