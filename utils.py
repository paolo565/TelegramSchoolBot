import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import urllib.parse
import config
import subprocess
import hashlib

database = sqlite3.connect('database.db')

cursor = database.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS classes (name TEXT NOT NULL, url TEXT NOT NULL, PRIMARY KEY (name));')
cursor.execute('CREATE TABLE IF NOT EXISTS teachers (name TEXT NOT NULL, url TEXT NOT NULL, PRIMARY KEY (name));')
cursor.execute('CREATE TABLE IF NOT EXISTS links (name TEXT NOT NULL, url TEXT NOT NULL, PRIMARY KEY (name));')
database.commit()


def refresh_main():
    response = requests.request('GET', config.SCHOOL_WEBSITE)
    if response.status_code != 200:
        print('Failed to request the main page')
        return None

    parsed_html = BeautifulSoup(response.text, 'html.parser')
    left_content = parsed_html.find('div', {'id': 'jsn-pleft'})
    links = left_content.find_all('a')
    for link in links:
        text = link.find('span').text
        if 'Orario' in text and 'lezioni' in text:
            return urllib.parse.urljoin(config.SCHOOL_WEBSITE, link.get('href'))


def refresh_redirect(url):
    response = requests.request('GET', url)
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

            cursor = database.cursor()
            cursor.execute('INSERT OR REPLACE INTO links VALUES(?, ?)', ('redirect_url', redirect_url))
            database.commit()

            return redirect_url


def refresh_calendar(url):
    response = requests.request('GET', url)
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
            ))
        elif href.startswith('Docenti/'):
            teachers.append((
                link.text,
                urllib.parse.urljoin(url, href),
            ))
    print('Classes: ', classes)
    print('Teachers: ', teachers)
    cursor = database.cursor()
    cursor.execute('DELETE FROM classes')
    cursor.execute('DELETE FROM teachers')
    cursor.executemany('INSERT INTO classes VALUES (?, ?)', classes)
    cursor.executemany('INSERT INTO teachers VALUES (?, ?)', teachers)
    database.commit()


def update():
    print('Updating...')

    main_url = refresh_main()
    if main_url is None:
        print('Failed to get the main url')
        return False
    print('Main URL: ', main_url)

    redirect_url = refresh_redirect(main_url)
    if redirect_url is None:
        print('Failed to get the redirect url')
        return False
    print('Redirect URL: ', redirect_url)

    refresh_calendar(redirect_url)


def link_to_image(link, file_name):
    subprocess.call(('./wkhtmltox/bin/wkhtmltoimage', link, file_name))


def get_redirect_url():
    result = database.execute("SELECT url FROM links WHERE name = 'redirect_url'")

    data = result.fetchone()
    if data is None:
        return None

    return data[0]


def get_class_name_and_url(name):
    result = database.execute("SELECT name, url FROM classes WHERE name = ?", (name,))

    data = result.fetchone()
    if data is None:
        return None, None

    return data[0], data[1]


def get_teacher_name_and_url(name):
    result = database.execute("SELECT name, url FROM teachers WHERE name = ?", (name,))

    data = result.fetchone()
    if data is None:
        return None, None

    return data[0], data[1]


def md5(text):
    h = hashlib.md5()
    h.update(text.encode('UTF-8'))
    return h.hexdigest()


def get_short_url(url):
    domain = urlparse(url).netloc
    return domain[4:] if domain.startswith('www.') else domain
