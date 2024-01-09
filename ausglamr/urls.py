"""
URL configuration for ausglamr project.
"""
from django.contrib import admin
from django.urls import path, re_path

from blogs import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.HomeFeed.as_view(), name="home"),
    re_path(r"^browse/?$", views.Browse.as_view(), name="browse"),
    re_path(r"^search/?$", views.Search.as_view(), name="search"),
    re_path(r"^help/?$", views.Help.as_view(), name="help"),
    path("contribute", views.Contribute.as_view(), name="contribute"),
    path("contact", views.Contact.as_view(), name="contact"),
    path("blogs", views.Blogs.as_view(), name="blogs"),
    path("blogs/<category>", views.Blogs.as_view(), name="blog-category "),
    path("events", views.Conferences.as_view(), name="events"),
    path("events/<category>", views.Conferences.as_view(), name="events-category"),
    re_path(r"^cfps/?$", views.CallsForPapers.as_view(), name="cfps"),
    path("groups", views.Groups.as_view(), name="groups"),
    path("groups/<category>", views.Groups.as_view(), name="group-category"),
    path("newsletters", views.Newsletters.as_view(), name="newsletters"),
    path("newsletters/<category>", views.Newsletters.as_view(), name="newsletters-category"),
    path("register-blog", views.RegisterBlog.as_view(), name="register-blog"),
    path(
        "submit-blog-registration",
        views.ConfirmBlogRegistration.as_view(),
        name="submit-blog-registration",
    ),
    path(
        "register-event",
        views.RegisterConference.as_view(),
        name="register-event",
    ),
    path("register-cfp", views.RegisterCallForPapers.as_view(), name="register-cfp"),
    path("register-group", views.RegisterGroup.as_view(), name="register-group"),
    path(
        "register-newsletter",
        views.RegisterNewsletter.as_view(),
        name="register-newsletter",
    ),
    path("thankyou/<register_type>", views.Thankyou.as_view(), name="thankyou"),
    path("subscribe", views.Subscribe.as_view(), name="subscribe"),
    path("subscribe-email", views.SubscribeEmail.as_view(), name="subscribe-email"),
    path(
        "confirm-subscribe-email/<token>/<user_id>",
        views.ConfirmEmail.as_view(),
        name="confirm-subscribe-email",
    ),
    path(
        "unsubscribe-email/<token>/<id>",
        views.UnsubscribeEmail.as_view(),
        name="unsubscribe-email",
    ),
    path("feeds/blogs", views.ArticleFeed(), name="article-feed"),
    path("feeds/events", views.EventFeed(), name="event-feed"),
]
