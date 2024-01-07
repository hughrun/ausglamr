"""send the weekly email"""

from datetime import timedelta
import logging
import random

from django.conf import settings
from django.utils import timezone
from django.core.management.base import BaseCommand

from blogs import models
from blogs.utilities import send_email
from blogs.models.utils import GroupType


class Command(BaseCommand):
    """the announce command"""

    # we could add arguments but we don't really need any

    def handle(self, *args, **options):
        """find subscribers and send an update"""

        subscribers = models.Subscriber.objects.filter(confirmed=True)

        logging.info(
            f"Sending weekly emails to {len(subscribers)} subscribers at {timezone.now()}"
        )

        cutoff = timezone.now() - timedelta(days=7)
        blogs = models.Blog.objects.filter(approved=True, updateddate__gte=cutoff)
        articles = models.Article.objects.filter(pubdate__gte=cutoff)
        events = models.Event.objects.filter(approved=True, pub_date__gte=cutoff)
        cfps = models.CallForPapers.objects.filter(
            event__approved=True, closing_date__gte=timezone.now().date()
        )
        newsletters = models.Newsletter.objects.filter(
            approved=True, pub_date__gte=cutoff
        )
        groups = models.Group.objects.filter(approved=True, pub_date__gte=cutoff)

        new_blogs = ""
        for blog in blogs:
            title_string = f"<h4><a href='{blog.url}'>{blog.title}</a></h4>"
            author_string = (
                f"<p><em>{blog.author_name}</em></p>" if blog.author_name else ""
            )
            description_string = (
                f"<p style='margin-bottom:24px;'>{blog.description}</p>"
            )

            string_list = [title_string, author_string, description_string]
            string = "".join(string_list)

            new_blogs = new_blogs + string

        if new_blogs != "":
            new_blogs = (
                "<h3 style='margin-top:20px;'>New Blogs</h3>" + new_blogs + "<hr/>"
            )

        new_articles = ""
        for post in articles:
            title_string = f"<h4><a href='{post.url}'>{post.title}</a></h4>"
            author_string = (
                f"<p><em>{post.author_name}</em></p>" if post.author_name else ""
            )
            description_string = (
                f"<p style='margin-bottom:24px;'>{post.description}</p>"
            )

            string_list = [title_string, author_string, description_string]
            string = "".join(string_list)

            new_articles = new_articles + string

        if new_articles != "":
            new_articles = (
                "<h3 style='margin-top:20px;'>New Articles</h3>"
                + new_articles
                + "<hr/>"
            )

        coming_events = ""
        for event in events:
            s_date = event.start_date
            title_string = f"<h4><a href='{event.url}'>{event.name}</a></h4>"
            date_string = (
                f"<p><em>{s_date:%a} {s_date.day} {s_date:%B} {s_date:%Y}</em></p>"
            )
            description_string = (
                f"<p style='margin-bottom:24px;'>{event.description}</p>"
            )

            string_list = [title_string, date_string, description_string]
            string = "".join(string_list)

            coming_events = coming_events + string

        if coming_events != "":
            coming_events = (
                "<h3 style='margin-top:20px;'>Upcoming Events</h3>"
                + coming_events
                + "<hr/>"
            )

        open_cfps = ""
        for instance in cfps:
            c_date = instance.closing_date
            title_string = (
                f"<h4><a href='{instance.event.url}'>{instance.name}</a></h4>"
            )
            dates_string = f"<p><strong>Closes:</strong><em>{c_date:%a} {c_date.day} {c_date:%B}</em></p>"
            description_string = (
                f"<p style='margin-bottom:24px;'>{instance.details}</p>"
            )

            string_list = [title_string, dates_string, description_string]
            string = "".join(string_list)

            open_cfps = open_cfps + string

        if open_cfps != "":
            open_cfps = (
                "<h3 style='margin-top:20px;'>Open Calls</h3>" + open_cfps + "<hr/>"
            )

        new_newsletters = ""
        for instance in newsletters:
            title_string = f"<h4><a href='{instance.url}'>{instance.name}</a></h4>"
            author_string = (
                f"<p><em>{instance.author}</em></p>" if instance.author else ""
            )
            description_string = (
                f"<p style='margin-bottom:24px;'>{instance.description}</p>"
            )
            string_list = [title_string, author_string, description_string]
            string = "".join(string_list)

            new_newsletters = new_newsletters + string

        if new_newsletters != "":
            new_newsletters = (
                "<h3 style='margin-top:20px;'>New Newsletters</h3>"
                + new_newsletters
                + "<hr/>"
            )

        new_groups = ""
        for instance in groups:
            group_type = GroupType(instance.type).label
            title_string = f"<h4><a href='{instance.url}'>{instance.name}</a></h4>"
            register_string = f"<p><em><a href='{instance.registration_url}'>Register</a> to join this {group_type}</em></p>"
            description_string = (
                f"<p style='margin-bottom:24px;'>{instance.description}</p>"
            )
            string_list = [title_string, register_string, description_string]
            string = "".join(string_list)

            new_groups = new_groups + string

        if new_groups != "":
            new_groups = (
                "<h3 style='margin-top:20px;'>New Groups</h3>" + new_groups + "<hr/>"
            )

        # Now let's put it all together...
        dt = timezone.now()
        choices = [
            "🍓",
            "🍒",
            "🍎",
            "🍊",
            "🍍",
            "🍋",
            "🍉",
            "🥝",
            "🥦",
            "🥒",
            "🥕",
            "🍏",
            "🍅",
            "🥬",
            "🫐",
            "🍐",
            "🥗",
            "☕️",
            "🚚",
            "📬",
            "🍣",
        ]
        emoji = random.choice(choices)
        subject = f"{emoji} Fresh Aus GLAMR updates for the week of {dt.day} {dt:%B} {dt.year}"
        sections = [
            new_articles,
            new_blogs,
            new_newsletters,
            new_groups,
            open_cfps,
            coming_events,
        ]
        body = "".join(sections)

        for subscriber in subscribers:
            opt_out = f"https://{settings.DOMAIN}/unsubscribe-email/{subscriber.token}/{subscriber.id}"
            start = "<html><body>"
            footer = f"<div style='padding: 20px; width: 100vw; background-color:#eee; margin-top: 100px;text-align:center;'><em><p>This email was sent to <strong>{subscriber.email}</strong> because you subscribed to email updates from <a href='https://{settings.DOMAIN}'>Aus GLAMR</a>.</p><p>You can <a href='{opt_out}'>unsubscribe</a> at any time.</p></em></div>"
            end = "</body></html>"
            parts = [start, body, footer, end]
            message = "".join(parts)

            send_email(subject, message, subscriber.email)

        logging.info(f"Weekly emails completed {timezone.now()}")
