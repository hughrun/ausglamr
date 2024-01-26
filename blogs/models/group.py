"""group models"""

from django.db import models
from django.utils import timezone

from .utils import Announcement, Category, GroupType


class Group(models.Model):
    """a group on email, discord, slack etc"""

    name = models.CharField(max_length=100)
    category = models.CharField(choices=Category.choices, max_length=4)
    type = models.CharField(choices=GroupType.choices, max_length=4)
    url = models.URLField(max_length=400, unique=True)
    registration_url = models.URLField(max_length=400, unique=True)
    description = models.TextField(null=True, blank=True, max_length=250)
    contact_email = models.EmailField(blank=True, null=True)

    announced = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    pubdate = models.DateTimeField(null=True, default=timezone.now)

    def announce(self):
        """create a group announcement"""

        category = Category(self.category).label
        type = GroupType(self.type).label
        status = f"{self.name} is a {type} about {category}!\n\nJoin them: {self.registration_url}"

        Announcement.objects.create(status=status)
        self.announced = True
        super().save()
