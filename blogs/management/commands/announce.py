"""announce something"""

from django.core.management.base import BaseCommand

from blogs.models import Announcement


class Command(BaseCommand):
    """the announce command"""

    # we could add arguments but we don't really need any

    def handle(self, *args, **options):
        """check for pending announcements and announce the latest"""

        announcement = Announcement.objects.filter().order_by("queued").first()

        if announcement:
            announcement.announce()
