"""
持股管理相关API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

from app.core.database import get_db
from app.models.user import User
from app.models.holding import Holding, Watchlist
from app.models.stock import Stock
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/holdings", tags=["持股管理"])


# Pydantic模型
class HoldingCreate(BaseModel):
    """创建持股模型"""
    stock_code: str
    cost_price: float
    quantity: int
    buy_date: Optional[date] = None
    notes: Optional[str] = None


class HoldingUpdate(BaseModel):
    """更新持股模型"""
    cost_price: Optional[float] = None
    quantity: Optional[int] = None
    buy_date: Optional[date] = None
    notes: Optional[str] = None


class HoldingResponse(BaseModel):
    """持股响应模型"""
    holding_id: int
    stock_code: str
    stock_name: str
    cost_price: float
    quantity: int
    buy_date: Optional[date] = None
    current_price: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_rate: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[HoldingResponse])
async def get_holdings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的持股列表
    """
    holdings = db.query(Holding).filter(
        Holding.user_id == current_user.user_id
    ).all()
    
    result = []
    for holding in holdings:
        stock = db.query(Stock).filter(Stock.stock_id == holding.stock_id).first()
        
        # 获取当前价格（从排行榜API获取）
        from app.services.eastmoney_api import EastMoneyAPI
        api = EastMoneyAPI()
        try:
            raw_data = await api.get_realtime_capital_flow_rank(page=1, page_size=100)
            current_price = None
            if raw_data and 'diff' in raw_data:
                for item in raw_data['diff']:
                    if item.get('f12') == holding.stock_code:
                        current_price = item.get('f2', 0)
                        break
        except:
            current_price = None
        finally:
            await api.close()
        
        # 计算盈亏
        profit_loss = None
        profit_loss_rate = None
        if current_price:
            total_cost = float(holding.cost_price) * holding.quantity
            total_value = current_price * holding.quantity
            profit_loss = total_value - total_cost
            profit_loss_rate = (profit_loss / total_cost * 100) if total_cost > 0 else 0
        
        result.append({
            "holding_id": holding.holding_id,
            "stock_code": holding.stock_code,
            "stock_name": stock.stock_name if stock else holding.stock_code,
            "cost_price": float(holding.cost_price),
            "quantity": holding.quantity,
            "buy_date": holding.buy_date,
            "current_price": current_price,
            "profit_loss": profit_loss,
            "profit_loss_rate": profit_loss_rate,
            "notes": holding.notes,
            "created_at": holding.created_at.isoformat() if holding.created_at else None
        })
    
    return result


@router.post("", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
async def create_holding(
    holding_data: HoldingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    添加持股
    """
    # 查找股票
    stock = db.query(Stock).filter(Stock.stock_code == holding_data.stock_code).first()
    
    if not stock:
        # 如果数据库没有，尝试从API获取
        from app.services.eastmoney_api import EastMoneyAPI
        from datetime import datetime
        api = EastMoneyAPI()
        try:
            raw_data = await api.get_realtime_capital_flow_rank(page=1, page_size=100)
            if raw_data and 'diff' in raw_data:
                for item in raw_data['diff']:
                    if item.get('f12') == holding_data.stock_code:
                        parsed = api.parse_rank_data({'diff': [item]})
                        if parsed:
                            # 保存股票信息
                            stock_item = parsed[0]
                            exchange_code = stock_item.get('exchange', '')
                            market_code = stock_item.get('market_code', '')
                            
                            if exchange_code == '1' or (market_code and market_code.startswith('1')):
                                exchange = 'SH'
                                market = '1'
                            else:
                                exchange = 'SZ'
                                market = '0'
                            
                            secid = f"{market}.{holding_data.stock_code}"
                            
                            stock = Stock(
                                stock_code=holding_data.stock_code,
                                stock_name=stock_item.get('stock_name', ''),
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
        finally:
            await api.close()
        
        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="股票不存在"
            )
    
    # 检查是否已存在
    existing = db.query(Holding).filter(
        Holding.user_id == current_user.user_id,
        Holding.stock_code == holding_data.stock_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该股票已在持股列表中"
        )
    
    # 创建持股记录
    holding = Holding(
        user_id=current_user.user_id,
        stock_id=stock.stock_id,
        stock_code=holding_data.stock_code,
        cost_price=holding_data.cost_price,
        quantity=holding_data.quantity,
        buy_date=holding_data.buy_date,
        notes=holding_data.notes
    )
    
    db.add(holding)
    db.commit()
    db.refresh(holding)
    
    return {
        "holding_id": holding.holding_id,
        "stock_code": holding.stock_code,
        "stock_name": stock.stock_name,
        "cost_price": float(holding.cost_price),
        "quantity": holding.quantity,
        "buy_date": holding.buy_date,
        "current_price": None,
        "profit_loss": None,
        "profit_loss_rate": None,
        "notes": holding.notes,
        "created_at": holding.created_at.isoformat() if holding.created_at else None
    }


@router.put("/{holding_id}", response_model=HoldingResponse)
async def update_holding(
    holding_id: int,
    holding_data: HoldingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新持股信息
    """
    holding = db.query(Holding).filter(
        Holding.holding_id == holding_id,
        Holding.user_id == current_user.user_id
    ).first()
    
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="持股记录不存在"
        )
    
    if holding_data.cost_price is not None:
        holding.cost_price = holding_data.cost_price
    if holding_data.quantity is not None:
        holding.quantity = holding_data.quantity
    if holding_data.buy_date is not None:
        holding.buy_date = holding_data.buy_date
    if holding_data.notes is not None:
        holding.notes = holding_data.notes
    
    db.commit()
    db.refresh(holding)
    
    stock = db.query(Stock).filter(Stock.stock_id == holding.stock_id).first()
    
    return {
        "holding_id": holding.holding_id,
        "stock_code": holding.stock_code,
        "stock_name": stock.stock_name if stock else holding.stock_code,
        "cost_price": float(holding.cost_price),
        "quantity": holding.quantity,
        "buy_date": holding.buy_date,
        "current_price": None,
        "profit_loss": None,
        "profit_loss_rate": None,
        "notes": holding.notes,
        "created_at": holding.created_at.isoformat() if holding.created_at else None
    }


@router.delete("/{holding_id}")
async def delete_holding(
    holding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除持股
    """
    holding = db.query(Holding).filter(
        Holding.holding_id == holding_id,
        Holding.user_id == current_user.user_id
    ).first()
    
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="持股记录不存在"
        )
    
    db.delete(holding)
    db.commit()
    
    return {"message": "删除成功"}

