import os
import re
import urllib.request

from home.models import BlogPostPage

pattern = re.compile(
    r'\"(?P<img_url>http(?:s)?://.+?\.(?:png|gif|jpg))(?:\\)?'
)
image_urls = []


def get_image_urls_from_text_recursive(source_text, url_container):
    matches = pattern.findall(source_text)
    for match_text in matches:
        if ">" in match_text or "<" in match_text:
            get_image_urls_from_text_recursive(match_text, url_container)
        else:
            url_container.append(match_text)


for post in BlogPostPage.objects.all():
    text = post.body
    get_image_urls_from_text_recursive(text, image_urls)

images_dir = os.path.abspath("media/_downloaded_images")
if not os.path.isdir(images_dir):
    os.makedirs(images_dir)

errors = []
image_urls = sorted(list(set(image_urls)))
num = len(image_urls)
for i, image_url in enumerate(image_urls):
    filename = os.path.basename(image_url)
    print(f"downloading: {i+1}/{num}: {image_url} -> {filename}")
    filepath = os.path.join(images_dir, filename)
    try:
        urllib.request.urlretrieve(
            image_url, filepath
        )
    except Exception as err:
        errors.append((image_url, err))
