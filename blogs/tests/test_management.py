"""test management commands"""

from datetime import datetime, timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from blogs import models, management


class ManagementTestCase(TestCase):
    """test management commands"""

    def setUp(self):
        """set up some things to announce"""

        self.conf = models.Event.objects.create(
            name="Amazing Conf",
            url="https://test.com",
            category="LIB",
            start_date=timezone.localtime(timezone.now()) + timedelta(days=3),
            activitypub_account_name="@conf@conf.conf",
            approved=True,
            announcements=1,
        )

        self.cfp = models.CallForPapers.objects.create(
            event=self.conf,
            name="Call for Papers for Amazing Conf",
            opening_date=timezone.localtime(timezone.now()) + timedelta(days=30),
            closing_date=timezone.localtime(timezone.now()) + timedelta(days=1),
        )

        self.cfp = models.CallForPapers.objects.create(
            event=self.conf,
            name="Call for posters",
            opening_date=timezone.localtime(timezone.now()) - timedelta(days=30),
            closing_date=timezone.localtime(timezone.now()) - timedelta(days=1),
        )

    def test_queue_announcements(self):
        """both in one"""

        call_command("queue_announcements")

        # call for posters is in the past, so should not be announced
        self.assertEqual(models.Announcement.objects.count(), 2)

        # event
        announcement = models.Announcement.objects.first()
        start_date = timezone.localtime(timezone.now()) + timedelta(days=3)
        date = start_date.strftime("%a %d %b %Y")
        status = f"Amazing Conf (@conf@conf.conf) is a event about Libraries, starting on {date}!\n\nhttps://test.com"

        self.assertEqual(announcement.status, status)

        # cfp
        announcement = models.Announcement.objects.last()
        opening_date = timezone.localtime(timezone.now()) + timedelta(days=30)
        closing_date = timezone.localtime(timezone.now()) + timedelta(days=1)
        opening_date_str = opening_date.strftime("%a %d %b %Y")
        closing_date_str = closing_date.strftime("%a %d %b %Y")
        status = f"Amazing Conf Call for Papers for Amazing Conf is open from {opening_date_str}, closing on {closing_date_str}!\n\nMore info at https://test.com"

        self.assertEqual(announcement.status, status)
