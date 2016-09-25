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


class Utils:
    def __init__(self, bot):
        self._bot = bot

        self._database = sqlite3.connect('database.db')

        self._database.execute('CREATE TABLE IF NOT EXISTS classes (name TEXT NOT NULL, url TEXT NOT NULL,'
                               ' file_id TEXT DEFAULT NULL, old TINYINT(1), PRIMARY KEY (name));')
        self._database.execute('CREATE TABLE IF NOT EXISTS teachers (name TEXT NOT NULL, url TEXT NOT NULL, '
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
        blogs = parsed_html.find_all('p', {'class': 'readmore'})
        for blog in blogs:
            link = blog.find('a')
            blogs_list.append((urllib.parse.urljoin(config.SCHOOL_WEBSITE, link.get('href')),))

        return redirect_url, blogs_list

    def refresh_redirect(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            print('Failed to request the redirect url')
            return None

        parsed_html = BeautifulSoup(response.text, 'html.parser')
        post_content = parsed_html.find('div', {'id': 'jsn-mainbody'})
        links = post_content.find_all('a')
        for link in links:
            href = link.get('href')
            if href.startswith('/web_orario_'):
                redirect_url = urllib.parse.urljoin(url, href)

                self._database.execute('INSERT OR REPLACE INTO links VALUES(?, ?)', ('redirect_url', redirect_url))
                self._database.commit()

                return redirect_url

    def refresh_calendar(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            print('Failed to request the classes url')
            return None

        classes = []
        teachers = []
        parsed_html = BeautifulSoup(response.text, 'html.parser')
        links = parsed_html.find_all('a')
        for link in links:
            href = link.get('href')
            if href.startswith('Classi/'):
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

        print('Classes:', len(classes))
        print('Teachers:', len(teachers))

        self._database.execute('UPDATE classes SET old = 1')
        self._database.execute('UPDATE teachers SET old = 1')
        self._database.executemany('INSERT OR REPLACE INTO classes (name, url, file_id, old) VALUES '
                                   '(?, ?, (SELECT file_id FROM classes WHERE name = ?), ?)', classes)
        self._database.executemany('INSERT OR REPLACE INTO teachers (name, url, file_id, old) VALUES '
                                   '(?, ?, (SELECT file_id FROM teachers WHERE name = ?), ?)', teachers)
        self._database.execute('DELETE FROM classes WHERE old = 1')
        self._database.execute('DELETE FROM teachers WHERE old = 1')

        self._database.commit()

    def process_blogs(self, blogs):
        for blog in blogs:
            try:
                self._database.execute('INSERT INTO blogs VALUES (?)', (blog[0],))
                self._database.commit()

                print('There\'s a new article:', blog[0])

                for user in self._database.execute('SELECT telegram_uid FROM blog_subscribers'):
                    self._bot.chat(user[0]).send('È uscito un nuovo articolo:\n%s' % (blog[0],))
                    time.sleep(1)
            except sqlite3.DatabaseError:
                pass

    def update(self):
        print('Updating...')

        main_url, blogs = self.refresh_main()
        self.process_blogs(blogs)
        if main_url is None:
            print('Failed to get the main url')
            return False
        print('Main URL:', main_url)

        redirect_url = self.refresh_redirect(main_url)
        if redirect_url is None:
            print('Failed to get the redirect url')
            return False
        print('Redirect URL:', redirect_url)

        self.refresh_calendar(redirect_url)

    def get_image_file(self, file_id, url, name, folder):
        prefix = './images/' + folder + '/' + self.md5(name)
        html_file = prefix + '.html'
        image_file = prefix + '.png'

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

            if content == response.text:
                return response_type, response_file
        else:
            with open(html_file, 'w+') as f:
                f.write(response.text)

        if os.path.isfile(image_file):
            os.remove(image_file)

        subprocess.call(('./wkhtmltox/bin/wkhtmltoimage', html_file, image_file))
        success = os.path.isfile(image_file)
        return 'file' if success else None, image_file if success else None

    def get_redirect_url(self):
        result = self._database.execute("SELECT url FROM links WHERE name = 'redirect_url'")

        data = result.fetchone()
        return None if data is None else data[0]

    def get_name_url_and_file_id(self, table_name, name):
        result = self._database.execute("SELECT name, url, file_id FROM %s WHERE name = ?" % (table_name,), (name,))

        data = result.fetchone()
        return None if data is None else data[0], data[1], data[2]

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
