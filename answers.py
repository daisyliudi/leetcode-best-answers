# coding: utf-8

import time
import pprint
from collections import defaultdict

import requests
import lxml.html
from lxml import etree

from pymongo import MongoClient

def get_doc_root(url):
    r = requests.get(url)
    html_text = r.text
    my_parser = etree.HTMLParser(encoding='utf-8')
    root = etree.HTML(html_text, parser=my_parser)
    return root

def get_answer(url):
    """ get answer info from the url
    """
    doc_root = get_doc_root(url)
    answer = {}
    content_ele = doc_root.cssselect('div.answer div.content')[0]
    answer['url'] = url
    answer['content'] = etree.tostring(content_ele)
    username_ele = doc_root.cssselect('div.user-info a')[0]
    answer['author_url'] = FORUM_URL + username_ele.attrib['href']
    answer['author'] = username_ele.text
    vote_ele = doc_root.cssselect('div.vote-count')[0]
    answer['vote'] = int(vote_ele.text)
    tags_ele = doc_root.cssselect('div.tags a')
    answer['tags'] = [] if not tags_ele else [tag_ele.text for tag_ele in tags_ele]
    question_url_ele = doc_root.cssselect('a#back_to_leetcode')[0]
    question_url = question_url_ele.attrib['href'] + "/"
    answer_dict[question_url].append(answer)

def get_answers():
    """parse urls.txt and parse html
    """
    answer_dict = defaultdict(list)
    started = False
    starting_question_num = 0

    with open('latest.txt') as f:
        lines = f.readlines()
        for line in lines:
            tried_again = False
            before_colon = line.split(':')[0]
            try:
                number = int(before_colon)
                if number >= starting_question_num:
                    started = True
                    continue
            except:
                if started:
                    url = line.strip()
                    time.sleep(3)
                    # sometimes get_answer fails, if so, we simply try again
                    try:
                        get_answer(url)
                    except:
                        if not tried_again:
                            get_answer(url)
                            tried_again = True

def write_answers():
    """ write answers into a MongoDB collection
    """
    for key in answer_dict:
        print key, len(answer_dict[key])
        collection.update({'url': key}, {'$set': {'answers': answer_dict[key]}})

if __name__ == "__main__":
    client = MongoClient('localhost', 27017)
    db = client.leetcode
    collection = db.answers
    FORUM_URL = "https://discuss.leetcode.com"
    answers = get_answers()
    write_answers(answers)
