"""custom tags"""

from django import template
from blogs import models

register = template.Library()


@register.inclusion_tag("messages.html")
def site_messages():
    """display site messages"""
    return {"messages": models.SiteMessage.objects.all()}
