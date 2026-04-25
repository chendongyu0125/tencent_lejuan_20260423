import logging
logging.basicConfig(level=logging.DEBUG)

import scrapy
import pandas as pd 
from scrapy.http import Request, FormRequest
import json
from tencent_lejuan_20260423.items import ProjectItem
from scrapy.loader import ItemLoader
import socket
from datetime import datetime
from bs4 import BeautifulSoup

# get all the detail information of projects


class LejuandetailsSpider(scrapy.Spider):
    '''
    This spider is developed to crawl details of all charity projects on the Lejuan platform
    '''
    name = "lejuandetails"
    allowed_domains = ["gongyi.qq.com"]
    # start_urls = ["https://gongyi.qq.com"]
    headers = {
        "Content-Type": "application/json",
        # 加上 Referer 和 User-Agent 可以模拟浏览器行为，防止被简单的反爬机制拦截
        "Referer": "https://gongyi.qq.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    apiurl_projectinfo = "https://ssl.gongyi.qq.com/gygw-app/ed/project_center_query/GetProjectInfoForC"
    apiurl_projectdata = "https://ssl.gongyi.qq.com/gygw-app/ed/gdata.query/GetProjData"



    def get_payload_projectinfo(self, project_no):
        payload = {
                "mini": False,
                "all": True,
                "project_no": project_no
            }
        return payload 
    
    def get_payload_projectdata(self, project_no):
        payload = {
            "pid": str(project_no)
        }


    def start_requests(self):

        # get all the projects
        projects = pd.read_csv("lejuan_snapshot.csv")[:5]
        for project_no in projects['project_no']:
            project_no = str(project_no)
            payload_info = self.get_payload_projectinfo(project_no)
            payload_data = self.get_payload_projectdata(project_no)
            
            # Get data from Project Inof
            yield Request(
                
                url=self.apiurl_projectinfo,
                method='POST',
                body=json.dumps(payload_info),
                meta={'payload':payload_info},
                callback=self.parse_info,
                headers=self.headers 
            )

            # Get data from ProjectData
            # yield Request(
            #     url = self.apiurl_projectdata, 
            #     method="POST", 
            #     body=json.dumps(payload_data),
            #     headers=self.headers,
            #     callback=self.parse_data,
            #     meta={'payload':payload_data}
            # )



 

    def parse(self, response):
        pass

    def parse_info(self, response):
        '''
        extract data from apiurl_info
        '''
        try:
            # logging.debug(f"response = {response.body}")
            json_data =  response.json()
            if not json_data:
                return 
            
            
            data = json_data.get("data")
            # logging.debug(f"data = {data}")

            # add all the values for each key in the section of "data" into the object of "item"
            item = ProjectItem()
            for k in data.keys():
                logging.debug(f"k={k}")
                item[k] = data.get(k)
            item['server'] = socket.gethostname()
            item['collection_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item['category'] = data.get('base').get('cateName')
            item['project_no'] = data.get('detail').get('id')

            # to crawl all the images in the detailed page
            desc = data['detail']['desc']
            soup = BeautifulSoup(desc, 'html.parser')
            img_tags = soup.find_all('img')
            image_urls = []
            for img in img_tags:
                src = img.get('src')
                if src:
                    image_urls.append(src)
            logging.debug(f"image_urls = {image_urls}")

            item['image_urls'] = []

            yield item

            
                



            

            
        except json.JSONDecodeError:
            logging.error("响应内容不是有效的 JSON 格式")
            logging.error(f"响应内容预览: {response.text[:500]}")   
            

    def parse_data(self, response):
        '''
        extract data from apiurl_data
        '''
        pass 
