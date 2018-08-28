import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from selenium import webdriver
import re
import time
from pymongo import MongoClient
class naverCrawler:
    def __init__(self,query,chromePath, town = ['서울특별시']):
        self.driver = webdriver.Chrome(chromePath)
        self.urls = []
        self.town = town
        self.query = query
        self.driver.get('https://store.naver.com/attractions/list?page='+'1'+'&query='+query+'&region='+town[0]+'&sortingOrder=precision')
        html = self.driver.page_source
        dom = BeautifulSoup(html.encode('utf-8'), 'html.parser')
        for i in range(1, int(dom.select('a.num')[-1].text)+1):
            for j in self.town:
                self.driver.get('https://store.naver.com/attractions/list?page='+str(i)+'&query='+query+'&region='+j+'&sortingOrder=precision')
                html = self.driver.page_source
                dom = BeautifulSoup(html.encode('utf-8'), 'html.parser')
                tmp = [i.get('href') for i in dom.select('a.name')]
                self.urls += tmp
    def get(self):
        self.client = MongoClient("localhost")
        db = self.client.get_database('naver')
        try:
            naver = db.create_collection("naverCrawled")
        except:
            naver = db.get_collection("naverCrawled")
        #places = []
        patLng = re.compile(r'12[5-7][.][0-9]+')
        patLat = re.compile(r'3[6-8][.][0-9]+')
        for i in self.urls :
            self.driver.get(i)
            html = self.driver.page_source.encode('utf-8')
            dom = BeautifulSoup(html, 'html.parser')
            tmp = {}
            tmp['title'] = dom.select('strong.name')[0].text
            tmp['addr'] = dom.select('span.addr')[0].text
            tmp['call'] = dom.select('div.list_item.list_item_biztel > div.txt')[0].text
            tmp['text'] = [self.query]
            latlng = dom.select('a.btn')[0].get('href')
            tmp['lat'] = patLat.findall(latlng)
            tmp['lon'] = patLng.findall(latlng)
            self.driver.find_element_by_css_selector('a#tab03 > svg.name').click()
            html = self.driver.page_source
            dom = BeautifulSoup(html.encode('utf-8', 'html.parser'))
            tmp['img'] = [i.get('src') for i in dom.select('div.thumb > img')]
            naver.insert_one(tmp)
            #places.append(tmp)