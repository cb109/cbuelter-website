from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page


class HomePage(Page):
    pass


class BlogPostPage(Page):
    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("body", classname="full"),
    ]
