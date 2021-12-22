from collections import defaultdict

from jsonfield import JSONField
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.blocks import RichTextBlock
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtailcodeblock.blocks import CodeBlock


class HomePage(Page):
    """The parent of all other Pages."""

    @property
    def blogposts(self):
        return (
            BlogPostPage.objects.child_of(self)
            .live()
            .public()
            .order_by("-first_published_at")
        )

    @property
    def blogposts_grouped_by_year(self):
        year_to_posts = defaultdict(list)
        for blogpost in self.blogposts:
            post_year = blogpost.first_published_at.year
            year_to_posts[post_year].append(blogpost)
        return year_to_posts.items()


class BlogPostPage(Page):
    body = StreamField(
        [
            ("paragraph", RichTextBlock()),
            ("image", ImageChooserBlock()),
            ("code", CodeBlock()),
        ]
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
    ]

    _original_wp_post = JSONField(null=True, blank=True, default=None)
    """Temporary field as we migrate from Wordpress.

    Holds the original Post as JSON, including all metadata.

    TODO: Remove this field once happy with the migration.

    """