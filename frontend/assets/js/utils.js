/**
 * 工具函数库
 */

/**
 * 格式化金额（元转亿元，保留2位小数）
 * @param {number} amount - 金额（元）
 * @returns {string} 格式化后的字符串，如 "1.23亿"
 */
function formatAmount(amount) {
    if (amount === null || amount === undefined || isNaN(amount)) {
        return '-';
    }
    
    const yi = 100000000; // 1亿
    const wan = 10000;     // 1万
    
    if (Math.abs(amount) >= yi) {
        return (amount / yi).toFixed(2) + '亿';
    } else if (Math.abs(amount) >= wan) {
        return (amount / wan).toFixed(2) + '万';
    } else {
        return amount.toFixed(2);
    }
}

/**
 * 格式化百分比
 * @param {number} value - 百分比值
 * @param {number} decimals - 小数位数，默认2位
 * @returns {string} 格式化后的字符串，如 "5.23%"
 */
function formatPercent(value, decimals = 2) {
    if (value === null || value === undefined || isNaN(value)) {
        return '-';
    }
    return value.toFixed(decimals) + '%';
}

/**
 * 格式化价格
 * @param {number} price - 价格
 * @param {number} decimals - 小数位数，默认2位
 * @returns {string} 格式化后的字符串
 */
function formatPrice(price, decimals = 2) {
    if (price === null || price === undefined || isNaN(price)) {
        return '-';
    }
    return price.toFixed(decimals);
}

/**
 * 格式化日期
 * @param {string|Date} date - 日期
 * @param {string} format - 格式，默认 'YYYY-MM-DD'
 * @returns {string} 格式化后的日期字符串
 */
function formatDate(date, format = 'YYYY-MM-DD') {
    if (!date) return '-';
    
    const d = new Date(date);
    if (isNaN(d.getTime())) return '-';
    
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hour = String(d.getHours()).padStart(2, '0');
    const minute = String(d.getMinutes()).padStart(2, '0');
    const second = String(d.getSeconds()).padStart(2, '0');
    
    return format
        .replace('YYYY', year)
        .replace('MM', month)
        .replace('DD', day)
        .replace('HH', hour)
        .replace('mm', minute)
        .replace('ss', second);
}

/**
 * 获取涨跌颜色类名
 * @param {number} value - 涨跌值（正数为涨，负数为跌）
 * @returns {string} CSS类名
 */
function getChangeColorClass(value) {
    if (value === null || value === undefined || isNaN(value)) {
        return '';
    }
    if (value > 0) return 'text-up';      // 上涨 - 红色
    if (value < 0) return 'text-down';    // 下跌 - 绿色
    return '';                             // 平盘
}

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 节流函数
 * @param {Function} func - 要节流的函数
 * @param {number} limit - 时间限制（毫秒）
 * @returns {Function} 节流后的函数
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * 显示加载状态
 * @param {HTMLElement} container - 容器元素
 */
function showLoading(container) {
    if (!container) return;
    container.innerHTML = '<div class="loading">加载中...</div>';
}

/**
 * 显示错误信息
 * @param {HTMLElement} container - 容器元素
 * @param {string} message - 错误消息
 */
function showError(container, message = '加载失败，请稍后重试') {
    if (!container) return;
    container.innerHTML = `<div class="error">${message}</div>`;
}

// 导出函数（如果使用模块化）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatAmount,
        formatPercent,
        formatPrice,
        formatDate,
        getChangeColorClass,
        debounce,
        throttle,
        showLoading,
        showError
    };
}

