/**
 * 排行榜页面逻辑
 */
class RankingPage {
    constructor() {
        this.data = [];
        this.filteredData = [];
        this.currentPage = 1;
        this.pageSize = CONFIG.PAGE_SIZE;
        this.total = 0;
        this.totalPages = 0;
        this.sortField = 'f62';  // 默认按今日主力净流入排序
        this.currentFilter = 'all';  // 当前筛选：all, inflow, outflow
        
        this.init();
    }
    
    async init() {
        this.bindEvents();
        await this.loadData();
        this.render();
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 排序字段改变
        document.getElementById('sortField').addEventListener('change', (e) => {
            this.sortField = e.target.value;
            this.currentPage = 1;
            this.loadData();
        });
        
        // 刷新按钮
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadData();
        });
        
        // 筛选按钮
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // 更新活动状态
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                
                this.currentFilter = e.target.dataset.filter;
                this.applyFilter();
            });
        });
    }
    
    /**
     * 加载数据
     */
    async loadData() {
        const tableBody = document.getElementById('tableBody');
        showLoading(tableBody);
        
        try {
            const response = await API.getCapitalFlowRank({
                page: this.currentPage,
                page_size: this.pageSize,
                sort_field: this.sortField
            });
            
            if (response.code === 200 && response.data) {
                this.data = response.data.items || [];
                this.total = response.data.total || 0;
                this.totalPages = response.data.total_pages || 1;
                
                this.filteredData = [...this.data];
                this.applyFilter();
                this.updateUpdateTime();
            } else {
                showError(tableBody, response.message || '加载失败');
            }
        } catch (error) {
            console.error('加载数据失败:', error);
            showError(tableBody, '网络错误，请稍后重试');
        }
    }
    
    /**
     * 应用筛选
     */
    applyFilter() {
        if (this.currentFilter === 'all') {
            this.filteredData = [...this.data];
        } else if (this.currentFilter === 'inflow') {
            this.filteredData = this.data.filter(item => item.main_inflow > 0);
        } else if (this.currentFilter === 'outflow') {
            this.filteredData = this.data.filter(item => item.main_inflow < 0);
        }
        
        this.render();
    }
    
    /**
     * 渲染表格
     */
    render() {
        const tableBody = document.getElementById('tableBody');
        
        if (this.filteredData.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="12" class="text-center">暂无数据</td></tr>';
            return;
        }
        
        let html = '';
        const startRank = (this.currentPage - 1) * this.pageSize + 1;
        
        this.filteredData.forEach((item, index) => {
            const rank = startRank + index;
            const changeClass = getChangeColorClass(item.change_percent);
            const inflowClass = item.main_inflow >= 0 ? 'text-up' : 'text-down';
            
            html += `
                <tr>
                    <td>${rank}</td>
                    <td><span class="stock-code">${item.stock_code}</span></td>
                    <td><span class="stock-name">${item.stock_name}</span></td>
                    <td class="price">${formatPrice(item.current_price)}</td>
                    <td class="${changeClass}">${formatPercent(item.change_percent)}</td>
                    <td class="amount-cell ${inflowClass}">${formatAmount(item.main_inflow)}</td>
                    <td class="percent-cell ${inflowClass}">${formatPercent(item.main_inflow_rate)}</td>
                    <td class="amount-cell">${formatAmount(item.super_inflow)}</td>
                    <td class="percent-cell">${formatPercent(item.super_inflow_rate)}</td>
                    <td class="amount-cell">${(item.net_inflow_5d === null || item.net_inflow_5d === undefined || item.net_inflow_5d === 0 || item.net_inflow_5d === '-') ? '-' : formatAmount(item.net_inflow_5d)}</td>
                    <td class="amount-cell">${(item.net_inflow_10d === null || item.net_inflow_10d === undefined || item.net_inflow_10d === 0 || item.net_inflow_10d === '-') ? '-' : formatAmount(item.net_inflow_10d)}</td>
                    <td>
                        <button class="action-btn" onclick="rankingPage.viewDetail('${item.stock_code}')">详情</button>
                    </td>
                </tr>
            `;
        });
        
        tableBody.innerHTML = html;
        this.renderPagination();
    }
    
    /**
     * 渲染分页
     */
    renderPagination() {
        const pagination = document.getElementById('pagination');
        
        if (this.totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }
        
        let html = '';
        
        // 上一页按钮
        html += `
            <button class="pagination-btn" ${this.currentPage === 1 ? 'disabled' : ''} 
                    onclick="rankingPage.goToPage(${this.currentPage - 1})">
                上一页
            </button>
        `;
        
        // 页码按钮
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(this.totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage < maxVisiblePages - 1) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        if (startPage > 1) {
            html += `<button class="pagination-btn" onclick="rankingPage.goToPage(1)">1</button>`;
            if (startPage > 2) {
                html += `<span class="pagination-info">...</span>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            html += `
                <button class="pagination-btn ${i === this.currentPage ? 'active' : ''}" 
                        onclick="rankingPage.goToPage(${i})">
                    ${i}
                </button>
            `;
        }
        
        if (endPage < this.totalPages) {
            if (endPage < this.totalPages - 1) {
                html += `<span class="pagination-info">...</span>`;
            }
            html += `<button class="pagination-btn" onclick="rankingPage.goToPage(${this.totalPages})">${this.totalPages}</button>`;
        }
        
        // 下一页按钮
        html += `
            <button class="pagination-btn" ${this.currentPage === this.totalPages ? 'disabled' : ''} 
                    onclick="rankingPage.goToPage(${this.currentPage + 1})">
                下一页
            </button>
        `;
        
        // 分页信息
        html += `
            <span class="pagination-info">
                第 ${this.currentPage} / ${this.totalPages} 页，共 ${this.total} 条
            </span>
        `;
        
        pagination.innerHTML = html;
    }
    
    /**
     * 跳转到指定页码
     */
    goToPage(page) {
        if (page < 1 || page > this.totalPages || page === this.currentPage) {
            return;
        }
        this.currentPage = page;
        this.loadData();
    }
    
    /**
     * 查看详情
     */
    viewDetail(stockCode) {
        window.location.href = `detail.html?code=${stockCode}`;
    }
    
    /**
     * 更新最后更新时间
     */
    updateUpdateTime() {
        const updateTimeEl = document.getElementById('updateTime');
        const now = new Date();
        updateTimeEl.textContent = `最后更新：${formatDate(now, 'YYYY-MM-DD HH:mm:ss')}`;
    }
}

// 页面加载完成后初始化
let rankingPage;
document.addEventListener('DOMContentLoaded', () => {
    rankingPage = new RankingPage();
    
    // 设置自动刷新（每5分钟）
    setInterval(() => {
        rankingPage.loadData();
    }, CONFIG.REFRESH_INTERVAL);
});

