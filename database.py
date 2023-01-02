import os
import re

import pickledb
from bs4 import BeautifulSoup

db = pickledb.load("urls.db", True)


def save_url_content(url, content):
    db.set(url, content)


def exist(url):
    return db.exists(url)


def get_page(url):
    return db.get(url)


def populate():
    regex = re.compile("https://www.linkedin.com/in/.*?/")
    for filename in os.listdir("data/"):
        if filename.endswith(".html"):
            with open("data/" + filename) as f:
                content = f.read()
                soup = BeautifulSoup(content, features="html.parser")
                for link in soup.findAll('a'):
                    match = regex.match(link.get("href"))
                    if match is not None:
                        url = match.group().strip("/")
                        save_url_content(url, content)
                        print(url)
                        break

