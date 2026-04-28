#!/bin/bash

# 1. 自动获取脚本文件所在的绝对路径
# 无论你在哪里调用这个脚本，$PROJECT_DIR 都会指向脚本所在的目录
PROJECT_DIR=$(cd "$(dirname "$0")"; pwd)
cd "$PROJECT_DIR"

# 2. 打印当前路径确保正确 (调试用)
echo "当前项目根目录: $PROJECT_DIR"

# 3. 激活环境 (conda 最好还是用绝对路径，保证可靠)
source /Users/chendongyu/anaconda3/bin/activate base

# 4. 获取日期后缀
DATE_SUFFIX=$(date +%Y%m%d)

# 5. 清理旧的进度文件 (此时可以使用文件名，因为已经 cd 到了根目录)
rm -f crawled_projects_with_snapshots.txt
rm -f crawled_projects_with_details.txt
rm -f crawled_donation_stats.txt
rm -f crawled_project_updates.txt

echo "开始月度定时爬取任务，日期后缀: $DATE_SUFFIX"

# 3. 按顺序执行爬虫
# 注意：文件名使用了变量 $DATE_SUFFIX

echo "正在执行: lejuansnapshots..."
scrapy crawl lejuansnapshots -o "lejuan_snapshot_${DATE_SUFFIX}.csv"

echo "正在执行: lejuandetails..."
scrapy crawl lejuandetails -o "lejuan_details_${DATE_SUFFIX}.jsonl"

echo "正在执行: lejuandonations..."
scrapy crawl lejuandonations -o "lejuan_donations_${DATE_SUFFIX}.csv"

echo "正在执行: lejuanupdates..."
scrapy crawl lejuanupdates -o "lejuan_updates_${DATE_SUFFIX}.csv"

echo "所有爬取任务已完成。"
# (后续命令保持不变)