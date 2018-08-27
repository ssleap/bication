import requests, json, csv, time, urllib3
from urllib.parse import urlencode, quote_plus, unquote
from pymongo import MongoClient
import os
import pandas as pd
import pickle

class DataConnect():
    def __init__(self, url, headers, params=None):
        self.url = url
        self.params = params
        self.headers = headers
        self.data = ""

    def getData(self, num_retries=5):
        with requests.Session() as s:
            s.keep_alive = False
            try:
                res = s.get(url=self.url, params = self.params, headers=self.headers, timeout=10)
    #         res = requests.get(url=self.url, params = self.params, headers=self.headers, timeout=1)
                if 500 <= res.status_code<600:
                    print(html.status_code, res, reason)
                    raise ConnectionError

            except:
                s.close()
                print("--TRY CONNECTION {0}...--".format(num_retries))
                if num_retries > 0:
#                     time.sleep(60)
                    return self.getData(num_retries = (num_retries-1))
                else:
                    s.close()
                    print("--MAX RETRY REACHED!--")
                    return None
            else:
                resStr = res.content
                resStr = resStr.decode('utf-8')
                resObj = json.loads(resStr)
        #         print(json.dumps(resObj, indent="  ",  ensure_ascii=False))
                self.data = resObj
                s.close()
                return resObj


    def setUrl(self, url):
        self.url = url

    def setParams(self, params):
        self.params = params

    def setHeaders(self, headers):
        self.headers = headers

class APIConnect():
    def __init__(self, api_list):
        self.api_list = api_list
        self.reconnect_url = []

    def seoul_api(self, db_conn):

        for api in self.api_list:
            if "_w_" in api:
                db_conn.set_db("OpenAPIWithPos")
            else:
                db_conn.set_db("OpenAPIWithoutPos")
            db_conn.set_item("seoul")
            with open(api, 'r', newline='') as f:
                f_csv = csv.reader(f, delimiter='\t')
                url_list = []

                for row in (row for row in f_csv if row[0] == 'seoul'):
                    url_list.append(row)

                for url_data in url_list:
                    if 'http' in url_data[3]:
                        # Initial data getter
                        url_origin = url_data[3]+"/"+url_data[5]+"/json/"+url_data[4]
                        url_init = url_origin+"/1/1"
#                         print(url_init)
                        headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
                                "Connection": "close",
                                }
                        data_connect = DataConnect(url=url_init, headers=headers)
                        res_data = data_connect.getData()


                        try:
                            res_data[url_data[4]]
                        except Exception as e:
                            print(e)
                            print(res_data["RESULT"]["CODE"], ":", res_data["RESULT"]["MESSAGE"])
                        else:
                            # Seoul API의 category data를 입력한다
                            db_conn.update_category(res_data, "seoul")
                            divisor = 250
                            data_count = res_data[url_data[4]]["list_total_count"]
                            loop_count = data_count // divisor
                            loop_remain = data_count % divisor
                            print("--LOAD {0} ITEMS, SEPERATED BY 1000 ({1}, {2})--".format(data_count, loop_count, loop_remain))
                            for i in range(loop_count):
                                url_req = url_origin+"/"+str(i*divisor+1)+"/"+str((i+1)*divisor)
                                print(url_req)
                                data_connect.setUrl(url_req)
                                res_data = data_connect.getData()
                                # 이후 DB에 넣음
                                db_conn.update_seoul(res_data, i*divisor)
                            if loop_remain > 0:
                                url_req = url_origin+"/"+str(loop_count*divisor+1)+"/"+str((loop_count*divisor)+loop_remain)
                                print(url_req)
                                data_connect.setUrl(url_req)
                                res_data = data_connect.getData()
                                # 이후 DB에 넣음
                                db_conn.update_seoul(res_data, loop_count*divisor)
                            # print(data_count)


    def data_go_api(self, db_conn, api_name, params):

        for api in self.api_list:
            if "_w_" in api:
                db_conn.set_db("OpenAPIWithPos")
            else:
                db_conn.set_db("OpenAPIWithoutPos")
            db_conn.set_item("data_go")
            with open(api, 'r', newline='') as f:
                f_csv = csv.reader(f, delimiter='\t')
                url_list = []

                for row in (row for row in f_csv if row[0] == 'data_go'):
                    url_list.append(row)

                for url_data in url_list:
                    if 'http' in url_data[3] and api_name == url_data[4]:
                        # Initial data getter
                        url_origin = url_data[3]+"/"+api_name
                        url_init = url_origin
                        print(url_init)
#                         print(url_init)
                        headers={
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
                            'Connection':'close',
                                }

                        try:
                            data_connect = DataConnect(url=url_init, params = params, headers=headers)
                            res_data = data_connect.getData()
                            res_data["body"]["items"]
                        except:
                            print(res_data["header"]["resultCode"], ":", res_data["header"]["resultMsg"])
                        else:
                            # 이후 DB에 넣음
                            db_conn.update_data_go(res_data, api_name)
                            # print(data_count)


class DBConnect():
    def __init__(self, host="127.0.0.1", port=27017, db="admin"):
        print("--INIT MONGO DB CONNECTION--")
        self.client = MongoClient(host = host, port = port)
        self.db = self.client.get_database(db)
        self.item = self.db['item']
        print("--CLIENT : {0}--".format(self.client))
        print("--DB : {0}--".format(self.db))
        print("--ITEM : {0}--".format(self.item))


    def set_item(self, item="item"):
        self.item = self.db[item]

    def set_db(self, db):
        self.db = self.client.get_database(db)


    def get_item_by_cat(self, search_key):
        self.set_db("map_db")
        self.set_item("place")
        result = self.item.find({
            'cat_name':search_key
        },
        {
            '_id': False
        })
        return result

    def get_item_by_title(self, search_key):
        self.set_db("map_db")
        self.set_item("place")
        result = self.item.find({
            'items.title':search_key
        },
        {
            '_id': False
        })
        return result

    def get_item_by_latlon(self, search_key):
        self.set_db("map_db")
        self.set_item("place")
        result = self.item.find({
            "$or":[ {'items.lat':search_key[0]}, {'items.lon':search_key[1]}]

        },
        {
            '_id': False
        })
        return result


    def update_seoul(self, items, index):
        print("--UPDATE START--")
#         print(self.item)
#         print(self.db)
#         print(self.client)
#         print(items[list(items.keys())[0]]["row"])
        if items == None:
            print("--NO ITEMS!--")
            return
        for row in items[list(items.keys())[0]]["row"]:
            try:
#                 print(index, row)
                result = self.item.update_one(
                    {
                        "api_id": list(items.keys())[0]+"_"+str(index)
                    },
                    {
                        '$set': row
                    },
                    upsert=True,
                )
#                 print(result.raw_result)

                index += 1
            except Exception as e:
                print(e)

        print("--DATA UPDATE IS COMPLETED--")

    def update_data_go(self, items, name):
        print("--UPDATE START--")
        index = 0
        items = items["body"]
        if len(items.keys()) == 0:
            print("--NO ITEMS!--")
            return
        for row in items["items"]:
            try:
#                 print(index, row)
                result = self.item.update_one(
                    {
                        "api_id": list(name+"_"+str(index))
                    },
                    {
                        '$set': row
                    },
                    upsert=True,
                )
#                 print(result.raw_result)

                index += 1
            except Exception as e:
                print(e)

        print("--DATA UPDATE IS COMPLETED--")

    def update_csv(self, name, csv_id = ""):
        self.set_db("OpenAPIWithPos")
        self.set_item("csv_"+name)
        print("--UPDATE START--")
        url = "csv/"+name
        file_list = []
        for(dirpath, dirnames, filenames) in os.walk(url):
            file_list.extend(filenames)
            break
        print(file_list)
        if len(file_list) == 0:
            print("--NO ITEMS!--")
            return

        # 일단 다 지우기...
        result = self.item.delete_many({})
        for file in file_list:
            df = pd.read_csv(url+"/"+file, engine='python')
            data = df[df["시도명"] == "서울특별시"]
            data_json = json.loads(data.to_json(orient='records'))
#             print(data_json)
            try:
#                 print(index, row)
                result = self.item.insert_many(
                    data_json,
                )
#                 print(result.raw_result)

            except Exception as e:
                print(e)

        print("--DATA UPDATE IS COMPLETED--")

    def update_crawl(self, name = "/", crawl_id = ""):
        self.set_db("OpenAPIWithPos")

        print("--UPDATE START--")
        url = "crawl"+name
        file_list = []
        for(dirpath, dirnames, filenames) in os.walk(url):
            file_list.extend(filenames)
            break

        print(file_list)
        if len(file_list) == 0:
            print("--NO ITEMS!--")
            return

        # 일단 다 지우기...

        for file in file_list:
            self.set_item("crawl_"+file.split(".")[0])
            result = self.item.delete_many({})
            with open(url+"/"+file, 'rb') as f:
                data = pickle.load(f)
            for i in range(len(data)):
#                 data[i]["api_id"] = "diningCode_"+str(i)
                data[i]["api_id"] = "diningCode_"+str(i)

#                 print(data[i])
            data_json = data

#             print(data_json)
            try:
#                 print(index, row)
                result = self.item.insert_many(

                    data_json,
                )
#                 print(result.raw_result)

            except Exception as e:
                print(e)

        print("--DATA UPDATE IS COMPLETED--")


    def update_map_db(self):
        print("--SET DB POINTER TO OPENAPIWITHPOS--")
#         self.db = self.client.get_database("OpenAPIWithPos")
        self.set_db("OpenAPIWithPos")
        print("--SELECT ITEMS--")

        items = []
        # seoul data
        self.set_item("seoul")
        items.extend(list(self.item.find({})))

        # csv data(우선은 직접 명시)
        self.set_item("csv_small_shop")
        items.extend(list(self.item.find({})))

        # crawl data
        self.set_item("crawl_dining_code")
        items.extend(list(self.item.find({})))



        print("--SET DISCRIMINATOR--")
        disc_api_id = ['api_id', '상가업소번호']
        disc_title = ['title', 'TITLE', 'GIGU', 'GOSU_CD','COURSE_NAME', 'NM', 'LBRRY_NAME', 'NAME_KOR', 'COT_CONTS_NAME', '상호명']
        disc_x = ['lat','X', 'XCODE', 'XCNTS', 'WGS84_X', 'COT_COORD_X', '위도']
        disc_y = ['lon','Y', 'YCODE', 'YDNTS', 'WGS84_Y', 'COT_COORD_Y', '경도']
        disc_text = ['text','CONTENT','REMARK', 'CULTURE_BUSINESS_TYPE', 'CODENAME', '표준산업분류명']
        disc_tag = []
        disc_cat = ['상권업종중분류명']
        disc_addr = ['addr','ADDR', 'ADDR_OLD', 'ADRES', 'ADD_KOR', 'COT_ADDR_FULL_NEW', 'COT_ADDR_FULL_OLD', '도로명주소']
        disc_call = ['call','TEL_NO', 'TEL']
        disc_image = ['img']
        print("--SET DB POINTER TO MAP_DB--")
        self.set_db("map_db")

        print("--SELECT ITEMS--")
        self.set_item("place")

        print("--UPDATE START--")

        for row in items:
            set_api_id = ""
            set_title = ""
            set_text=""
            set_tag=""
            set_cat=""
            set_addr=""
            set_call=""
            set_x = ""
            set_y = ""
            set_image = ""


            for api_id in disc_api_id:
                if api_id in row.keys():
                    set_api_id = row[api_id]
            for title in disc_title:
                if title in row.keys():
                    set_title = row[title]
            for x in disc_x:
                if x in row.keys():
                    set_x = row[x]
            for y in disc_y:
                if y in row.keys():
                    set_y = row[y]

            for text in disc_text:
                if text in row.keys():
                    set_text = row[text]
            for tag in disc_tag:
                if tag in row.keys():
                    set_tag = row[tag]
            for cat in disc_cat:
                if cat in row.keys():
                    set_cat = row[cat]
            for addr in disc_addr:
                if addr in row.keys():
                    set_addr = row[addr]
            for call in disc_call:
                if call in row.keys():
                    set_call = row[call]
            for image in disc_image:
                if image in row.keys():
                    set_image = row[image]
            insert_data = {
                            'cat_name':set_cat,
                            'pop_tags':set_tag,
                            'items':{
                                'title': set_title,
                                'text':set_text,
                                'star_cnt':"",
                                'rev_cnt':"",
                                'addr':set_addr,
                                'call':set_call,
                                'lon': set_x,
                                'lat': set_y,
                                'image' : set_image
                            }
                }
#             print(insert_data)
            try:
#                 print(index, row)


                result = self.item.update_one(
                    {
                        "cat_id": set_api_id
                    },
                    {
                        '$set': insert_data

                    },
                    upsert=True,
                )
#                 print(result.raw_result)

            except Exception as e:
#                 print(e)
                print("--ERROR!--")
            else:
                pass
#                 print("--ONE ITEM UPDATED--")

        print("--DATA UPDATE IS COMPLETED--")

    def update_category(self, items, name):
        print("--UPDATE START--")
        db = self.client.get_database("OpenAPICategory")
        db_item = db[name]

#         items = items["body"]
#         if len(items.keys()) == 0:
#             print("--NO ITEMS!--")
#             return

        if items == None:
            print("--NO ITEMS!--")
            return
        for row in items[list(items.keys())[0]]["row"]:
            try:
#                 print(index, row)
                result = db_item.update_one(
                    {
                        "api_id": list(items.keys())[0]
                    },
                    {
                        '$set': row

                    },
                    upsert=True,
                )
#                 print(result.raw_result)

            except Exception as e:
                print(e)

if __name__=="__main__":
    api_connect = APIConnect(["url_list_w_lat.txt", "url_list_wo_lat.txt"])
    db_conn = DBConnect()
#     api_connect.seoul_api(db_conn)

#     params={
#         'radius':5000,
#         'cx':127.004528,
#         'cy':37.567538,
#         'type':'json',
#         'ServiceKey':unquote('9yufdGwfG5nTrm48106s%2B%2FQK%2Bz6byu8kQyqGYX7ywOTcSZz5hKnJG6OSAFPymm3Ei6TrKcsL3Osas1zm4v6HmA%3D%3D'),
#     }
#     api_connect.data_go_api(db_conn,"storeZoneInRadius",params)


    db_conn.update_csv("small_shop")
#     db_conn.update_crawl()
    db_conn.update_map_db()
