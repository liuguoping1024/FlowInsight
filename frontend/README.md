# FlowInsight 前端项目

## 项目结构

```
frontend/
├── index.html              # 排行榜页
├── detail.html             # 详情页
├── holdings.html           # 持股管理
├── login.html              # 登录页
│
├── assets/
│   ├── js/
│   │   ├── config.js       # 配置文件
│   │   ├── api.js          # API封装层
│   │   ├── utils.js        # 工具函数
│   │   ├── auth.js         # 认证相关
│   │   ├── pages/          # 页面逻辑
│   │   └── components/     # 可复用组件
│   ├── css/
│   │   ├── common.css      # 公共样式
│   │   ├── components.css  # 组件样式
│   │   └── pages/          # 页面特定样式
│   └── lib/                # 第三方库
│       ├── echarts.min.js
│       └── axios.min.js
│
└── README.md
```

## 使用说明

### 1. 引入依赖

在HTML文件中引入必要的库：

```html
<!-- ECharts -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>

<!-- Axios (可选，如果使用fetch则不需要) -->
<script src="https://cdn.jsdelivr.net/npm/axios@1.6.0/dist/axios.min.js"></script>
```

### 2. 引入项目文件

```html
<!-- 配置和工具 -->
<script src="assets/js/config.js"></script>
<script src="assets/js/utils.js"></script>
<script src="assets/js/api.js"></script>

<!-- 样式 -->
<link rel="stylesheet" href="assets/css/common.css">
```

### 3. 页面结构示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlowInsight</title>
    <link rel="stylesheet" href="assets/css/common.css">
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
</head>
<body>
    <div class="container">
        <!-- 页面内容 -->
    </div>
    
    <script src="assets/js/config.js"></script>
    <script src="assets/js/utils.js"></script>
    <script src="assets/js/api.js"></script>
    <script src="assets/js/pages/your-page.js"></script>
</body>
</html>
```

## 开发规范

### 代码组织
- 每个页面一个独立的JS文件
- 使用类组织页面逻辑
- 公共功能抽取到utils.js或components中

### 命名规范
- CSS类名：BEM命名（如：`.ranking-table`, `.ranking-table__row`）
- JavaScript变量：驼峰命名（如：`currentPage`, `filterParams`）
- 文件命名：小写+连字符（如：`capital-flow.js`）

### API调用
统一使用 `API` 对象进行调用：

```javascript
// 获取排行榜
const data = await API.getCapitalFlowRank({ page: 1, page_size: 50 });

// 获取股票详情
const detail = await API.getStockDetail(123);
```

### 工具函数
使用 `utils.js` 中的工具函数：

```javascript
// 格式化金额
formatAmount(123456789);  // "1.23亿"

// 格式化百分比
formatPercent(5.23);  // "5.23%"

// 获取涨跌颜色
getChangeColorClass(5.5);  // "text-up"
```

## 待实现页面

- [ ] index.html - 排行榜页
- [ ] detail.html - 详情页
- [ ] holdings.html - 持股管理
- [ ] login.html - 登录页

