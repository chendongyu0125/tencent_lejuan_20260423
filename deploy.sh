#!/bin/bash
# ============================================================
# 腾讯乐捐数据爬虫 — 一键部署脚本
# 用法: bash deploy.sh
# 适用: macOS (Apple Silicon / Intel)
# ============================================================

set -e

# ---- 配置（可按需修改）----
GITEE_REPO="https://gitee.com/chendongyu0125/tencent_lejuan_20260423.git"
PROJECT_DIR="$HOME/tencent_lejuan_20260423"
CONDA_ENV_NAME="lejuan"
PYTHON_VER="3.12"
CRON_SCHEDULE="0 0 * * 1"  # 每周一凌晨 0:00

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step()  { echo -e "\n${GREEN}[步骤 $1/$TOTAL_STEPS]${NC} $2"; }
print_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
print_warn()  { echo -e "${YELLOW}[警告]${NC} $1"; }
print_err()   { echo -e "${RED}[错误]${NC} $1"; }
TOTAL_STEPS=7

# -----------------------------------------------------------
# 步骤 1：检查基础环境
# -----------------------------------------------------------
step=1
print_step $step "检查基础环境"

# 检测架构
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
else
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
fi
print_ok "CPU 架构: $ARCH"

# 检查网络
if curl -s --connect-timeout 5 https://gitee.com > /dev/null 2>&1; then
    print_ok "网络正常，可访问 Gitee"
else
    print_err "无法访问 Gitee，请检查网络连接"
    exit 1
fi

# -----------------------------------------------------------
# 步骤 2：安装 Miniconda（如果未安装）
# -----------------------------------------------------------
step=$((step + 1))
print_step $step "检查/安装 Miniconda"

CONDA_PATH=""
for candidate in \
    "$HOME/miniconda3" \
    "$HOME/anaconda3" \
    "/opt/miniconda3" \
    "/opt/anaconda3" \
    "/usr/local/anaconda3"; do
    if [ -f "$candidate/bin/conda" ]; then
        CONDA_PATH="$candidate"
        break
    fi
done

if [ -n "$CONDA_PATH" ]; then
    print_ok "已安装 conda: $CONDA_PATH"
else
    echo "未找到 conda，开始安装 Miniconda..."
    INSTALLER="/tmp/miniconda_installer.sh"
    curl -L -o "$INSTALLER" "$MINICONDA_URL"
    bash "$INSTALLER" -b -p "$HOME/miniconda3"
    rm -f "$INSTALLER"
    CONDA_PATH="$HOME/miniconda3"
    print_ok "Miniconda 安装完成: $CONDA_PATH"
fi

# 初始化 conda（使当前 shell 可用）
source "$CONDA_PATH/bin/activate" 2>/dev/null || true

# -----------------------------------------------------------
# 步骤 3：克隆/更新项目代码
# -----------------------------------------------------------
step=$((step + 1))
print_step $step "克隆/更新项目代码"

if [ -d "$PROJECT_DIR/.git" ]; then
    echo "项目目录已存在，拉取最新代码..."
    cd "$PROJECT_DIR"
    git pull origin main 2>&1 || print_warn "拉取失败，可能有本地修改，继续使用当前版本"
    print_ok "代码已更新"
else
    echo "克隆项目到: $PROJECT_DIR"
    if [ -d "$PROJECT_DIR" ]; then
        print_warn "$PROJECT_DIR 已存在但不是 git 仓库，备份为 ${PROJECT_DIR}_backup"
        mv "$PROJECT_DIR" "${PROJECT_DIR}_backup_$(date +%Y%m%d%H%M%S)"
    fi
    git clone "$GITEE_REPO" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    print_ok "代码已克隆"
fi

# -----------------------------------------------------------
# 步骤 4：创建 conda 环境并安装依赖
# -----------------------------------------------------------
step=$((step + 1))
print_step $step "创建 conda 环境并安装依赖"

# 检查环境是否已存在
if $CONDA_PATH/bin/conda env list 2>/dev/null | grep -q "^${CONDA_ENV_NAME} "; then
    echo "conda 环境 '${CONDA_ENV_NAME}' 已存在，跳过创建"
else
    $CONDA_PATH/bin/conda create -n "$CONDA_ENV_NAME" python="$PYTHON_VER" -y
    print_ok "conda 环境 '${CONDA_ENV_NAME}' 创建完成"
fi

# 安装 pip 依赖
source "$CONDA_PATH/bin/activate" "$CONDA_ENV_NAME" 2>/dev/null || \
    source "$CONDA_PATH/bin/activate" "$CONDA_ENV_NAME"

if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    pip install -r "$PROJECT_DIR/requirements.txt" -q
    print_ok "Python 依赖安装完成"
else
    print_err "未找到 requirements.txt"
    exit 1
fi

# 验证 scrapy
if python -c "import scrapy" 2>/dev/null; then
    print_ok "scrapy 可用: $(python -c 'import scrapy; print(scrapy.__version__)')"
else
    print_err "scrapy 安装失败"
    exit 1
fi

# -----------------------------------------------------------
# 步骤 5：初始化项目数据文件
# -----------------------------------------------------------
step=$((step + 1))
print_step $step "初始化项目数据文件"

cd "$PROJECT_DIR"

# 检查 project_nos.dat 是否存在
if [ -f "project_nos.dat" ] && [ -s "project_nos.dat" ]; then
    print_ok "project_nos.dat 已存在，跳过生成"
else
    # 检查是否有 snapshot CSV 文件
    SNAPSHOT_FILE=$(ls lejuan_snapshot*.csv 2>/dev/null | head -1)
    if [ -n "$SNAPSHOT_FILE" ]; then
        echo "从 $SNAPSHOT_FILE 生成 project_nos.dat ..."
        python -c "
from tencent_lejuan_20260423.tools import generate_project_no_file
from tencent_lejuan_20260423 import settings
generate_project_no_file('$SNAPSHOT_FILE', settings.PROJECT_NO_FILE)
"
        print_ok "project_nos.dat 生成完成"
    else
        print_warn "无 snapshot CSV 文件，project_nos.dat 将在首次运行快照爬虫后自动生成"
        print_warn "请先手动运行: scrapy crawl lejuansnapshots -o lejuan_snapshot.csv"
    fi
fi

# -----------------------------------------------------------
# 步骤 6：配置 crontab 定时任务
# -----------------------------------------------------------
step=$((step + 1))
print_step $step "配置每周定时任务"

CRON_CMD="$CRON_SCHEDULE cd $PROJECT_DIR && bash run_weekly_crawl.sh >> $PROJECT_DIR/cron_log.log 2>&1"
CRON_MARKER="# tencent-lejuan-weekly-crawl"

# 检查 crontab 中是否已有我们的任务
if crontab -l 2>/dev/null | grep -qF "$CRON_MARKER"; then
    print_ok "定时任务已配置，跳过"
else
    # 追加到 crontab（保留原有内容）
    (
        crontab -l 2>/dev/null || true
        echo ""
        echo "$CRON_MARKER"
        echo "$CRON_CMD"
    ) | crontab -
    print_ok "定时任务已添加: 每周一 0:00 自动运行"
fi

echo -e "\n当前 crontab 中与本项目相关的任务:"
crontab -l 2>/dev/null | grep -A1 "$CRON_MARKER" || true

# -----------------------------------------------------------
# 步骤 7：验证部署
# -----------------------------------------------------------
step=$((step + 1))
print_step $step "部署验证"

echo "项目目录:   $PROJECT_DIR"
echo "conda 路径: $CONDA_PATH"
echo "conda 环境: $CONDA_ENV_NAME"
echo "Python:     $(python --version 2>&1)"
echo "scrapy:     $(scrapy version 2>&1)"

# 测试爬虫能否正常启动（只检查不实际运行）
if scrapy check 2>&1 | tail -5; then
    print_ok "爬虫配置正确"
else
    print_warn "爬虫 check 有告警，可能不影响使用"
fi

# -----------------------------------------------------------
# 完成
# -----------------------------------------------------------
echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo "常用命令："
echo "  手动运行全部爬虫:   cd $PROJECT_DIR && bash run_weekly_crawl.sh"
echo "  单独运行快照爬虫:   cd $PROJECT_DIR && scrapy crawl lejuansnapshots -o snapshot.csv"
echo "  查看定时任务:       crontab -l"
echo "  查看运行日志:       tail -f $PROJECT_DIR/cron_log.log"
echo "  激活 conda 环境:    source $CONDA_PATH/bin/activate $CONDA_ENV_NAME"
echo ""
echo "定时任务: 每周一凌晨 0:00 自动运行（已配置）"
echo ""
