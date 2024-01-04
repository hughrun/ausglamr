"""email subscriptions"""

import uuid

from django.conf import settings
from django.db import models

from blogs.utilities import send_email


class Subscriber(models.Model):
    """a person who wants to receive weekly emails"""

    email = models.EmailField(blank=True, null=True, unique=True)
    confirmed = models.BooleanField(default=False, editable=False)
    token = models.UUIDField(default=uuid.uuid4, editable=False)

    def save(self, *args, **kwargs):
        """always reset the token on save"""

        self.token = uuid.uuid4()
        super().save(*args, **kwargs)

    def send_confirmation_email(self):
        """send an email requesting confirmation"""

        subject = "Please confirm your email address"
        recipient = self.email
        url = f"{settings.DOMAIN}/confirm-subscribe-email/{self.token}/{self.id}"
        opt_out = f"{settings.DOMAIN}/unsubscribe-email/{self.token}/{self.id}"
        start = "<html><body>"
        body = f"<p>Please <a href='{url}'>confirm your email address</a> to receive weekly updates.</p>"
        footer = (
            f"<p><em>You can <a href='{opt_out}'>unsubscribe</a> at any time.</em></p>"
        )
        end = "</body></html>"

        parts = [start, body, footer, end]
        message = "".join(parts)

        send_email(subject, message, recipient)
