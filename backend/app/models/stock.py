"""
股票相关数据模型
"""
from sqlalchemy import Column, Integer, String, Date, Boolean, Text, TIMESTAMP, BIGINT, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

# SQLAlchemy 2.0中使用Numeric替代Decimal
Decimal = Numeric


class Stock(Base):
    """股票基础信息表"""
    __tablename__ = "stocks"
    
    stock_id = Column(Integer, primary_key=True, autoincrement=True, comment='股票ID')
    stock_code = Column(String(10), nullable=False, comment='股票代码')
    stock_name = Column(String(50), nullable=False, comment='股票名称')
    exchange = Column(String(10), nullable=False, comment='交易所: SH-上海, SZ-深圳')
    market_code = Column(String(5), nullable=False, comment='市场代码: 1-沪市, 0-深市')
    secid = Column(String(20), unique=True, nullable=False, comment='东财证券ID')
    industry = Column(String(50), comment='所属行业')
    industry_code = Column(String(20), comment='行业代码')
    concept = Column(Text, comment='所属概念')
    area = Column(String(50), comment='所属地区')
    market_cap = Column(Decimal(20, 2), comment='总市值')
    circulation_cap = Column(Decimal(20, 2), comment='流通市值')
    total_shares = Column(BIGINT, comment='总股本')
    circulation_shares = Column(BIGINT, comment='流通股本')
    listing_date = Column(Date, comment='上市日期')
    pe_ratio = Column(Decimal(10, 4), comment='市盈率')
    pb_ratio = Column(Decimal(10, 4), comment='市净率')
    status = Column(String(20), default='normal', comment='状态')
    is_st = Column(Boolean, default=False, comment='是否ST股')
    is_star = Column(Boolean, default=False, comment='是否科创板')
    is_gem = Column(Boolean, default=False, comment='是否创业板')
    last_sync_at = Column(TIMESTAMP, comment='最后同步时间')
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', comment='更新时间')
    remarks = Column(Text, comment='备注')
    
    # 关系（暂时注释，避免SQLAlchemy关系错误）
    # capital_flows = relationship("CapitalFlow", back_populates="stock", foreign_keys="CapitalFlow.stock_id")


class CapitalFlow(Base):
    """资金流向数据表"""
    __tablename__ = "capital_flow"
    
    flow_id = Column(BIGINT, primary_key=True, autoincrement=True, comment='流向ID')
    stock_id = Column(Integer, nullable=False, comment='股票ID')
    trade_date = Column(Date, nullable=False, comment='交易日期')
    
    # 主力资金数据
    main_inflow = Column(Decimal(15, 2), comment='主力净流入')
    main_inflow_rate = Column(Decimal(8, 4), comment='主力净流入占比')
    
    # 超大单数据
    super_inflow = Column(Decimal(15, 2), comment='超大单净流入')
    super_inflow_rate = Column(Decimal(8, 4), comment='超大单净流入占比')
    
    # 大单数据
    large_inflow = Column(Decimal(15, 2), comment='大单净流入')
    large_inflow_rate = Column(Decimal(8, 4), comment='大单净流入占比')
    
    # 中单数据
    medium_inflow = Column(Decimal(15, 2), comment='中单净流入')
    medium_inflow_rate = Column(Decimal(8, 4), comment='中单净流入占比')
    
    # 小单数据
    small_inflow = Column(Decimal(15, 2), comment='小单净流入')
    small_inflow_rate = Column(Decimal(8, 4), comment='小单净流入占比')
    
    # 价格数据
    open_price = Column(Decimal(10, 3), comment='开盘价')
    high_price = Column(Decimal(10, 3), comment='最高价')
    low_price = Column(Decimal(10, 3), comment='最低价')
    close_price = Column(Decimal(10, 3), comment='收盘价')
    pre_close_price = Column(Decimal(10, 3), comment='昨收价')
    change_amount = Column(Decimal(10, 3), comment='涨跌额')
    change_percent = Column(Decimal(8, 4), comment='涨跌幅')
    
    # 成交数据
    volume = Column(BIGINT, comment='成交量')
    amount = Column(Decimal(20, 2), comment='成交额')
    turnover_rate = Column(Decimal(8, 4), comment='换手率')
    volume_ratio = Column(Decimal(10, 4), comment='量比')
    amplitude = Column(Decimal(8, 4), comment='振幅')
    
    # 元数据
    data_source = Column(String(50), default='eastmoney', comment='数据来源')
    is_valid = Column(Boolean, default=True, comment='数据是否有效')
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', comment='更新时间')
    
    # 关系（暂时注释，避免SQLAlchemy关系错误）
    # stock = relationship("Stock", back_populates="capital_flows", foreign_keys=[stock_id])

