"""
Interact with your school website with telegram!

Copyright (c) 2016-2017 Paolo Barbolini <paolo@paolo565.org>
Released under the MIT license
"""

from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
import urllib

import os
import requests
import subprocess


def send_cached_photo(bot, message, file_id, caption):
    args = {
        "chat_id": message.chat.id,
        "reply_to_message_id": message.message_id,
        "photo": file_id,
        "caption": caption,
    }
    bot.api.call("sendPhoto", args)


def prettify_page(page_url, html):
    parsed_html = BeautifulSoup(html, "html.parser")

    # Find all images
    for img in parsed_html.find_all("img"):
        img["src"] = urllib.parse.urljoin(page_url, img["src"])

    # Remove the default styles
    for p in parsed_html.find_all("style"):
        p.decompose()

    # Custom css
    custom_style = parsed_html.new_tag("style")
    custom_style.string = """
        * {
            font-weight: bold;
            text-decoration: none;
            text-transform: uppercase;
            font-family: 'Designosaur';
            font-size: 12pt;
        }

        .nodecBlack {
            color: #000000;
        }

        .nodecWhite {
            color: #FFFFFF;
        }
    """
    parsed_html.html.head.contents.insert(0, custom_style)

    # Remove text outsite the table
    for p in parsed_html.select('center p[class="mathema"]'):
        p.decompose()

    # Remove big empty rows
    for p in parsed_html.select('center p[id="mathema"]'):
        p.decompose()

    return str(parsed_html)


def send_page(db, bot, message, page, caption):
    # Did we check if the page changed in the last hour?
    if page.last_check is not None and \
       (datetime.utcnow() - page.last_check).seconds < 3600:
        send_cached_photo(bot, message, page.last_file_id, caption)
        return

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; TelegramSchoolBot/2.0; "
                      "+https://github.com/paolobarbolini/TelegramSchoolBot)",
    }

    # Add the If-Modified-Since header if we have an already cached image.
    # With this header if the file didn't change since the last check
    # the server will reply with a 304 response code
    if page.last_file_id is not None:
        nowstr = page.last_check.strftime("%a, %d %b %Y %H:%M:%S GMT")
        headers["If-Modified-Since"] = nowstr

    response = requests.get(page.url, headers=headers)
    print(response.status_code)
    if response.status_code != 200 and response.status_code != 304:
        raise ValueError("Got %i from %s" % (response.status_code, page.url))

    session = db.Session()
    session = session.object_session(page)
    session.add(page)

    if response.status_code == 304:
        # The page didn't change, send a cached photo and update the last_check
        send_cached_photo(bot, message, page.last_file_id, caption)

        page.last_check = datetime.utcnow()
        session.commit()
        return

    # The page did change, prepare the html file for wkhtmltoimage
    html_path = "/tmp/tsb-body-%i.html" % page.id
    prettified_body = prettify_page(page.url, response.text)
    with open(html_path, "w") as f:
        f.write(prettified_body)

    # Render the html file into a jpeg image
    # (png is a waste because telegram compresses the image)
    image_path = "/tmp/tsb-image-%i.jpeg" % page.id
    subprocess.call(("xvfb-run", "wkhtmltoimage",
                     "--format", "jpeg", "--quality", "100",
                     html_path, image_path))

    message = message.reply_with_photo(image_path, caption=caption)

    # Update the database with the new telegram file id and the last time
    # we checked for changes
    page.last_file_id = message.photo.file_id
    page.last_check = datetime.utcnow()
    session.commit()

    # Remove the temporary files
    os.remove(html_path)
    os.remove(image_path)


def shorten_url(url):
    domain = urlparse(url).netloc

    if domain.startswith("www."):
        domain = domain[4:]

    return domain
