"""
板块相关数据模型
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Sector(Base):
    """板块信息表"""
    __tablename__ = "sectors"
    
    sector_id = Column(Integer, primary_key=True, autoincrement=True, comment='板块ID')
    sector_code = Column(String(20), unique=True, nullable=False, comment='板块代码')
    sector_name = Column(String(100), nullable=False, comment='板块名称')
    sector_type = Column(String(20), nullable=False, comment='板块类型: industry-行业, concept-概念, area-地域')
    parent_sector_id = Column(Integer, ForeignKey('sectors.sector_id'), comment='父板块ID')
    stock_count = Column(Integer, default=0, comment='包含股票数量')
    stock_codes = Column(Text, comment='包含的股票代码列表,逗号分隔')
    leading_stocks = Column(JSON, comment='龙头股信息,JSON数组')
    description = Column(Text, comment='板块描述')
    hot_rank = Column(Integer, comment='热度排名')
    status = Column(String(20), default='active', comment='状态: active-活跃, inactive-不活跃')
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', comment='更新时间')
    
    # 关系
    # parent_sector = relationship("Sector", remote_side=[sector_id])

