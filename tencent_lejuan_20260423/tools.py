
import logging
logging.basicConfig(level=logging.INFO)

import os 
import settings

# get all the detail information of projects
def load_crawled_projects(file_path):
    '''
    load the crawled project numbers from the file, and return a set of crawled project numbers
    '''

    logging.debug(f"Loading crawled projects from {file_path}...")

    if not os.path.exists(file_path):
        return set()
    
    with open(file_path, 'r') as f:
        crawled_projects = set(line.strip() for line in f)
    return crawled_projects

def save_crawled_project(project_no, file_path):
    '''
    save the crawled project number into the file
    '''
    crawled = load_crawled_projects(file_path)
    # logging.debug(f"project_no={project_no}, crowled={crawled}")
    if project_no in crawled:
        logging.info(f"Project {project_no} has already been crawled.")
        return  
    with open(file_path, 'a') as f:
        f.write(project_no + '\n')

# 生成一个文件，记录所有需要爬取的项目编号，供爬虫使用
def generate_project_no_file(snapshot_path, file_path):
    if not os.path.exists(snapshot_path):
        logging.error(f"Snapshot file {snapshot_path} does not exist.")
        return
    import pandas as pd
    df = pd.read_csv(snapshot_path, dtype={'project_no': str})
    project_nos = set(df['project_no'].dropna().unique())

    with open(file_path, 'w') as f:
        for project_no in project_nos:
            f.write(str(project_no) + '\n')

    
# tools.py 中的 fix_url_scheme 修改建议
def fix_url_scheme(url):
    if not url:
        return None 
    if url.startswith('//'):
        return 'https:' + url
    # 将 http 替换为 https 以减少重定向
    if url.startswith('http://'):
        return url.replace('http://', 'https://', 1)
    if not url.startswith('https://'):
        return 'https://' + url
    return url


def extract_element_from_list(value):
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    return value


if __name__ == "__main__":
    # 测试 fix_url_scheme 函数
    
    generate_project_no_file(settings.PROJECT_SNAPSHOT_DATAFILE, settings.PROJECT_NO_FILE)
    

