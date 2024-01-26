"""model tests"""

from datetime import date, datetime
from datetime import timezone as dt_tz

from django.test import TestCase
from django.utils import timezone

from blogs import models


class BlogTestCase(TestCase):
    """test cases for Blog model"""

    def setUp(self):
        """set up test blog"""
        self.blog = models.Blog.objects.create(
            title="mya awesome blog",
            url="https://test.com",
            feed="https://test.com/feed.xml",
            category="LIB",
        )

    def test_get_absolute_url(self):
        """get_absolute_url class function"""

        self.assertEqual(self.blog.get_absolute_url(), "https://test.com")

    def test_set_success(self):
        """set_success class function"""

        self.blog.failing = True
        self.blog.save()
        self.blog.set_success(
            updateddate=datetime(2020, 1, 1, 12, 59, 0, tzinfo=dt_tz.utc)
        )

        self.assertEqual(self.blog.failing, False)
        self.assertEqual(self.blog.updateddate.isoformat(), "2020-01-01T12:59:00+00:00")

    def test_set_failing(self):
        """set_failing class function"""

        self.blog.failing = False
        self.blog.save()
        self.blog.set_failing()
        self.assertEqual(self.blog.failing, True)

    def test_announce_article(self):
        """announcing a blog article"""

        article = models.Article.objects.create(
            title="My article",
            author_name="Hugh",
            url="https://example.blog/1",
            blog=self.blog,
            pubdate=timezone.now(),
            guid="123-123-123",
        )

        article.announce()
        status = f"My article (Hugh on mya awesome blog)\n\nhttps://example.blog/1"
        self.assertTrue(models.Announcement.objects.filter(status=status).exists())


class ConferenceTestCase(TestCase):
    """test event functions"""

    def setUp(self):
        """set up test conf"""
        self.conf = models.Event.objects.create(
            name="Awesome Conf",
            url="https://test.com",
            category="LIB",
            start_date=date.fromisoformat("2030-12-01"),
            activitypub_account_name="@conf@conf.conf",
            approved=True,
        )

        self.cfp = models.CallForPapers.objects.create(
            event=self.conf,
            name="Call for Tests",
            opening_date=date.fromisoformat("2030-11-01"),
            closing_date=date.fromisoformat("2030-11-30"),
        )

    def test_announce(self):
        """test announcing a conf"""

        self.conf.announce()

        announcement = models.Announcement.objects.first()
        self.assertEqual(
            announcement.status,
            f"Awesome Conf (@conf@conf.conf) is a event about Libraries, starting on Sun 01 Dec 2030!\n\nhttps://test.com",
        )

    def test_announce_cfp(self):
        """test announcing a conf CFP"""

        self.cfp.announce()

        announcement = models.Announcement.objects.first()
        self.assertEqual(
            announcement.status,
            f"Awesome Conf Call for Tests is open from Fri 01 Nov 2030, closing on Sat 30 Nov 2030!\n\nMore info at https://test.com",
        )


class GroupTestCase(TestCase):
    """test group functions"""

    def setUp(self):
        """set up test gropu"""
        self.group = models.Group.objects.create(
            name="Awesome group",
            url="https://test.com",
            category="LIB",
            type="KBIN",
            registration_url="https://test.com/reg",
        )

    def test_announce(self):
        """test announcing a group"""

        self.group.announce()

        announcement = models.Announcement.objects.first()
        self.assertEqual(
            announcement.status,
            f"Awesome group is a KBin server about Libraries!\n\nJoin them: https://test.com/reg",
        )


class NewsletterTestCase(TestCase):
    """test newsletter functions"""

    def setUp(self):
        """set up test newsletter"""
        self.news = models.Newsletter.objects.create(
            name="Awesome news",
            author_name="Hugh",
            url="https://test.com",
            category="ARC",
        )

    def test_announce(self):
        """test announcing a group"""

        self.news.announce()

        announcement = models.Announcement.objects.first()
        self.assertEqual(
            announcement.status,
            f"Awesome news is a newsletter about Archives from Hugh. Check it out:\n\nhttps://test.com",
        )


class UtilsTestCase(TestCase):
    """test utility functions"""

    def test_content_warning(self):
        """test CWs"""

        warning = models.ContentWarning.objects.create(
            match_text="horrible thing", display="bad shit"
        )

        self.assertTrue(warning.is_in("I saw a horrible thingy"))
