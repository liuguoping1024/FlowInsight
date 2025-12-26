/**
 * 详情页面逻辑
 */
class DetailPage {
    constructor() {
        this.stockCode = null;
        this.stockInfo = null;
        this.historyData = [];
        this.trendChart = null;
        
        this.init();
    }
    
    /**
     * 初始化
     */
    init() {
        // 从URL获取股票代码
        const urlParams = new URLSearchParams(window.location.search);
        this.stockCode = urlParams.get('code');
        
        if (!this.stockCode) {
            this.showError('缺少股票代码参数');
            return;
        }
        
        this.loadData();
        this.initChart();
    }
    
    /**
     * 初始化图表
     */
    initChart() {
        const chartDom = document.getElementById('trendChart');
        if (!chartDom) return;
        
        this.trendChart = echarts.init(chartDom);
        
        // 设置响应式
        window.addEventListener('resize', () => {
            if (this.trendChart) {
                this.trendChart.resize();
            }
        });
    }
    
    /**
     * 加载数据
     */
    async loadData() {
        await Promise.all([
            this.loadStockInfo(),
            this.loadCapitalFlowHistory()
        ]);
    }
    
    /**
     * 加载股票基本信息
     */
    async loadStockInfo() {
        const headerEl = document.getElementById('stockHeader');
        
        try {
            // 先尝试从API获取股票详情
            const detail = await API.getStockDetail(this.stockCode);
            
            if (detail.code === 200 && detail.data) {
                this.stockInfo = detail.data;
                this.renderStockHeader();
            } else {
                // 如果API没有数据，显示基本信息
                this.renderStockHeaderBasic();
            }
        } catch (error) {
            console.error('加载股票信息失败:', error);
            this.renderStockHeaderBasic();
        }
    }
    
    /**
     * 加载资金流向历史数据
     */
    async loadCapitalFlowHistory() {
        const tableBody = document.getElementById('historyTableBody');
        const todayFlowEl = document.getElementById('todayFlow');
        
        try {
            const response = await API.getStockCapitalFlowHistory(this.stockCode, {
                days: 30
            });
            
            if (response.code === 200 && response.data) {
                this.historyData = response.data.flows || [];
                
                if (this.historyData.length > 0) {
                    // 显示今日资金流向（最新的一条）
                    this.renderTodayFlow(this.historyData[0]);
                    
                    // 渲染历史数据表格
                    this.renderHistoryTable();
                    
                    // 渲染趋势图
                    this.renderTrendChart();
                } else {
                    showError(tableBody, '暂无历史数据');
                    showError(todayFlowEl, '暂无今日数据');
                }
            } else {
                showError(tableBody, response.message || '加载失败');
                showError(todayFlowEl, response.message || '加载失败');
            }
        } catch (error) {
            console.error('加载资金流向历史失败:', error);
            showError(tableBody, '网络错误，请稍后重试');
            showError(todayFlowEl, '网络错误，请稍后重试');
        }
    }
    
    /**
     * 渲染股票头部信息
     */
    renderStockHeader() {
        const headerEl = document.getElementById('stockHeader');
        
        if (!this.stockInfo) {
            this.renderStockHeaderBasic();
            return;
        }
        
        const changeClass = this.stockInfo.change_percent >= 0 ? 'text-up' : 'text-down';
        
        headerEl.innerHTML = `
            <div class="stock-name">${this.stockInfo.stock_name || '--'}</div>
            <div class="stock-code">${this.stockCode}</div>
            <div class="stock-info">
                <div class="stock-info-item">
                    <span class="stock-info-label">交易所</span>
                    <span class="stock-info-value">${this.stockInfo.exchange || '--'}</span>
                </div>
                <div class="stock-info-item">
                    <span class="stock-info-label">行业</span>
                    <span class="stock-info-value">${this.stockInfo.industry || '--'}</span>
                </div>
                <div class="stock-info-item">
                    <span class="stock-info-label">地区</span>
                    <span class="stock-info-value">${this.stockInfo.area || '--'}</span>
                </div>
                <div class="stock-info-item">
                    <span class="stock-info-label">市盈率</span>
                    <span class="stock-info-value">${this.stockInfo.pe_ratio ? this.stockInfo.pe_ratio.toFixed(2) : '--'}</span>
                </div>
                <div class="stock-info-item">
                    <span class="stock-info-label">市净率</span>
                    <span class="stock-info-value">${this.stockInfo.pb_ratio ? this.stockInfo.pb_ratio.toFixed(2) : '--'}</span>
                </div>
            </div>
        `;
    }
    
    /**
     * 渲染股票头部基本信息（当API没有数据时）
     */
    renderStockHeaderBasic() {
        const headerEl = document.getElementById('stockHeader');
        headerEl.innerHTML = `
            <div class="stock-name">股票代码：${this.stockCode}</div>
            <div class="stock-code">正在加载详细信息...</div>
        `;
    }
    
    /**
     * 渲染今日资金流向
     */
    renderTodayFlow(data) {
        const todayFlowEl = document.getElementById('todayFlow');
        
        const mainInflowClass = data.main_inflow >= 0 ? 'inflow' : 'outflow';
        const superInflowClass = data.super_inflow >= 0 ? 'inflow' : 'outflow';
        const largeInflowClass = data.large_inflow >= 0 ? 'inflow' : 'outflow';
        const mediumInflowClass = data.medium_inflow >= 0 ? 'inflow' : 'outflow';
        const smallInflowClass = data.small_inflow >= 0 ? 'inflow' : 'outflow';
        
        todayFlowEl.innerHTML = `
            <div class="flow-item ${mainInflowClass}">
                <div class="flow-item-label">主力净流入</div>
                <div class="flow-item-value">${formatAmount(data.main_inflow)}</div>
                <div class="flow-item-rate">占比 ${formatPercent(data.main_inflow_rate)}</div>
            </div>
            <div class="flow-item ${superInflowClass}">
                <div class="flow-item-label">超大单净流入</div>
                <div class="flow-item-value">${formatAmount(data.super_inflow)}</div>
                <div class="flow-item-rate">占比 ${formatPercent(data.super_inflow_rate)}</div>
            </div>
            <div class="flow-item ${largeInflowClass}">
                <div class="flow-item-label">大单净流入</div>
                <div class="flow-item-value">${formatAmount(data.large_inflow)}</div>
                <div class="flow-item-rate">占比 ${formatPercent(data.large_inflow_rate)}</div>
            </div>
            <div class="flow-item ${mediumInflowClass}">
                <div class="flow-item-label">中单净流入</div>
                <div class="flow-item-value">${formatAmount(data.medium_inflow)}</div>
                <div class="flow-item-rate">占比 ${formatPercent(data.medium_inflow_rate)}</div>
            </div>
            <div class="flow-item ${smallInflowClass}">
                <div class="flow-item-label">小单净流入</div>
                <div class="flow-item-value">${formatAmount(data.small_inflow)}</div>
                <div class="flow-item-rate">占比 ${formatPercent(data.small_inflow_rate)}</div>
            </div>
        `;
    }
    
    /**
     * 渲染历史数据表格
     */
    renderHistoryTable() {
        const tableBody = document.getElementById('historyTableBody');
        
        if (this.historyData.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="9" class="text-center">暂无数据</td></tr>';
            return;
        }
        
        let html = '';
        this.historyData.forEach(item => {
            const mainInflowClass = item.main_inflow >= 0 ? 'text-up' : 'text-down';
            const superInflowClass = item.super_inflow >= 0 ? 'text-up' : 'text-down';
            const changeClass = getChangeColorClass(item.change_percent);
            
            html += `
                <tr>
                    <td>${formatDate(item.trade_date)}</td>
                    <td class="${mainInflowClass}">${formatAmount(item.main_inflow)}</td>
                    <td class="${mainInflowClass}">${formatPercent(item.main_inflow_rate)}</td>
                    <td class="${superInflowClass}">${formatAmount(item.super_inflow)}</td>
                    <td class="${superInflowClass}">${formatPercent(item.super_inflow_rate)}</td>
                    <td>${formatPrice(item.close_price)}</td>
                    <td class="${changeClass}">${formatPercent(item.change_percent)}</td>
                    <td>${formatAmount(item.volume)}</td>
                    <td>${formatAmount(item.amount)}</td>
                </tr>
            `;
        });
        
        tableBody.innerHTML = html;
    }
    
    /**
     * 渲染趋势图
     */
    renderTrendChart() {
        if (!this.trendChart || this.historyData.length === 0) {
            return;
        }
        
        // 准备数据（按日期正序排列，从旧到新）
        const sortedData = [...this.historyData].sort((a, b) => {
            return new Date(a.trade_date) - new Date(b.trade_date);
        });
        
        const dates = sortedData.map(item => formatDate(item.trade_date, 'MM-DD'));
        const mainInflow = sortedData.map(item => item.main_inflow / 100000000); // 转换为亿元
        const superInflow = sortedData.map(item => item.super_inflow / 100000000);
        const closePrice = sortedData.map(item => item.close_price);
        
        const option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross'
                },
                formatter: function(params) {
                    let result = params[0].name + '<br/>';
                    params.forEach(param => {
                        if (param.seriesName.includes('流入')) {
                            result += `${param.seriesName}: ${formatAmount(param.value * 100000000)}<br/>`;
                        } else {
                            result += `${param.seriesName}: ${formatPrice(param.value)}<br/>`;
                        }
                    });
                    return result;
                }
            },
            legend: {
                data: ['主力净流入', '超大单净流入', '收盘价'],
                top: 10
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: dates
            },
            yAxis: [
                {
                    type: 'value',
                    name: '资金流入（亿元）',
                    position: 'left',
                    axisLabel: {
                        formatter: '{value}亿'
                    }
                },
                {
                    type: 'value',
                    name: '价格（元）',
                    position: 'right',
                    axisLabel: {
                        formatter: '{value}'
                    }
                }
            ],
            series: [
                {
                    name: '主力净流入',
                    type: 'bar',
                    data: mainInflow,
                    itemStyle: {
                        color: function(params) {
                            return params.value >= 0 ? CONFIG.CHART_COLORS.inflow : CONFIG.CHART_COLORS.outflow;
                        }
                    },
                    yAxisIndex: 0
                },
                {
                    name: '超大单净流入',
                    type: 'bar',
                    data: superInflow,
                    itemStyle: {
                        color: function(params) {
                            return params.value >= 0 ? CONFIG.CHART_COLORS.super : CONFIG.CHART_COLORS.outflow;
                        }
                    },
                    yAxisIndex: 0
                },
                {
                    name: '收盘价',
                    type: 'line',
                    data: closePrice,
                    smooth: true,
                    lineStyle: {
                        color: CONFIG.CHART_COLORS.main,
                        width: 2
                    },
                    itemStyle: {
                        color: CONFIG.CHART_COLORS.main
                    },
                    yAxisIndex: 1
                }
            ]
        };
        
        this.trendChart.setOption(option);
    }
    
    /**
     * 显示错误信息
     */
    showError(message) {
        const container = document.querySelector('.container');
        if (container) {
            container.innerHTML = `
                <div class="error" style="text-align: center; padding: 40px;">
                    <h2>错误</h2>
                    <p>${message}</p>
                    <a href="index.html" class="back-btn">返回排行榜</a>
                </div>
            `;
        }
    }
}

// 页面加载完成后初始化
let detailPage;
document.addEventListener('DOMContentLoaded', () => {
    detailPage = new DetailPage();
});

