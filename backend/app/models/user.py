"""
用户相关数据模型
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = Column(String(50), unique=True, nullable=False, comment='用户名')
    password_hash = Column(String(255), nullable=False, comment='密码哈希值')
    email = Column(String(100), unique=True, comment='邮箱')
    phone = Column(String(20), comment='手机号')
    real_name = Column(String(50), comment='真实姓名')
    avatar_url = Column(String(255), comment='头像URL')
    status = Column(String(20), default='active', comment='账户状态: active-激活, disabled-禁用, locked-锁定')
    last_login_at = Column(TIMESTAMP, comment='最后登录时间')
    last_login_ip = Column(String(50), comment='最后登录IP')
    login_count = Column(Integer, default=0, comment='登录次数统计')
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', comment='更新时间')
    created_by = Column(Integer, ForeignKey('users.user_id'), comment='创建者用户ID')
    remarks = Column(Text, comment='备注信息')


class UserGroup(Base):
    """用户组表"""
    __tablename__ = "user_groups"
    
    group_id = Column(Integer, primary_key=True, autoincrement=True, comment='组ID')
    group_code = Column(String(50), unique=True, nullable=False, comment='组代码: user, admin')
    group_name = Column(String(100), nullable=False, comment='组名称')
    group_level = Column(Integer, default=1, comment='组级别: 1-普通用户, 99-管理员')
    permissions = Column(JSON, comment='权限列表,JSON格式')
    description = Column(Text, comment='组描述')
    is_system = Column(Boolean, default=False, comment='是否系统组')
    status = Column(String(20), default='active', comment='状态: active-启用, disabled-禁用')
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', comment='更新时间')


class UserGroupRelation(Base):
    """用户组关系表"""
    __tablename__ = "user_group_relations"
    
    relation_id = Column(Integer, primary_key=True, autoincrement=True, comment='关系ID')
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, comment='用户ID')
    group_id = Column(Integer, ForeignKey('user_groups.group_id'), nullable=False, comment='组ID')
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', comment='创建时间')

