
# scrapy crawl lejuanupdates -o updates_data.csv

# import scrapy


# class LejuanupdatesSpider(scrapy.Spider):
#     name = "lejuanupdates"
#     allowed_domains = ["qq.com"]
#     start_urls = ["https://qq.com"]

#     def parse(self, response):
#         pass


import scrapy
import json
import pandas as pd
import logging
import socket
import re
from datetime import datetime
from tencent_lejuan_20260423.items import UpdateItem
from tencent_lejuan_20260423.tools import fix_url_scheme
from tencent_lejuan_20260423.tools import load_crawled_projects
from tencent_lejuan_20260423.settings import CRAWLED_UPDATES_FILE
import settings

class LejuanupdatesSpider(scrapy.Spider):
    name = "lejuanupdates"
    allowed_domains = ["gongyi.qq.com", "qq.com"]
    api_url = "https://ssl.gongyi.qq.com/gygw-app/ed/project_data_agg/GetProjectProcessList"
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'tencent_lejuan_20260423.pipelines.UpdateImagesPipeline': 300,
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Referer": "https://gongyi.qq.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    def __init__(self, name=None, **kwargs):
            super().__init__(name, **kwargs)
            # 启动时加载进度
            self.crawled_projects = load_crawled_projects(CRAWLED_UPDATES_FILE)
            logging.info(f"Loaded {len(self.crawled_projects)} crawled updates from {CRAWLED_UPDATES_FILE}")
            try:
                self.project_nos = set(pd.read_csv(settings.PROJECT_NO_FILE, header=None, dtype=str)[0].dropna().unique())
                logging.info(f"已加载 {len(self.project_nos)} 个需要爬取的项目编号")
            except FileNotFoundError:
                logging.error("未找到 project_nos.dat 文件，请先运行 generate_project_no_file 函数生成该文件")
                self.project_nos = set()

    def start_requests(self):

        for project_no in self.project_nos:
            if not project_no or project_no == 'nan':
                continue

            # 断点续传：如果项目编号已在记录文件中，则跳过
            if project_no in self.crawled_projects:
                logging.info(f"Project {project_no} updates already crawled. Skipping.")
                continue
            
            # 初始请求第一页
            yield self.generate_request(project_no, page=1)

    def generate_request(self, project_no, page):
        payload = {
            "project_no": str(project_no),
            "page": page,
            "size": 10
        }
        return scrapy.Request(
            url=self.api_url,
            method='POST',
            body=json.dumps(payload),
            headers=self.headers,
            callback=self.parse,
            meta={'project_no': project_no, 'page': page}
        )

    def parse(self, response):
        project_no = response.meta.get('project_no')
        current_page = response.meta.get('page')
        
        try:
            json_data = response.json()
            if json_data.get("code") != 0:
                return

            data = json_data.get("data", {})
            process_list = data.get("list", [])
            total_count = data.get("total", 0)

            for entry in process_list:
                # 1. 提取进展主数据
                p = entry.get("process", {})
                # 2. 提取互动数据
                like_data = entry.get("process_like", {})
                
                item = UpdateItem()
                
                # --- 基础字段赋值 ---
                item['project_no'] = project_no
                item['process_id'] = p.get('process_id')
                item['content_title'] = p.get('content_title')
                item['content'] = p.get('content')
                item['desc'] = p.get('desc')
                item['publish_time'] = p.get('publish_time')
                item['org_name'] = p.get('org_name')
                item['org_no'] = p.get('org_no')
                item['type'] = p.get('type')
                
                # --- 结构化/动态表单字段 ---
                item['template_id'] = p.get('template_id')
                item['template_form_id'] = p.get('template_form_id')
                item['template_form_data'] = p.get('template_form_data')
                # concrete 字段可能存在于 entry 外层或 process 内层，此处取外层
                item['concrete'] = json.dumps(entry.get('concrete', {})) 
                
                # --- 互动字段 ---
                item['likes'] = like_data.get('likes', 0)
                item['treads'] = like_data.get('treads', 0)
                
                # --- 系统字段 ---
                item['collection_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                item['server'] = socket.gethostname()

                # --- 图片 URL 深度提取 ---
                image_urls = set()
                
                # A. 提取 image_list 字段
                raw_img_list = p.get('image_list', [])
                item['image_list'] = raw_img_list
                for img in raw_img_list:
                    image_urls.add(fix_url_scheme(img))

                # B. 从 content (HTML) 中正则提取详情图
                content_html = p.get('content', '')
                if content_html:
                    # 匹配 src 属性
                    img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
                    found_urls = img_pattern.findall(content_html)
                    for url in found_urls:
                        image_urls.add(fix_url_scheme(url))

                item['image_urls'] = [u for u in image_urls if u]
                
                yield item

            # 自动翻页逻辑
            if current_page * 10 < total_count:
                yield self.generate_request(project_no, page=current_page + 1)

        except Exception as e:
            logging.error(f"Error parsing updates for project {project_no}: {str(e)}")