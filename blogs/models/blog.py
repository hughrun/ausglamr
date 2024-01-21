"""blog models"""

import re

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .utils import Announcement, Category, ContentWarning


def validate_ap_address(value):
    """is the activitypub address valid?"""
    p = re.compile("@(.*)@((\w|-)*)\.((\w)*)")
    m = p.match(value)
    if not m:
        raise ValidationError(
            _("%(value)s should be in the form '@user@domain.tld'"),
            params={"value": value},
        )


class BlogData(models.Model):
    """Base bloggy data"""

    title = models.CharField(max_length=2000)
    author_name = models.CharField(max_length=1000, null=True, blank=True)
    url = models.URLField(max_length=2000, unique=True)
    description = models.TextField(null=True, blank=True)
    updateddate = models.DateTimeField()

    class Meta:
        """This is an abstract model for common data"""

        abstract = True

    def __str__(self):
        """display for admin dropdowns"""
        return self.title

    def get_absolute_url(self):
        """override"""

        return self.url

    def save(self, *args, **kwargs):
        if not self.updateddate:
            self.updateddate = timezone.now()
        super().save(*args, **kwargs)


class Blog(BlogData):
    """A blog"""

    feed = models.URLField(max_length=2000)
    category = models.CharField(choices=Category.choices, max_length=4)
    added = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)
    announced = models.BooleanField(default=False)
    failing = models.BooleanField(default=False, blank=True, null=True)
    suspended = models.BooleanField(default=False, blank=True, null=True)
    suspension_lifted = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(null=True, default=True)
    activitypub_account_name = models.CharField(
        max_length=200, blank=True, null=True, validators=[validate_ap_address]
    )
    contact_email = models.EmailField(blank=True, null=True)

    def announce(self):
        """queue announcement"""

        if self.activitypub_account_name:
            author = f" by {self.activitypub_account_name}"
        elif self.author_name:
            author = f" by {self.author_name}"
        else:
            author = ""

        category = Category(self.category).label
        status = f"{self.title}{author} has been added to Aus GLAMR! \
        \n\nIt's about {category}\n\n{self.url}"

        Announcement.objects.create(status=status)
        self.announced = True
        super().save()

    def set_failing(self):
        """set the blog feed as failing"""

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


class Article(BlogData):
    """A blog post"""

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="articles")
    pubdate = models.DateTimeField()
    guid = models.CharField(max_length=2000)
    tags = models.ManyToManyField("Tag", related_name="articles")

    # pylint: disable=undefined-variable
    def announce(self):
        """queue a blog post announcement"""

        summary = []
        warnings = ContentWarning.objects.all()
        for warning in warnings:
            for text in [self.title, self.description]:
                label = warning.is_in(text)
                if label:
                    summmary.append(label)
            for tag in self.tags:  # pylint: disable=E1133
                label = warning.is_in(tag.name)
                if label:
                    summmary.append(label)

        summary_text = ", ".join(summary) if len(summary) > 0 else None
        author = self.blog.activitypub_account_name or self.author_name

        if self.blog.activitypub_account_name:
            author = f"{self.blog.activitypub_account_name} "
        elif self.author_name:
            author = f"{self.author_name} "
        else:
            author = ""

        status = f"{self.title} ({author}on {self.blog.title})\n\n{self.url}"

        Announcement.objects.create(status=status, summary=summary_text)


class Tag(models.Model):
    """An article tag"""

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        """display for admin dropdowns"""
        return self.name
