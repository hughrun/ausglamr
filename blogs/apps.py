"""django apps"""
from django.apps import AppConfig


class BlogsConfig(AppConfig):
    """default config class"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "blogs"
