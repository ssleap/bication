import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from selenium import webdriver
import re
import time
from pymongo import MongoClient
class diningCrawler:
    def __init__(self, townList = ['종로구','서울중구','용산구','성동구','광진구','동대문구','중랑구','성북구','강북구','도봉구','노원구','은평구','서대문구','마포구',
     '양천구','강서구','구로구','금천구','영등포구','동작구','관악구','서초구','송파구','강동구','신사동','논현1동','논현2동','압구정동','청담동','삼성1동',
     '삼성2동','대치1동','대치2동','대치4동','역삼1동','역삼2동','도곡1동','도곡2동','개포1동', '개포2동',   '개포4동', '세곡동', '일원본동', '일원1동',  '일원2동','수서동']):
        
        urls = ['https://www.diningcode.com/list.php?page='+str(k)+'&chunk=10&query='+i+'+%ED%85%8C%EC%9D%B4%ED%81%AC%EC%95%84%EC%9B%83'.format(i) for i in townList for k in range(1,11)]


        seoul = []
        for i in urls :
            html = requests.get(i)
            dom = BeautifulSoup(html.content, 'lxml')
            seoul += dom.select('div.dc-restaurant-name > a')
    

        takeout = []
        for i in seoul :
            if i.get('href') != '#':
                takeout.append(i.get('href'))
        self.takeouts = ['https://www.diningcode.com/'+i for i in takeout]

    #crawling method
    def get(self, chromePath):
        self.client = MongoClient("localhost")
        imgPat = r'.+cloudfront[.]net.+'
        r = re.compile(imgPat)
        driver = webdriver.Chrome(chromePath)
        db = self.client.get_database('dining')
        try:
            dining = db.create_collection("diningCrawled")
        except:
            dining = db.get_collection("diningCrawled")
        for i in self.takeouts :
            tmp = {}
            driver.get(i)
            html = driver.page_source.encode('utf-8')
            dom = BeautifulSoup(html, 'lxml')
            tmp['title'] = dom.select('div#item-rn > span.item-rn-title')[0].text
            tmp['addr'] = dom.select('div.item-information-text')[-2].text
            tmp['call'] = dom.select('div.item-information-text')[-1].text
            var = dom.select('div#map_area > script')[2].text
            v = word_tokenize(var)
            tmp['lat'] = v[16]
            tmp['lon'] = v[18]
            #tmp = [tnum, name, adrs, lat, lng]
            tags = dom.select('div#item-rn  a.urlkeyword')
            tagTmp = [tag.text for tag in tags]
            tmp['text'] = tagTmp
            img = dom.select('a.popup1')
            imgList = []
            for i in img :
                if r.findall(i.get('href')):
                    imgList += [i.get('href')]

            tmp['img'] = imgList
            dining.insert_one(tmp)
            time.sleep(5)
        
    


'''
sto 예시
[{'title': '육회자매집 ',
  'addr': '서울특별시 종로구 종로4가 177',
  'call': '02-2272-3069',
  'lat': '37.570569',
  'lon': '126.999887',
  'text': ['육회', '육회비빔밥'],
  'img': ['https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/51226/57132/51226_57132_86_5_4436_201652191711372.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/59489/56188/59489_56188_86_5_9320_201641602558167.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/53590/52938/53590_52938_76_0_9649_2016522134113992.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/54861/53276/54861_53276_85_0_551_2016520213519954.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/54044/58019/54044_58019_77_0_5353_20165230554544.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/59800/52158/59800_52158_76_0_3016_2016522164946832.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/50095/54555/50095_54555_80_0_1691_2016416104116866.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/59183/51031/59183_51031_86_5_9787_2016521162439791.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/55132/59236/55132_59236_89_0_8193_2016523175654179.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/55132/59236/55132_59236_89_0_8193_2016523175654179.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/57673/51334/57673_51334_85_0_3528_20165212341860.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/52605/55409/52605_55409_85_0_4797_201641615223121.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/58252/58951/58252_58951_86_5_877_201641514255981.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/56329/55383/56329_55383_77_0_7783_201652316742953.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/53126/51740/53126_51740_89_0_5016_2016522105912772.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/53126/51740/53126_51740_89_0_5016_2016522105912772.jpg',
   'https://d2t7cq5f1ua57i.cloudfront.net/images/r_images/56645/50782/56645_50782_76_0_372_2016520205650724.jpg']},.......]
'''

if __name__ == '__main__':
	ddd = diningCrawler()
	ddd.get('chromedriver.exe')
	ddd.client.close()
	
