"""useful functions that are not associated with models or views"""

import re

from bs4 import BeautifulSoup
import feedparser
import requests

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.encoding import iri_to_uri

headers = {"user-agent": "Aus-GLAM-Blogs/0.0.1"}
timeout = (4, 13)


def get_feed_info(feed):
    """parse a feed for basic blog info"""

    b = feedparser.parse(feed)
    blog = {}
    blog["feed"] = feed
    blog["title"] = getattr(b.feed, "title", "")
    blog["author_name"] = getattr(b.feed, "author", None)
    blog["description"] = getattr(b.feed, "subtitle", "")
    blog["last_updated"] = getattr(b.feed, "updated_parsed", "")

    return blog


def get_blog_info(url):
    """given a url, return info from the site
    including the feed URL"""

    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.find_all(type=["application/rss+xml", "application/atom+xml"])
        blog_info = {}

        try:
            author = soup.select_one('meta[name="author"]').get("content")
        except AttributeError:
            try:
                author = soup.select_one('meta[name="creator"]').get("content")
            except AttributeError:
                author = ""

        if len(links) > 0:
            blog_info = get_feed_info(links[0].get("href"))

            blog_info["title"] = blog_info["title"] or soup.title.string
            blog_info["author_name"] = blog_info["author_name"] or author

        return blog_info

    except requests.Timeout:
        print(f"TIMEOUT error registering {url}, trying longer timeout")
        r = requests.get(url, headers=headers, timeout=(31, 31))
        r.raise_for_status()  # let it flow through, a timeout here means the site is unreasonably slow

    except Exception as e:
        print(f"CONNECTION ERROR when registering {url}")
        print(e)
        return False


def get_webfinger_subscribe_uri(username):
    """given a username, return the url needed to follow the user"""

    try:
        regex = re.match(r"(?:.*@)(.*)", username)
        domain = regex.group(1)
        if username[0] == "@":
            username = username[1:]
        webfinger_url = (
            f"https://{domain}/.well-known/webfinger/?resource=acct:{username}"
        )

        r = requests.get(webfinger_url, headers=headers, timeout=timeout)
        r.raise_for_status()

    except requests.Timeout:
        print(f"TIMEOUT error finding {username}, trying longer timeout")
        r = requests.get(webfinger_url, headers=headers, timeout=(31, 31))
        r.raise_for_status()  # let it flow through, a timeout here means the site is unreasonably slow

    except Exception as e:
        print(f"CONNECTION ERROR when subscribing via {username}")
        print(e)
        return None

    data = r.json()

    user_id = False
    template = False

    for link in data["links"]:
        if link["rel"] == "self":
            user_id = link["href"]
        if link["rel"] == "http://ostatus.org/schema/1.0/subscribe":
            template = link["template"]

    if user_id and template:
        encoded_user = iri_to_uri("blogs@ausglam.space")
        uri = template.replace("{uri}", encoded_user)
        return uri

    return None


def send_email(subject, message, recipient):
    """send an email"""

    msg = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
    )
    msg.content_subtype = "html"
    msg.send()
