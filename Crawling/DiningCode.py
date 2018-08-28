import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from selenium import webdriver
import re
import time



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
        
        imgPat = r'.+cloudfront[.]net.+'
        r = re.compile(imgPat)
        driver = webdriver.Chrome(chromePath)
        sto = []
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
            sto.append(tmp)
            time.sleep(5)
        return sto
        
    

	
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

class townListMaker :
    def __init__(self):
        self.dList = ['종로구',
     '서울중구', '용산구', '성동구', '광진구', '동대문구', '중랑구','성북구', '강북구', '도봉구', '노원구', '은평구', '서대문구', '마포구', '양천구', '강서구',
     '구로구', '금천구', '영등포구', '동작구', '관악구', '서초구', '송파구', '강동구', '신사동', '논현1동', '논현2동', '압구정동', '청담동',
     '삼성1동', '삼성2동', '대치1동', '대치2동', '대치4동', '역삼1동', '역삼2동', '도곡1동', '도곡2동', '개포1동', '개포2동', '개포4동', '세곡동',
     '일원본동', '일원1동', '일원2동', '수서동']
        self.guList = ['종로구','서울중구', '용산구', '성동구', '광진구', '동대문구','중랑구', '성북구', '강북구', '도봉구', '노원구', '은평구', '서대문구', '마포구',
         '양천구', '강서구', '구로구', '금천구', '영등포구', '동작구', '관악구', '서초구', '강남구', '송파구', '강동구']
        self.dongList = ['청운효자동', '사직동', '삼청동', '부암동', '평창동', '무악동', '교남동', '가회동', '종로1·2·3·4가동', '종로5·6가동', '이화동', '혜화동', '창신1동', '창신2동', '창신3동', '숭인1동', '숭인2동', '소공동', '회현동', '명동', '필동', '장충동', '광희동', '을지로동', '신당동', '다산동', '약수동', '청구동', '신당5동', '동화동', '황학동', '중림동', '후암동', '용산2가동', '남영동', '청파동', '원효로1동', '원효로2동', '효창동', '용문동', '한강로동', '이촌1동', '이촌2동', '이태원1동', '이태원2동', '한남동', '서빙고동', '보광동', '왕십리도선동', '왕십리2동', '마장동', '사근동', '행당1동', '행당2동', '응봉동', '금호1가동', '금호2·3가동', '금호4가동', '옥수동', '성수1가1동', '성수1가2동', '성수2가1동', '성수2가3동', '송정동', '용답동', '중곡1동', '중곡2동', '중곡3동', '중곡4동', '능동', '구의1동', '구의2동', '구의3동', '광장동', '자양1동', '자양2동', '자양3동', '자양4동', '화양동', '군자동', '용신동', '제기동', '전농1동', '전농2동', '답십리1동', '답십리2동', '장안1동', '장안2동', '청량리동', '회기동', '휘경1동', '휘경2동', '이문1동', '이문2동', '면목본동', '면목2동', '면목3·8동', '면목4동', '면목5동', '면목7동', '상봉1동', '상봉2동', '중화1동', '중화2동', '묵1동', '묵2동', '망우본동', '망우3동', '신내1동', '신내2동', '성북동', '삼선동', '동선동', '돈암1동', '돈암2동', '안암동', '보문동', '정릉1동', '정릉2동', '정릉3동', '정릉4동', '길음1동', '길음2동', '종암동', '월곡1동', '월곡2동', '장위1동', '장위2동', '장위3동', '석관동', '삼양동', '미아동', '송중동', '송천동', '삼각산동', '번1동', '번2동', '번3동', '수유1동', '수유2동', '수유3동', '우이동', '인수동', '쌍문1동', '쌍문2동', '쌍문3동', '쌍문4동', '방학1동', '방학2동', '방학3동', '창1동', '창2동', '창3동', '창4동', '창5동', '도봉1동', '도봉2동', '월계1동', '월계2동', '월계3동', '공릉1동', '공릉2동', '하계1동', '하계2동', '중계본동', '중계1동', '중계2·3동', '중계4동', '상계1동', '상계2동', '상계3·4동', '상계5동', '상계6·7동', '상계8동', '상계9동', '상계10동', '녹번동', '불광1동', '불광2동', '갈현1동', '갈현2동', '구산동', '대조동', '응암1동', '응암2동', '응암3동', '역촌동', '신사1동', '신사2동', '증산동', '수색동', '진관동', '충현동', '천연동', '북아현동', '신촌동', '연희동', '홍제1동', '홍제2동', '홍제3동', '홍은1동', '홍은2동', '남가좌1동', '남가좌2동', '북가좌1동', '북가좌2동', '공덕동', '아현동', '도화동', '용강동', '대흥동', '염리동', '신수동', '서강동', '서교동', '합정동', '망원1동', '망원2동', '연남동', '성산1동', '성산2동', '상암동', '목1동', '목2동', '목3동', '목4동', '목5동', '신월1동', '신월2동', '신월3동', '신월4동', '신월5동', '신월6동', '신월7동', '신정1동', '신정2동', '신정3동', '신정4동', '신정6동', '신정7동', '염창동', '등촌1동', '등촌2동', '등촌3동', '화곡본동', '화곡1동', '화곡2동', '화곡3동', '화곡4동', '화곡6동', '화곡8동', '우장산동', '가양1동', '가양2동', '가양3동', '발산1동', '공항동', '방화1동', '방화2동', '방화3동', '신도림동', '구로1동', '구로2동', '구로3동', '구로4동', '구로5동', '가리봉동', '수궁동', '고척1동', '고척2동', '개봉1동', '개봉2동', '개봉3동', '오류1동', '오류2동', '가산동', '독산1동', '독산2동', '독산3동', '독산4동', '시흥1동', '시흥2동', '시흥3동', '시흥4동', '시흥5동', '영등포본동', '영등포동', '여의동', '당산1동', '당산2동', '도림동', '문래동', '양평1동', '양평2동', '신길1동', '신길3동 ·신길4동', '신길5동', '신길6동', '신길7동', '대림1동', '대림2동', '대림3동', '노량진1동', '노량진2동', '상도1동', '상도2동', '상도3동', '상도4동', '흑석동', '사당1동', '사당2동', '사당3동', '사당4동', '사당5동', '대방동', '신대방1동', '신대방2동', '보라매동', '은천동', '성현동', '중앙동', '청림동', '행운동', '청룡동', '낙성대동', '인헌동', '남현동', '신림동', '신사동', '조원동', '미성동', '난곡동', '난향동', '서원동', '신원동', '서림동', '삼성동', '대학동', '서초1동', '서초2동', '서초3동', '서초4동', '잠원동', '반포본동', '반포1동', '반포2동', '반포3동', '반포4동', '방배본동', '방배1동', '방배2동', '방배3동', '방배4동', '양재1동', '양재2동', '내곡동', '신사동', '압구정동', '청담동', '논현1동', '논현2동', '삼성1동', '삼성2동', '대치1동', '대치2동', '대치4동', '역삼1동', '역삼2동', '도곡1동', '도곡2동', '개포1동', '개포2동', '개포4동', '일원본동', '일원1동', '일원2동', '수서동', '세곡동', '풍납1동', '풍납2동', '거여1동', '거여2동', '마천1동', '마천2동', '방이1동', '방이2동', '오륜동', '오금동', '송파1동', '송파2동', '석촌동', '삼전동', '가락본동', '가락1동', '가락2동', '문정1동', '문정2동', '장지동', '위례동', '잠실본동', '잠실2동', '잠실3동', '잠실4동', '잠실6동', '잠실7동', '강일동', '상일동', '명일1동', '명일2동', '고덕1동', '고덕2동', '암사1동', '암사2동', '암사3동', '천호1동', '천호2동', '천호3동', '성내1동', '성내2동', '성내3동', '길동', '둔촌1동', '둔촌2동']
        
        
    def getTownList(self, div = 'normal', size = 1):
        # div : normal 을 선택하면 서울의 기본 구 + 강남구만 따로, dong 은 동별로, gu는 구별로
        # size를 이용해서 선택한 행정구역 리스트를 size만큼 쪼개는 것이 가능.
        if size > 10 :
            raise Exception('size 10이하로 입력')
        import math
        
        if div == 'dong':
            if size == 1:
                return self.dongList
            self.size = float(size)
            listSize = float(len(dongList))
            conNum = math.ceil(listSize/self.size)
            frontNum = 0
            result = []
            while conNum != int(listSize) :
                try :
                    result.append(dongList[frontNum : conNum])
                    frontNum = conNum
                    conNum *= 2
                except IndexError:
                    result.append(dongList[frontNum:])
                    return result
            return result
            
        elif div == 'gu':
            if size == 1:
                return self.guList
            self.size = float(size)
            listSize = float(len(guList))
            conNum = math.ceil(listSize/self.size)
            frontNum = 0
            result = []
            while conNum != int(listSize) :
                try :
                    result.append(guList[frontNum : conNum])
                    frontNum = conNum
                    conNum *= 2
                except IndexError:
                    result.append(guList[frontNum:])
                    return result
            return result
            
        if size == 1:
            return self.dList
        self.size = float(size)
        listSize = float(len(dList))
        conNum = math.ceil(listSize/self.size)
        frontNum = 0
        result = []
        while conNum != int(listSize) :
            try :
                result.append(dList[frontNum : conNum])
                frontNum = conNum
                conNum *= 2
            except IndexError:
                result.append(dList[frontNum:])
                return result
        return result
        
    
#     def wikiCrawler(self):
#         import requests
#         from bs4 import BeautifulSoup
#         seoul = requests.get('https://ko.wikipedia.org/wiki/%EA%B0%95%EB%82%A8%EA%B5%AC%EC%9D%98_%ED%96%89%EC%A0%95_%EA%B5%AC%EC%97%AD')
#         seoul = BeautifulSoup(seoul.content, 'lxml')
#         slist = seoul.select('b > a')
#         seoul_gu = requests.get('https://ko.wikipedia.org/wiki/%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C%EC%9D%98_%ED%96%89%EC%A0%95_%EA%B5%AC%EC%97%AD')
#         seoul_gu = BeautifulSoup(seoul_gu.content, 'lxml')
#         gList = seoul_gu.select('b > a')
#         guList = [i.text for i in gList]
#         guList[1] = '서울중구'
#         dList = guList + [i.text for i in slist]
#         dList.remove('강남구')
#         dList[1] = '서울중구'
#         html = requests.get('https://ko.wikipedia.org/wiki/%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C%EC%9D%98_%ED%96%89%EC%A0%95_%EA%B5%AC%EC%97%AD')
#         dom = BeautifulSoup(html.content, 'html.parser')
#         ddList = [i.text.split(' · ') for i in dom.select('#mw-content-text > div > dl > dd')]
#         dongList = []
#             for i in ddList :
#                 dongList += i
        

if __name__ == '__main__':
	import pickle
	ddd = diningCrawler()
	with open('diningCrawled.plk', 'wb') as f:
		sto = ddd.get('chromedriver.exe')
		pickle.dump(sto, f)

