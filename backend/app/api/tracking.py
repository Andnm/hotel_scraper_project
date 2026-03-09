from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.database.repositories import TrackingRepository
from app.core.database import get_db

router = APIRouter()
tracking_repo = TrackingRepository(get_db())


class TrackingDataRequest(BaseModel):
    history_id: int
    year: int
    month: int
    market: str
    cluster: str
    breakfast: str
    room_group: str
    level: str
    compare_history_id: Optional[int] = None


@router.get("/history-list")
async def get_tracking_history_list():
    """
    Lấy danh sách các phiên cào với type = 'price'
    """
    try:
        histories = tracking_repo.get_price_crawl_histories()
        return {
            "success": True,
            "data": histories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data")
async def get_tracking_data(request: TrackingDataRequest):
    """
    Lấy dữ liệu tracking với filters
    """
    try:
        # Validate month
        if request.month < 1 or request.month > 12:
            raise HTTPException(status_code=400, detail="Tháng không hợp lệ")
        
        # Get main data
        main_data = tracking_repo.get_tracking_data(
            history_id=request.history_id,
            year=request.year,
            month=request.month,
            market=request.market,
            cluster=request.cluster,
            breakfast=request.breakfast,
            room_group=request.room_group,
            level=request.level
        )
        
        # Get compare data if requested
        compare_data = None
        if request.compare_history_id:
            compare_data = tracking_repo.get_tracking_data(
                history_id=request.compare_history_id,
                year=request.year,
                month=request.month,
                market=request.market,
                cluster=request.cluster,
                breakfast=request.breakfast,
                room_group=request.room_group,
                level=request.level
            )
        
        # Generate date columns for the month
        date_columns = tracking_repo.generate_month_dates(request.year, request.month)
        
        return {
            "success": True,
            "data": {
                "main": main_data,
                "compare": compare_data,
                "date_columns": date_columns
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
