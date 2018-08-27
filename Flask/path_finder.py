from pymongo import MongoClient as mc
import math
from geopy.distance import distance
import requests
import json


class playFinder:
    def __init__(self, start, end, bikeCol):

        #       A20D145F-A461-3D2B-9BAC-622B2005AAD7 Key

        sjson = requests.get(
            'http://api.vworld.kr/req/address?service=address&request=getCoord&key=A20D145F-A461-3D2B-9BAC-622B2005AAD7&address=' + start + '&type=ROAD').json()
        if sjson['response']['status'] == 'NOT_FOUND':
            sjson = requests.get(
                'http://api.vworld.kr/req/address?service=address&request=getCoord&key=A20D145F-A461-3D2B-9BAC-622B2005AAD7&address=' + start + '&type=PARCEL').json()

        ejson = requests.get(
            'http://api.vworld.kr/req/address?service=address&request=getCoord&key=A20D145F-A461-3D2B-9BAC-622B2005AAD7&address=' + end + '&type=ROAD').json()
        if ejson['response']['status'] == 'NOT_FOUND':
            ejson = requests.get('http://api.vworld.kr/req/address?service=address&request=getCoord&key=A20D145F-A461-3D2B-9BAC-622B2005AAD7&address='+end+'&type=PARCEL').json()
        try:
            self.sloc = (
            float(sjson['response']['result']['point']['y']), float(sjson['response']['result']['point']['x']))
        except:
            sjson = requests.get(
                'http://api.vworld.kr/req/address?service=address&request=getCoord&key=A20D145F-A461-3D2B-9BAC-622B2005AAD7&address=' + start + '&type=PARCEL').json()
            self.sloc = (
            float(sjson['response']['result']['point']['y']), float(sjson['response']['result']['point']['x']))
        try:
            self.eloc = float(ejson['response']['result']['point']['y']), float(
                ejson['response']['result']['point']['x'])
        except:
            ejson = requests.get(
                'http://api.vworld.kr/req/address?service=address&request=getCoord&key=A20D145F-A461-3D2B-9BAC-622B2005AAD7&address=' + end + '&type=PARCEL').json()
            self.eloc = float(ejson['response']['result']['point']['y']), float(
                ejson['response']['result']['point']['x'])
        print('주소값 변환 완료')############################################
        print(sjson, ejson)
        self.bikeCol = bikeCol
        print('################################################')
        self.bicol = list(bikeCol.find({}))[0]['realtimeList']
        print(len(self.bicol))#############################
        sdist = 1000.0
        edist = 1000.0
        self.dist = distance(self.sloc, self.eloc).km
        for i in range(len(self.bicol)):
            print(i)#####################################################
            tloc = (float(self.bicol[i]['stationLatitude']),
                    float(self.bicol[i]['stationLongitude']))
            if distance(self.sloc, tloc).km < sdist:
                sdist = distance(self.sloc, tloc).km
                self.sid = self.bicol[i]['stationId']
            if distance(self.eloc, tloc).km < edist:
                edist = distance(self.eloc, tloc).km
                self.eid = self.bicol[i]['stationId']
        print('자전거 DB 처리 완료')#####################################################

    def __grid__(self, v1, v2):
        RE = 6371.00877
        GRID = 5.0
        SLAT1 = 30.0
        SLAT2 = 60.0
        OLON = 126.0
        OLAT = 38.0
        XO = 43
        YO = 136
        DEGRAD = math.pi / 180.0
        RADDEG = 180.0 / math.pi
        re = RE / GRID;
        slat1 = SLAT1 * DEGRAD
        slat2 = SLAT2 * DEGRAD
        olon = OLON * DEGRAD
        olat = OLAT * DEGRAD
        sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
        sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
        sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
        sf = math.pow(sf, sn) * math.cos(slat1) / sn
        ro = math.tan(math.pi * 0.25 + olat * 0.5)
        ro = re * sf / math.pow(ro, sn);
        rs = {};
        ra = math.tan(math.pi * 0.25 + (v1) * DEGRAD * 0.5)
        ra = re * sf / math.pow(ra, sn)
        theta = v2 * DEGRAD - olon
        if theta > math.pi:
            theta -= 2.0 * math.pi
        if theta < -math.pi:
            theta += 2.0 * math.pi
        theta *= sn
        rs['x'] = (ra * math.sin(theta) + XO + 0.5)
        rs['y'] = (ro - ra * math.cos(theta) + YO + 0.5)
        return rs['x'], rs['y']

    def __selector__(self, x1, y1, x2, y2, x, y):
        m = (y2 - y1) / (x2 - x1)
        the = math.tanh(m)
        newx = x * math.cos(the) + y * math.sin(the)
        newy = x * math.cos(the) - y * math.sin(the)
        csq = ((self.dist) / 2) ** 2
        bsq = 180
        asq = csq ** 2 + bsq ** 2
        cenx = (x1 + x2) / 2
        ceny = (y1 + y2) / 2
        ellipse = (newx - cenx) ** 2 / asq + (newy - ceny) ** 2 / bsq
        if ellipse <= 1:
            return True
        else:
            return False

    def finder(self, collection):
        self.collection = collection
        col = list(self.collection.find({}))[0:500]
        x1, y1 = self.__grid__(self.sloc[0], self.sloc[1])
        x2, y2 = self.__grid__(self.eloc[0], self.eloc[1])
        self.result = []
        for i in range(len(self.bicol)):

            x, y = self.__grid__(float(self.bicol[i]['stationLatitude']), float(self.bicol[i]['stationLongitude']))
            if self.__selector__(x1, y1, x2, y2, x, y):
                self.result.append([self.bicol[i]['stationId'], (
                float(self.bicol[i]['stationLatitude']), float(self.bicol[i]['stationLongitude']))])



        self.resdict = {}

        for i in range(500):
            print(i)
            cloc = (col[i]['items']['lon'], col[i]['items']['lat'])
            cdist = distance(self.result[0][1], cloc).km
            self.resdict[i] = (col[i]['cat_id'], self.result[0][0])
            for j in range(1, len(self.result)):
                if cdist > distance(self.result[j][1], cloc).km:
                    cdist = distance(self.result[j][1], cloc).km
                    self.resdict[i] = (col[i]['cat_id'], self.result[j][0])


        return self.resdict