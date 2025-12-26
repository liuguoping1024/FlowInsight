"""
股票相关API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.models.stock import Stock
from app.services.eastmoney_api import EastMoneyAPI

router = APIRouter(prefix="/stocks", tags=["股票"])


def _save_stock_from_rank_data(db: Session, rank_item: dict) -> Stock:
    """
    从排行榜数据保存股票信息到数据库
    """
    stock_code = rank_item.get('stock_code', '')
    stock_name = rank_item.get('stock_name', '')
    exchange_code = rank_item.get('exchange', '')
    market_code = rank_item.get('market_code', '')
    
    # 判断交易所
    if exchange_code == '1' or (market_code and market_code.startswith('1')):
        exchange = 'SH'
        market = '1'
    else:
        exchange = 'SZ'
        market = '0'
    
    secid = f"{market}.{stock_code}"
    
    # 检查是否已存在
    stock = db.query(Stock).filter(Stock.stock_code == stock_code).first()
    if stock:
        # 更新信息
        stock.stock_name = stock_name
        stock.exchange = exchange
        stock.market_code = market
        stock.secid = secid
        stock.last_sync_at = datetime.now()
    else:
        # 创建新记录
        stock = Stock(
            stock_code=stock_code,
            stock_name=stock_name,
            exchange=exchange,
            market_code=market,
            secid=secid,
            status='normal',
            last_sync_at=datetime.now()
        )
        db.add(stock)
    
    db.commit()
    db.refresh(stock)
    return stock


@router.get("/{stock_code}")
async def get_stock_detail(
    stock_code: str,
    db: Session = Depends(get_db)
):
    """
    获取股票详情
    
    如果数据库没有，从排行榜API获取并保存
    """
    try:
        stock = db.query(Stock).filter(Stock.stock_code == stock_code).first()
        
        # 如果数据库没有，尝试从排行榜API获取
        if not stock:
            try:
                api = EastMoneyAPI()
                # 获取排行榜数据（只获取第一页，查找目标股票）
                raw_data = await api.get_realtime_capital_flow_rank(
                    page=1,
                    page_size=100,
                    sort_field='f62'
                )
                await api.close()
                
                if raw_data and 'diff' in raw_data:
                    # 在排行榜中查找目标股票
                    for item in raw_data['diff']:
                        if item.get('f12') == stock_code:
                            # 解析并保存
                            parsed_item = api.parse_rank_data({'diff': [item]})
                            if parsed_item:
                                stock = _save_stock_from_rank_data(db, parsed_item[0])
                                break
                
                # 如果还是没找到，返回404
                if not stock:
                    return {
                        "code": 404,
                        "message": "股票不存在",
                        "data": None
                    }
            except Exception as e:
                return {
                    "code": 500,
                    "message": f"获取股票信息失败: {str(e)}",
                    "data": None
                }
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "stock_id": stock.stock_id,
                "stock_code": stock.stock_code,
                "stock_name": stock.stock_name,
                "exchange": stock.exchange,
                "industry": stock.industry,
                "area": stock.area,
                "market_cap": float(stock.market_cap) if stock.market_cap else None,
                "circulation_cap": float(stock.circulation_cap) if stock.circulation_cap else None,
                "pe_ratio": float(stock.pe_ratio) if stock.pe_ratio else None,
                "pb_ratio": float(stock.pb_ratio) if stock.pb_ratio else None,
                "status": stock.status,
            }
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "data": None
        }


@router.get("/{stock_code}/capital-flow")
async def get_stock_capital_flow_history(
    stock_code: str,
    days: int = Query(30, ge=1, le=365, description="查询天数"),
    db: Session = Depends(get_db)
):
    """
    获取股票资金流向历史数据
    
    这个接口会重定向到 /capital-flow/stock/{stock_code}
    """
    from app.api.v1.capital_flow import get_stock_capital_flow
    return await get_stock_capital_flow(stock_code, days, db)

