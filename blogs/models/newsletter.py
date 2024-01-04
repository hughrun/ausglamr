"""newsletter models"""

from django.db import models
from django.utils import timezone

from .utils import Announcement, Category


class Newsletter(models.Model):
    """a newsletter"""

    name = models.CharField(max_length=999)
    author = models.CharField(max_length=999)
    category = models.CharField(choices=Category.choices, max_length=4)
    url = models.URLField(max_length=400, unique=True)

    description = models.TextField(null=True, blank=True)
    activitypub_account_name = models.CharField(max_length=200, blank=True, null=True)
    owner_email = models.EmailField(blank=True, null=True)
    announced = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    pub_date = models.DateTimeField(null=True, default=None)

    def announce(self):
        """create a event announcement"""

        category = Category(self.category).label
        name = self.name
        if self.activitypub_account_name:
            name = f"{self.name} ({self.activitypub_account_name})"

        status = f"{name} is a newsletter about {category} from {self.author}. Check it out:\n\n{self.url}"

        Announcement.objects.create(status=status)
        self.announced = True
        super().save()

    def save(self, *args, **kwargs):
        if not self.pub_date:
            self.pub_date = timezone.now()
        super().save(*args, **kwargs)
