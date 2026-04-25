import logging
logging.basicConfig(level=logging.DEBUG)
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request

class CustomImagesPipeline(ImagesPipeline):
    '''
    Customize image download, save the images according to their project_no
    '''
    def get_media_requests(self, item, info):
        project_no = item.get('project_no')[0]
        # print(f'project_no={project_no}')
        

        for image_url in item.get('image_urls', []):
            yield(
                Request(image_url, meta = {'project_no': project_no})
            )

    def file_path(self, request, response = None, info = None, *, item = None):
        project_no = str(request.meta['project_no'])

        # to get the extension of the image file
        image_extension = request.url.split('.')[-1]
        
        # construct the image file path
        if len(project_no) <=3:
            image_path = f"00/{project_no}/{project_no}.{image_extension}"
        else:
            image_path = f"{project_no[-2:]}/{project_no}/{project_no}.{image_extension}"

        return image_path


class TencentLejuan20260423Pipeline:
    def process_item(self, item, spider):
        return item
