/**
 * 收藏列表页面逻辑
 */
class WatchlistPage {
    constructor() {
        this.watchlist = [];
        this.init();
    }
    
    async init() {
        this.checkAuth();
        this.bindEvents();
        await this.loadWatchlist();
    }
    
    checkAuth() {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = 'login.html';
            return;
        }
        this.updateUserMenu();
    }
    
    updateUserMenu() {
        const navUser = document.getElementById('navUser');
        if (navUser) {
            navUser.innerHTML = `
                <span class="nav-link">已登录</span>
                <a href="#" class="nav-link" id="logoutBtn">退出</a>
            `;
            document.getElementById('logoutBtn').addEventListener('click', (e) => {
                e.preventDefault();
                API.logout();
                window.location.href = 'login.html';
            });
        }
    }
    
    bindEvents() {
        document.getElementById('addWatchlistBtn').addEventListener('click', () => {
            this.showModal();
        });
        
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadWatchlist();
        });
        
        document.getElementById('closeModal').addEventListener('click', () => {
            this.hideModal();
        });
        
        document.getElementById('cancelBtn').addEventListener('click', () => {
            this.hideModal();
        });
        
        document.getElementById('watchlistForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveWatchlist();
        });
    }
    
    async loadWatchlist() {
        const tableBody = document.getElementById('tableBody');
        showLoading(tableBody);
        
        try {
            const watchlist = await API.getWatchlist();
            this.watchlist = watchlist;
            this.render();
        } catch (error) {
            console.error('加载收藏失败:', error);
            if (error.message && error.message.includes('401')) {
                window.location.href = 'login.html';
            } else {
                showError(tableBody, '加载失败，请稍后重试');
            }
        }
    }
    
    render() {
        const tableBody = document.getElementById('tableBody');
        
        if (this.watchlist.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="8" class="text-center">暂无收藏记录，点击"添加收藏"开始管理</td></tr>';
            return;
        }
        
        let html = '';
        this.watchlist.forEach(item => {
            const changeClass = getChangeColorClass(item.change_percent);
            const inflowClass = item.main_inflow >= 0 ? 'text-up' : 'text-down';
            
            html += `
                <tr>
                    <td><span class="stock-code">${item.stock_code}</span></td>
                    <td><span class="stock-name">${item.stock_name}</span></td>
                    <td>${item.current_price ? formatPrice(item.current_price) : '--'}</td>
                    <td class="${changeClass}">${item.change_percent !== null ? formatPercent(item.change_percent) : '--'}</td>
                    <td class="amount-cell ${inflowClass}">${item.main_inflow !== null ? formatAmount(item.main_inflow) : '--'}</td>
                    <td>--</td>
                    <td>${item.created_at ? formatDate(item.created_at, 'YYYY-MM-DD') : '--'}</td>
                    <td>
                        <button class="action-btn" onclick="watchlistPage.viewDetail('${item.stock_code}')">详情</button>
                        <button class="action-btn" onclick="watchlistPage.removeFromWatchlist(${item.watch_id})">删除</button>
                    </td>
                </tr>
            `;
        });
        
        tableBody.innerHTML = html;
    }
    
    showModal() {
        document.getElementById('watchlistForm').reset();
        document.getElementById('watchlistModal').style.display = 'flex';
    }
    
    hideModal() {
        document.getElementById('watchlistModal').style.display = 'none';
    }
    
    async saveWatchlist() {
        const formData = new FormData(document.getElementById('watchlistForm'));
        const data = {
            stock_code: formData.get('stock_code'),
            notes: formData.get('notes') || null
        };
        
        try {
            await API.addToWatchlist(data);
            this.hideModal();
            await this.loadWatchlist();
        } catch (error) {
            console.error('保存失败:', error);
            alert(error.message || '保存失败，请重试');
        }
    }
    
    viewDetail(stockCode) {
        window.location.href = `detail.html?code=${stockCode}`;
    }
    
    async removeFromWatchlist(watchId) {
        if (!confirm('确定要删除这条收藏记录吗？')) {
            return;
        }
        
        try {
            await API.delete(`/watchlist/${watchId}`);
            await this.loadWatchlist();
        } catch (error) {
            console.error('删除失败:', error);
            alert('删除失败，请重试');
        }
    }
}

// 页面加载完成后初始化
let watchlistPage;
document.addEventListener('DOMContentLoaded', () => {
    watchlistPage = new WatchlistPage();
});

