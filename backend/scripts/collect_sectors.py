#!/usr/bin/env python3
"""
板块信息采集脚本
从东方财富API获取板块信息并保存到数据库
"""
import sys
import os
import asyncio
from pathlib import Path
import json

# 添加项目根目录到路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import SessionLocal
from app.models.sector import Sector
from app.services.eastmoney_api import EastMoneyAPI
from loguru import logger

# 配置日志
logger.add("logs/collect_sectors.log", rotation="10 MB", level="INFO")


def save_sector_from_api_data(db: Session, sector_item: dict, sector_type: str) -> Sector:
    """
    从API数据保存板块信息到数据库
    """
    sector_code = sector_item.get('f12', '')  # 板块代码
    sector_name = sector_item.get('f14', '')   # 板块名称
    
    if not sector_code or not sector_name:
        return None
    
    # 检查是否已存在
    sector = db.query(Sector).filter(
        Sector.sector_code == sector_code,
        Sector.sector_type == sector_type
    ).first()
    
    if sector:
        # 更新信息
        sector.sector_name = sector_name
        sector.updated_at = datetime.now()
        logger.info(f"更新板块: {sector_code} {sector_name}")
    else:
        # 创建新记录
        sector = Sector(
            sector_code=sector_code,
            sector_name=sector_name,
            sector_type=sector_type,
            status='active',
            stock_count=0
        )
        db.add(sector)
        logger.info(f"新增板块: {sector_code} {sector_name}")
    
    return sector


async def collect_sectors(sector_type: str = 'industry'):
    """
    采集板块信息
    
    Args:
        sector_type: 板块类型 (industry/concept/area)
    """
    db = SessionLocal()
    api = EastMoneyAPI()
    
    try:
        total_collected = 0
        total_updated = 0
        
        logger.info(f"开始采集 {sector_type} 板块信息...")
        
        # 获取板块数据
        raw_data = await api.get_sector_capital_flow(sector_type=sector_type)
        
        if not raw_data or 'diff' not in raw_data:
            logger.warning(f"{sector_type} 板块数据为空")
            return
        
        # 解析数据
        sectors_data = raw_data['diff']
        
        logger.info(f"获取到 {len(sectors_data)} 个板块")
        
        # 保存到数据库
        for sector_item in sectors_data:
            try:
                existing = db.query(Sector).filter(
                    Sector.sector_code == sector_item.get('f12', ''),
                    Sector.sector_type == sector_type
                ).first()
                
                if existing:
                    total_updated += 1
                else:
                    total_collected += 1
                
                save_sector_from_api_data(db, sector_item, sector_type)
                db.commit()
            except Exception as e:
                logger.error(f"保存板块失败 {sector_item.get('f12', 'unknown')}: {e}")
                db.rollback()
                continue
        
        logger.info(f"{sector_type} 板块采集完成！新增: {total_collected}, 更新: {total_updated}")
        
    except Exception as e:
        logger.error(f"采集过程出错: {e}")
        raise
    finally:
        await api.close()
        db.close()


async def collect_all_sectors():
    """采集所有类型的板块"""
    sector_types = ['industry', 'concept', 'area']
    
    for sector_type in sector_types:
        try:
            await collect_sectors(sector_type)
            await asyncio.sleep(2)  # 避免请求过快
        except Exception as e:
            logger.error(f"采集 {sector_type} 板块失败: {e}")
            continue


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="板块信息采集脚本")
    parser.add_argument(
        "--type",
        type=str,
        choices=['industry', 'concept', 'area', 'all'],
        default='all',
        help="板块类型: industry(行业), concept(概念), area(地域), all(全部)"
    )
    
    args = parser.parse_args()
    
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    # 运行采集
    if args.type == 'all':
        asyncio.run(collect_all_sectors())
    else:
        asyncio.run(collect_sectors(args.type))

