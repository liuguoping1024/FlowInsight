"""
东方财富API数据采集模块
"""
import httpx
import asyncio
from typing import Optional, Dict, List, Any
from datetime import datetime, date
from loguru import logger


class EastMoneyAPI:
    """东方财富API封装类"""
    
    def __init__(self, base_url: str = "http://push2.eastmoney.com", 
                 history_url: str = "http://push2his.eastmoney.com"):
        """
        初始化API客户端
        
        Args:
            base_url: 实时数据API基础URL
            history_url: 历史数据API基础URL
        """
        self.base_url = base_url
        self.history_url = history_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
    
    async def _request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        发送HTTP请求
        
        Args:
            url: 请求URL
            params: 请求参数
            
        Returns:
            响应数据字典，失败返回None
        """
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # 东方财富API通常返回格式: {"rc": 0, "rt": ..., "data": {...}}
            if isinstance(data, dict) and data.get("rc") == 0:
                return data.get("data")
            return data
            
        except Exception as e:
            logger.error(f"API请求失败: {url}, 错误: {e}")
            return None
    
    # ========== 实时数据API ==========
    
    async def get_realtime_capital_flow_rank(
        self, 
        page: int = 1, 
        page_size: int = 100,
        sort_field: str = 'f62'  # f62=今日主力净流入
    ) -> Optional[Dict]:
        """
        获取实时资金流向排行榜
        
        Args:
            page: 页码
            page_size: 每页数量
            sort_field: 排序字段
                - f62: 今日主力净流入
                - f184: 今日主力净流入占比
                - f204: 5日主力净流入
                - f205: 10日主力净流入
                
        Returns:
            排行榜数据
        """
        url = f"{self.base_url}/api/qt/clist/get"
        params = {
            'pn': page,
            'pz': page_size,
            'po': 1,  # 排序方式：1-降序
            'np': 1,
            'fltt': 2,
            'invt': 2,
            'fid': sort_field,
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',  # 全市场
            'fields': 'f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13'
        }
        
        return await self._request(url, params)
    
    async def get_stock_realtime_flow(
        self, 
        stock_code: str, 
        market: str = 'sh'
    ) -> Optional[Dict]:
        """
        获取个股实时资金流向
        
        Args:
            stock_code: 股票代码（如：600118）
            market: 市场代码（sh-上海, sz-深圳）
            
        Returns:
            实时资金流向数据
        """
        market_code = '1' if market == 'sh' else '0'
        secid = f"{market_code}.{stock_code}"
        
        url = f"{self.base_url}/api/qt/stock/fflow/get"
        params = {
            'fields1': 'f1,f2,f3,f7',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65',
            'secid': secid
        }
        
        return await self._request(url, params)
    
    async def get_stock_realtime_quote(
        self,
        stock_code: str,
        market: str = 'sh'
    ) -> Optional[Dict]:
        """
        获取个股实时行情
        
        Args:
            stock_code: 股票代码
            market: 市场代码
            
        Returns:
            实时行情数据
        """
        market_code = '1' if market == 'sh' else '0'
        secid = f"{market_code}.{stock_code}"
        
        url = f"{self.base_url}/api/qt/stock/get"
        params = {
            'secid': secid,
            'fields': 'f57,f58,f43,f44,f45,f46,f47,f48,f49,f50,f169,f170,f171'
        }
        
        return await self._request(url, params)
    
    # ========== 历史数据API ==========
    
    async def get_stock_capital_flow_history(
        self,
        stock_code: str,
        market: str = 'sh',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        获取个股历史资金流向数据
        
        Args:
            stock_code: 股票代码
            market: 市场代码
            start_date: 开始日期（格式：YYYYMMDD）
            end_date: 结束日期（格式：YYYYMMDD）
            
        Returns:
            历史资金流向数据列表
        """
        market_code = '1' if market == 'sh' else '0'
        secid = f"{market_code}.{stock_code}"
        
        url = f"{self.history_url}/api/qt/stock/fflow/daykline/get"
        params = {
            'secid': secid,
            'fields1': 'f1,f2,f3,f7',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65'
        }
        
        if start_date:
            params['lmt'] = None  # 如果需要限制日期范围
        if end_date:
            params['end'] = end_date
        
        data = await self._request(url, params)
        
        # 解析返回的数据格式
        if data and 'klines' in data:
            return self._parse_history_data(data['klines'])
        
        return []
    
    def _parse_history_data(self, klines: List[str]) -> List[Dict]:
        """
        解析历史数据
        
        Args:
            klines: 原始数据列表（每行是一个字符串，字段用逗号分隔）
            
        Returns:
            解析后的数据列表
        """
        result = []
        for line in klines:
            if not line:
                continue
            
            fields = line.split(',')
            if len(fields) < 15:
                continue
            
            try:
                result.append({
                    'trade_date': fields[0],  # 交易日期
                    'main_inflow': float(fields[1]) if fields[1] else 0,  # 主力净流入
                    'main_inflow_rate': float(fields[2]) if fields[2] else 0,  # 主力净流入占比
                    'super_inflow': float(fields[3]) if fields[3] else 0,  # 超大单净流入
                    'super_inflow_rate': float(fields[4]) if fields[4] else 0,  # 超大单净流入占比
                    'large_inflow': float(fields[5]) if fields[5] else 0,  # 大单净流入
                    'large_inflow_rate': float(fields[6]) if fields[6] else 0,  # 大单净流入占比
                    'medium_inflow': float(fields[7]) if fields[7] else 0,  # 中单净流入
                    'medium_inflow_rate': float(fields[8]) if fields[8] else 0,  # 中单净流入占比
                    'small_inflow': float(fields[9]) if fields[9] else 0,  # 小单净流入
                    'small_inflow_rate': float(fields[10]) if fields[10] else 0,  # 小单净流入占比
                    'close_price': float(fields[11]) if fields[11] else 0,  # 收盘价
                    'change_percent': float(fields[12]) if fields[12] else 0,  # 涨跌幅
                    'volume': int(float(fields[13])) if fields[13] else 0,  # 成交量
                    'amount': float(fields[14]) if fields[14] else 0,  # 成交额
                })
            except (ValueError, IndexError) as e:
                logger.warning(f"解析历史数据失败: {line}, 错误: {e}")
                continue
        
        return result
    
    # ========== 板块数据API ==========
    
    async def get_sector_capital_flow(
        self,
        sector_type: str = 'industry'  # industry-行业, concept-概念, area-地域
    ) -> Optional[Dict]:
        """
        获取板块资金流向
        
        Args:
            sector_type: 板块类型
            
        Returns:
            板块资金流向数据
        """
        sector_map = {
            'industry': 'm:90+t:2',
            'concept': 'm:90+t:3',
            'area': 'm:90+t:1'
        }
        
        url = f"{self.base_url}/api/qt/clist/get"
        params = {
            'fid': 'f62',
            'po': 1,
            'pz': 100,
            'pn': 1,
            'np': 1,
            'fltt': 2,
            'invt': 2,
            'fs': sector_map.get(sector_type, 'm:90+t:2'),
            'fields': 'f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f124,f128'
        }
        
        return await self._request(url, params)
    
    # ========== 工具方法 ==========
    
    def parse_rank_data(self, raw_data: Dict) -> List[Dict]:
        """
        解析排行榜数据
        
        Args:
            raw_data: 原始API返回数据
            
        Returns:
            解析后的股票列表
        """
        if not raw_data or 'diff' not in raw_data:
            return []
        
        stocks = []
        for item in raw_data['diff']:
            try:
                stock = {
                    'stock_code': item.get('f12', ''),  # 股票代码
                    'stock_name': item.get('f14', ''),   # 股票名称
                    'market_code': item.get('f1', ''),    # 市场代码
                    'exchange': item.get('f13', ''),      # 交易所代码
                    'current_price': item.get('f2', 0),  # 最新价
                    'change_percent': item.get('f3', 0), # 涨跌幅
                    'main_inflow': item.get('f62', 0),  # 今日主力净流入
                    'main_inflow_rate': item.get('f184', 0),  # 今日主力净流入占比
                    'super_inflow': item.get('f66', 0),  # 今日超大单净流入
                    'super_inflow_rate': item.get('f69', 0),  # 今日超大单净流入占比
                    'large_inflow': item.get('f72', 0),  # 今日大单净流入
                    'large_inflow_rate': item.get('f75', 0),  # 今日大单净流入占比
                    'medium_inflow': item.get('f78', 0),  # 今日中单净流入
                    'medium_inflow_rate': item.get('f81', 0),  # 今日中单净流入占比
                    'small_inflow': item.get('f84', 0),  # 今日小单净流入
                    'small_inflow_rate': item.get('f87', 0),  # 今日小单净流入占比
                    'net_inflow_5d': item.get('f204', 0),  # 5日主力净流入
                    'net_inflow_10d': item.get('f205', 0),  # 10日主力净流入
                    'timestamp': item.get('f124', 0),  # 时间戳
                }
                stocks.append(stock)
            except Exception as e:
                logger.warning(f"解析排行榜数据失败: {item}, 错误: {e}")
                continue
        
        return stocks

