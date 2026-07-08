#!/bin/bash
set -e

echo "=== MoneyTree 一键部署 ==="
echo ""

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到 python3，请先安装 Python 3.9+"
    exit 1
fi

PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python 版本: $PY_VERSION"

# 检查 MySQL
if ! command -v mysql &> /dev/null; then
    echo "错误：未找到 mysql 命令，请先安装 MySQL"
    exit 1
fi
echo "MySQL: 已安装"

# 安装 Python 依赖
echo ""
echo ">>> 安装 Python 依赖..."
pip3 install -r requirements.txt -q

# 配置环境变量
if [ ! -f .env ]; then
    echo ""
    echo ">>> 配置环境变量..."
    cp .env.example .env
    echo ""
    echo "请填写 LLM 配置（OpenAI 兼容接口）："
    read -p "  API_KEY: " api_key
    read -p "  BASE_URL (如 https://api.openai.com/v1): " base_url
    read -p "  MODEL_ID (默认 claude-sonnet-4-6): " model_id
    model_id=${model_id:-claude-sonnet-4-6}

    echo ""
    echo "MySQL 配置（回车使用默认值）："
    read -p "  MYSQL_HOST (默认 localhost): " mysql_host
    mysql_host=${mysql_host:-localhost}
    read -p "  MYSQL_PORT (默认 3306): " mysql_port
    mysql_port=${mysql_port:-3306}
    read -p "  MYSQL_USER (默认 root): " mysql_user
    mysql_user=${mysql_user:-root}
    read -p "  MYSQL_PASSWORD (默认为空): " mysql_password
    read -p "  MYSQL_DB (默认 moneytree): " mysql_db
    mysql_db=${mysql_db:-moneytree}

    cat > .env << EOF
API_KEY=$api_key
BASE_URL=$base_url
MODEL_ID=$model_id

MYSQL_HOST=$mysql_host
MYSQL_PORT=$mysql_port
MYSQL_USER=$mysql_user
MYSQL_PASSWORD=$mysql_password
MYSQL_DB=$mysql_db
EOF
    echo "  .env 已生成"
else
    echo ""
    echo ">>> .env 已存在，跳过配置"
    mysql_user=$(grep MYSQL_USER .env | cut -d= -f2)
    mysql_password=$(grep MYSQL_PASSWORD .env | cut -d= -f2)
    mysql_db=$(grep MYSQL_DB .env | cut -d= -f2)
    mysql_user=${mysql_user:-root}
    mysql_db=${mysql_db:-moneytree}
fi

# 初始化数据库
echo ""
echo ">>> 初始化数据库..."
if [ -z "$mysql_password" ]; then
    mysql -u "$mysql_user" < schema.sql 2>/dev/null && echo "  数据库初始化完成" || echo "  数据库已存在，跳过"
else
    mysql -u "$mysql_user" -p"$mysql_password" < schema.sql 2>/dev/null && echo "  数据库初始化完成" || echo "  数据库已存在，跳过"
fi

# 下载前端依赖
echo ""
echo ">>> 下载前端 JS 库..."
if [ ! -f frontend/js/markdown-it.min.js ]; then
    curl -sL "https://cdn.jsdelivr.net/npm/markdown-it@14.0.0/dist/markdown-it.min.js" -o frontend/js/markdown-it.min.js
    echo "  markdown-it.min.js 下载完成"
else
    echo "  markdown-it.min.js 已存在"
fi

if [ ! -f frontend/js/mermaid.min.js ]; then
    curl -sL "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js" -o frontend/js/mermaid.min.js
    echo "  mermaid.min.js 下载完成"
else
    echo "  mermaid.min.js 已存在"
fi

# 启动
echo ""
echo "==========================="
echo "部署完成！启动服务..."
echo "访问地址: http://localhost:8000"
echo "==========================="
echo ""
python3 run.py
