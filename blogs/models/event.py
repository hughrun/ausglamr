"""event models"""

from django.db import models
from django.utils import timezone

from .utils import Announcement, Category


class Event(models.Model):
    """a event"""

    name = models.CharField(max_length=999)
    category = models.CharField(choices=Category.choices, max_length=4)
    url = models.URLField(max_length=400, unique=True)
    description = models.TextField(null=True, blank=True)
    pub_date = models.DateTimeField()  # for RSS feed
    start_date = models.DateField()
    announcements = models.IntegerField(null=True, blank=True, default=0)
    activitypub_account_name = models.CharField(max_length=200, blank=True, null=True)
    owner_email = models.EmailField(blank=True, null=True)
    approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pub_date:
            self.pub_date = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        """display for admin dropdowns"""
        return self.name

    def get_absolute_url(self):
        """override for rss feed"""
        return self.url

    def announce(self):
        """announce a event"""

        date = self.start_date.strftime("%a %d %b %Y")
        category = Category(self.category).label
        name = self.name
        if self.activitypub_account_name:
            name = f"{self.name} ({self.activitypub_account_name})"

        status = (
            f"{name} is a event about {category}, starting on {date}!\n\n{self.url}"
        )

        Announcement.objects.create(status=status)
        self.announcements = self.announcements + 1
        super().save()


class CallForPapers(models.Model):
    """a event call for papers/presentations"""

    name = models.CharField(
        max_length=999
    )  # "Call for papers", "call for participation" etc
    details = models.TextField(null=True, blank=True)
    pub_date = models.DateTimeField(null=True, default=None)
    opening_date = models.DateField()
    closing_date = models.DateField()
    announcements = models.IntegerField(null=True, default=0)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="cfp")
    approved = models.BooleanField(default=False)

    def announce(self):
        """create a call for papers announcement"""

        opening_date = self.opening_date.strftime("%a %d %b %Y")
        closing_date = self.closing_date.strftime("%a %d %b %Y")

        status = f"{self.event.name} {self.name } is open from {opening_date}, closing on {closing_date}!\n\nMore info at {self.event.url}"

        if self.event.approved:
            Announcement.objects.create(status=status)
            self.announcements = self.announcements + 1
            super().save()

    def save(self, *args, **kwargs):
        """save a CFP with pub_date"""
        if not self.pub_date:
            self.pub_date = timezone.now()
        super().save(*args, **kwargs)
