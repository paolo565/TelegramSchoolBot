"""
Interact with your school website with telegram!

Copyright (c) 2016-2017 Paolo Barbolini <paolo@paolo565.org>
Released under the MIT license
"""

from bs4 import BeautifulSoup
import botogram
import requests
import urllib

from . import models
from . import utils


class Tasks(botogram.components.Component):
    """All of the TelegramSchoolBot tasks"""

    component_name = "tsb-tasks"

    def __init__(self, config, db):
        self.config = config
        self.db = db

        self.add_timer(3600, self.run)


    def query_main_page(self):
        response = requests.get(self.config["school_website"], headers=utils.REQUESTS_HEADERS)
        if response.status_code != 200:
            raise ValueError("Failed to query the main page, website responded with response code: %i" % (response.status_code,))

        parsed_html = BeautifulSoup(response.text, "html.parser")

        # Find the url of the calendar article
        calendar_article_url = None
        left_content = parsed_html.find("div", {"id": "jsn-pleft"})
        left_links = left_content.find_all("a")
        for link in left_links:
            tag = link.find("span")
            if tag is None:
                continue

            text = tag.text
            if not ("Orario" in text and "lezioni" in text):
                continue

            calendar_article_url = urllib.parse.urljoin(self.config["school_website"], link.get("href"))
            break

        # Generate the list of posts
        posts = []
        post_titles = parsed_html.find_all("h2", {"class": "contentheading"})
        post_urls = parsed_html.find_all("p", {"class": "readmore"})
        for i in range(0, len(post_urls)):
            title = post_titles[i].text.strip()
            url = urllib.parse.urljoin(self.config["school_website"], post_urls[i].find("a").get("href"))
            posts.append(models.Post(url=url, title=title))

        return calendar_article_url, posts


    def query_calendar_article(self, url):
        response = requests.get(url, headers=utils.REQUESTS_HEADERS)
        if response.status_code != 200:
            raise ValueError("Failed to query the calendar article page, website responded with response code: %i" % (response.status_code,))

        # Find the url of the orario facile page
        parsed_html = BeautifulSoup(response.text, "html.parser")
        post_content = parsed_html.find("div", {"id": "jsn-mainbody"})
        post_urls = post_content.find_all("a")
        for link in post_urls:
            href = link.get("href")
            lower_href = href.lower()
            if not lower_href.startswith("/web_orario") and not lower_href.startswith("/weborario"):
                continue

            calendar_url = urllib.parse.urljoin(url, href)
            return calendar_url


    def query_calendar(self, url):
        response = requests.get(url, headers=utils.REQUESTS_HEADERS)
        if response.status_code != 200:
            raise ValueError("Failed to query the calendar page, website responded with response code: %i" % (response.status_code,))

        pages = []
        # Generate the list of pages about classes, teachers and classrooms
        parsed_html = BeautifulSoup(response.text, "html.parser")
        links = parsed_html.find_all("a")
        for link in links:
            href = link.get("href")

            if href.startswith("Classi/"):
                type = "class"
            elif href.startswith("Docenti/"):
                type = "teacher"
            elif href.startswith("Aule/"):
                type = "classroom"
            else:
                continue

            pages.append(models.Page(type=type, name=link.text, url=urllib.parse.urljoin(url, href)))

        return pages


    def update_pages_table(self, pages):
        session = self.db.Session()

        database_pages = session.query(models.Page).all()
        database_pages = list(database_pages)

        # Add missing pages
        for page in pages:
            exists = any(page.type == database_page.type and page.name == database_page.name and page.url == database_page.url for database_page in database_pages)
            if not exists:
                session.add(page)

        # Remove removed pages
        for database_page in database_pages:
            exists = any(page.type == database_page.type and page.name == database_page.name and page.url == database_page.url for page in pages)
            if not exists:
                session.delete(database_page)

        session.commit()


    def update_posts_table_and_notify(self, bot, posts):
        writes = []

        session = self.db.Session()
        post_urls = [post.url for post in posts]
        database_posts = session.query(models.Post).filter(models.Post.url.in_(post_urls))
        database_posts = list(database_posts)

        for local_post in posts:
            if not any(local_post.url == database_post.url for database_post in database_posts):
                writes.append(local_post)

        if len(writes) == 0:
            return

        # Generate the text of the message
        messages = []
        if len(writes) == 1:
            messages.append("<b>È uscito il seguente articolo:</b>")
        else:
            messages.append("<b>Sono usciti i seguenti articoli:</b>")

        for write in writes:
            messages.append("▪️ <a href=\"%s\">%s</a>" % (write.url, write.title))

        message = "\n".join(messages)

        # Send the message to the subscribers
        for subscriber in session.query(models.Subscriber).all():
            try:
                bot.chat(subscriber.chat_id).send(message)
            except botogram.api.ChatUnavailableError:
                session.delete(subscriber)

        for write in writes:
            session.add(write)

        # Commit new pages only at this point because it's better sending
        # a notification more than one time rather than skipping some
        # users because of an unexpected error
        session.commit()


    def run(self, bot):
        calendar_article_url, posts = self.query_main_page()

        # This default makes all of the classes, teachers and classrooms
        # go away if we can't find the page listing them
        calendar_pages = []
        if calendar_article_url is not None:
            calendar_url = self.query_calendar_article(calendar_article_url)

            if calendar_url is not None:
                calendar_pages = self.query_calendar(calendar_url)

        self.update_pages_table(calendar_pages)
        self.update_posts_table_and_notify(bot, posts)
