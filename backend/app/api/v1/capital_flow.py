"""
资金流向相关API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import date, datetime, timedelta
from loguru import logger

from app.core.database import get_db
from app.models.stock import Stock, CapitalFlow
from app.services.eastmoney_api import EastMoneyAPI
from app.core.config import settings

router = APIRouter(prefix="/capital-flow", tags=["资金流向"])


@router.get("/rank")
async def get_capital_flow_rank(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页数量"),
    sort_field: str = Query("f62", description="排序字段: f62-今日主力, f204-5日主力, f205-10日主力"),
    db: Session = Depends(get_db)
):
    """
    获取资金流向排行榜
    
    从东方财富API获取实时排行榜数据
    """
    try:
        api = EastMoneyAPI()
        
        # 获取实时排行榜数据
        raw_data = await api.get_realtime_capital_flow_rank(
            page=page,
            page_size=page_size,
            sort_field=sort_field
        )
        
        await api.close()
        
        if not raw_data:
            return {
                "code": 500,
                "message": "获取数据失败",
                "data": []
            }
        
        # 解析数据
        stocks = api.parse_rank_data(raw_data)
        
        # 获取总数（如果有）
        total = raw_data.get("total", len(stocks))
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "items": stocks,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "data": []
        }


@router.get("/stock/{stock_code}")
async def get_stock_capital_flow(
    stock_code: str,
    days: int = Query(30, ge=1, le=365, description="查询天数"),
    db: Session = Depends(get_db)
):
    """
    获取指定股票的资金流向数据
    
    优先从数据库查询，如果没有则从API获取并保存
    """
    try:
        # 从数据库查询股票信息
        stock = db.query(Stock).filter(Stock.stock_code == stock_code).first()
        
        # 如果数据库没有股票，先尝试从排行榜API获取并保存
        if not stock:
            try:
                api = EastMoneyAPI()
                raw_data = await api.get_realtime_capital_flow_rank(
                    page=1,
                    page_size=100,
                    sort_field='f62'
                )
                await api.close()
                
                if raw_data and 'diff' in raw_data:
                    for item in raw_data['diff']:
                        if item.get('f12') == stock_code:
                            parsed_item = api.parse_rank_data({'diff': [item]})
                            if parsed_item:
                                # 保存股票信息
                                stock_code_val = parsed_item[0].get('stock_code', '')
                                stock_name = parsed_item[0].get('stock_name', '')
                                exchange_code = parsed_item[0].get('exchange', '')
                                market_code = parsed_item[0].get('market_code', '')
                                
                                if exchange_code == '1' or (market_code and market_code.startswith('1')):
                                    exchange = 'SH'
                                    market = '1'
                                else:
                                    exchange = 'SZ'
                                    market = '0'
                                
                                secid = f"{market}.{stock_code_val}"
                                
                                stock = db.query(Stock).filter(Stock.stock_code == stock_code_val).first()
                                if stock:
                                    stock.stock_name = stock_name
                                    stock.exchange = exchange
                                    stock.market_code = market
                                    stock.secid = secid
                                    stock.last_sync_at = datetime.now()
                                else:
                                    stock = Stock(
                                        stock_code=stock_code_val,
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
                                break
                
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
        
        # 计算查询日期范围
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # 从数据库查询资金流向数据
        flows = db.query(CapitalFlow).filter(
            CapitalFlow.stock_id == stock.stock_id,
            CapitalFlow.trade_date >= start_date,
            CapitalFlow.trade_date <= end_date
        ).order_by(desc(CapitalFlow.trade_date)).all()
        
        # 如果数据库没有历史数据，从API获取
        if not flows:
            try:
                api = EastMoneyAPI()
                market = 'sh' if stock.exchange == 'SH' else 'sz'
                history_data = await api.get_stock_capital_flow_history(
                    stock_code=stock_code,
                    market=market
                )
                await api.close()
                
                # 保存历史数据到数据库
                if history_data:
                    from datetime import datetime as dt
                    for item in history_data:
                        trade_date_str = item.get('trade_date', '')
                        if trade_date_str:
                            try:
                                trade_date = dt.strptime(trade_date_str, '%Y-%m-%d').date()
                                if start_date <= trade_date <= end_date:
                                    # 检查是否已存在
                                    existing = db.query(CapitalFlow).filter(
                                        CapitalFlow.stock_id == stock.stock_id,
                                        CapitalFlow.trade_date == trade_date
                                    ).first()
                                    
                                    if not existing:
                                        flow = CapitalFlow(
                                            stock_id=stock.stock_id,
                                            trade_date=trade_date,
                                            main_inflow=item.get('main_inflow', 0),
                                            main_inflow_rate=item.get('main_inflow_rate', 0),
                                            super_inflow=item.get('super_inflow', 0),
                                            super_inflow_rate=item.get('super_inflow_rate', 0),
                                            large_inflow=item.get('large_inflow', 0),
                                            large_inflow_rate=item.get('large_inflow_rate', 0),
                                            medium_inflow=item.get('medium_inflow', 0),
                                            medium_inflow_rate=item.get('medium_inflow_rate', 0),
                                            small_inflow=item.get('small_inflow', 0),
                                            small_inflow_rate=item.get('small_inflow_rate', 0),
                                            close_price=item.get('close_price', 0),
                                            change_percent=item.get('change_percent', 0),
                                            volume=item.get('volume', 0),
                                            amount=item.get('amount', 0),
                                        )
                                        db.add(flow)
                            except Exception as e:
                                logger.warning(f"保存历史数据失败: {e}")
                                continue
                    
                    db.commit()
                    
                    # 重新查询
                    flows = db.query(CapitalFlow).filter(
                        CapitalFlow.stock_id == stock.stock_id,
                        CapitalFlow.trade_date >= start_date,
                        CapitalFlow.trade_date <= end_date
                    ).order_by(desc(CapitalFlow.trade_date)).all()
            except Exception as e:
                logger.warning(f"从API获取历史数据失败: {e}")
        
        # 转换为字典格式
        flow_list = []
        for flow in flows:
            flow_list.append({
                "trade_date": flow.trade_date.isoformat(),
                "main_inflow": float(flow.main_inflow) if flow.main_inflow else 0,
                "main_inflow_rate": float(flow.main_inflow_rate) if flow.main_inflow_rate else 0,
                "super_inflow": float(flow.super_inflow) if flow.super_inflow else 0,
                "super_inflow_rate": float(flow.super_inflow_rate) if flow.super_inflow_rate else 0,
                "large_inflow": float(flow.large_inflow) if flow.large_inflow else 0,
                "large_inflow_rate": float(flow.large_inflow_rate) if flow.large_inflow_rate else 0,
                "medium_inflow": float(flow.medium_inflow) if flow.medium_inflow else 0,
                "medium_inflow_rate": float(flow.medium_inflow_rate) if flow.medium_inflow_rate else 0,
                "small_inflow": float(flow.small_inflow) if flow.small_inflow else 0,
                "small_inflow_rate": float(flow.small_inflow_rate) if flow.small_inflow_rate else 0,
                "close_price": float(flow.close_price) if flow.close_price else 0,
                "change_percent": float(flow.change_percent) if flow.change_percent else 0,
                "volume": int(flow.volume) if flow.volume else 0,
                "amount": float(flow.amount) if flow.amount else 0,
            })
        
        return {
            "code": 200,
            "message": "success",
            "data": {
                "stock": {
                    "stock_id": stock.stock_id,
                    "stock_code": stock.stock_code,
                    "stock_name": stock.stock_name,
                    "exchange": stock.exchange,
                },
                "flows": flow_list,
                "total": len(flow_list)
            }
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "data": None
        }

