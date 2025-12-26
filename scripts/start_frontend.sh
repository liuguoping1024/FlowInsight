#!/bin/bash
# 启动前端服务脚本

cd "$(dirname "$0")/../frontend"

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3"
    exit 1
fi

# 启动HTTP服务器（HTML端口：8888）
echo "启动前端服务（HTML端口：8888）..."
echo "访问地址: http://$(hostname -I | awk '{print $1}'):8888"
echo "或访问: http://localhost:8888"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python3 -m http.server 8888

