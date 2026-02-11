from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import date
from app.schemas.scraper import CrawlHistoryResponse, ApiDataQuery
from app.database.repositories import CrawlHistoryRepository, CrawlDataRepository
import json

router = APIRouter()

@router.get("/histories")
async def get_histories(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    source: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
):
    try:
        history_repo = CrawlHistoryRepository()
        
        total_count = history_repo.get_total_count(
            source_filter=source,
            date_from=date_from,
            date_to=date_to
        )
        
        offset = (page - 1) * page_size
        
        histories = history_repo.get_all_histories(
            limit=page_size,
            offset=offset,
            source_filter=source,
            date_from=date_from,
            date_to=date_to
        )
        
        return {
            'items': histories,
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/histories/{history_id}")
async def get_history_detail(
    history_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000)
):
    try:
        history_repo = CrawlHistoryRepository()
        data_repo = CrawlDataRepository()
        
        history = history_repo.get_history_by_id(history_id)
        if not history:
            raise HTTPException(status_code=404, detail="History not found")
        
        total_records = data_repo.get_data_count(history_id)
        offset = (page - 1) * page_size
        
        data_records = data_repo.get_data_by_history(
            history_id,
            limit=page_size,
            offset=offset
        )
        
        return {
            'history': history,
            'data': data_records,
            'total_records': total_records,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_records + page_size - 1) // page_size
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/histories/{history_id}")
async def delete_history(history_id: int):
    try:
        history_repo = CrawlHistoryRepository()
        history_repo.delete_history(history_id)
        return {'message': 'History deleted successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/{history_id}")
async def export_history_data(history_id: int):
    try:
        data_repo = CrawlDataRepository()
        records = data_repo.export_data_by_history(history_id)
        
        formatted_records = []
        for record in records:
            options = record.get('options', {})
            if isinstance(options, str):
                options = json.loads(options) if options else {}
            
            formatted_records.append({
                'Hàng_gốc': options.get('row_number', 'N/A'),
                'Ngày cào': record['crawl_date'].isoformat() if record.get('crawl_date') else 'N/A',
                'Ngày cần cào': options.get('target_date', record.get('crawl_target') or 'N/A'),
                'Tên khách sạn': record.get('hotel_name') or 'N/A',
                'Link khách sạn': record.get('hotel_link') or 'N/A',
                'Giá sau giảm': record.get('price_after_discount') if record.get('price_after_discount') else 'N/A',
                'Giá gốc': record.get('price_original') if record.get('price_original') else 'N/A',
                'Số lượng review': record.get('review_count') if record.get('review_count') else 'N/A',
                'Điểm review': record.get('review_score') if record.get('review_score') else 'N/A',
                'Tên hạng phòng': record.get('room_type') or 'N/A',
                'Số lượng người': record.get('num_people') if record.get('num_people') else 'N/A',
                'Giường': record.get('bed_info') or 'N/A',
                'Diện tích phòng': record.get('room_area') or 'N/A',
                'Các lựa chọn': options.get('facilities', 'N/A')
            })
        
        return formatted_records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api")
async def get_api_data(
    mode: str = Query("latest", regex="^(latest|all|filter)$"),
    source: Optional[str] = None,
    history_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
):
    try:
        history_repo = CrawlHistoryRepository()
        data_repo = CrawlDataRepository()
        
        if mode == "latest":
            latest = history_repo.get_latest_history(source=source)
            if not latest:
                return []
            records = data_repo.export_data_by_history(latest["id"])
        elif mode == "all":
            records = data_repo.export_all_data()
        elif mode == "filter":
            if history_id:
                records = data_repo.export_data_by_history(history_id)
            else:
                records = data_repo.export_data_by_filters(
                    source_filter=source,
                    date_from=date_from,
                    date_to=date_to,
                )
        else:
            raise HTTPException(status_code=400, detail="Unsupported mode")
        
        formatted_records = []
        for record in records:
            options = record.get('options', {})
            if isinstance(options, str):
                options = json.loads(options) if options else {}
            
            formatted_records.append({
                'Hàng_gốc': options.get('row_number', 'N/A'),
                'Ngày cào': record['crawl_date'].isoformat() if record.get('crawl_date') else 'N/A',
                'Ngày cần cào': options.get('target_date', record.get('crawl_target') or 'N/A'),
                'Tên khách sạn': record.get('hotel_name') or 'N/A',
                'Link khách sạn': record.get('hotel_link') or 'N/A',
                'Giá sau giảm': record.get('price_after_discount') if record.get('price_after_discount') else 'N/A',
                'Giá gốc': record.get('price_original') if record.get('price_original') else 'N/A',
                'Số lượng review': record.get('review_count') if record.get('review_count') else 'N/A',
                'Điểm review': record.get('review_score') if record.get('review_score') else 'N/A',
                'Tên hạng phòng': record.get('room_type') or 'N/A',
                'Số lượng người': record.get('num_people') if record.get('num_people') else 'N/A',
                'Giường': record.get('bed_info') or 'N/A',
                'Diện tích phòng': record.get('room_area') or 'N/A',
                'Các lựa chọn': options.get('facilities', 'N/A')
            })
        
        return formatted_records
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
