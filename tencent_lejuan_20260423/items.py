# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class TencentLejuan20260423Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class DonationItem(scrapy.Item):
    # 系统与关联信息
    project_no = scrapy.Field()       # 项目编号 (pid)
    collection_time = scrapy.Field()  # 采集时间
    server = scrapy.Field()           # 服务器名

    # 捐赠统计数据 (对应接口返回的 data 字段)
    sum_money = scrapy.Field()        # 累计筹款金额 (单位：分)
    sum_times = scrapy.Field()        # 累计捐赠人次
    month_money = scrapy.Field()      # 本月筹款金额
    month_times = scrapy.Field()      # 本月捐赠人次
    together_money = scrapy.Field()   # 组队筹款金额
    together_times = scrapy.Field()   # 组队捐赠人次
    sub_money = scrapy.Field()        # 支款金额
    sub_times = scrapy.Field()        # 支款次数
    project_cnt = scrapy.Field()      # 相关项目数


class ProjectItem(Item):

    # 项目详细信息
    category = Field()
    project_no = Field()
    collection_time = Field()
    server = Field()

    # details
    base = Field()
    detail = Field()
    filing_budget = Field()
    tmjh =Field()
    v3_budget = Field()
    v3_detail = Field()
    v3_donate = Field()
    v3_exec = Field()
    v3_info = Field()
    v3_love_story = Field()








class SnapshotItem(Item):
     # addr
    city_name = Field()
    province_name=Field()

    # donate
    current_donate_amount = Field()
    current_donate_count = Field()
    donate_type = Field()
    start_time=Field()
    state = Field()
    target = Field()

    # info
    info = Field()
    donate_id = Field()
    exe_org_name = Field()
    exe_org_no = Field()
    object_second_code_name = Field()
    org_name = Field()
    org_no = Field()
    phone_list_image=Field()
    project_first_code_name=Field()
    project_intro = Field()
    project_name=Field()
    project_no = Field()
    project_second_code_name = Field()
    type =Field()
    yqj_detail_address = Field()

    # system info
    category = Field()
    collection_time = Field()
    server = Field()
    page = Field()
    position = Field()

class UpdateItem(scrapy.Item):
    # --- 系统与关联信息 ---
    project_no = scrapy.Field()       # 项目编号 (pid)
    process_id = scrapy.Field()       # 进展唯一ID
    collection_time = scrapy.Field()  # 采集时间
    server = scrapy.Field()           # 服务器名
    
    # --- 进展核心内容 ---
    content_title = scrapy.Field()    # 进展标题
    content = scrapy.Field()          # 进展正文 (包含 HTML 标签)
    desc = scrapy.Field()             # 进展简述/摘要
    publish_time = scrapy.Field()     # 发布时间
    org_name = scrapy.Field()         # 执行机构名称
    org_no = scrapy.Field()           # 执行机构编号
    type = scrapy.Field()             # 进展类型 (如 1 表示项目进展)
    
    # --- 动态表单与结构化数据 ---
    # 接口中 process 节点下的 template 相关字段
    template_id = scrapy.Field()      # 模板ID
    template_form_id = scrapy.Field() # 模板表单ID
    template_form_data = scrapy.Field() # 表单结构化数据 (JSON 字符串)
    concrete = scrapy.Field()         # 具体的业务结构化数据 (JSON 字符串)
    
    # --- 交互数据 (来自 process_like 节点) ---
    likes = scrapy.Field()            # 点赞数
    treads = scrapy.Field()           # 踩数 (反对数)

    # --- 媒体资源 ---
    image_list = scrapy.Field()       # 原始图片 URL 列表
    image_urls = scrapy.Field()       # 供 Scrapy 下载的图片 URL 列表 (去重后)
    images = scrapy.Field()           # Scrapy 下载结果信息
    
    image_paths = scrapy.Field()         # 下载成功的本地路径列表 (供后续存储使用)
    failed_images_count = scrapy.Field() # 下载失败的图片数量 (供后续存储使用)
