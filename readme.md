
# 腾讯公益数据爬取项目

## 一键部署（新 Mac 机器）

在新 Mac 终端中运行以下命令即可完成全部部署：

```bash
bash <(curl -sSL https://gitee.com/chendongyu0125/tencent_lejuan_20260423/raw/main/deploy.sh)
```

或者从 GitHub：

```bash
bash <(curl -sSL https://raw.githubusercontent.com/chendongyu0125/tencent_lejuan_20260423/main/deploy.sh)
```

**部署脚本会自动完成：**
1. 检查网络和系统环境
2. 安装 Miniconda（如未安装）
3. 从 Gitee 克隆项目代码
4. 创建 conda 虚拟环境并安装 Python 依赖
5. 初始化项目数据文件
6. 配置每周一 0:00 的自动爬取定时任务
7. 验证部署是否成功

## 单次爬取命令

- **爬取项目列表简介**：`scrapy crawl lejuansnapshots -o lejuan_snapshot.csv`
- **爬取项目详细信息**：`scrapy crawl lejuandetails -o lejuan_details.jsonl`
- **爬取项目资助统计**：`scrapy crawl lejuandonations -o lejuan_donations.csv`
- **爬取项目更新进展**：`scrapy crawl lejuanupdates -o lejuan_updates.jsonl`

## 定时任务设置 (Crontab)

本项目支持通过 `crontab` 实现**每周一凌晨 0 点**自动全量爬取（不含项目更新进展和图片下载）。

1. 在终端输入 `crontab -e`。
2. 将以下配置添加到文件末尾：

```cron
0 0 * * 1 /Users/chendongyu/Claude/tencent_lejuan_20260423/run_weekly_crawl.sh >> /Users/chendongyu/Claude/tencent_lejuan_20260423/cron_log.log 2>&1
```

### 定时任务说明

- **运行频率**：每周一凌晨 0:00
- **爬取策略**：每次全量重新爬取（删除进度文件，获取所有项目最新数据）
- **执行顺序**：项目快照 → 项目详情 → 捐赠统计
- **输出文件**：以日期后缀命名，如 `lejuan_snapshot_20260706.csv`
- **日志文件**：`cron_log.log`
- **注意事项**：
  - 项目更新进展（lejuanupdates）不在定时任务中执行，如需可手动运行
  - 图片/视频数据不再下载，仅保留项目和捐赠的结构化数据
