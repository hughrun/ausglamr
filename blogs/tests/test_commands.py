"""test utility functions"""

from datetime import datetime, timezone

from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from blogs import models


class FeedParserItemMock(object):
    title = ""
    tags = []
    author = ""
    link = ""
    summary = ""
    updated_parsed = ((),)
    published_parsed = ((),)
    id = ""

    def __init__(
        self, title, tags, author, link, summary, updated_parsed, published_parsed, id
    ):
        self.title = title
        self.tags = tags
        self.author = author
        self.link = link
        self.summary = summary
        self.updated_parsed = updated_parsed
        self.published_parsed = published_parsed
        self.id = id


class FeedParserTagMock(object):
    term = ""

    def __init__(self, term):
        self.term = term


class FeedParserMock(object):
    entries = []

    def __init__(self, entries):
        self.entries = entries


class CommandsTestCase(TestCase):
    """test management command functions"""

    def setUp(self):
        """set up test conf"""

        self.blog = models.Blog.objects.create(
            title="My awesome blog",
            url="https://test.com",
            feed="https://test.com/feed.xml",
            category="LIB",
            approved=True,
            suspended=False,
        )

        tag_one = FeedParserTagMock(term="testing")
        tag_two = FeedParserTagMock(term="python")
        tag_three = FeedParserTagMock(term="notglam")

        article = FeedParserItemMock(
            title="My amazing blog post",
            tags=[tag_one, tag_two],
            author="Hugh Rundle",
            link="https://test.com/1",
            summary="A short summary of my post",
            updated_parsed=(2024, 1, 1, 19, 48, 21, 3, 1, 0),
            published_parsed=(2024, 1, 1, 19, 48, 21, 3, 1, 0),
            id="1",
        )

        article_two = FeedParserItemMock(
            title="My really amazing blog post",
            tags=[tag_one, tag_two, tag_three],
            author="Hugh Rundle",
            link="https://test.com/2",
            summary="A short summary of my next post",
            updated_parsed=(2024, 1, 2, 19, 48, 21, 3, 1, 0),
            published_parsed=(2024, 1, 2, 19, 48, 21, 3, 1, 0),
            id="999",
        )

        self.feedparser = FeedParserMock(entries=[article])

        self.feedparser_exclude = FeedParserMock(entries=[article_two])

    def test_check_feeds(self):
        """test parse a feed for basic blog info"""

        args = {"-q": True}
        opts = {}

        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.Tag.objects.count(), 0)

        with patch("feedparser.parse", return_value=self.feedparser):
            value = call_command("check_feeds", *args, **opts)

            self.assertEqual(models.Article.objects.count(), 1)
            self.assertEqual(models.Tag.objects.count(), 2)
            article = models.Article.objects.all().first()
            self.assertEqual(article.title, "My amazing blog post")

    def test_check_feeds_exclude_tag(self):
        """test parse a feed with exclude tag"""

        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.Tag.objects.count(), 0)

        with patch("feedparser.parse", return_value=self.feedparser_exclude):
            args = {"-q": True}
            opts = {}

            value = call_command("check_feeds", *args, **opts)

            self.assertEqual(models.Article.objects.count(), 0)
            self.assertEqual(models.Tag.objects.count(), 0)

    def test_check_feeds_unapproved(self):
        """test check unapproved blog feed"""

        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.Tag.objects.count(), 0)

        self.blog.approved = False
        self.blog.save()

        with patch("feedparser.parse", return_value=self.feedparser):
            args = {"-q": True}
            opts = {}

            value = call_command("check_feeds", *args, **opts)

            self.assertEqual(models.Article.objects.count(), 0)
            self.assertEqual(models.Tag.objects.count(), 0)

    def test_check_feeds_inactive(self):
        """test ignore inactive blog feed"""

        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.Tag.objects.count(), 0)

        self.blog.active = False
        self.blog.save()

        with patch("feedparser.parse", return_value=self.feedparser):
            args = {"-q": True}
            opts = {}

            value = call_command("check_feeds", *args, **opts)

            self.assertEqual(models.Article.objects.count(), 0)
            self.assertEqual(models.Tag.objects.count(), 0)

    def test_check_feeds_suspended(self):
        """test check suspended blog feed"""

        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.Tag.objects.count(), 0)

        self.blog.suspended = True
        self.blog.save()

        with patch("feedparser.parse", return_value=self.feedparser):
            args = {"-q": True}
            opts = {}

            value = call_command("check_feeds", *args, **opts)

            self.assertEqual(models.Article.objects.count(), 0)
            self.assertEqual(models.Tag.objects.count(), 0)

    def test_check_feeds_previously_suspended(self):
        """test blog published prior to suspension lifted is not ingested"""

        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.Tag.objects.count(), 0)

        self.blog.suspended = False
        self.blog.suspension_lifted = datetime(
            2024, 1, 2, 21, 0, 0, 0, tzinfo=timezone.utc
        )
        self.blog.save()

        with patch("feedparser.parse", return_value=self.feedparser):
            args = {"-q": False}
            opts = {}

            value = call_command("check_feeds", *args, **opts)

            self.assertEqual(models.Article.objects.count(), 0)
            self.assertEqual(models.Tag.objects.count(), 0)

    def test_check_feeds_previously_suspended_post_after(self):
        """test blog published after suspension lifted is ingested"""

        self.assertEqual(models.Article.objects.count(), 0)
        self.assertEqual(models.Tag.objects.count(), 0)

        self.blog.suspended = False
        self.blog.suspension_lifted = datetime(
            2023, 12, 31, 0, 0, 0, 0, tzinfo=timezone.utc
        )
        self.blog.save()

        with patch("feedparser.parse", return_value=self.feedparser):
            args = {"-q": False}
            opts = {}

            value = call_command("check_feeds", *args, **opts)

            self.assertEqual(models.Article.objects.count(), 1)
            self.assertEqual(models.Tag.objects.count(), 2)
