"""rss feeds"""

from itertools import chain
from operator import attrgetter

from django.conf import settings

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed


from blogs import models

# pylint: disable=R6301


class ArticleFeed(Feed):
    """Combined RSS feed for all the articles"""

    feed_type = Atom1Feed
    link = "/blog-articles"
    feed_url = "/blog-articles/feed"
    feed_guid = f"https://{settings.DOMAIN}/blog-articles/feed"

    title = "Aus GLAMR Blog articles"
    description = "Posts from Australasian Galleries, Libraries, Archives, Museums, Records and associated blogs"

    def items(self):
        """each article in the feed"""
        return models.Article.objects.order_by("-pubdate")[:20]

    def item_title(self, item):
        """article title"""
        return item.title

    def item_description(self, item):
        """article description"""
        return getattr(item, "description", None) or getattr(item, "summary", None)

    def item_author_name(self, item):
        """article author"""
        return item.author_name

    def item_link(self, item):
        """item url"""
        return item.url

    def item_pubdate(self, item):
        """article publication date"""
        return item.pubdate

    def item_updateddate(self, item):
        """updated date"""
        return item.updateddate

    def item_categories(self, item):
        """article tags"""
        categories = []
        for tag in item.tags.all():
            categories.append(tag.name)
        return categories


class EventFeed(Feed):
    """Combined feed for all events and calls for papers"""

    feed_type = Atom1Feed
    link = "/events"
    feed_url = "/events/feed"
    feed_guid = f"https://{settings.DOMAIN}/events/feed"

    title = "Aus GLAMR events"
    description = "Australasian events for Galleries, Libraries, Archives, Museums, Records workers"

    def items(self):
        """event and CFP items for the feed"""

        events = models.Event.objects.filter(approved=True)
        cfps = models.CallForPapers.objects.all()

        result_list = sorted(
            chain(events, cfps),
            key=attrgetter("pubdate"),
            reverse=True,
        )
        return result_list[:20]

    def item_title(self, item):
        """event or CFP name"""
        return item.name

    def item_description(self, item):
        """description or details"""
        return (
            item.description
            if hasattr(item, "description")
            else item.details
            if hasattr(item, "details")
            else None
        )

    def item_link(self, item):
        """item url"""
        return item.url if hasattr(item, "url") else item.event.url

    def item_pubdate(self, item):
        """date event/CFP was registered"""
        return item.pubdate

    def item_categories(self, item):
        """event GLAMR category"""
        if hasattr(item, "category"):
            return [models.Category(item.category).label]


class EditionFeed(Feed):
    """Newsletter editions"""

    feed_type = Atom1Feed
    link = "/newsletter-editions"
    feed_url = "/newsletter-editions/feed"
    feed_guid = f"https://{settings.DOMAIN}/newsletter-editions/feed"

    title = "Aus GLAMR Blog newsletter editions"
    description = "Newsletters from Australasian Galleries, Libraries, Archives, Museums, Records and associated blogs"

    def items(self):
        """each article in the feed"""
        return models.Edition.objects.order_by("-pubdate")[:20]

    def item_title(self, item):
        """article title"""
        return item.title

    def item_description(self, item):
        """article description"""
        return item.description

    def item_author_name(self, item):
        """article author"""
        return item.author_name

    def item_link(self, item):
        """item url"""
        return item.url

    def item_pubdate(self, item):
        """article publication date"""
        return item.pubdate

    def item_updateddate(self, item):
        """updated date"""
        return item.updateddate

    def item_categories(self, item):
        """newsletter category"""
        return [models.Category(item.newsletter.category).label]


class CombinedFeed(Feed):
    """Combined Atom feed for everything"""

    feed_type = Atom1Feed
    link = "/"
    feed_url = "/feed"
    feed_guid = f"https://{settings.DOMAIN}/feed"

    title = "Aus GLAMR"
    description = "Latest news and opinion from Australasian Galleries, Libraries, Archives, Museums, Records professionals"
    categories = [
        "GLAM",
        "GLAMR",
        "Galleries",
        "Libraries",
        "Archives",
        "Museums",
        "Records",
    ]
    feed_copyright = "Copyright is owned by individual authors"
    ttl = 600

    def items(self):
        """items for the feed"""

        blog_objects = models.Blog.objects.filter(
            approved=True, suspended=False, active=True
        )

        posts = models.Article.objects.all()

        newsletters = models.Newsletter.objects.filter(approved=True, active=True)

        editions = models.Edition.objects.all()

        groups = models.Group.objects.filter(approved=True)

        events = models.Event.objects.filter(approved=True)

        cfps = models.CallForPapers.objects.all()

        result_list = sorted(
            chain(blog_objects, posts, newsletters, editions, groups, events, cfps),
            key=attrgetter("pubdate"),
            reverse=True,
        )

        return result_list[:30]

    def item_title(self, item):
        """title or name"""
        return item.name if hasattr(item, "name") else item.title

    def item_description(self, item):
        """description"""
        return (
            item.description
            if hasattr(item, "description")
            else item.details
            if hasattr(item, "details")
            else None
        )

    def item_link(self, item):
        """item url"""
        return item.url if hasattr(item, "url") else item.event.url

    def item_guid(self, item):
        """guid"""

        return item.url if hasattr(item, "url") else f"{item.event.url}-cfp-{item.id}"

    def item_author_name(self, item):
        """author"""
        return getattr(item, "author_name", None)

    def item_pubdate(self, item):
        """date item was published"""

        pubdate = getattr(item, "pubdate", None)
        return pubdate

    def item_updateddate(self, item):
        """updated date"""
        if hasattr(item, "updateddate"):
            return item.updateddate

        if hasattr(item, "pubdate"):
            return item.pubdate

        return None

    def item_categories(self, item):
        """GLAMR category or tags"""

        if hasattr(item, "category"):
            return [models.Category(item.category).label]

        if hasattr(item, "tags"):
            categories = []
            for tag in item.tags.all():
                categories.append(tag.name)
            return categories

        return None
