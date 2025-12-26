/**
 * 登录/注册页面逻辑
 */
class AuthPage {
    constructor() {
        this.currentTab = 'login';
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.checkAuthStatus();
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 标签切换
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.dataset.tab;
                this.switchTab(tab);
            });
        });
        
        // 登录表单提交
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });
        
        // 注册表单提交
        document.getElementById('registerForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });
    }
    
    /**
     * 切换标签
     */
    switchTab(tab) {
        this.currentTab = tab;
        
        // 更新按钮状态
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tab);
        });
        
        // 更新表单显示
        document.querySelectorAll('.auth-form').forEach(form => {
            form.classList.toggle('active', form.id === `${tab}Form`);
        });
        
        // 清除错误信息
        this.clearErrors();
    }
    
    /**
     * 检查认证状态
     */
    checkAuthStatus() {
        const token = localStorage.getItem('token');
        if (token) {
            // 已登录，跳转到首页
            window.location.href = 'index.html';
        }
    }
    
    /**
     * 处理登录
     */
    async handleLogin() {
        const form = document.getElementById('loginForm');
        const formData = new FormData(form);
        
        const username = formData.get('username');
        const password = formData.get('password');
        
        if (!username || !password) {
            this.showError('loginError', '请输入用户名和密码');
            return;
        }
        
        try {
            // 使用OAuth2格式
            const params = new URLSearchParams();
            params.append('username', username);
            params.append('password', password);
            
            const response = await fetch(`${CONFIG.API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: params.toString()
            });
            
            const data = await response.json();
            
            if (response.ok && data.access_token) {
                // 保存token
                localStorage.setItem('token', data.access_token);
                
                // 跳转到首页
                window.location.href = 'index.html';
            } else {
                this.showError('loginError', data.detail || '登录失败，请检查用户名和密码');
            }
        } catch (error) {
            console.error('登录失败:', error);
            this.showError('loginError', '网络错误，请稍后重试');
        }
    }
    
    /**
     * 处理注册
     */
    async handleRegister() {
        const form = document.getElementById('registerForm');
        const formData = new FormData(form);
        
        const username = formData.get('username');
        const password = formData.get('password');
        const email = formData.get('email');
        const phone = formData.get('phone');
        
        if (!username || !password) {
            this.showError('registerError', '用户名和密码为必填项');
            return;
        }
        
        if (username.length < 3) {
            this.showError('registerError', '用户名至少3个字符');
            return;
        }
        
        if (password.length < 6) {
            this.showError('registerError', '密码至少6个字符');
            return;
        }
        
        try {
            const response = await API.post('/auth/register', {
                username,
                password,
                email: email || null,
                phone: phone || null
            });
            
            if (response.user_id) {
                // 注册成功，自动登录
                await this.handleLogin();
            } else {
                this.showError('registerError', '注册失败，请重试');
            }
        } catch (error) {
            console.error('注册失败:', error);
            const errorMsg = error.message || '注册失败，请重试';
            this.showError('registerError', errorMsg);
        }
    }
    
    /**
     * 显示错误信息
     */
    showError(elementId, message) {
        const errorEl = document.getElementById(elementId);
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.style.display = 'block';
        }
    }
    
    /**
     * 清除错误信息
     */
    clearErrors() {
        document.querySelectorAll('.error-message').forEach(el => {
            el.style.display = 'none';
            el.textContent = '';
        });
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new AuthPage();
});

