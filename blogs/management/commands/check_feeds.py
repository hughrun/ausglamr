"""call this from cron to run through all the feeds to find new posts"""

import logging
import traceback

from datetime import datetime, timedelta, timezone

import feedparser

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import html
from django.utils import timezone as django_timezone

from blogs import models

from django.forms.models import model_to_dict

agent = "AusGLAMR/1.0 +https://ausglamr.newcardigan.org"


def date_to_tz_aware(date_tuple):
    """turn a 9-tuple into something usable"""

    # we are assuming all dates are UTC which is a bit dodgy but it works
    return datetime(*date_tuple[0:7], tzinfo=timezone.utc)


def get_tags(dictionary):
    """parse out tags from blog and upsert as tag instances"""
    tags = []
    for tag_obj in dictionary:
        if tag_obj.term.lower() != "uncategorized":
            tag = models.Tag.objects.filter(name=tag_obj.term.lower()).first()
            if not tag:
                tag = models.Tag.objects.create(name=tag_obj.term.lower())

            tags.append(tag)

    return tags


class Command(BaseCommand):
    """the check_feeds command"""

    def add_arguments(self, parser):
        parser.add_argument(
            "-q",
            action="store_true",
            help="Suppress non-error messages",
        )
        parser.add_argument(
            "-blogs",
            action="store_true",
            help="Only check blog posts",
        )
        parser.add_argument(
            "-newsletters",
            action="store_true",
            help="Only check editions",
        )

    def handle(self, *args, **options):
        """check feeds and update database"""

        if not options["q"]:
            logging.info(
                f"checking feeds at {django_timezone.localtime(django_timezone.now())}"
            )

        if not options["newsletters"]:
            blogs = models.Blog.objects.filter(
                approved=True, suspended=False, active=True
            ).all()
            for blog in blogs:
                try:
                    data = feedparser.parse(blog.feed, agent=agent)

                    for article in data.entries:
                        if not models.Article.objects.filter(
                            Q(url=article.link)
                            | Q(guid=getattr(article, "id", article.link))
                        ).exists():
                            if blog.suspension_lifted and (
                                blog.suspension_lifted
                                > date_to_tz_aware(article.updated_parsed)
                            ):
                                continue  # don't ingest posts published prior to suspension being lifted (we should already have older ones from prior to suspension)

                            taglist = getattr(article, "tags", None) or getattr(
                                article, "categories", []
                            )

                            tags = [tag.term.lower() for tag in taglist]

                            opt_out = False
                            # don't include posts with opt out tags
                            for tag in tags:
                                if (
                                    len(
                                        {tag}
                                        & {
                                            "notglam",
                                            "notglamr",
                                            "notausglamblogs",
                                            "notausglamr",
                                            "notglamblogs",
                                            "#notglam",
                                        }
                                    )
                                    > 0
                                ):
                                    opt_out = True
                                else:
                                    continue

                            if not opt_out:
                                author_name = getattr(
                                    article, "author", None
                                ) or getattr(blog, "author", None)

                                description = (
                                    html.strip_tags(article.summary)
                                    if (
                                        hasattr(article, "summary")
                                        and len(article.summary) > 0
                                    )
                                    else html.strip_tags(article.description)
                                    if (
                                        hasattr(article, "description")
                                        and len(article.summary)
                                    )
                                    else html.strip_tags(article.content[0].value)[:200]
                                    if (
                                        hasattr(article, "content")
                                        and len(article.content)
                                    )
                                    else ""
                                )
                                if description:
                                    description += "..."

                                instance = models.Article.objects.create(
                                    title=article.title,
                                    author_name=author_name,
                                    url=article.link,
                                    description=description,
                                    updateddate=date_to_tz_aware(
                                        article.updated_parsed
                                    ),
                                    blog=blog,
                                    pubdate=date_to_tz_aware(article.published_parsed),
                                    guid=getattr(article, "id", article.link),
                                )

                                tags_to_add = get_tags(
                                    getattr(article, "tags", None)
                                    or getattr(article, "categories", [])
                                )

                                for tag in tags_to_add:
                                    instance.tags.add(tag)

                                instance.save()

                                cutoff = django_timezone.now() - timedelta(days=3)
                                newish = instance.pubdate > cutoff
                                if newish:
                                    instance.announce()
                                    blog.set_success(
                                        updateddate=date_to_tz_aware(article.updated_parsed)
                                    )

                except Exception as e:
                    blog.set_failing()
                    logging.error(f"ERROR WITH BLOG {blog.title} - {blog.url}")
                    logging.info(article)
                    logging.error(e)

        if not options["blogs"]:
            newsletters = models.Newsletter.objects.filter(
                approved=True, active=True, feed__isnull=False
            ).all()
            for newsletter in newsletters:
                try:
                    data = feedparser.parse(newsletter.feed, agent=agent)

                    for edition in data.entries:
                        if not models.Edition.objects.filter(
                            Q(url=edition.link)
                            | Q(guid=getattr(edition, "id", edition.link))
                        ).exists():
                            author_name = getattr(edition, "author", None) or getattr(
                                edition, "author", None
                            )

                            description = (
                                html.strip_tags(edition.summary)
                                if (
                                    hasattr(edition, "summary") and len(edition.summary)
                                )
                                else html.strip_tags(edition.description)
                                if (
                                    hasattr(edition, "description")
                                    and len(edition.description)
                                )
                                else html.strip_tags(edition.content[0].value)[:200] + "..."
                                if (
                                    hasattr(article, "content")
                                    and len(article.content)
                                )
                                else ""
                            )
                            if description:
                                description += "..."

                            instance = models.Edition.objects.create(
                                title=edition.title,
                                author_name=author_name,
                                url=edition.link,
                                description=description,
                                updateddate=date_to_tz_aware(edition.updated_parsed),
                                newsletter=newsletter,
                                pubdate=date_to_tz_aware(edition.published_parsed),
                                guid=getattr(edition, "id", edition.link),
                            )

                            instance.save()

                            cutoff = django_timezone.now() - timedelta(days=3)
                            newish = instance.pubdate > cutoff
                            if newish:
                                instance.announce()

                    newsletter.set_success(
                        updateddate=date_to_tz_aware(edition.updated_parsed)
                    )

                except Exception as e:
                    newsletter.set_failing()
                    logging.error(
                        f"ERROR WITH NEWSLETTER {newsletter.name} - {newsletter.url}"
                    )
                    logging.error(e)

        if not options["q"]:
            logging.info(
                f"completed run at {django_timezone.localtime(django_timezone.now())}"
            )
