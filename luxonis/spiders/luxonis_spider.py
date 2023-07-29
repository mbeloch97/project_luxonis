import scrapy
from scrapy import signals
import time
import json
from pydispatch import dispatcher
import psycopg2

class SrealitySpider(scrapy.Spider):
    name = "sreality"
    start_urls = ["https://www.sreality.cz/en/search/for-sale/apartments?_escaped_fragment_="];
    results = {}
    counter = 0
    page = 1;
    def __init__(self):
        self.create_database()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def parse(self, response):
        print("Parsing page %d" %(self.page))
        for sel in response.css("div.dir-property-list > div.property.ng-scope"):
            if (sel):

                sel_imgs = sel.css("preact.ng-scope.ng-isolate-scope "
                                "> div._15Md1MuBeW62jbm5iL0XqR._1sm7uHIebD7tngzBEQy3dD "
                                "> div._2xzMRvpz7TDA2twKCXTS4R "
                                "> a._2vc3VMce92XEJFrv8_jaeN > img::attr('src')")
                #print(sel_imgs.get())

                sel_title = sel.css("div.info.clear.ng-scope > div.text-wrap > "
                                     "span.basic > h2 > a.title > span.name.ng-binding::text")
                #print(sel_title.get())

                sel_place = sel.css("div.info.clear.ng-scope > div.text-wrap > "
                                    "span.basic > span.locality.ng-binding::text")
                #print(sel_place.get())

                sel_price = sel.css("div.info.clear.ng-scope > div.text-wrap > "
                                    "span.basic > span.price.ng-scope> span.norm-price.ng-binding::text")

                price = ""
                if sel_price is not None:
                    price = sel_price.get().replace(u"\xa0", "")
                    price = price.replace("CZK", "")
                    #print(price)

                self.results[self.counter] = {
                    "img_url": sel_imgs.get(),
                    "title": sel_title.get(),
                    "place": sel_place.get(),
                    "price": price
                }
                self.counter += 1
            #time.sleep(2)
        if self.counter <= 480:
            self.page +=1 ;
            nextPage = "https://www.sreality.cz/en/search/for-sale/apartments?page=%d&_escaped_fragment_=" %(self.page)
            print(nextPage)
            time.sleep(4)
            yield response.follow(nextPage, self.parse)

    def create_database(self):
        try:
            print("CONNECTING")
            conn = psycopg2.connect(host="db", user="postgres", password="1234", port="5432")
            print("CONNECTING OK")
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute("SELECT EXISTS(SELECT datname FROM pg_catalog.pg_database WHERE datname = 'mydatabase')")
            exists = cursor.fetchone()
            print(exists[0])
            if not exists[0]:
                cursor.execute("CREATE DATABASE mydatabase")
                print("Database mydatabase created.")
            else:
                print("Database mydatabase already exists.")
            conn.close()
        except Exception as e:
            print("Error:", str(e))


    def spider_closed(self, spider):
        with open('results.json', 'w', encoding='utf-8') as fp:
            json.dump(self.results, fp, ensure_ascii=False)

        try:
            conn = psycopg2.connect(host="db", database="mydatabase", user="postgres", password="1234", port="5432")
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS scrab ("
                           "id BIGSERIAL NOT NULL PRIMARY KEY,"
                           "title VARCHAR(200) NOT NULL,"
                           "place VARCHAR(100) NOT NULL,"
                           "price VARCHAR(100) NOT NULL,"
                           "img VARCHAR(300) NOT NULL)")
            cursor.execute("DELETE FROM scrab")
            for key, value in self.results.items():
                cursor.execute("INSERT INTO scrab (title, place, price, img) "
                               "VALUES (%s, %s, %s, %s)", (value["title"], value["place"], value["price"], value["img_url"]))
            #cursor.commit()
        except Exception as e:
            print("Error:", str(e))
        finally:
            #cursor.close()
            conn.close()
