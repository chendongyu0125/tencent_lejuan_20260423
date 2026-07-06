#!/bin/bash

# ============================================================
# 腾讯乐捐数据 — 每周定时爬取脚本
# 运行时间：每周一 0:00（通过 crontab 调度）
# 每次全量重新爬取所有项目的最新数据
# ============================================================

# 1. 自动获取脚本文件所在的绝对路径
PROJECT_DIR=$(cd "$(dirname "$0")"; pwd)
cd "$PROJECT_DIR"

# 2. 打印当前路径确保正确
echo "当前项目根目录: $PROJECT_DIR"

# 3. 激活 conda 环境
source /Users/chendongyu/anaconda3/bin/activate base

# 4. 获取日期后缀
DATE_SUFFIX=$(date +%Y%m%d)

# 5. 清理旧的进度文件（每次全量重新爬取）
rm -f crawled_projects_with_snapshots.txt
rm -f crawled_projects_with_details.txt
rm -f crawled_donation_stats.txt

echo "开始每周定时爬取任务，日期后缀: $DATE_SUFFIX"

# 6. 按顺序执行爬虫（不包含项目更新进展 lejuanupdates）

echo "正在执行: lejuansnapshots（项目快照）..."
scrapy crawl lejuansnapshots -o "lejuan_snapshot_${DATE_SUFFIX}.csv"

echo "正在执行: lejuandetails（项目详情）..."
scrapy crawl lejuandetails -o "lejuan_details_${DATE_SUFFIX}.jsonl"

echo "正在执行: lejuandonations（捐赠统计）..."
scrapy crawl lejuandonations -o "lejuan_donations_${DATE_SUFFIX}.csv"

echo "所有爬取任务已完成。"
echo "输出文件："
echo "  - lejuan_snapshot_${DATE_SUFFIX}.csv"
echo "  - lejuan_details_${DATE_SUFFIX}.jsonl"
echo "  - lejuan_donations_${DATE_SUFFIX}.csv"
