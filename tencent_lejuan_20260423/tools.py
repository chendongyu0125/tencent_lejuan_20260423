
import logging
logging.basicConfig(level=logging.INFO)

import os 

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


# added: 补全URL协议的工具函数
def fix_url_scheme(url):
    if not url:
        return None 
    
    if url.startswith('//'):
        return 'https:' + url
    elif not url.startswith(('http://', 'https://')):
        return 'https://' + url
    
    return url

def extract_element_from_list(value):
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    return value