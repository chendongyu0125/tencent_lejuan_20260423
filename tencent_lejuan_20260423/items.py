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

class ProjectItem(Item):
    
    # system info
    category = Field()
    project_no = Field()
    collection_time = Field()
    server = Field()


    # download snapshot image
    image_urls = Field()
    images = Field()

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

    # download snapshot image
    image_urls = Field()
    images = Field()
