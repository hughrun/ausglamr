"""utility models for use in other models"""

import requests

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Category(models.TextChoices):
    """what GLAMR are you"""

    GALLERIES = "GAL", _("Galleries")
    LIBRARIES = "LIB", _("Libraries")
    ARCHIVES = "ARC", _("Archives")
    MUSEUMS = "MUS", _("Museums")
    RECORDS = "REC", _("Records")
    DIGITAL_HUMANITIES = "DH", _("Digital Humanities")
    GLAM = "GLAM", _("GLAMR")


class GroupType(models.TextChoices):
    """what GLAMR are you"""

    DISCORD = "DISC", _("Discord server")
    DISCOURSE = "DCRS", _("Discourse community")
    EMAIL = "EML", _("email list")
    GOOGLE = "GOOG", _("Google group")
    KBIN = "KBIN", _("KBin server")
    LEMMY = "LEMM", _("Lemmy server")
    MASTODON = "MAS", _("Mastodon server")
    REDDIT = "RED", _("subreddit")
    SLACK = "SLAC", _("Slack channel")
    ZULIP = "ZLIP", _("Zulip server")
    OTHER = "OTHR", _("group")


class Announcement(models.Model):
    """an announcement on Mastodon"""

    status = models.TextField()
    summary = models.TextField(null=True)
    queued = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.queued:
            self.queued = timezone.now()
        super().save(*args, **kwargs)

    def announce(self):
        """tell the world about it"""

        key = settings.MASTODON_ACCESS_TOKEN
        headers = {"Authorization": f"Bearer {key}"}
        params = {"status": self.status}
        if self.summary:
            params["spoiler_text"] = self.summary

        url = f"{settings.MASTODON_DOMAIN}/api/v1/statuses"
        r = requests.post(url, data=params, headers=headers, timeout=(4, 13))
        if r.status_code == 200:
            self.delete()


class ContentWarning(models.Model):
    """content warnings"""

    match_text = models.CharField(max_length=999, null=True)
    display = models.CharField(max_length=999, null=True)

    def is_in(self, text):
        """check some text and return a CW if needed"""

        warning = None
        if self.match_text in text.lower():
            warning = self.display
        return warning


class SiteMessage(models.Model):
    """A message to be displayed somewhere"""

    message = models.TextField(max_length=999)
