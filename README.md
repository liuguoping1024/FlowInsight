# FlowInsight - 股票资金流向监控分析系统

## 项目简介

FlowInsight 是一个股票资金流向监控分析系统，核心功能包括：
- 监控A股市场所有股票的资金流入/流出情况
- 追踪大资本的资金流向和操作痕迹
- 帮助用户提前感知大资本选择或撤出哪些股票
- 多用户系统，支持个人持股管理和智能建议

## 技术栈

### 后端
- Python 3.9+
- FastAPI（异步Web框架）
- MariaDB 10.11+（数据库）
- Redis（缓存）
- Celery（定时任务）

### 前端
- 纯HTML + JavaScript（ES6+）
- ECharts（图表库）
- Axios（HTTP客户端）

## 端口配置

- **前端HTML服务**: 端口 **8888** （吉利！）
- **后端API服务**: 端口 **8887**

## 快速开始

### 1. 数据库设置

```bash
# 连接到MariaDB
mysql -u root -p -h 192.168.66.6

# 执行SQL脚本创建数据库和表
mysql -u root -p -h 192.168.66.6 < database/sql/01_core_tables.sql
```

### 2. 启动服务

#### 方法一：使用启动脚本（推荐）

```bash
# 启动后端（终端1）
./scripts/start_backend.sh

# 启动前端（终端2）
./scripts/start_frontend.sh
```

#### 方法二：手动启动

```bash
# 启动后端
cd backend
source venv/bin/activate
python -m app.main

# 启动前端（新终端）
cd frontend
python3 -m http.server 8888
```

### 3. 访问地址

- **前端页面**: http://your-server-ip:8888
- **后端API**: http://your-server-ip:8887
- **API文档**: http://your-server-ip:8887/docs

## IP地址配置说明

### 自动检测机制（推荐）

前端会自动检测当前访问的主机地址，**无需手动配置IP**：

- **本地开发**: 访问 `http://localhost:8888` → API自动使用 `http://localhost:8887`
- **局域网访问**: 访问 `http://192.168.66.6:8888` → API自动使用 `http://192.168.66.6:8887`
- **云服务器**: 访问 `http://your-domain.com:8888` → API自动使用 `http://your-domain.com:8887`

### 手动指定API地址（可选）

如果需要手动指定API地址（例如API和前端不在同一台服务器），可以在HTML的`<head>`中添加：

```html
<script>
    window.API_BASE_URL = 'http://your-api-server:8887/api/v1';
</script>
```

## 项目结构

```
FlowInsight.git/
├── backend/              # 后端代码
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据模型
│   │   ├── services/    # 业务逻辑
│   │   └── utils/       # 工具函数
│   ├── requirements.txt # Python依赖
│   └── main.py          # 应用入口
│
├── frontend/            # 前端代码
│   ├── assets/
│   │   ├── js/         # JavaScript文件
│   │   ├── css/        # 样式文件
│   │   └── lib/        # 第三方库
│   └── *.html          # HTML页面
│
├── database/            # 数据库相关
│   └── sql/            # SQL脚本
│
├── scripts/             # 启动脚本
│   ├── start_backend.sh
│   └── start_frontend.sh
│
└── README.md           # 本文档
```

## 开发进度

### ✅ 已完成
- [x] 项目目录结构创建
- [x] MariaDB数据库表结构设计（核心表）
- [x] 后端基础框架（FastAPI）
- [x] 东方财富API数据采集模块
- [x] 基础API接口实现
- [x] 前端排行榜页面
- [x] 端口配置优化（HTML:8888, API:8887）
- [x] IP地址动态检测（支持云部署）

### 🚧 进行中
- [ ] 前端详情页面

### 📋 待完成
- [ ] 用户认证系统
- [ ] 定时任务系统
- [ ] 持股管理功能

## 部署说明

详细部署说明请参考：[README_DEPLOY.md](README_DEPLOY.md)

## 文档

- [项目计划文档](PROJECT_PLAN.md) - 详细的项目计划和设计
- [部署说明](README_DEPLOY.md) - 部署到云服务器的详细指南

## 许可证

[待定]

## 联系方式

[待定]
