/**
 * 配置文件
 * 集中管理所有配置项
 */
(function() {
    'use strict';
    
    // 动态获取API地址
    function getApiBaseUrl() {
        // 优先级1: 如果设置了全局变量，优先使用（可以通过HTML中设置）
        if (typeof window !== 'undefined' && window.API_BASE_URL) {
            return window.API_BASE_URL;
        }
        
        // 优先级2: 从当前页面URL动态构建API地址
        // 获取当前页面的协议和主机名
        const protocol = window.location.protocol;
        const hostname = window.location.hostname;
        const apiPort = '8887';  // API端口固定为8887
        
        // 构建API地址：使用相同协议和主机名，端口为8887
        return `${protocol}//${hostname}:${apiPort}/api/v1`;
    }
    
    window.CONFIG = {
        // API配置（动态获取）
        get API_BASE_URL() {
            return getApiBaseUrl();
        },
        
        // 分页配置
        PAGE_SIZE: 50,
        
        // 图表颜色配置
        CHART_COLORS: {
            inflow: '#00C853',      // 流入 - 绿色
            outflow: '#FF5252',     // 流出 - 红色
            main: '#2196F3',         // 主力 - 蓝色
            super: '#FF9800',        // 超大单 - 橙色
            large: '#9C27B0',        // 大单 - 紫色
            medium: '#00BCD4',       // 中单 - 青色
            small: '#9E9E9E'         // 小单 - 灰色
        },
        
        // 数据刷新间隔（毫秒）
        REFRESH_INTERVAL: 300000,  // 5分钟
        
        // 格式化配置
        NUMBER_FORMAT: {
            // 金额格式化：保留2位小数，使用千分位
            amount: {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
                useGrouping: true
            },
            // 百分比格式化：保留2位小数
            percent: {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
                style: 'percent'
            }
        }
    };
    
    // 导出配置（如果使用模块化）
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = window.CONFIG;
    }
})();
