"""newsletter models"""

from django.db import models
from django.utils import timezone

from .utils import Announcement, Category


class Newsletter(models.Model):
    """a newsletter"""

    name = models.CharField(max_length=100)
    author_name = models.CharField(max_length=100)
    category = models.CharField(choices=Category.choices, max_length=4)
    url = models.URLField(max_length=400, unique=True)
    feed = models.URLField(max_length=1000, unique=True, blank=True, null=True)
    description = models.TextField(null=True, blank=True, max_length=250)
    activitypub_account_name = models.CharField(max_length=200, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)

    announced = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    active = models.BooleanField(null=True, default=True)
    failing = models.BooleanField(default=False, blank=True, null=True)

    updateddate = models.DateTimeField()
    pubdate = models.DateTimeField(null=True, default=None)

    def __str__(self):
        """display for admin dropdowns"""
        return self.name

    def announce(self):
        """create a event announcement"""

        category = Category(self.category).label
        name = self.author_name
        if self.activitypub_account_name:
            name = f"{self.author_name} ({self.activitypub_account_name})"

        status = f"{self.name} is a newsletter about {category} from {name}. Check it out:\n\n{self.url}"

        Announcement.objects.create(status=status)
        self.announced = True
        super().save()

    def save(self, *args, **kwargs):
        if not self.updateddate:
            self.updateddate = timezone.now()
        super().save(*args, **kwargs)

    def set_failing(self):
        """set the newsletter feed as failing"""

        self.failing = True
        super().save()

    def set_success(self, updateddate):
        """
        set failing to false
        set the updateddate to a datetime

        """

        self.failing = False
        self.updateddate = updateddate
        super().save()


class Edition(models.Model):
    """A newsletter edition"""

    title = models.CharField(max_length=2000)
    author_name = models.CharField(max_length=1000, null=True, blank=True)
    url = models.URLField(max_length=2000, unique=True)
    description = models.TextField(null=True, blank=True)
    updateddate = models.DateTimeField()
    newsletter = models.ForeignKey(
        Newsletter, on_delete=models.CASCADE, related_name="editions"
    )
    pubdate = models.DateTimeField(null=True, default=timezone.now)
    guid = models.CharField(max_length=2000)

    def announce(self):
        """queue an edition announcement"""

        author = self.newsletter.activitypub_account_name or self.author_name

        if self.newsletter.activitypub_account_name:
            author = f"{self.newsletter.activitypub_account_name} - "
        elif self.author_name:
            author = f"{self.author_name} - "
        else:
            author = ""

        status = f"📬 {self.title} ({author}{self.newsletter.name})\n\n{self.url}"

        Announcement.objects.create(status=status)
