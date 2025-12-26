"""
持股和收藏相关数据模型
"""
from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

Decimal = Numeric


class Holding(Base):
    """用户持股表"""
    __tablename__ = "holdings"
    
    holding_id = Column(Integer, primary_key=True, autoincrement=True, comment='持股ID')
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, comment='用户ID')
    stock_id = Column(Integer, ForeignKey('stocks.stock_id'), nullable=False, comment='股票ID')
    stock_code = Column(String(10), nullable=False, comment='股票代码（冗余字段，便于查询）')
    cost_price = Column(Decimal(10, 3), nullable=False, comment='成本价')
    quantity = Column(Integer, nullable=False, comment='持股数量（股）')
    buy_date = Column(Date, comment='买入日期')
    notes = Column(Text, comment='备注')
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', comment='更新时间')


class Watchlist(Base):
    """用户收藏表"""
    __tablename__ = "watchlist"
    
    watch_id = Column(Integer, primary_key=True, autoincrement=True, comment='收藏ID')
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, comment='用户ID')
    stock_id = Column(Integer, ForeignKey('stocks.stock_id'), nullable=False, comment='股票ID')
    stock_code = Column(String(10), nullable=False, comment='股票代码（冗余字段，便于查询）')
    notes = Column(Text, comment='备注')
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', comment='更新时间')

