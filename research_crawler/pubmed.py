# AUTOGENERATED! DO NOT EDIT! File to edit: 00_pubmed.ipynb (unless otherwise specified).

__all__ = ['get_max_pages', 'request_headers', 'write_db', 'extract_page', 'extract_and_write', 'process_many',
           'crawl_list', 'crawl_pubmed']

# Cell
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import re
import random
from pymongo import MongoClient
import pandas as pd
import multiprocessing as mp
from tqdm.notebook import tqdm

# Cell
def get_max_pages(keywords):
    # build search link
    url = f'{URL}/pubmed/?term={keywords}'
    browser.get(url)
    browser.implicitly_wait(1) # wait to avoid traffic

    s = BeautifulSoup(browser.page_source, 'html.parser')
    max_pages = int(s.find('input', {'id': 'pageno2'}).get('last'))
    return max_pages

# Cell
def request_headers(url):
    return {
            'User-Agent':random.choice(user_agent),
            'Referer': url,
            'Connection':'keep-alive',
            'Host':'www.ncbi.nlm.nih.gov'}

# Cell
def write_db(data):
    # check if already exists
#     if db.pubmed_meta.find({'url': data['url']}).limit(1):
#         print(data['url'], 'already exists')
#     else:
    db.pubmed_meta.insert_one(data)

# Cell
def extract_page(url):
    browser.implicitly_wait(random.randint(2,3))
    html = requests.get(url, headers=request_headers(url))
    bs = BeautifulSoup(html.text, 'html.parser')

    title = bs.find('title').get_text()
    authors = bs.find('div', {'class': 'auths'}).get_text()
    orgs = get_orgs(bs)
    kwords = get_kwords(bs)
    cit = bs.find('div', {'class': 'cit'}).get_text()
#     date = re.findall(r'\d{4}\s\w{3}\s\d{2}', citation)[0]
    return dict(title=title, authors=authors, organizations=orgs,
                keywords=kwords, citation=cit, url=url)

# Cell
def extract_and_write(url):
    data = extract_page(url)
    return write_db(data)

# Cell
def process_many(urls):
    p = mp.Pool()
    for u in urls:
        p.apply_async(extract, args=(u,))

    p.close()
    p.join()

# Cell
def crawl_list(page):
    bs = BeautifulSoup(page, 'html.parser')
    divs = bs.find_all('div', {'class': 'rslt'})
    for d in tqdm(divs):
        # get paper's link
        u = URL + d.find('a').get('href')
        extract_and_write(u)

# Cell
def crawl_pubmed(keywords):
    url = f'{URL}/pubmed/?term={search_keywords}'
    browser.get(url)
    max_pages = get_max_pages(keywords)
    for _ in tqdm(range(max_pages)):
        crawl_list(browser.page_source)
        browser.implicitly_wait(1)
        # Click next buttion to navigate to the next page
        browser.find_element_by_xpath('//*[@title="Next page of results"]').click()