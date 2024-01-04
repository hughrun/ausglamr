"""test views"""

from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.core import mail
from django.test import Client, TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils import timezone

from blogs import forms, models, views


class PublicTests(TestCase):
    """Public views test cases"""

    def setUp(self):
        start_date = timezone.now()

        self.factory = RequestFactory()
        self.glam_conf = models.Event.objects.create(
            name="Awesome conf",
            url="https://awesome.conf",
            category="GLAM",
            description="An awesome conf",
            start_date=start_date,
        )

    def test_public_views_load(self):
        """
        Do public views load correctly?
        """

        home = self.client.get(reverse("home"))
        self.assertEqual(home.status_code, 200)

        browse = self.client.get(reverse("browse"))
        self.assertEqual(browse.status_code, 200)

        search = self.client.get(reverse("search"))
        self.assertEqual(search.status_code, 200)

        help = self.client.get(reverse("help"))
        self.assertEqual(help.status_code, 200)

        contribute = self.client.get(reverse("contribute"))
        self.assertEqual(contribute.status_code, 200)

        contact = self.client.get(reverse("contact"))
        self.assertEqual(contact.status_code, 200)

        blogs_response = self.client.get(reverse("blogs"))
        self.assertEqual(blogs_response.status_code, 200)

        confs_response = self.client.get(reverse("conferences"))
        self.assertEqual(confs_response.status_code, 200)

        groups_response = self.client.get(reverse("groups"))
        self.assertEqual(groups_response.status_code, 200)

        news_response = self.client.get(reverse("newsletters"))
        self.assertEqual(news_response.status_code, 200)

        rblog_response = self.client.get(reverse("register-blog"))
        self.assertEqual(rblog_response.status_code, 200)

        submit = self.client.get(reverse("submit-blog-registration"))
        self.assertEqual(submit.status_code, 200)  # 301?

        rconf_response = self.client.get(reverse("register-event"))
        self.assertEqual(rconf_response.status_code, 200)

        rcfp_response = self.client.get(reverse("register-cfp"))
        self.assertEqual(rcfp_response.status_code, 200)

        rgroup_response = self.client.get(reverse("register-group"))
        self.assertEqual(rgroup_response.status_code, 200)

        rnews_response = self.client.get(reverse("register-newsletter"))
        self.assertEqual(rnews_response.status_code, 200)

        rnews_response = self.client.get(
            reverse("thankyou", args=({"register_type": "blog"}))
        )
        self.assertEqual(rnews_response.status_code, 200)

        subscribe = self.client.get(reverse("subscribe"))
        self.assertEqual(subscribe.status_code, 200)

        af = self.client.get(reverse("article-feed"))
        self.assertEqual(af.status_code, 200)

        cf = self.client.get(reverse("event-feed"))
        self.assertEqual(cf.status_code, 200)

    def test_confirm_register_blog(self):
        """post final event registration form"""

        view = views.ConfirmBlogRegistration.as_view()
        form = forms.ConfirmBlogForm()
        form.data["title"] = "My blog"
        form.data["author_name"] = "Bob Bobson"
        form.data["url"] = "https://www.example.com"
        form.data["feed"] = "https://www.example.com/feed"
        form.data["category"] = "LIB"

        request = self.factory.post("/submit-blog-registration", form.data)
        request.user = AnonymousUser()

        view(request)

        exists = models.Blog.objects.filter(title="My blog").exists()
        self.assertTrue(exists)

    def test_register_conference(self):
        """post event registration form"""

        view = views.RegisterConference.as_view()
        form = forms.RegisterConferenceForm()
        form.data["name"] = "My event"
        form.data["description"] = "A conf for gallerists"
        form.data["url"] = "https://awesome.conf/cfp"
        form.data["category"] = "GAL"
        form.data["start_date"] = "30/01/2024"

        request = self.factory.post("register-event/", form.data)

        request.user = AnonymousUser()

        view(request)

        exists = models.Event.objects.filter(name="My event").exists()
        self.assertTrue(exists)

    def test_register_cfp(self):
        """post CFP registration form"""

        view = views.RegisterCallForPapers.as_view()
        form = forms.RegisterCallForPapersForm()
        form.data["event"] = self.glam_conf.id
        form.data["name"] = "Call for Papers"
        form.data["url"] = "https://www.example.com"
        form.data["category"] = "GLAM"
        form.data["opening_date"] = "01/01/2024"
        form.data["closing_date"] = "28/01/2024"

        request = self.factory.post("register-cfp/", form.data)
        request.user = AnonymousUser()

        view(request)

        exists = models.CallForPapers.objects.filter(name="Call for Papers").exists()
        self.assertTrue(exists)

    def test_register_group(self):
        """post group registration form"""

        view = views.RegisterGroup.as_view()
        form = forms.RegisterGroupForm()
        form.data["name"] = "GLAMR testers"
        form.data["category"] = "GLAM"
        form.data["type"] = "KBIN"
        form.data["url"] = "https://kibin.test"
        form.data["registration_url"] = "https://kbin.test/glamr"
        form.data["description"] = "GLAMR testers"

        request = self.factory.post("register-group/", form.data)
        request.user = AnonymousUser()

        view(request)

        exists = models.Group.objects.filter(name="GLAMR testers").exists()
        self.assertTrue(exists)

    def test_register_newsletter(self):
        """post newsletter registration form"""

        view = views.RegisterNewsletter.as_view()
        form = forms.RegisterNewsletterForm()
        form.data["name"] = "My newsletter"
        form.data["author"] = "Bob Bobson"
        form.data["url"] = "https://www.example.com"
        form.data["category"] = "LIB"

        request = self.factory.post("register-newsletter/", form.data)
        request.user = AnonymousUser()

        view(request)

        exists = models.Newsletter.objects.filter(name="My newsletter").exists()
        self.assertTrue(exists)

    def test_contact(self):
        """post message"""

        view = views.Contact.as_view()
        form = forms.ContactForm()
        form.data["from_email"] = "example@example.mail"
        form.data["subject"] = "Hello"
        form.data["message"] = "Hi there"

        request = self.factory.post("contact/", form.data)
        request.user = AnonymousUser()

        view(request)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, "Message via Aus GLAMR: Hello")

    def test_search(self):
        """post search query"""

        # TODO
        pass

    def test_browse(self):
        """post browse tags query"""

        # TODO
        pass
