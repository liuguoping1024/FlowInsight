#!/usr/bin/env python3
"""
股票基础信息采集脚本
从东方财富API获取股票列表并保存到数据库
"""
import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import SessionLocal
from app.models.stock import Stock
from app.services.eastmoney_api import EastMoneyAPI
from loguru import logger

# 配置日志
logger.add("logs/collect_stocks.log", rotation="10 MB", level="INFO")


def save_stock_from_rank_data(db: Session, rank_item: dict) -> Stock:
    """
    从排行榜数据保存股票信息到数据库
    """
    stock_code = rank_item.get('stock_code', '')
    stock_name = rank_item.get('stock_name', '')
    exchange_code = rank_item.get('exchange', '')
    market_code = rank_item.get('market_code', '')
    
    # 判断交易所
    market_code_str = str(market_code) if market_code else ''
    if exchange_code == '1' or (market_code_str and market_code_str.startswith('1')):
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
        logger.info(f"更新股票: {stock_code} {stock_name}")
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
        logger.info(f"新增股票: {stock_code} {stock_name}")
    
    return stock


async def collect_stocks_from_rank(max_pages: int = 10):
    """
    从排行榜API采集股票信息
    
    Args:
        max_pages: 最大采集页数（每页100条）
    """
    db = SessionLocal()
    api = EastMoneyAPI()
    
    try:
        total_collected = 0
        total_updated = 0
        
        logger.info(f"开始采集股票信息，最多采集 {max_pages} 页")
        
        for page in range(1, max_pages + 1):
            logger.info(f"正在采集第 {page} 页...")
            
            # 获取排行榜数据
            raw_data = await api.get_realtime_capital_flow_rank(
                page=page,
                page_size=100,
                sort_field='f62'
            )
            
            if not raw_data or 'diff' not in raw_data:
                logger.warning(f"第 {page} 页数据为空")
                break
            
            # 解析数据
            stocks = api.parse_rank_data(raw_data)
            
            if not stocks:
                logger.warning(f"第 {page} 页解析后数据为空")
                break
            
            # 保存到数据库
            for stock_item in stocks:
                try:
                    existing = db.query(Stock).filter(
                        Stock.stock_code == stock_item['stock_code']
                    ).first()
                    
                    if existing:
                        total_updated += 1
                    else:
                        total_collected += 1
                    
                    save_stock_from_rank_data(db, stock_item)
                    db.commit()
                except Exception as e:
                    logger.error(f"保存股票失败 {stock_item.get('stock_code', 'unknown')}: {e}")
                    db.rollback()
                    continue
            
            logger.info(f"第 {page} 页完成，本页采集 {len(stocks)} 只股票")
            
            # 避免请求过快
            await asyncio.sleep(1)
        
        logger.info(f"采集完成！新增: {total_collected}, 更新: {total_updated}, 总计: {total_collected + total_updated}")
        
    except Exception as e:
        logger.error(f"采集过程出错: {e}")
        raise
    finally:
        await api.close()
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="股票基础信息采集脚本")
    parser.add_argument(
        "--pages",
        type=int,
        default=10,
        help="采集页数（每页100条，默认10页）"
    )
    
    args = parser.parse_args()
    
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    # 运行采集
    asyncio.run(collect_stocks_from_rank(max_pages=args.pages))

