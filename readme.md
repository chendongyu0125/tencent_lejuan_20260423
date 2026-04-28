
# 腾讯公益数据爬取项目

## 单次爬取命令

- **爬取项目列表简介**：`scrapy crawl lejuansnapshots -o lejuan_snapshot.csv`
- **爬取项目详细信息**：`scrapy crawl lejuandetails -o lejuan_details.jsonl`
- **爬取项目资助统计**：`scrapy crawl lejuandonations -o lejuan_donations.csv`
- **爬取项目更新进展**：`scrapy crawl lejuanupdates -o lejuan_updates.jsonl`

## 定时任务设置 (Crontab)

本项目支持通过 `crontab` 实现月度自动化爬取。

1. 在终端输入 `crontab -e`。
2. 将以下脚本配置添加到文件末尾（每月 1 号凌晨 2 点运行）：

```cron
0 2 1 * * /Users/chendongyu/tencent_lejuan_20260324/run_monthly_crawl.sh >> /Users/chendongyu/tencent_lejuan_20260324/cron_log.log 2>&1




