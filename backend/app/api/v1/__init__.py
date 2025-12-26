"""
API v1 路由
"""
from fastapi import APIRouter
from app.api.v1 import capital_flow, stocks, auth, holdings, watchlist

router = APIRouter()

# 注册子路由
router.include_router(auth.router)
router.include_router(capital_flow.router)
router.include_router(stocks.router)
router.include_router(holdings.router)
router.include_router(watchlist.router)


@router.get("/")
async def api_v1_root():
    """API v1 根路径"""
    return {"message": "API v1", "version": "1.0.0"}

