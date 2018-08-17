import requests, json, csv, time, urllib3
from urllib.parse import urlencode, quote_plus, unquote
from pymongo import MongoClient

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
                res = s.get(url=self.url, params = self.params, headers=self.headers, timeout=150)
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


    def data_go_api(self, db_conn, params):

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
                    if 'http' in url_data[3]:
                        # Initial data getter
                        url_origin = url_data[3]+"/"+url_data[4]
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
                            db_conn.update_data_go(res_data, url_data[4])
                            # print(data_count)


class DBConnect():
    def __init__(self, host="127.0.0.1", port=27017, db="admin"):
        print("--INIT MONGO DB CONNECTION--")
        self.client = MongoClient(host = host, port = port)
        self.db = self.client.get_database(db)
        self.item = self.db['item']

    def set_item(self, item="item"):
        self.item = self.db[item]

    def set_db(self, db):
        self.db = self.client.get_database(db)

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


if __name__=="__main__":
    api_connect = APIConnect(["url_list_w_lat.txt", "url_list_wo_lat.txt"])
    db_conn = DBConnect()
    api_connect.seoul_api(db_conn)

    params={
        'radius':500,
        'cx':127.004528,
        'cy':37.567538,
        'type':'json',
        'ServiceKey':unquote('9yufdGwfG5nTrm48106s%2B%2FQK%2Bz6byu8kQyqGYX7ywOTcSZz5hKnJG6OSAFPymm3Ei6TrKcsL3Osas1zm4v6HmA%3D%3D'),
    }
    api_connect.data_go_api(db_conn, params)
