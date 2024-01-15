from collections import defaultdict

from jsonfield import JSONField
from readtime.utils import DEFAULT_WPM
from readtime.utils import read_time_as_seconds
from readtime.utils import Result
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import RichTextBlock
from wagtail.fields import StreamField
from wagtail.models import Page
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
        ],
        use_json_field=True
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    _original_wp_post = JSONField(null=True, blank=True, default=None)
    """Temporary field as we migrate from Wordpress.

    Holds the original Post as JSON, including all metadata.

    TODO: Remove this field once happy with the migration.

    """

    def get_read_time(self, wpm=DEFAULT_WPM):
        text = " ".join(
            [
                str(block.value)
                for block in self.body
                if block.block_type in ("paragraph", "code")
            ]
        )
        num_images = len([block for block in self.body if block.block_type == "image"])
        seconds = read_time_as_seconds(text, images=num_images)
        return Result(seconds, wpm=wpm)
