
# coding: utf-8

# In[2]:

import requests
import lxml.html
from lxml import etree


# In[40]:

import time
import pprint
from collections import defaultdict


# In[45]:

from pymongo import MongoClient


# In[46]:

client = MongoClient('localhost', 27017)
db = client.geekreader
collection = db.leets


# In[20]:

FORUM_URL = "https://discuss.leetcode.com"


# In[35]:

answer_dict = defaultdict(list)


# In[3]:

def get_doc_root(url):
    r = requests.get(url)
    html_text = r.text
    my_parser = etree.HTMLParser(encoding='utf-8')
    root = etree.HTML(html_text, parser=my_parser)
    return root


# In[39]:

def get_answer(url):
    doc_root = get_doc_root(url)
    answer = {}
    content_ele = root.cssselect('div.answer div.content')[0]
    answer['url'] = url
    answer['content'] = etree.tostring(content_ele)
    username_ele = root.cssselect('div.user-info a')[0]
    answer['author_url'] = FORUM_URL + username_ele.attrib['href']
    answer['author'] = username_ele.text
    vote_ele = root.cssselect('div.vote-count')[0]
    answer['vote'] = int(vote_ele.text)
    tags_ele = root.cssselect('div.tags a')
    if not tags_ele:
        tags = []
    else:
        tags = [tag_ele.text for tag_ele in tags_ele]
    answer['tags'] = tags
    question_url_ele = root.cssselect('a#back_to_leetcode')[0]
    question_url = question_url_ele.attrib['href'] + "/"
    answer_dict[question_url].append(answer)


# In[42]:

for line in open('urls.txt').readlines()[:20]:
    url = line.strip()
    time.sleep(3)
    get_answer(url)


# In[44]:

for key in answer_dict:
    collection.update({url: key}, {'$set': {'answers': answer_dict[key]}})

