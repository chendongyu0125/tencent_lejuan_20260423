
单次爬取的命令如下：

* 爬取项目列表中的简介信息
scrapy crawl lejuansnapshots -o lejuan_snapshot.csv

* 爬取项目详细信息
scrapy crawl lejuandetails -o lejuan_details.jsonl

* 爬取项目的资助统计信息
scrapy crawl lejuandonations -o lejuan_donations.csv

* 爬取项目的更新信息
scrapy crawl lejuanupdates -o lejuan_updates.csv


也可以设置好脚本，定时爬取构建面板数据库

设置定时任务 (Crontab)
在 macOS 或 Linux 系统中，crontab 是最常用的定时工具。

在终端输入 crontab -e 进入编辑模式。

在文件末尾添加以下一行（假设你想在每月 1 号的凌晨 2 点执行）：

代码段
0 2 1 * * /Users/chendongyu/tencent_lejuan_20260324/run_monthly_crawl.sh >> /Users/chendongyu/tencent_lejuan_20260324/cron_log.log 2>&1
Cron 表达式说明：

0 2 1 * *：分别代表 分、时、日、月、周。1 表示每月 1 号。

>> ... 2>&1：将爬虫的运行日志保存到 cron_log.log 中，方便你检查是否执行成功。
说明：此处的路径为绝对路径，在不同的电脑上执行路径需要做相应修改。





