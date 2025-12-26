/**
 * 持股管理页面逻辑
 */
class HoldingsPage {
    constructor() {
        this.holdings = [];
        this.editingId = null;
        this.init();
    }
    
    async init() {
        this.checkAuth();
        this.bindEvents();
        await this.loadHoldings();
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
        document.getElementById('addHoldingBtn').addEventListener('click', () => {
            this.showModal();
        });
        
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadHoldings();
        });
        
        document.getElementById('closeModal').addEventListener('click', () => {
            this.hideModal();
        });
        
        document.getElementById('cancelBtn').addEventListener('click', () => {
            this.hideModal();
        });
        
        document.getElementById('holdingForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveHolding();
        });
    }
    
    async loadHoldings() {
        const tableBody = document.getElementById('tableBody');
        showLoading(tableBody);
        
        try {
            const holdings = await API.getHoldings();
            this.holdings = holdings;
            this.render();
            this.updateSummary();
        } catch (error) {
            console.error('加载持股失败:', error);
            if (error.message && error.message.includes('401')) {
                window.location.href = 'login.html';
            } else {
                showError(tableBody, '加载失败，请稍后重试');
            }
        }
    }
    
    render() {
        const tableBody = document.getElementById('tableBody');
        
        if (this.holdings.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="10" class="text-center">暂无持股记录，点击"添加持股"开始管理</td></tr>';
            return;
        }
        
        let html = '';
        this.holdings.forEach(holding => {
            const profitClass = holding.profit_loss >= 0 ? 'text-up' : 'text-down';
            const marketValue = holding.current_price ? (holding.current_price * holding.quantity) : null;
            
            html += `
                <tr>
                    <td><span class="stock-code">${holding.stock_code}</span></td>
                    <td><span class="stock-name">${holding.stock_name}</span></td>
                    <td>${formatPrice(holding.cost_price)}</td>
                    <td>${holding.current_price ? formatPrice(holding.current_price) : '--'}</td>
                    <td>${holding.quantity.toLocaleString()}</td>
                    <td>${marketValue ? formatAmount(marketValue) : '--'}</td>
                    <td class="${profitClass}">${holding.profit_loss !== null ? formatAmount(holding.profit_loss) : '--'}</td>
                    <td class="${profitClass}">${holding.profit_loss_rate !== null ? formatPercent(holding.profit_loss_rate) : '--'}</td>
                    <td>${holding.buy_date || '--'}</td>
                    <td>
                        <button class="action-btn" onclick="holdingsPage.editHolding(${holding.holding_id})">编辑</button>
                        <button class="action-btn" onclick="holdingsPage.deleteHolding(${holding.holding_id})">删除</button>
                    </td>
                </tr>
            `;
        });
        
        tableBody.innerHTML = html;
    }
    
    updateSummary() {
        let totalCost = 0;
        let totalValue = 0;
        
        this.holdings.forEach(holding => {
            totalCost += holding.cost_price * holding.quantity;
            if (holding.current_price) {
                totalValue += holding.current_price * holding.quantity;
            }
        });
        
        const totalProfitLoss = totalValue - totalCost;
        const profitLossRate = totalCost > 0 ? (totalProfitLoss / totalCost * 100) : 0;
        
        document.getElementById('totalCost').textContent = formatAmount(totalCost);
        document.getElementById('totalValue').textContent = totalValue > 0 ? formatAmount(totalValue) : '--';
        
        const profitClass = totalProfitLoss >= 0 ? 'text-up' : 'text-down';
        document.getElementById('totalProfitLoss').textContent = totalValue > 0 ? formatAmount(totalProfitLoss) : '--';
        document.getElementById('totalProfitLoss').className = `summary-value ${profitClass}`;
        document.getElementById('profitLossRate').textContent = totalValue > 0 ? formatPercent(profitLossRate) : '--';
        document.getElementById('profitLossRate').className = `summary-value ${profitClass}`;
    }
    
    showModal(holding = null) {
        this.editingId = holding ? holding.holding_id : null;
        document.getElementById('modalTitle').textContent = holding ? '编辑持股' : '添加持股';
        document.getElementById('holdingForm').reset();
        
        if (holding) {
            document.getElementById('stockCode').value = holding.stock_code;
            document.getElementById('stockCode').disabled = true;
            document.getElementById('costPrice').value = holding.cost_price;
            document.getElementById('quantity').value = holding.quantity;
            document.getElementById('buyDate').value = holding.buy_date || '';
            document.getElementById('notes').value = holding.notes || '';
        } else {
            document.getElementById('stockCode').disabled = false;
        }
        
        document.getElementById('holdingModal').style.display = 'flex';
    }
    
    hideModal() {
        document.getElementById('holdingModal').style.display = 'none';
        this.editingId = null;
    }
    
    async saveHolding() {
        const formData = new FormData(document.getElementById('holdingForm'));
        const data = {
            stock_code: formData.get('stock_code'),
            cost_price: parseFloat(formData.get('cost_price')),
            quantity: parseInt(formData.get('quantity')),
            buy_date: formData.get('buy_date') || null,
            notes: formData.get('notes') || null
        };
        
        try {
            if (this.editingId) {
                await API.put(`/holdings/${this.editingId}`, data);
            } else {
                await API.addHolding(data);
            }
            this.hideModal();
            await this.loadHoldings();
        } catch (error) {
            console.error('保存失败:', error);
            alert(error.message || '保存失败，请重试');
        }
    }
    
    editHolding(holdingId) {
        const holding = this.holdings.find(h => h.holding_id === holdingId);
        if (holding) {
            this.showModal(holding);
        }
    }
    
    async deleteHolding(holdingId) {
        if (!confirm('确定要删除这条持股记录吗？')) {
            return;
        }
        
        try {
            await API.delete(`/holdings/${holdingId}`);
            await this.loadHoldings();
        } catch (error) {
            console.error('删除失败:', error);
            alert('删除失败，请重试');
        }
    }
}

// 页面加载完成后初始化
let holdingsPage;
document.addEventListener('DOMContentLoaded', () => {
    holdingsPage = new HoldingsPage();
});

