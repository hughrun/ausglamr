"""public views (no need to log in)"""

# pylint: disable=R6301
from itertools import chain
from operator import attrgetter

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.postgres.search import SearchRank, SearchVector
from django.utils.translation import gettext_lazy as _
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from blogs import forms, models
from blogs.utilities import get_blog_info, get_webfinger_subscribe_uri


class HomeFeed(View):
    """the home feed when someone visits the site"""

    def get(self, request):
        """display home page"""

        latest = models.Article.objects.order_by("-pubdate")[:10]

        data = {"title": "Latest blog posts", "latest": latest}
        return render(request, "index.html", data)


class Blogs(View):
    """browse the list of blogs"""

    def get(self, request):
        """here they are"""

        blogs = models.Blog.objects.filter(approved=True, active=True).order_by(
            "-updateddate"
        )
        for blog in blogs:
            blog.category_name = models.Category(blog.category).label
        data = {"title": "Blogs and websites", "blogs": blogs}
        return render(request, "browse/blogs.html", data)


class Conferences(View):
    """browse the list of conferences"""

    def get(self, request):
        """here they are"""
        now = timezone.now()
        cons = models.Event.objects.filter(approved=True, start_date__gte=now).order_by(
            "start_date"
        )
        for con in cons:
            con.category_name = models.Category(con.category).label
            con.call_for_papers = con.cfp.all().last()
            if con.call_for_papers and (con.call_for_papers.closing_date > now.date()):
                date = con.call_for_papers.closing_date.strftime("%a %d %b %Y")
                con.call_for_papers = f"{con.call_for_papers.name} closes {date}"

        data = {"title": "Upcoming events", "cons": cons}
        return render(request, "browse/events.html", data)


class CallsForPapers(View):
    """browse the list of CFPs"""

    def get(self, request):
        """here they are"""
        now = timezone.now()
        cfps = models.CallForPapers.objects.filter(
            approved=True, closing_date__gte=now
        ).order_by("closing_date")
        data = {"title": "Calls for Papers open now", "cfps": cfps}
        return render(request, "browse/cfp.html", data)


class Groups(View):
    """browse the list of groups"""

    def get(self, request):
        """here they are"""
        groups = models.Group.objects.filter(approved=True).order_by("name")
        for group in groups:
            group.category_name = models.Category(group.category).label
            group.reg_type = models.utils.GroupType(group.type).label
        data = {"title": "Groups and discussion lists", "groups": groups}
        return render(request, "browse/groups.html", data)


class Newsletters(View):
    """browse the list of groups"""

    def get(self, request):
        """here they are"""
        news = models.Newsletter.objects.filter(approved=True).order_by("name")
        for letter in news:
            letter.category_name = models.Category(letter.category).label
        data = {"title": "Newsletters", "news": news}
        return render(request, "browse/newsletters.html", data)


class RegisterBlog(View):
    """register a blog"""

    def get(self, request):
        """the registration page with a form"""

        form = forms.RegisterBlogForm()
        data = {"title": "Register your blog", "form": form}
        return render(request, "blogs/register.html", data)

    def post(self, request):
        """receive POSTED RegisterBlogForm"""

        form = forms.RegisterBlogForm(request.POST)
        if form.is_valid():
            try:
                blog_info = get_blog_info(form.cleaned_data["url"])
            except KeyError:
                return render(
                    request,
                    "blogs/register.html",
                    {"title": "Complete blog registration", "form": form},
                )

            data = {
                "title": "Complete blog registration",
                "form": form,
            }

            if blog_info:
                data["blog_info"] = blog_info

            else:
                data[
                    "error"
                ] = "Could not auto-discover your feed info, please enter manually"

            return render(request, "blogs/confirm-register.html", data)

        data = {"title": "Register your blog", "form": form}
        return render(request, "blogs/register.html", data)


class ConfirmBlogRegistration(View):
    """submit validated and pre-filled registration form"""

    def get(self, request):
        """the confirm registration page"""

        form = forms.ConfirmBlogForm(request.POST)
        data = {"title": "Complete blog registration", "form": form}

        return render(request, "blogs/confirm-register.html", data)

    def post(self, request):
        """the final form has been submitted!"""

        form = forms.ConfirmBlogForm(request.POST)
        if form.is_valid():
            blog = form.save()
            send_email("blog", blog)
            return redirect("/thankyou/blog")

        data = {"title": "Oops!", "form": form}
        return render(request, "blogs/confirm-register.html", data)


class RegisterConference(View):
    """register a event"""

    def get(self, request):
        """the registration page with a form"""

        form = forms.RegisterConferenceForm()
        data = {"title": "Register your event", "form": form}
        return render(request, "events/register.html", data)

    def post(self, request):
        """receive form"""

        form = forms.RegisterConferenceForm(request.POST)
        if form.is_valid():
            conf = form.save()
            send_email("event", conf)
            cfp_form = forms.RegisterCallForPapersForm({"event": conf.id})
            data = {
                "title": "Register your Call for Papers",
                "form": cfp_form,
                "conf_name": conf.name,
            }

            return render(request, "events/cfp.html", data)

        data = {"title": "Complete blog registration", "form": form, "errors": True}
        return render(request, "events/register.html", data)


class RegisterCallForPapers(View):
    """register a RegisterCallForPapers"""

    def get(self, request):
        """the registration page with a form"""

        form = forms.RegisterCallForPapersForm()
        data = {"title": "Register your Call For Papers", "form": form}

        return render(request, "events/cfp.html", data)

    def post(self, request):
        """receive POSTED RegisterCallForPapersForm"""

        form = forms.RegisterCallForPapersForm(request.POST)

        if form.is_valid():
            cfp = form.save()
            send_email("Call for Papers", cfp)
            return redirect("/thankyou/Call For Papers")

        data = {
            "title": "Register your Call For Papers",
            "form": form,
            "errors": True,
        }

        return render(request, "events/cfp.html", data)


class RegisterGroup(View):
    """register a group"""

    def get(self, request):
        """the registration page with a form"""

        form = forms.RegisterGroupForm()
        data = {"title": "Register your group", "form": form}

        return render(request, "register-group.html", data)

    def post(self, request):
        """receive POSTED form"""

        form = forms.RegisterGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            send_email("group", group)
            return redirect("/thankyou/group")

        data = {"title": "Oops!", "form": form, "errors": True}

        return render(request, "register-group.html", data)


class RegisterNewsletter(View):
    """register a newsletter"""

    def get(self, request):
        """the registration page with a form"""

        form = forms.RegisterNewsletterForm()
        data = {"title": "Register your newsletter", "form": form}

        return render(request, "register-newsletter.html", data)

    def post(self, request):
        """receive POSTED form"""

        form = forms.RegisterNewsletterForm(request.POST)

        if form.is_valid():
            newsletter = form.save()
            send_email("newsletter", newsletter)
            return redirect("/thankyou/newsletter")

        data = {"title": "Oops!", "form": form, "errors": True}

        return render(request, "register-newsletter.html", data)


class Search(View):
    """search functions"""

    def get(self, request, articles=None):
        """display search page"""

        query = request.GET.get("q")

        article_vector = (
            SearchVector("tags__name", weight="A")
            + SearchVector("title", weight="B")
            + SearchVector("description", weight="C")
        )

        articles = (
            models.Article.objects.annotate(rank=SearchRank(article_vector, query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
        )

        conference_vector = SearchVector("name", weight="A") + SearchVector(
            "description", weight="C"
        )

        events = (
            models.Event.objects.annotate(rank=SearchRank(conference_vector, query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
        )

        cfp_vector = SearchVector("name", weight="B") + SearchVector(
            "details", weight="C"
        )

        cfps = (
            models.CallForPapers.objects.annotate(rank=SearchRank(cfp_vector, query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
        )

        news_vector = SearchVector("name", weight="A") + SearchVector(
            "description", weight="C"
        )

        newsletters = (
            models.Newsletter.objects.annotate(rank=SearchRank(news_vector, query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
        )

        group_vector = SearchVector("name", weight="A") + SearchVector(
            "description", weight="C"
        )

        groups = (
            models.Event.objects.annotate(rank=SearchRank(group_vector, query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
        )

        combined = sorted(
            chain(articles, events, cfps, newsletters, groups),
            key=attrgetter("rank"),
            reverse=True,
        )

        for item in combined:
            if hasattr(item, "category"):
                item.category_name = models.Category(item.category).label
            if hasattr(item, "event"):
                item.category = models.Category(item.event.category)
                item.category_name = models.Category(item.event.category).label

        paginator = Paginator(combined, 10)
        page_number = request.GET.get("page")
        paged = paginator.get_page(page_number)

        data = {"title": "Search Aus GLAMR", "items": paged, "query": query}

        return render(request, "search.html", data)


class Browse(View):
    """browse by clicking on a tag"""

    def get(self, request):
        """display browse results"""

        query = request.GET.get("q")
        results = models.Article.objects.filter(tags__name=query).order_by("-pubdate")
        trending = models.Tag.objects.annotate(count=Count("articles")).order_by(
            "-count"
        )[:10]

        paginator = Paginator(results, 10)
        page_number = request.GET.get("page")
        paged = paginator.get_page(page_number)

        data = {
            "title": f"Articles tagged '{query}'",
            "trending": trending,
            "items": paged,
            "query": query,
        }

        return render(request, "browse/tags.html", data)


class Subscribe(View):
    """Subscribe page showing RSS feed link and mastodon follow form"""

    def get(self, request):
        """display subscribe page"""

        return render(request, "subscribe.html", {})

    def post(self, request):
        """subscribe to Mastodon account"""

        form = forms.SubscribeViaMastodon(request.POST)
        if form.is_valid():
            try:
                username = form.cleaned_data["username"]
                uri = get_webfinger_subscribe_uri(username)

                if uri:
                    return redirect(uri)

                form.add_error(
                    "username", "Enter a valid username e.g. @example@ausglam.space"
                )

            except KeyError:
                pass

        return render(request, "subscribe.html", {"form": form})


class SubscribeEmail(View):
    """Subscribe to weekly emails"""

    def get(self, request):
        """display subscribe page"""

        form = forms.SubscribeEmailForm()
        data = {"title": "Get weekly email updates", "form": form}

        return render(request, "subscribe-email.html", data)

    def post(self, request):
        """subscribe to Mastodon account"""

        form = forms.SubscribeEmailForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.send_confirmation_email()
            return redirect("/thankyou/email%20address")

        return render(request, "subscribe.html", {"form": form})


class ConfirmEmail(View):
    """Hit this when click to confirm email subscription"""

    def get(self, request, token, user_id):
        """display confirmation page"""

        user = get_object_or_404(models.Subscriber, id=user_id, token=token)

        user.confirmed = True
        user.save()

        return render(request, "confirm-email.html", {"title": "Confirmed!"})


class UnsubscribeEmail(View):
    """Hit this when click to confirm email subscription"""

    def get(self, request, token, user_id):
        """unsubscribe conf page"""

        user = get_object_or_404(models.Subscriber, id=user_id, token=token)
        user.delete()

        return render(request, "unsubscribe.html", {"title": "Sorry to see you go"})


class Contribute(View):
    """help page"""

    def get(self, request):
        """display contribute page"""

        data = {
            "title": "Contribute",
        }
        return render(request, "contribute.html", data)


class Help(View):
    """help page"""

    def get(self, request):
        """display help page"""

        data = {
            "title": "Help",
        }
        return render(request, "help.html", data)


class Contact(View):
    """contact Hugh"""

    def get(self, request):
        """the contact page with a form"""

        form = forms.ContactForm()
        data = {"title": "Get in touch", "form": form}

        return render(request, "contact.html", data)

    def post(self, request):
        """receive POSTED form"""

        form = forms.ContactForm(request.POST)

        if form.is_valid():
            from_email = form.cleaned_data["from_email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]
            send_contact_email(from_email, subject, message)
            return redirect("/thankyou/message")

        data = {"title": "Oops!", "form": form, "errors": True}

        return render(request, "contact.html", data)


class Thankyou(View):
    """thankyou for registering page"""

    def get(self, request, register_type):
        """display thankyou page"""

        data = {"title": "Thanks!", "register_type": register_type}
        return render(request, "thanks.html", data)


def send_email(instance, obj):
    """send an email alert to admin"""

    html_message = f"<html><body>\
    <p>A new {instance} has been registered:</p>\
    <strong>{obj.title if hasattr(obj, 'title') else obj.name}</strong></p>\
    <p>To approve or reject visit <a href='https://{settings.DOMAIN}/admin'>{settings.DOMAIN}/admin</a></p>\
    </body></html>"

    msg = EmailMessage(
        f"📥 Someone has registered a new {instance}!",
        html_message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
    )
    msg.content_subtype = "html"
    msg.send()


def send_contact_email(from_email, subject, message):
    """email the message"""

    html_message = f"<html><body><p>{message}</p></body></html>"

    msg = EmailMessage(
        f"Message via Aus GLAMR: {subject}",
        html_message,
        f"{from_email}",
        [settings.ADMIN_EMAIL],
    )
    msg.content_subtype = "html"
    msg.send()
