import logging
logging.basicConfig(level=logging.DEBUG)
import scrapy
from scrapy.http import FormRequest
import json
from tencent_lejuan_20260423.items import SnapshotItem 
from scrapy.loader import ItemLoader
import socket
from datetime import datetime
import math
import time
import image

class LejuanSpider(scrapy.Spider):
    '''
    To crawl the snapshot lsting of projects
    '''
    
    name = "lejuan"
    allowed_domains = ["gongyi.qq.com"]
    categories = [71, 72, 73, 74, 75, 900]
    project_first_codes = ['PM0101', 'PM0102', 'PM0103', 'PM0104', 'PM0105','PM0106']
    api_url = "https://ssl.gongyi.qq.com/gygw-app/ed/project_es_search_pc/ProjectSearchByClass"
    # start_urls = ["https://gongyi.qq.com/succor/project_list.htm#s_tid={s_tid}" for s_tid in (categories)]
    # Start with a login request
    headers = {
            "Content-Type": "application/json",
            # 加上 Referer 和 User-Agent 可以模拟浏览器行为，防止被简单的反爬机制拦截
            "Referer": "https://gongyi.qq.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def generate_payload(self, project_first_code, page=0):
            '''
            Generate payload post parameters which will be used for the url request. 
            return: payload
            '''
            
            payload = {"cate_id":71, 
                "key_word":  "null", 
                "keyword": "null", 
                "p":"null", 
                "page":page, 
                "page_size": 5,
                "project_first_code":project_first_code, 
                "s_fid": "null",
                "s_key":"null",
                "s_puin":"null",
                "s_status":1,
                "s_tid":71
                }
            return payload
    

    def start_requests(self):

        
        # 2. 设置请求头，告诉服务器我们发送的是 JSON 数据


        # 3. 发送 POST 请求
        # 注意：使用 body=json.dumps(payload) 将字典转换为 JSON 字符串
        for project_first_code in self.project_first_codes:
            payload = self.generate_payload(project_first_code, page=0)

            yield scrapy.Request(
                url=self.api_url,
                method='POST',
                headers=self.headers,
                body=json.dumps(payload),
                callback=self.parse,
                meta={"payload":payload}
            )

    def parse(self, response):

        # 调试：打印状态码，确保是 200
        logging.debug(f"Response Status: {response.status}")



        try:
        # 4. 解析 JSON 数据
        # response.json() 是 Scrapy 2.6+ 的新特性，可以直接将响应体转为字典
        # 如果你的 Scrapy 版本较低，请使用 json.loads(response.text)
            df = response.json()
            page = response.meta['payload']['page'] # 当前访问的是第几页
            project_first_code = response.meta['payload']['project_first_code']
            total_num = df.get("data").get("total_num")
            
            
            logging.debug(f"total_num={total_num}")
            logging.debug(f"current_pag = {page}" )

            

            project_list = df.get("data").get("proj_list")
            logging.debug(f"item_num = {len(project_list)}")
            position = 0
            for project in project_list:
                 
                # addr
                addr = project.get('addr')
                # city_name = project.get('addr').get('city_name')
                # province_name=project.get('addr').get('province_name')

                # donate
                donate = project.get('donate')                
                # current_donate_amount = project.get('donate').get('current_donate_amount')
                # current_donate_count = project.get('donate').get('current_donate_count')
                # donate_type = project.get('donate').get('donate_type')
                # start_time=project.get('donate').get('start_time')
                # state = project.get('donate').get('state')
                # target = project.get('donate').get('target')

                # info
                info = project.get('info')
                # donate_id = info.get('donate_id')
                # exe_org_name = info.get('exe_org_name')
                # exe_org_no =info.get('exe_org_no')
                # object_second_code_name = info.get('object_second_code_name')
                # org_name = info.get('org_name')
                # org_no = info.get('org_no')
                # phone_list_image=info.get('phone_list_image')
                # project_first_code_name=info.get('project_first_code_name')
                # project_intro = info.get('project_intro')
                # project_name=info.get('project_name')
                # project_no = info.get('project_no')
                # project_second_code_name = info.get('project_second_code_name')
                # type =info.get('type')
                # yqj_detail_address = info.get('yqj_detail_address')

                # load item
                item = SnapshotItem()
                l = ItemLoader(item=item)
                for field in addr.keys():
                    l.add_value(field, str(addr.get(field)))

                for field in donate.keys():
                    l.add_value(field, str(donate.get(field)))
                
                for field in info.keys():
                    l.add_value(field, str(info.get(field)))

                l.add_value('category', response.meta['payload']['project_first_code'])
                l.add_value('server', socket.gethostname())
                l.add_value('collection_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                l.add_value('page', str(response.meta['payload']['page']))
                l.add_value('position',str(position))
                position = position + 1

                # download snapshot image of each project
                image_url = info.get('phone_list_image')                
                project_no = str(info.get('project_no'))
                l.add_value('image_urls', [image_url])               

                yield l.load_item()
                
                
            # Crawl a new page of project listing 
            payload = response.meta['payload']
            page = response.meta['payload']['page'] # 当前访问的是第几页
            total_pages = math.ceil(total_num / 10) 
            if page < total_pages:
                page = page + 1 
                # if page == 3:
                #     return 
                payload['page'] = page
                yield scrapy.Request(
                    url=self.api_url,
                    method='POST',
                    headers=self.headers,
                    body=json.dumps(payload),
                    callback=self.parse,
                    meta={"payload":payload}
                )




                
                      
                


                 
            


        except json.JSONDecodeError:
            logging.error("响应内容不是有效的 JSON 格式")
            logging.error(f"响应内容预览: {response.text[:500]}")   