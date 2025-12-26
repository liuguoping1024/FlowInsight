# 数据采集脚本说明

## 脚本列表

### 1. collect_stocks.py - 股票基础信息采集

从东方财富API获取股票列表并保存到数据库。

**使用方法：**
```bash
cd backend
python scripts/collect_stocks.py --pages 10
```

**参数：**
- `--pages`: 采集页数（每页100条，默认10页）

**功能：**
- 从排行榜API获取股票列表
- 自动识别股票所属交易所（上海/深圳）
- 如果股票已存在则更新，不存在则新增
- 保存股票代码、名称、交易所等基本信息

### 2. collect_sectors.py - 板块信息采集

从东方财富API获取板块信息并保存到数据库。

**使用方法：**
```bash
cd backend
python scripts/collect_sectors.py --type all
```

**参数：**
- `--type`: 板块类型
  - `industry`: 行业板块
  - `concept`: 概念板块
  - `area`: 地域板块
  - `all`: 全部类型（默认）

**功能：**
- 采集行业/概念/地域板块信息
- 保存板块代码、名称、类型等信息

## 运行前准备

1. 确保数据库已创建并配置正确
2. 确保后端依赖已安装：`pip install -r requirements.txt`
3. 确保数据库连接配置正确（`backend/app/core/config.py`）

## 日志

所有脚本的日志会保存在 `backend/logs/` 目录下：
- `collect_stocks.log` - 股票采集日志
- `collect_sectors.log` - 板块采集日志

## 注意事项

1. 采集脚本会向东方财富API发送请求，请控制请求频率
2. 建议在非交易时间运行，避免影响实时数据查询
3. 首次运行建议采集10-20页股票数据，覆盖主要股票
4. 板块数据相对较少，可以一次性采集全部

