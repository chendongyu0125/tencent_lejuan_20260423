import logging
logging.basicConfig(level=logging.INFO)

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
import os 

from tencent_lejuan_20260423.tools import load_crawled_projects, fix_url_scheme
from tencent_lejuan_20260423.settings import CRAWLED_PROJECTS_FILE




def get_payload_projectinfo(project_no):
    payload = {
            "mini": False,
            "all": True,
            "project_no": project_no
        }
    return payload 

def get_payload_projectdata(project_no):
    payload = {
        "pid": str(project_no)
    }
    return payload


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

    def __init__(self, name = None, **kwargs):
        super().__init__(name, **kwargs)
        self.total = 0
        self.skipped = 0
        self.crawled = 0
        self.crawled_projects = load_crawled_projects(CRAWLED_PROJECTS_FILE)
        logging.info(f"Loaded {len(self.crawled_projects)} crawled projects from {CRAWLED_PROJECTS_FILE}")

    

    




    def start_requests(self):

        # get all the projects
        # projects = pd.read_csv("lejuan_snapshot.csv")[:1000] # 先测试前100个项目，后续可以去掉这个限制
        projects = pd.read_csv("lejuan_snapshot.csv")

        # statistics of the project numbers
        # total = 0
        # skipped = 0
        # crawled = 0

        for project_no in projects['project_no']:
            project_no = str(project_no)
            self.total += 1

            if project_no in self.crawled_projects:
                logging.info(f"Project {project_no} has already been crawled. Skipping.")
                self.skipped += 1
                continue
            
            # for uncrawled project, we will crawl the details of the project, and save the project number into the file
            self.crawled += 1
            
            
            payload_info = get_payload_projectinfo(project_no)
            payload_data = get_payload_projectdata(project_no)

            meta = {
                'payload_info': payload_info,
                'project_no': project_no
            }
            
            # Get data from Project Inof
            yield Request(
                
                url=self.apiurl_projectinfo,
                method='POST',
                body=json.dumps(payload_info),
                meta=meta,
                callback=self.parse_info,
                headers=self.headers 
            )
        
        # statistics of the project numbers
        logging.info(f"Total projects: {self.total}")
        logging.info(f"Skipped projects: {self.skipped}")
        logging.info(f"Crawled projects: {self.crawled}")

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
            fixed_url = fix_url_scheme(url)
            if fixed_url:
                all_image_urls.add(fixed_url)

        # 提取列表中的图片链接
        for img in base_data.get('img_list', []):
            fixed_url = fix_url_scheme(img)
            if fixed_url:
                all_image_urls.add(fixed_url)

        for img in detail_data.get('img_mob_list', []):
            fixed_url = fix_url_scheme(img)
            if fixed_url:
                all_image_urls.add(fixed_url)

        


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
                    fixed_url = fix_url_scheme(url)
                    if fixed_url:
                        all_image_urls.add(fixed_url)

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
            
            # get project_no from meta
            project_no = response.meta.get('project_no')
            if not project_no:
                logging.error("No project_no found in response meta. Skipping this item.")
                return
            
            data = json_data.get("data")
            if not data:
                logging.error(f"No 'data' field found in JSON response for project {project_no}. Skipping this item.")
                return
            # logging.debug(f"data = {data}")

            # add all the values for each key in the section of "data" into the object of "item"
            item = ProjectItem()
            # for k in data.keys():
            #     # logging.debug(f"k={k}")
            #     item[k] = data.get(k)
            for k in data.keys():
                if k in item.fields:
                    item[k] = data.get(k)

            # 补充系统字段
            item['server'] = socket.gethostname()
            item['collection_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 嵌套字段的安全获取
            base_data = data.get('base', {})
            item['category'] = base_data.get('cateName', 'unknown')
            item['project_no'] = project_no


            # to crawl all the images in the detailed page
            # 图片提取
            all_image_urls = self.extract_image_urls(json_data)
            item['image_urls'] = [url for url in all_image_urls if url]   


            yield item
         
        except json.JSONDecodeError:
            project_no = response.meta.get('project_no', 'Unknown')
            logging.error(f"Project {project_no} 响应内容不是有效的 JSON 格式")
            logging.error(f"响应内容预览: {response.text[:500]}")   
            

    def parse_data(self, response):
        '''
        extract data from apiurl_data
        '''
        pass 
