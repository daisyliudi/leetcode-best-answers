"""
Author: Jing Zhou
Version: 0.2

Update questions and answers
"""

import re
import codecs
import datetime
from tqdm import tqdm

import requests
import lxml.html
from lxml import etree
from pymongo import MongoClient
import pymongo

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display

from settings import user_info

client = MongoClient('localhost', 27017)
leet_answers = client.geekreader
answers_collection = leet_answers.leets

LEETCODE_SITE = "https://leetcode.com"
LEETCODE_DISCUSS = "https://leetcode.com/discuss"

class Problem:
    def __init__(self, number, title, url, level, accepted_rate, is_locked):
        self.number = int(number)
        self.title = title
        self.url = url
        self.level = level
        self.accepted_rate = accepted_rate
        self.is_locked = is_locked
        self.submission_url = self.url + "submissions/"
        self.discussion_url = "https://leetcode.com/discuss/questions/oj/" + self.url.split('/')[-2] + "?sort=votes"
        self.ancher = "#" + self.url.split('/')[-2]


def login(driver, username, password):
    username_ele = driver.find_element_by_id("id_login")
    password_ele = driver.find_element_by_id("id_password")
    username_ele.send_keys(username)
    password_ele.send_keys(password)
    driver.find_element_by_css_selector('button.btn-primary').click()

def setup_driver():
    os.environ["webdriver.chrome.driver"] = chrome_driver_location
    # display = Display(visible=0, size=(1800, 900))
    # display.start()
    driver = webdriver.Chrome(chrome_driver_location)
    driver.set_window_size(1280, 800)
    return driver

def replace_utf8_symbols(s):
    s = s.replace('\\u002D', '-').replace('\\u000D\\u000A', '\n')
    s = s.replace('\\u003D', '=').replace('\\u003C', '<').replace('\\u003E', '>').replace('\\u003B', ';')
    s = s.replace('\\u0027', "'").replace('\\u0022', '"')
    return s

def get_doc_root(url):
    r = requests.get(url, cookies=cookies)
    htmltext = r.text
    myparser = etree.HTMLParser(encoding="utf-8")
    root = etree.HTML(htmltext, parser=myparser)
    return root

def get_question_des(url):
    result = {}
    question_tags = []
    similars = []
    companies = []
    question_root = get_doc_root(url)
    question_content = question_root.xpath("//div[@class='question-content']")
    for image in question_content[0].xpath("//img"):
        image_url = image.get('src')
        if not image_url.startswith('http'):
            image.attrib['src'] = LEETCODE_SITE + image_url
    company = question_content[0].xpath('//div[@id="company_tags"]')
    if company:
        for a in company[0].getnext().xpath('a'):
            companies.append(a.xpath('.//text()')[0])
            a.attrib['href'] = LEETCODE_SITE + a.attrib['href']
    tags = question_content[0].xpath('//div[@id="tags"]')
    if tags:
        for a in tags[0].getnext().xpath('a'):
            question_tags.append(a.xpath('.//text()')[0])
            a.attrib['href'] = LEETCODE_SITE + a.attrib['href']
    similar = question_content[0].xpath('//div[@id="similar"]')
    if similar:
        for a in similar[0].getnext().xpath('a'):
            similars.append(a.attrib['href'].split('/')[-2])
            a.attrib['href'] = "#" + a.attrib['href'].split('/')[-2]
    content = lxml.html.tostring(question_content[0])
    result["tags"] = question_tags
    result["content"] = content
    result["text"] = "".join([x for x in question_content[0].itertext()]).strip()
    result["companies"] = companies
    return result

def get_answer(url):
    answer = {}
    answer["url"] = url
    answer_root = get_doc_root(url)
    post_content = answer_root.xpath("//div[@class='entry-content']")
    content = lxml.html.tostring(post_content[0])
    author = answer_root.xpath("//span[@class='vcard author']/a/@href")
    answer["author"] = author[0].split('/')[-1]
    answer["author_url"] = LEETCODE_DISCUSS+author[0][2:]
    answer["content"] = content
    return answer

def get_solution(discussion_url, n_posts=3):
    answers = []
    post_urls = []
    discussion_doc_root = get_doc_root(discussion_url)
    items = discussion_doc_root.xpath('//div[contains(@class, "qa-q-list-item")]')
    for item in items:
        votes = item.xpath(".//div[@class='qa-q-item-stats']/div[@class='qa-voting qa-voting-net']")[0]
        votes = [x for x in votes.itertext() if x.strip()]
        tags = []
        tags_ele = item.xpath(".//div[@class='qa-q-item-main']/div[@class='qa-q-item-tags']")
        if tags_ele:
            tags = [x for x in tags_ele[0].itertext() if x.strip()]
        votes = int(votes[0])
        if votes == 0:
            break
        post_url = item.xpath(".//div[@class='qa-q-item-main']/div[@class='qa-q-item-title']/a/@href")
        post_url = "https://leetcode.com/discuss/" + post_url[0][6:]
        post_urls.append((votes, post_url, tags))

    for vote, url, tags in post_urls:
        answer = get_answer(url)
        answer["vote"] = vote
        answer["tags"] = tags
        answers.append(answer)
    return answers

def write_to_solution_file(problem):
    # get solution
    doc = {}
    result = get_question_des(problem.url)
    q_des, text_desc, tags, companies = result["content"], result["text"], result["tags"], result["companies"]
    ancher = problem.url.split('/')[-2]
    answers = get_solution(problem.discussion_url, n_posts=10)
    first_period_pos = text_desc.find('.')
    if first_period_pos < 150:
        short_desc = text_desc[:first_period_pos]
    else:
        short_desc = " ".join(text_desc.split()[:32])
    doc["number"] = problem.number
    doc["title"] = problem.title
    doc["url"] = problem.url
    doc["locked"] = problem.is_locked
    doc["accepted_rate"] = problem.accepted_rate
    doc["tags"] = tags
    doc["companies"] = companies
    doc["answers"] = answers
    doc["short_desc"] = short_desc
    doc["ancher"] = ancher
    doc["desc"] = q_des
    doc["short_desc"] = short_desc
    doc["discussion_url"] = problem.discussion_url
    doc["level"] = problem.level
    answers_collection.insert(doc)

def get_last_question_num():
    number = answers_collection.find_one(sort=[('number', pymongo.DESCENDING)])
    return number.get("number", 0)


def getAllproblems(url):
    driver = setup_driver()
    problem_list_id = "problemList"
    ps = driver.find_elements_by_xpath('//table[@id="' + problem_list_id + '"]')
    last_question_number = get_last_question_num()
    updated = False
    for tbl in tqdm(ps):
        for tr in tbl.find_elements_by_xpath('.//tr'):
            problems_nodes = tr.find_elements_by_xpath('.//td')
            problems = tr.find_elements_by_xpath('.//td//text()')
            problems = [item for item in problems if item.strip()]
            print(problems)
            if not problems:
                continue
            problem_num, problem_title, accepted_rate, level = problems
            if int(problem_num) <= last_question_number:
                updated = True
                break
            # print lxml.html.tostring(problems_nodes[2])
            is_locked = True if problems_nodes[2].find_elements_by_xpath('.//i[@class="fa fa-unlock"]') else False
            problem_url = LEETCODE_SITE + problems_nodes[2].find_elements_by_xpath('.//a/@href')[0]
            problem = Problem(problem_num, problem_title, problem_url, level, accepted_rate, is_locked)

            write_to_solution_file(problem)
        if updated:
            break

if __name__ == "__main__":
    login()
    leetcode_problem_url = "https://leetcode.com/problemset/algorithms/"
    getAllproblems(leetcode_problem_url)
