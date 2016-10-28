import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import urllib.parse
import config
import subprocess
import hashlib
import os
import time
import botogram
import html


class Utils:
    def __init__(self, bot):
        self._bot = bot

        self._database = sqlite3.connect('database.db')

        self._database.execute('CREATE TABLE IF NOT EXISTS classes (name TEXT NOT NULL, url TEXT NOT NULL,'
                               ' file_id TEXT DEFAULT NULL, old TINYINT(1), PRIMARY KEY (name));')
        self._database.execute('CREATE TABLE IF NOT EXISTS teachers (name TEXT NOT NULL, url TEXT NOT NULL, '
                               'file_id TEXT DEFAULT NULL, old TINYINT(1), PRIMARY KEY (name));')
        self._database.execute('CREATE TABLE IF NOT EXISTS teachers2 (name TEXT NOT NULL, url TEXT NOT NULL, '
                               'file_id TEXT DEFAULT NULL, old TINYINT(1), PRIMARY KEY (name));')
        self._database.execute('CREATE TABLE IF NOT EXISTS classrooms (name TEXT NOT NULL, url TEXT NOT NULL, '
                               'file_id TEXT DEFAULT NULL, old TINYINT(1), PRIMARY KEY (name));')

        self._database.execute('CREATE TABLE IF NOT EXISTS links (name TEXT NOT NULL, url TEXT NOT NULL, '
                               'PRIMARY KEY (name));')
        self._database.execute('CREATE TABLE IF NOT EXISTS blogs (link TEXT NOT NULL, PRIMARY KEY (link));')
        self._database.execute(
            'CREATE TABLE IF NOT EXISTS blog_subscribers (telegram_uid INT NOT NULL, PRIMARY KEY (telegram_uid));')

        self._database.commit()

        if not os.path.isdir('./images/classes/'):
            os.makedirs('./images/classes/')

        if not os.path.isdir('./images/teachers/'):
            os.makedirs('./images/teachers/')

        if not os.path.isdir('./images/teachers2/'):
            os.makedirs('./images/teachers2/')

        if not os.path.isdir('./images/classrooms/'):
            os.makedirs('./images/classrooms/')

    @staticmethod
    def refresh_main():
        response = requests.get(config.SCHOOL_WEBSITE)
        if response.status_code != 200:
            print('Failed to request the main page')
            return None

        redirect_url = None
        parsed_html = BeautifulSoup(response.text, 'html.parser')

        left_content = parsed_html.find('div', {'id': 'jsn-pleft'})
        links = left_content.find_all('a')
        for link in links:
            text = link.find('span').text
            if 'Orario' in text and 'lezioni' in text:
                redirect_url = urllib.parse.urljoin(config.SCHOOL_WEBSITE, link.get('href'))
                break

        blogs_list = []
        blogs_titles = parsed_html.find_all('h2', {'class': 'contentheading'})
        blogs = parsed_html.find_all('p', {'class': 'readmore'})
        for i in range(0, len(blogs)):
            title = blogs_titles[i].text.lstrip().rstrip()
            link = urllib.parse.urljoin(config.SCHOOL_WEBSITE, blogs[i].find('a').get('href'))
            blogs_list.append((title, link))

        return redirect_url, blogs_list

    def refresh_redirect(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            print('Failed to request the redirect url')
            return None

        calendar1 = None
        calendar2 = None

        parsed_html = BeautifulSoup(response.text, 'html.parser')
        post_content = parsed_html.find('div', {'id': 'jsn-mainbody'})
        links = post_content.find_all('a')
        for link in links:
            href = link.get('href')
            if href.startswith('/web_orario') or href.startswith('/weborario'):
                redirect_url = urllib.parse.urljoin(url, href)

                if calendar1 is None:
                    calendar1 = redirect_url
                    key = 'calendar1'
                else:
                    calendar2 = redirect_url
                    key = 'calendar2'

                self._database.execute('INSERT OR REPLACE INTO links VALUES(?, ?)', (key, redirect_url))
                self._database.commit()

                if calendar2 is not None:
                    break

        return calendar1, calendar2

    def refresh_calendar(self, url, first_calendar):
        response = requests.get(url)
        if response.status_code != 200:
            print('Failed to request the classes url')
            return None

        classes = []
        teachers = []
        classrooms = []

        parsed_html = BeautifulSoup(response.text, 'html.parser')
        links = parsed_html.find_all('a')
        for link in links:
            href = link.get('href')
            if first_calendar and href.startswith('Classi/'):
                classes.append((
                    link.text,
                    urllib.parse.urljoin(url, href),
                    link.text,
                    0,
                ))
            elif href.startswith('Docenti/'):
                teachers.append((
                    link.text,
                    urllib.parse.urljoin(url, href),
                    link.text,
                    0,
                ))
            elif first_calendar and href.startswith('Aule/'):
                classrooms.append((
                    link.text,
                    urllib.parse.urljoin(url, href),
                    link.text,
                    0,
                ))

        print('Classes:', len(classes))
        print('Teachers:', len(teachers))
        print('Classrooms:', len(classrooms))

        if first_calendar:
            self._database.execute('UPDATE classes SET old = 1')
            self._database.executemany('INSERT OR REPLACE INTO classes (name, url, file_id, old) VALUES '
                                       '(?, ?, (SELECT file_id FROM classes WHERE name = ?), ?)', classes)
            self._database.execute('DELETE FROM classes WHERE old = 1')

            self._database.execute('UPDATE classrooms SET old = 1')
            self._database.executemany('INSERT OR REPLACE INTO classrooms (name, url, file_id, old) VALUES '
                                       '(?, ?, (SELECT file_id FROM classes WHERE name = ?), ?)', classrooms)
            self._database.execute('DELETE FROM classrooms WHERE old = 1')

        table_name = 'teachers' if first_calendar else 'teachers2'
        self._database.execute('UPDATE %s SET old = 1' % (table_name,))
        self._database.executemany('INSERT OR REPLACE INTO %s (name, url, file_id, old) VALUES '
                                   '(?, ?, (SELECT file_id FROM teachers WHERE name = ?), ?)' % (table_name,), teachers)
        self._database.execute('DELETE FROM %s WHERE old = 1' % (table_name,))

        self._database.commit()

    def process_blogs(self, blogs):
        messages = []

        for blog in blogs:
            try:
                self._database.execute('INSERT INTO blogs VALUES (?)', (blog[1],))
                self._database.commit()

                messages.append('- <a href="%s">%s</a>' % (html.escape(blog[1]), html.escape(blog[0])))

                print('There\'s a new article, title:', blog[0])
            except sqlite3.DatabaseError:
                pass

        if len(messages) > 0:
            if len(messages) == 1:
                text = "<b>È uscito il seguente articolo:</b>"
            else:
                text = "<b>Sono usciti i seguenti articoli:</b>"

            text += "\n" + "\n".join(messages)

            for user in self._database.execute('SELECT telegram_uid FROM blog_subscribers'):
                try:
                    self._bot.chat(user[0]).send(text, syntax='HTML')
                except botogram.api.ChatUnavailableError:
                    self.remove_blog_subscriber(user[0])

                time.sleep(2)

    def update(self):
        print('Updating...')

        main_url, blogs = self.refresh_main()
        self.process_blogs(blogs)
        if main_url is None:
            print('Failed to get the main url')
            return False
        print('Main URL:', main_url)

        calendar1, calendar2 = self.refresh_redirect(main_url)
        if calendar1 is None:
            print('Failed to get the calendars')
            return False
        print('Calendar1:', calendar1)

        self.refresh_calendar(calendar1, True)

        if calendar2 is None:
            print('Failed to get the second calendar')
            return False
        print('Calendar2:', calendar2)
        self.refresh_calendar(calendar2, False)

    def get_image_file(self, file_id, url, name, folder):
        prefix = './images/' + folder + '/' + self.md5(name)
        html_file = prefix + '.html'
        image_file = prefix + '.jpg'

        response_type = 'file' if file_id is None else 'id'
        response_file = image_file if file_id is None else file_id

        if os.path.isfile(html_file) and os.path.isfile(image_file):
            last_edit = os.path.getmtime(html_file)
            current_time = time.time()

            if (current_time - 300) < last_edit:
                return response_type, response_file

        response = requests.get(url)
        if response.status_code != 200:
            return None, None

        if os.path.isfile(html_file):
            with open(html_file, 'r') as f:
                content = f.read()

        with open(html_file, 'w+') as f:
            f.write(response.text)

        if os.path.isfile(image_file):
            if content == response.text:
                return response_type, response_file

            os.remove(image_file)

        subprocess.call(('./wkhtmltox/bin/wkhtmltoimage', '--format', 'jpeg', '--quality', '100', html_file, image_file))
        success = os.path.isfile(image_file)
        return 'file' if success else None, image_file if success else None

    def get_calendar(self, calendar_number):
        result = self._database.execute("SELECT url FROM links WHERE name = 'calendar%i'" % (calendar_number,))

        data = result.fetchone()
        return None if data is None else data[0]

    def get_name_url_and_file_id(self, table_name, name):
        result = self._database.execute("SELECT name, url, file_id FROM %s WHERE name LIKE ? COLLATE NOCASE "
                                        "ORDER BY abs(length(?) - length(name)), name;" %
                                        (table_name,), ('%' + name.replace('%', '\\%') + '%', name,))

        data = result.fetchall()
        if data is None or len(data) == 0:
            return None, None, None

        return data[0][0], data[0][1], data[0][2]

    def update_file_id(self, table_name, name, file_id):
        self._database.execute('UPDATE %s SET file_id = ? WHERE name = ?' % (table_name,), (file_id, name,))
        self._database.commit()

    def add_blog_subscriber(self, telegram_uid):
        self._database.execute('INSERT OR IGNORE INTO blog_subscribers VALUES (?)', (telegram_uid,))
        self._database.commit()

    def remove_blog_subscriber(self, telegram_uid):
        self._database.execute('DELETE FROM blog_subscribers WHERE telegram_uid = ?', (telegram_uid,))
        self._database.commit()

    @staticmethod
    def md5(text):
        h = hashlib.md5()
        h.update(text.encode('UTF-8'))
        return h.hexdigest()

    @staticmethod
    def get_short_domain(url):
        domain = urlparse(url).netloc
        return domain[4:] if domain.startswith('www.') else domain
