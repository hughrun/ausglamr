"""test utility functions"""

import pathlib

from django.test import TestCase
from unittest.mock import patch

from blogs import models, utilities


class FeedParserFeedMock(object):
    title = ""
    author = ""
    summary = ""

    def __init__(self, title, author, summary):
        self.title = title
        self.author = author
        self.summary = summary


class FeedParserMock(object):
    feed = FeedParserFeedMock

    def __init__(self, feed):
        self.feed = feed


def request_error():
    return None


class RequestsMock(object):
    text = ""
    raise_for_status = request_error

    def __init__(self, text, raise_for_status):
        self.text = text
        self.raise_for_status = raise_for_status


class UtilityTests(TestCase):
    """utility test cases"""

    def setUp(self):
        """set up shared data"""

        feed = FeedParserFeedMock(
            title="My amazing blog",
            author="Hugh Rundle",
            summary="A short summary of my blog",
        )

        feed_partial = FeedParserFeedMock(
            title="My amazing blog", author=None, summary=None
        )

        self.feedparser = FeedParserMock(feed=feed)
        self.feedparser_partial = FeedParserMock(feed=feed_partial)

    def test_get_feed_info(self):
        """test get feed info"""

        with patch("feedparser.parse", return_value=self.feedparser):
            data = utilities.get_feed_info("https://test.test")

            self.assertEqual(data["feed"], "https://test.test")
            self.assertEqual(data["title"], "My amazing blog")
            self.assertEqual(data["author_name"], "Hugh Rundle")
            self.assertEqual(data["description"], "A short summary of my blog")

    def test_get_blog_info_no_feed(self):
        """test get blog info"""

        with open(
            pathlib.Path(__file__).parent.joinpath("data/example.html"),
            "r",
            encoding="utf-8",
        ) as webfile:
            website = RequestsMock(text=webfile, raise_for_status=request_error)

            with patch("feedparser.parse", return_value=self.feedparser), patch(
                "requests.get", return_value=website
            ):
                data = utilities.get_blog_info("http://test.test")

                self.assertEqual(data, False)

    def test_get_blog_info_with_good_feed(self):
        """test get blog info"""

        with open(
            pathlib.Path(__file__).parent.joinpath("data/good-example.html"),
            "r",
            encoding="utf-8",
        ) as webfile:
            website = RequestsMock(text=webfile, raise_for_status=request_error)

            with patch("feedparser.parse", return_value=self.feedparser), patch(
                "requests.get", return_value=website
            ):
                data = utilities.get_blog_info("http://test.test")

                self.assertEqual(
                    data,
                    {
                        "feed": "https://test.test/rss.xml",
                        "title": "My test website with an RSS feed",
                        "author_name": "Testy McTestface",
                        "description": "My cool website",
                    },
                )

    def test_get_blog_info_with_incomplete_feed(self):
        """test get blog info where the feed is incomplete"""

        with open(
            pathlib.Path(__file__).parent.joinpath("data/good-example.html"),
            "r",
            encoding="utf-8",
        ) as webfile:
            website = RequestsMock(text=webfile, raise_for_status=request_error)

            with patch("feedparser.parse", return_value=self.feedparser_partial), patch(
                "requests.get", return_value=website
            ):
                data = utilities.get_blog_info("http://test.test")

                self.assertEqual(
                    data,
                    {
                        "feed": "https://test.test/rss.xml",
                        "title": "My test website with an RSS feed",
                        "author_name": "Testy McTestface",
                        "description": "My cool website",
                    },
                )

    def test_get_blog_info_with_incomplete_head(self):
        """test get blog info where the head info is incomplete"""

        with open(
            pathlib.Path(__file__).parent.joinpath("data/partial-example.html"),
            "r",
            encoding="utf-8",
        ) as webfile:
            website = RequestsMock(text=webfile, raise_for_status=request_error)

            with patch("feedparser.parse", return_value=self.feedparser), patch(
                "requests.get", return_value=website
            ):
                data = utilities.get_blog_info("http://test.test")

                self.assertEqual(data["title"], "My test website with an RSS feed")
                self.assertEqual(data["author_name"], "Hugh Rundle")
                self.assertEqual(data["description"], "A short summary of my blog")

    def test_get_blog_info_with_incomplete_head_and_partial_feed(self):
        """test get blog info where both the feed and website head are incomplete"""

        with open(
            pathlib.Path(__file__).parent.joinpath("data/partial-example.html"),
            "r",
            encoding="utf-8",
        ) as webfile:
            website = RequestsMock(text=webfile, raise_for_status=request_error)

            with patch("feedparser.parse", return_value=self.feedparser_partial), patch(
                "requests.get", return_value=website
            ):
                data = utilities.get_blog_info("http://test.test")

                self.assertEqual(data["title"], "My test website with an RSS feed")
                self.assertEqual(data["author_name"], None)
                self.assertEqual(data["description"], None)

    def test_get_webfinger_subscribe_uri(self):
        """test get webfinger data"""

        # TODO
        pass
