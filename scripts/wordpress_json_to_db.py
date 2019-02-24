"""One-off script to migrate wordpress exported JSON into our database.

Most functionality taken from:

    https://github.com/russellballestrini/blog-to-json

Usage:

    $ python wordpress_json_to_db.py wordpress.json

"""

import json
import sys
from datetime import datetime
from time import mktime

import dateutil.parser
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from home.models import HomePage
from home.models import BlogPostPage


def make_timestamp_from_datetime(datetime_object):
    return int(mktime(datetime_object.timetuple()))


def get_wordpress_timestamp(date_str):
    datetime_object = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return make_timestamp_from_datetime(datetime_object)


def get_comment_dict(comment):
    return {
        "id": int(comment["wp:comment_id"]),
        "parent_id": int(comment["wp:comment_parent"]),
        "author_ip": comment["wp:comment_author_IP"],
        "author": comment["wp:comment_author"],
        "email": comment["wp:comment_author_email"],
        "content": comment["wp:comment_content"],
        "date": comment["wp:comment_date"],
        "timestamp": get_wordpress_timestamp(comment["wp:comment_date"]),
    }


def get_comments_from_post(post):
    comments = []
    if "wp:comment" not in post:
        # some posts do not have comments.
        return comments

    post_comments = post["wp:comment"]
    if not isinstance(post_comments, list):
        # some posts have 1 comment, which is type Dict, so wrap in list.
        post_comments = [post_comments]

    for comment in post_comments:
        comments.append(get_comment_dict(comment))
    return comments


def get_metadata_from_post(post):
    metadata = {}
    if "wp:postmeta" not in post:
        return metadata
    for meta in post["wp:postmeta"]:
        if isinstance(meta, dict):
            metadata[meta["wp:meta_key"]] = meta["wp:meta_value"]
    return metadata


def wordpress_xml_dict_to_posts(document):
    posts = []
    for post in document["rss"]["channel"]["item"]:
        name = post["wp:post_name"]
        post_type = post["wp:post_type"]
        if post_type != "post":
            # an attachment might have the same "post_name" as an actual post.
            continue
        posts.append({
            "name": name,
            "id": post["wp:post_id"],
            "link": post["link"],
            "title": post["title"],
            "content": post["content:encoded"],
            "date": post["wp:post_date"],
            "timestamp": get_wordpress_timestamp(post["wp:post_date"]),
            "comments": get_comments_from_post(post),
            "metadata": get_metadata_from_post(post),
            "status": post["wp:status"],
        })
    return posts


@transaction.atomic()
def main(input_filepath):
    with open(input_filepath) as f:
        document = json.loads(f.read())

    homepage = HomePage.objects.last()

    posts = wordpress_xml_dict_to_posts(document)
    for post in posts:
        title = post["title"]
        slug = post["name"]
        date = timezone.make_aware(
            dateutil.parser.parse(post["date"])
        )
        is_published = post["status"] == "publish"

        if not slug:
            slug = slugify(title)
        blogpost = BlogPostPage(
            title=title,
            slug=slug,
            body=post["content"],
            first_published_at=date,
            last_published_at=date,
            latest_revision_created_at=date,
            live=is_published,
            _original_wp_post=post,
        )

        # TODO:
        # - [x] store original json temp. into each post so we can iterate
        # - [ ] separate content by parser and migrate into StreamField blocks
        # - [ ] migrate drafts as drafts, not published
        # - [ ] migrate categories / tags
        # - [ ] add simple blog-list and blog-detail templates

        # Ensure things like .depth and .path are set correctly.
        homepage.add_child(instance=blogpost)
        blogpost.save()

        print(blogpost.id)


if __name__ == "__main__":
    input_filepath = sys.argv[1]
    main(input_filepath)
