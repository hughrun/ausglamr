"""admin interface customisations"""

# pylint: disable=W0613

from django.conf import settings
from django.contrib import admin
from django.utils import timezone

from . import models
from . import utilities


@admin.action(description="Approve selected")
def approve(modeladmin, request, queryset):
    """approve selected"""
    queryset.update(approved=True)

    for instance in queryset:
        instance.announce()

        if hasattr(instance, "event"):  # CFP
            recipient = instance.event.contact_email
        if hasattr(
            instance, "contact_email"
        ):  # overrides above in case needed in future
            recipient = instance.contact_email

        if recipient:
            if hasattr(instance, "name"):
                title = instance.name
            else:
                title = instance.title

            subject = f"✅ {title} has been approved on AusGLAMR!"
            message = f"<html><body><p>{title} has been approved on <a href='https://{settings.DOMAIN}'>AusGLAMR</a>. Hooray!</p></body></html>"

            utilities.send_email(subject, message, recipient)


@admin.action(description="Unapprove selected")
def unapprove(modeladmin, request, queryset):
    """unapprove selected"""
    queryset.update(approved=False)


@admin.action(description="Suspend selected blogs")
def suspend(modeladmin, request, queryset):
    """suspend selected blogs"""
    queryset.update(suspended=True)

    for instance in queryset:
        if hasattr(instance, "contact_email"):
            if hasattr(instance, "name"):
                title = instance.name
            else:
                title = instance.title

            subject = f"⚠️ {title} has been suspended from AusGLAMR!"
            message = f"<html><body>\
            <p>Your blog {title} has been suspended from AusGLAMR. It may be unsuspended in future once the issue is resolved. If you would like more information, please reply to this email.</p> \
            </body></html>"

            utilities.send_email(subject, message, instance.contact_email)


@admin.action(description="Unsuspend selected blogs")
def unsuspend(modeladmin, request, queryset):
    """unsuspend selected blogs"""
    queryset.update(suspended=False, suspension_lifted=timezone.now())

    for instance in queryset:
        if hasattr(instance, "contact_email"):
            if hasattr(instance, "name"):
                title = instance.name
            else:
                title = instance.title

            subject = f"✅ The AusGLAMR suspension on {title} has been lifted"
            message = f"<html><body>\
            <p>The suspension on your blog {title} has been removed on AusGLAMR. Please note that articles published whilst it was suspended will not be added to AusGLAMR retrospectively. If you would like more information, please reply to this email.</p> \
            </body></html>"

            utilities.send_email(subject, message, instance.contact_email)


@admin.action(description="Confirm selected subscribers")
def confirm(modeladmin, request, queryset):
    """confirm selected"""
    queryset.update(confirmed=True)


@admin.action(description="Unconfirm selected subscribers")
def unconfirm(modeladmin, request, queryset):
    """unconfirm selected"""
    queryset.update(confirmed=False)


@admin.action(description="Deactivate selected blogs")
def disable(modeladmin, request, queryset):
    """disable selected"""
    queryset.update(active=False)


@admin.action(description="Activate selected blogs")
def activate(modeladmin, request, queryset):
    """un-disable selected"""
    queryset.update(active=True)


@admin.action(description="Send confirmation request to selected subscribers")
def send_conf_request(modeladmin, request, queryset):
    """send to selected"""

    for instance in queryset:
        instance.send_confirmation_email()


@admin.register(models.Blog)
class Blog(admin.ModelAdmin):
    """display settings for blogs"""

    list_display = (
        "url",
        "title",
        "author_name",
        "approved",
        "announced",
        "suspended",
        "failing",
        "active",
    )
    ordering = ["approved", "-suspended", "-failing"]
    actions = [approve, unapprove, suspend, unsuspend, activate, disable]


@admin.register(models.Article)
class Article(admin.ModelAdmin):
    """display settings for articles"""

    date_hierarchy = "pubdate"
    list_display = ("title", "blog_title", "pubdate")

    def blog_title(self, obj):  # pylint: disable=no-self-use
        """get the title of the parent blog"""
        return obj.blog.title


@admin.register(models.Tag)
class Tag(admin.ModelAdmin):
    """display settings for tags"""

    list_display = ("name",)


@admin.register(models.Event)
class Event(admin.ModelAdmin):
    """display settings for conferences"""

    list_display = (
        "name",
        "approved",
        "announcements",
        "category",
        "description",
        "start_date",
    )
    ordering = ["approved", "announcements"]
    actions = [approve, unapprove]


@admin.register(models.CallForPapers)
class CallForPapers(admin.ModelAdmin):
    """display settings for CFPs"""

    list_display = ("name", "event", "approved", "closing_date")
    list_select_related = ("event",)
    ordering = ["approved", "closing_date"]
    actions = [approve, unapprove]


@admin.register(models.Group)
class Group(admin.ModelAdmin):
    """display settings for groups"""

    list_display = ("name", "approved", "category", "description")
    ordering = ["approved", "name"]
    actions = [approve, unapprove]


@admin.register(models.Newsletter)
class Newsletter(admin.ModelAdmin):
    """display settings for newsletters"""

    list_display = ("name", "approved", "category", "description")
    ordering = ["approved", "name"]
    actions = [approve, unapprove]


@admin.register(models.ContentWarning)
class ContentWarning(admin.ModelAdmin):
    """display settings for CWs"""

    list_display = (
        "match_text",
        "display",
    )


@admin.register(models.Announcement)
class Announcement(admin.ModelAdmin):
    """display settings for announcements"""

    list_display = ("status",)


@admin.register(models.SiteMessage)
class SiteMessage(admin.ModelAdmin):
    """create a message"""

    list_display = ("message",)


@admin.register(models.Subscriber)
class Subscriber(admin.ModelAdmin):
    """email subscribers"""

    list_display = (
        "email",
        "confirmed",
    )
    actions = [confirm]
