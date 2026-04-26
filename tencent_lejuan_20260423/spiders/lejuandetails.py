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
import re

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

    custom_settings = {
        'ITEM_PIPELINES': {
            'tencent_lejuan_20260423.pipelines.DetailImagesPipeline': 300,
        }
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
        projects = pd.read_csv("lejuan_snapshot.csv")[:10]
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

    def extract_image_urls(self, json_data):
        '''
        extract image urls from the description of the project
        '''
        data = json_data.get('data', {})
        base_data = data.get('base', {})
        detail_data = data.get('detail', {})
        v3_detail = data.get('v3_detail', {})

        all_image_urls = set() # 使用集合去重

        # 1. 提取直接字段中的图片链接
        direct_fields = [
            base_data.get('listImg'),
            base_data.get('focusImg', {}).get('syn_url'),
            base_data.get('fundImg', {}).get('syn_url'),
            base_data.get('pUserFace', {}).get('syn_url'),
            base_data.get('funder', {}).get('face')
        ]
        
        for url in direct_fields:
            if url:
                all_image_urls.add(url)

        # 提取列表中的图片链接
        for img in base_data.get('img_list', []):
            all_image_urls.add(img)
        for img in base_data.get('img_mob_list', []):
            all_image_urls.add(img)

        # 2. 使用正则表达式提取富文本（HTML）中的图片链接
        # 需要扫描包含HTML的字段，例如项目介绍、预算等
        html_contents = [
            base_data.get('desc', ''),
            base_data.get('proj_budget', ''),
            detail_data.get('desc', ''),
            detail_data.get('proj_budget', ''),
            detail_data.get('proj_team_info', ''),
            v3_detail.get('backdrop', '')
        ]

        # 正则匹配 src="..." 或 src='...' 中的内容，忽略大小写
        img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
        
        for content in html_contents:
            if content:
                found_urls = img_pattern.findall(content)
                for url in found_urls:
                    # 修复以 // 开头的无协议链接 (例如预算图片)
                    if url.startswith('//'):
                        url = 'https:' + url
                    all_image_urls.add(url)
        return all_image_urls

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
                # logging.debug(f"k={k}")
                item[k] = data.get(k)
            item['server'] = socket.gethostname()
            item['collection_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item['category'] = data.get('base').get('cateName')
            item['project_no'] = data.get('detail').get('id')

            # to crawl all the images in the detailed page
            all_image_urls = self.extract_image_urls(json_data)
            logging.debug(f"all_image_urls = {all_image_urls}")
            item['image_urls'] = list(all_image_urls)            

            yield item

            
                



            

            
        except json.JSONDecodeError:
            logging.error("响应内容不是有效的 JSON 格式")
            logging.error(f"响应内容预览: {response.text[:500]}")   
            

    def parse_data(self, response):
        '''
        extract data from apiurl_data
        '''
        pass 
