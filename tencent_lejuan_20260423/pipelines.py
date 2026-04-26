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

class SnapshotImagesPipeline(ImagesPipeline):
    '''
    download snapshot images, and save them in the folder of "images"
    '''
    def get_media_requests(self, item, info):
        project_no = item.get("project_no")[0] # project_no is a list, we need to get the first element

        for image_url in item.get('image_urls', []):
            yield(
                Request(image_url, meta = {'project_no': project_no})
            )

    def file_path(self, request, response = None, info = None, *, item = None):
        project_no = str(request.meta['project_no'])

        # to get the extension of the image file
        image_extension = request.url.split('.')[-1]
        
        # construct the image file path, we save the image in the folder of "images/cover_images", and we use the last two digits of the project_no as the subfolder name, and we use the project_no as the image file name, and we use the original image extension as the image file extension       
        image_path = f"cover_images/{project_no[-2:]}/{project_no}/{project_no}.{image_extension}"
        return image_path
    

        
class DetailImagesPipeline(ImagesPipeline):
    '''
    download detail images, and save them in the folder of "images/details"
    '''
    def get_media_requests(self, item, info):
        project_no = item.get("project_no") # project_no is already a string, no need to get the first element

        for image_url in item.get('image_urls', []):
            yield(
                Request(image_url, meta = {'project_no': project_no})
            )

    def file_path(self, request, response = None, info = None, *, item = None):
        project_no = str(request.meta['project_no'])

        # get the image file name
        if request.url.endswith('/500'):            
            image_file_name = f"{request.url.split('/')[-2]}.png"
        else:            
            image_file_name = request.url.split('/')[-1]


        image_path = f"details/{project_no[-2:]}/{project_no}/{image_file_name}"
        return image_path



class TencentLejuan20260423Pipeline:
    def process_item(self, item, spider):
        return item
