"""rss feeds"""

from django.contrib.syndication.views import Feed
from django.utils.translation import gettext_lazy as _

from blogs.models.blog import Article
from blogs.models.event import Event

# pylint: disable=R6301


class ArticleFeed(Feed):
    """Combined RSS feed for all the articles"""

    title = "Aus GLAMR Blogs"
    link = "/feeds/blogs"
    description = "Posts from Australasian Galleries, Libraries, Archives, Museums, Records and associated blogs"

    def items(self):
        """each article in the feed"""
        return Article.objects.order_by("-pubdate")[:20]

    def item_title(self, item):
        """article title"""
        return item.title

    def item_description(self, item):
        """article description"""
        return getattr(item, "description", None) or getattr(item, "summary", None)

    def item_author_name(self, item):
        """article author"""
        return item.author_name

    def item_pubdate(self, item):
        """article publication date"""
        return item.pubdate

    def item_categories(self, item):
        """article tags"""
        categories = []
        for tag in item.tags.all():
            categories.append(tag.name)
        return categories


class EventFeed(Feed):
    """Combined RSS feed for all the articles"""

    title = "Aus GLAMR events"
    link = "/feeds/events"
    description = "Australasian events for Galleries, Libraries, Archives, Museums, Records workers"

    def items(self):
        """event items for the feed"""
        return Event.objects.order_by("-start_date")[:20]

    def item_title(self, item):
        """event name"""
        date = item.start_date.strftime("%d %b %Y")
        return f"{item.name} ({date})"

    def item_description(self, item):
        """event description"""
        return item.description

    def item_pubdate(self, item):
        """date event was registered"""
        return item.pub_date

    def item_categories(self, item):
        """event GLAMR category"""
        return [_(item.category)]
