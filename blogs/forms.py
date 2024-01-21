"""forms for use in views"""

from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Blog, CallForPapers, Event, Group, Newsletter, Subscriber


class DateInput(forms.DateInput):
    """make date input a date picker"""

    input_type = "date"


class RegisterBlogForm(forms.ModelForm):
    """form for registering a blog"""

    class Meta:
        """set fields and model"""

        model = Blog
        fields = ["url", "category", "activitypub_account_name", "contact_email"]


class ConfirmBlogForm(forms.ModelForm):
    """confirm all details are correct before final blog submission"""

    class Meta:
        """set fields and  model"""

        model = Blog
        fields = [
            "url",
            "feed",
            "title",
            "author_name",
            "description",
            "category",
            "activitypub_account_name",
            "contact_email",
        ]


class RegisterConferenceForm(forms.ModelForm):
    """form for registering a event"""

    class Meta:
        """set fields and model"""

        model = Event
        fields = [
            "name",
            "url",
            "category",
            "description",
            "start_date",
            "activitypub_account_name",
            "contact_email",
        ]
        widgets = {
            "start_date": DateInput(),
        }


class RegisterCallForPapersForm(forms.ModelForm):
    """form for registering a CallForPapers"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # we don't want every event ever created to be listed
        self.fields["event"].queryset = Event.objects.filter(
            approved=True, start_date__gte=timezone.now()
        ).order_by("start_date")

    class Meta:
        """set fields and model"""

        model = CallForPapers
        fields = ["event", "name", "details", "opening_date", "closing_date"]
        widgets = {
            "opening_date": DateInput(),
            "closing_date": DateInput(),
        }

        help_texts = {
            "name": _("'Call for papers', 'Call for participation' etc"),
        }


class RegisterGroupForm(forms.ModelForm):
    """form for registering a group"""

    class Meta:
        """set fields and model"""

        model = Group
        fields = [
            "name",
            "category",
            "type",
            "url",
            "registration_url",
            "description",
            "contact_email",
        ]


class RegisterNewsletterForm(forms.ModelForm):
    """form for registering a newsletter"""

    class Meta:
        """set fields and model"""

        model = Newsletter
        fields = [
            "name",
            "author",
            "category",
            "url",
            "feed",
            "description",
            "activitypub_account_name",
            "contact_email",
        ]

        help_texts = {
            "feed": _(
                "The Atom/RSS feed of your newsletter. If you include this, issues will be shown in AusGLAMR"
            ),
        }


class ContactForm(forms.Form):
    """form for contacting site admin"""

    from_email = forms.EmailField(label="Email", max_length=200)
    subject = forms.CharField(label="Subject", max_length=200)
    message = forms.CharField(widget=forms.Textarea)


class SubscribeViaMastodon(forms.Form):
    """form for subscribing to Mastodon bot"""

    username = forms.CharField(label="Username", max_length=200)


class SubscribeEmailForm(forms.ModelForm):
    """subscribe via email form"""

    class Meta:
        """set fields and model"""

        model = Subscriber
        fields = ["email"]
