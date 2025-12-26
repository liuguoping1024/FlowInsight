/**
 * API封装层
 * 统一管理所有API调用
 */
const API = {
    baseURL: CONFIG.API_BASE_URL,
    
    /**
     * 统一的请求方法
     * @param {string} url - 请求URL
     * @param {object} options - 请求选项
     * @returns {Promise} 请求Promise
     */
    async request(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        // 添加认证token（如果有）
        const token = localStorage.getItem('token');
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }
        
        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(`${this.baseURL}${url}`, finalOptions);
            
            // 处理非200状态码
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    },
    
    /**
     * GET请求
     */
    async get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const finalUrl = queryString ? `${url}?${queryString}` : url;
        return this.request(finalUrl, { method: 'GET' });
    },
    
    /**
     * POST请求
     */
    async post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },
    
    /**
     * PUT请求
     */
    async put(url, data = {}) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },
    
    /**
     * DELETE请求
     */
    async delete(url) {
        return this.request(url, { method: 'DELETE' });
    },
    
    /**
     * 获取当前用户信息
     */
    async getCurrentUser() {
        return this.get('/auth/me');
    },
    
    // ========== 资金流向相关API ==========
    
    /**
     * 获取资金流向排行榜
     * @param {object} params - 查询参数
     * @returns {Promise}
     */
    async getCapitalFlowRank(params = {}) {
        return this.get('/capital-flow/rank', params);
    },
    
    /**
     * 获取股票详情
     * @param {number|string} stockId - 股票ID或代码
     * @returns {Promise}
     */
    async getStockDetail(stockId) {
        return this.get(`/stocks/${stockId}`);
    },
    
    /**
     * 获取资金流向历史
     * @param {number|string} stockCode - 股票代码
     * @param {object} params - 查询参数（days等）
     * @returns {Promise}
     */
    async getStockCapitalFlowHistory(stockCode, params = {}) {
        // 使用 /capital-flow/stock/{stock_code} 接口
        return this.get(`/capital-flow/stock/${stockCode}`, params);
    },
    
    // ========== 用户相关API ==========
    
    /**
     * 用户登录
     * @param {object} credentials - 登录凭证
     * @returns {Promise}
     */
    async login(credentials) {
        const response = await this.post('/auth/login', credentials);
        // 保存token
        if (response.access_token) {
            localStorage.setItem('token', response.access_token);
        }
        return response;
    },
    
    /**
     * 用户登出
     */
    logout() {
        localStorage.removeItem('token');
    },
    
    // ========== 持股相关API ==========
    
    /**
     * 获取用户持股列表
     * @returns {Promise}
     */
    async getHoldings() {
        return this.get('/holdings');
    },
    
    /**
     * 添加持股
     * @param {object} data - 持股数据
     * @returns {Promise}
     */
    async addHolding(data) {
        return this.post('/holdings', data);
    },
    
    // ========== 收藏相关API ==========
    
    /**
     * 获取收藏列表
     * @returns {Promise}
     */
    async getWatchlist() {
        return this.get('/watchlist');
    },
    
    /**
     * 添加收藏
     * @param {object} data - 收藏数据
     * @returns {Promise}
     */
    async addToWatchlist(data) {
        return this.post('/watchlist', data);
    },
};

// 导出API（如果使用模块化）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
}

