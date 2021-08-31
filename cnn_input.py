import json
import re
import sqlite3
import requests
from bs4 import BeautifulSoup

from db_control import DbControl

cnn_edition_host = 'https://edition.cnn.com'

# CNN has several layouts that needs different url handling
section_1 = ['business', 'africa', 'australia', 'china', 'europe', 'middle-east', 'asia', 'world', 'health',
             'entertainment', 'travel']
section_2 = ['uk', 'americas', 'india', ]
section_3 = ['style', ]
section_4 = ['sport', ]
section_5 = ['politics', ]

word_set = dict()
db_control = DbControl()

# ------- open and check database -------
if not db_control.open_database('words.db'):
    exit()

word_set = db_control.get_all_words()

def get_links_section_1(section):
    req = requests.get(f'{cnn_edition_host}/{section}')

    soup = BeautifulSoup(req.text, "html.parser")
    # CNN use date as url
    links = soup.findAll('a', href=re.compile(r"^(/\d+/\d+/\d+)"))
    links = [cnn_edition_host + li.attrs['href'] for li in links]
    return links


def get_links_section_2(section):
    # americas section go this way
    detail_links = []
    req = requests.get(f'{cnn_edition_host}/{section}')
    soup = BeautifulSoup(req.text, "html.parser")

    content_manager = soup.findAll('link',
                                   href=re.compile(r"list-(?:hierarchical-)?xs/views/containers/common/container-manager.html"))
    upper_links = [li.attrs['href'] for li in content_manager]
    for upper_link in upper_links:
        req = requests.get(f'{cnn_edition_host}{upper_link}')
        soup = BeautifulSoup(req.text, "html.parser")
        # CNN use date as url
        links = soup.findAll('a', href=re.compile(r"^(/\d+/\d+/\d+)"))
        links = [cnn_edition_host + li.attrs['href'] for li in links]
        detail_links.extend(links)

    return detail_links


def get_links_section_3():
    detail_links = []
    req = requests.get('https://verticals-data.api.cnn.io/most-popular')

    json_result = json.loads(req.text)
    for item in json_result['body']:
        detail_links.append(cnn_edition_host + item['url'])

    return detail_links


def get_links_section_4(section):
    req = requests.get(f'{cnn_edition_host}/{section}')

    soup = BeautifulSoup(req.text, "html.parser")
    # CNN use date as url
    links = soup.findAll('a', href=re.compile(r"https://www.cnn.com/\d+/\d+/\d+"))
    links = [li.attrs['href'] for li in links]
    return links


def get_links_section_5(section):
    req = requests.get(f'{cnn_edition_host}/{section}')

    matched = re.findall(r"(/\d+/\d+/\d+/\w+/[\w\d-]*/index.html)", req.text)
    matched = [cnn_edition_host + item for item in matched]
    return matched


def update_words_with_link(links):
    global word_set, sqlite_con

    for link in links:
        full_url = link

        if db_control.is_url_captured(full_url):
            continue

        req = requests.get(full_url)

        soup = BeautifulSoup(req.text, "html.parser")

        possible_classes = ['SpecialArticle__paragraph', 'zn-body__paragraph', 'Paragraph__component']

        for possible_class in possible_classes:
            paragraphs = soup.findAll(class_=possible_class)
            if len(paragraphs) != 0:
                break

        for paragraph in paragraphs:
            text = paragraph.text.replace('\'s', '').replace('n\'t', '')
            text = re.sub(r'[^\w]', ' ', text)
            text = re.sub(r'[\d]', '', text)

            for word in text.split(' '):
                word = word.lower()
                if word.lower() not in word_set:
                    word_set[word] = 1
                else:
                    word_set[word] += 1

        # ------ Update result to database ------
        for key, value in word_set.items():
            if len(key) > 0:
                db_control.upsert_words(key, value)

        db_control.upsert_url(full_url, 'cnn')
        sqlite_con.commit()


for section in section_2:
    update_words_with_link(get_links_section_2(section))

for section in section_1:
    update_words_with_link(get_links_section_1(section))

for section in section_5:
    update_words_with_link(get_links_section_5(section))

for section in section_4:
    update_words_with_link(get_links_section_4(section))

for section in section_3:
    update_words_with_link(get_links_section_3())

if db_control is not None:
    db_control.close_database()
