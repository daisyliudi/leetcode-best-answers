
# coding: utf-8

# To sort the answers in the discussion forum by votes, it appears we have to log in first...
# So we use selenium to log in to the site and click on sort by most votes.
#
# Therefore to use this script you need to use your username and password to login.

# In[32]:

import os
import time


# In[33]:

import requests


# In[34]:

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display


from config import username, password, chrome_driver_location

DISCUSSION_FORUM_INDEX = "https://discuss.leetcode.com/category/8/oj"


first_select = True


def get_answer_urls(driver, url):
    """ return at most 10 top voted answers
    """
    global first_select
    driver.get(url)
    time.sleep(2)
    dropdown_buttons = driver.find_elements_by_css_selector('button.dropdown-toggle')
    assert len(dropdown_buttons) == 2
    dropdown_buttons[1].click()
    time.sleep(2)
    if first_select:
        driver.find_element_by_css_selector('a.most_votes').click()
        time.sleep(5)
        first_select = False
    elements = driver.find_elements_by_css_selector('ul.topic-list h2.title > a')[:10]
    return [ele.get_attribute("href") for ele in elements]


# In[40]:

def get_answer(driver, url):
    """ element.get_attribute('innerHTML')
    elem.get_attribute("outerHTML")
    """
    answer = {}
    driver.get(url)
    time.sleep(2)
    up_button = driver.find_element_by_css_selector('li i.fa-angle-double-up')
    up_button.click()
    driver.implicitly_wait(3)
    answer["url"] = url
    author_element = driver.find_element_by_css_selector("span.username a")
    answer["author"] = author_element.text
    answer["author_url"] = author_element.get_attribute('href')
    vote_element = driver.find_element_by_css_selector("div.vote-count")
    answer["vote"] = int(vote_element.text)
    content_element = driver.find_element_by_css_selector("div.answer .content")
    answer["content"] = content_element.get_attribute('outerHTML')
    return answer


# In[41]:

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

def start_driver():
    driver = setup_driver()

    driver.get(DISCUSSION_FORUM_INDEX)

    time.sleep(2)

    driver.find_element_by_link_text("Login").click()
    time.sleep(2)

    login(driver, username, password)

    time.sleep(2)

    driver.get(DISCUSSION_FORUM_INDEX)

    time.sleep(2)

    links = [link.get_attribute("href") for link in driver.find_elements_by_css_selector('ul.categories h2 a')]

    with open('latest.txt', 'w') as urls_file:
        for index, link in enumerate(links):
            if index < 375:
                continue
            answer_urls = get_answer_urls(driver, link)
            answer_count = len(answer_urls)
            urls_file.write("{}:{}\n".format(str(index), str(answer_count)))
            for answer_url in answer_urls:
                urls_file.write(answer_url + '\n')
            time.sleep(2)

    driver.quit()
    # display.stop()

if __name__ == "__main__":
    start_driver()


# In[ ]:

"""
# could be useful in the future
cookies = driver.get_cookies()
headers = {
"User-Agent":
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
}
s = requests.session()
s.headers.update(headers)

for cookie in driver.get_cookies():
    c = {cookie['name']: cookie['value']}
    s.cookies.update(c)
"""
