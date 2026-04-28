# import scrapy


# class DonationinfoSpider(scrapy.Spider):
#     name = "donationinfo"
#     allowed_domains = ["gongyi.qq.com"]
#     start_urls = ["https://gongyi.qq.com"]

#     def parse(self, response):
#         pass


import scrapy
import json
import pandas as pd
import logging
import socket
from datetime import datetime

# 导入工具函数和配置
from tencent_lejuan_20260423.items import DonationItem
from tencent_lejuan_20260423.tools import load_crawled_projects, save_crawled_project
# 建议在 settings.py 中定义这个新文件路径
CRAWLED_DONATION_FILE = "crawled_donation_stats.txt" 

class DonationinfoSpider(scrapy.Spider):
    name = "lejuandonations"
    allowed_domains = ["gongyi.qq.com"]
    api_url = "https://ssl.gongyi.qq.com/gygw-app/ed/gdata.query/GetProjData"
    
    headers = {
        "Content-Type": "application/json",
        "Referer": "https://gongyi.qq.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        # 初始化时加载已爬取的项目编号
        self.crawled_projects = load_crawled_projects(CRAWLED_DONATION_FILE)
        logging.info(f"已加载 {len(self.crawled_projects)} 个已爬取的捐赠数据记录")

    def start_requests(self):
        try:
            # 强制 project_no 为字符串
            projects = pd.read_csv("lejuan_snapshot.csv", dtype={'project_no': str})
        except FileNotFoundError:
            logging.error("未找到 lejuan_snapshot.csv")
            return

        for project_no in projects['project_no'].unique():
            if not project_no or project_no == 'nan':
                continue
            
            # 断点续传逻辑
            if project_no in self.crawled_projects:
                logging.debug(f"项目 {project_no} 已存在统计数据，跳过。")
                continue
                
            payload = {"pid": str(project_no)}
            yield scrapy.Request(
                url=self.api_url,
                method='POST',
                body=json.dumps(payload),
                headers=self.headers,
                callback=self.parse,
                meta={'project_no': project_no}
            )

    def parse(self, response):
        project_no = response.meta.get('project_no')
        try:
            json_data = response.json()
            if json_data.get("code") == 0:
                data = json_data.get("data", {})
                
                item = DonationItem()
                item['project_no'] = project_no
                item['collection_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                item['server'] = socket.gethostname()
                
                # 填充统计字段
                for field in data.keys():
                    if field in item.fields:
                        item[field] = data.get(field)
                
                # 保存进度：成功解析并 yield 后再记录
                save_crawled_project(project_no, CRAWLED_DONATION_FILE)
                
                yield item
            else:
                logging.warning(f"项目 {project_no} 接口返回 code 非 0")
                
        except json.JSONDecodeError:
            logging.error(f"项目 {project_no} 响应 JSON 解析失败")