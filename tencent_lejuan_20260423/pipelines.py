import logging
logging.basicConfig(level=logging.INFO)
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request

from tencent_lejuan_20260423.tools import save_crawled_project
from tencent_lejuan_20260423.settings import CRAWLED_PROJECTS_FILE, CRAWLED_SNAPSHOTS_FILE

import os
from urllib.parse import urlparse  # 必须添加这一行

class ImageDownloadPipeline(ImagesPipeline):
    def _clean_project_no(self, item):
        project_no = item.get("project_no")
        if isinstance(project_no, (list, tuple)):
            project_no = project_no[0] if project_no else "unknown"
        return str(project_no) if project_no else "unknown"

    def get_media_requests(self, item, info):
        project_no = self._clean_project_no(item)
        
        for image_url in item.get('image_urls', []):
            if image_url.startswith('data:'):
                continue

            # 处理 // 开头的协议自适应 URL
            if image_url and image_url.startswith('//'):
                image_url = 'https:' + image_url
                
            if not image_url or not image_url.startswith(('http://', 'https://')):
                logging.warning(f"Project {project_no} has invalid URL: {image_url}")
                continue
                
            yield Request(image_url, 
                          meta={'project_no': project_no},
                          headers={'Referer': 'https://gongyi.qq.com/'} # 添加 Referer 绕过 CDN 防盗链
                    )
            

    def file_path(self, request, response=None, info=None, *, item=None):
        project_no = request.meta.get('project_no', 'unknown')
        
        # 使用 urlparse 清除查询参数
        path = urlparse(request.url).path
        if path.endswith('/'):
            path = path[:-1]
        
        base_name = os.path.basename(path)
        
        # 处理特殊结尾如 /500
        if path.endswith('/500'):
            base_name = f"{path.split('/')[-2]}.png"
        
        # 确保目录分级安全 (取最后两位)
        prefix = project_no[-2:] if len(project_no) >= 2 else "00"
        return f"{prefix}/{project_no}/{base_name}"

    def item_completed(self, results, item, info):
        
        success_results = [x for ok, x in results if ok]
        # 失败的列表 (包含具体的 Failure 错误信息)
        failed_results = [x for ok, x in results if not ok]
        project_no = self._clean_project_no(item)

        if not success_results:
            # 如果有失败记录，打印更具体的错误
            if failed_results:
                logging.error(f"Project {project_no}: All {len(failed_results)} images failed. Errors: {failed_results}")
            else:
                logging.warning(f"Project {project_no}: No image URLs found to download.")
        else:
            logging.info(f"Project {project_no}: {len(success_results)} images downloaded, {len(failed_results)} failed.")
            
            # 将下载成功的本地路径保存到 item 中，方便后续存储
            item['image_paths'] = [x['path'] for x in success_results]
            item['failed_images_count'] = len(failed_results)

        
        return item

class SnapshotImagesPipeline(ImageDownloadPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        path = super().file_path(request, response, info, item=item)
        return f"cover_images/{path}"

    def item_completed(self, results, item, info):
        # 先执行父类逻辑
        item = super().item_completed(results, item, info)
        
        # 只有在有成功结果时才保存标记
        success_results = [x for x in results if x[0]]
        if success_results:
            project_no = self._clean_project_no(item)
            save_crawled_project(project_no, CRAWLED_SNAPSHOTS_FILE)
            
        return item

class DetailImagesPipeline(ImageDownloadPipeline):
    '''
    下载详情图，并保存在 "details/" 目录下
    '''

    def file_path(self, request, response=None, info=None, *, item=None):
        # 调用父类逻辑生成基础路径 (例如: 01/project123/image.jpg)
        image_path = super().file_path(request, response, info, item=item)
        # 拼接详情图专用的前缀
        full_path = f"details/{image_path}"
        logging.debug(f"Saving detail image to {full_path}")
        return full_path
    
    def item_completed(self, results, item, info):
        # 1. 调用父类方法完成基础的日志记录（不建议在父类直接写数据库/文件，父类只负责通用逻辑）
        item = super().item_completed(results, item, info)
        
        # 2. 只有当确实有图片下载成功时，才执行保存标记的操作
        success_results = [x for x in results if x[0]]
        
        if success_results:
            # 使用统一的清洗逻辑获取 project_no
            project_no = self._clean_project_no(item)
            
            # 只有下载成功才记录到已爬取详情的项目文件中
            save_crawled_project(project_no, CRAWLED_PROJECTS_FILE)
            logging.info(f"Project {project_no} marked as completed in {CRAWLED_PROJECTS_FILE}")
            
        return item


class UpdateImagesPipeline(ImageDownloadPipeline):
    '''
    专门处理项目进展图片的下载与存储
    '''
    def file_path(self, request, response=None, info=None, *, item=None):
        # 调用父类生成基础路径 (例如: 26/34553/filename.jpg)
        base_path = super().file_path(request, response, info, item=item)
        # 强制添加 updates 前缀，最终路径为 images/updates/26/34553/...
        full_path = f"updates/{base_path}"
        return full_path

    def item_completed(self, results, item, info):
        # 执行父类基础逻辑 (如日志打印)
        item = super().item_completed(results, item, info)
        
        # 检查是否有图片下载成功
        success_results = [x for x in results if x[0]]
        
        if success_results:
            # 使用统一清洗逻辑获取项目编号
            project_no = self._clean_project_no(item)
            
            # 记录到项目进展进度文件中
            from tencent_lejuan_20260423.settings import CRAWLED_UPDATES_FILE
            save_crawled_project(project_no, CRAWLED_UPDATES_FILE)
            logging.info(f"Project {project_no} updates images marked as completed.")
            
        return item

class TencentLejuan20260423Pipeline:
    def process_item(self, item, spider):
        return item
