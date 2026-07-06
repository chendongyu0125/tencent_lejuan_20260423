import logging
logging.basicConfig(level=logging.INFO)

from tencent_lejuan_20260423 import settings
import scrapy
import pandas as pd 
from scrapy.http import Request, FormRequest
import json
from tencent_lejuan_20260423.items import ProjectItem
from scrapy.loader import ItemLoader
import socket
from datetime import datetime
from bs4 import BeautifulSoup
import os

from tencent_lejuan_20260423.tools import load_crawled_projects
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
    # allowed_domains = ["gongyi.qq.com"]
    allowed_domains = ["gongyi.qq.com", "qq.com"]
    # start_urls = ["https://gongyi.qq.com"]
    headers = {
        "Content-Type": "application/json",
        # 加上 Referer 和 User-Agent 可以模拟浏览器行为，防止被简单的反爬机制拦截
        "Referer": "https://gongyi.qq.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        'Referer': 'http://gongyi.qq.com/'
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
                # 初始化时加载所有需要爬取的项目编号
        try:
            self.project_nos = set(pd.read_csv(settings.PROJECT_NO_FILE, header=None, dtype=str)[0].dropna().unique())
            logging.info(f"已加载 {len(self.project_nos)} 个需要爬取的项目编号")
        except FileNotFoundError:
            logging.error("未找到 project_nos.dat 文件，请先运行 generate_project_no_file 函数生成该文件")
            self.project_nos = set()

    

    




    def start_requests(self):

        # get all the projects


        for project_no in self.project_nos:
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
            
            # Get data from Project Info
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
