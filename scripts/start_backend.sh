#!/bin/bash
# 启动后端服务脚本

cd "$(dirname "$0")/../backend"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖是否安装
if ! python -c "import fastapi" 2>/dev/null; then
    echo "安装依赖..."
    pip install -r requirements.txt
fi

# 启动服务（API端口：8887）
echo "启动后端服务（API端口：8887）..."
python -m app.main

