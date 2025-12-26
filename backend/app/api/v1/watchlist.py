"""
收藏列表相关API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User
from app.models.holding import Watchlist
from app.models.stock import Stock
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/watchlist", tags=["收藏列表"])


# Pydantic模型
class WatchlistItem(BaseModel):
    """收藏项模型"""
    watch_id: int
    stock_code: str
    stock_name: str
    current_price: Optional[float] = None
    change_percent: Optional[float] = None
    main_inflow: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class WatchlistCreate(BaseModel):
    """创建收藏模型"""
    stock_code: str
    notes: Optional[str] = None


@router.get("", response_model=List[WatchlistItem])
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的收藏列表
    """
    watchlist = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.user_id
    ).all()
    
    result = []
    for item in watchlist:
        stock = db.query(Stock).filter(Stock.stock_id == item.stock_id).first()
        
        # 获取实时数据
        from app.services.eastmoney_api import EastMoneyAPI
        api = EastMoneyAPI()
        try:
            raw_data = await api.get_realtime_capital_flow_rank(page=1, page_size=100)
            current_price = None
            change_percent = None
            main_inflow = None
            
            if raw_data and 'diff' in raw_data:
                for stock_item in raw_data['diff']:
                    if stock_item.get('f12') == item.stock_code:
                        current_price = stock_item.get('f2', 0)
                        change_percent = stock_item.get('f3', 0)
                        main_inflow = stock_item.get('f62', 0)
                        break
        except:
            pass
        finally:
            await api.close()
        
        result.append({
            "watch_id": item.watch_id,
            "stock_code": item.stock_code,
            "stock_name": stock.stock_name if stock else item.stock_code,
            "current_price": current_price,
            "change_percent": change_percent,
            "main_inflow": main_inflow,
            "notes": item.notes,
            "created_at": item.created_at.isoformat() if item.created_at else None
        })
    
    return result


@router.post("", response_model=WatchlistItem, status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    watchlist_data: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    添加收藏
    """
    # 查找股票
    stock = db.query(Stock).filter(Stock.stock_code == watchlist_data.stock_code).first()
    
    if not stock:
        # 如果数据库没有，尝试从API获取
        from app.services.eastmoney_api import EastMoneyAPI
        from datetime import datetime
        api = EastMoneyAPI()
        try:
            raw_data = await api.get_realtime_capital_flow_rank(page=1, page_size=100)
            if raw_data and 'diff' in raw_data:
                for item in raw_data['diff']:
                    if item.get('f12') == watchlist_data.stock_code:
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
                            
                            secid = f"{market}.{watchlist_data.stock_code}"
                            
                            stock = Stock(
                                stock_code=watchlist_data.stock_code,
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
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.user_id,
        Watchlist.stock_code == watchlist_data.stock_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该股票已在收藏列表中"
        )
    
    # 创建收藏记录
    watchlist_item = Watchlist(
        user_id=current_user.user_id,
        stock_id=stock.stock_id,
        stock_code=watchlist_data.stock_code,
        notes=watchlist_data.notes
    )
    
    db.add(watchlist_item)
    db.commit()
    db.refresh(watchlist_item)
    
    return {
        "watch_id": watchlist_item.watch_id,
        "stock_code": watchlist_item.stock_code,
        "stock_name": stock.stock_name,
        "current_price": None,
        "change_percent": None,
        "main_inflow": None,
        "notes": watchlist_item.notes,
        "created_at": watchlist_item.created_at.isoformat() if watchlist_item.created_at else None
    }


@router.delete("/{watch_id}")
async def remove_from_watchlist(
    watch_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除收藏
    """
    watchlist_item = db.query(Watchlist).filter(
        Watchlist.watch_id == watch_id,
        Watchlist.user_id == current_user.user_id
    ).first()
    
    if not watchlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏记录不存在"
        )
    
    db.delete(watchlist_item)
    db.commit()
    
    return {"message": "删除成功"}

