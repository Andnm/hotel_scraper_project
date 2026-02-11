from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class CrawlHistoryCreate(BaseModel):
    crawl_date: date
    crawl_target: Optional[str] = None
    source: str = "booking"

class CrawlHistoryResponse(BaseModel):
    id: int
    crawl_date: date
    crawl_target: Optional[str]
    source: str
    total_records: int
    created_at: datetime

class CrawlDataCreate(BaseModel):
    hotel_name: str
    hotel_link: str
    price_after_discount: Optional[float]
    price_original: Optional[float]
    review_count: Optional[int]
    review_score: Optional[float]
    room_type: str
    num_people: Optional[int]
    bed_info: str
    room_area: str
    options: Dict[str, Any]

class CrawlDataResponse(BaseModel):
    id: int
    history_id: int
    hotel_name: str
    hotel_link: str
    price_after_discount: Optional[float]
    price_original: Optional[float]
    review_count: Optional[int]
    review_score: Optional[float]
    room_type: str
    num_people: Optional[int]
    bed_info: str
    room_area: str
    options: Dict[str, Any]
    created_at: datetime
    crawl_date: Optional[date] = None
    crawl_target: Optional[str] = None

class ScrapeRequest(BaseModel):
    links: List[Dict[str, Any]]
    date_ranges: List[Dict[str, str]]
    source: str = "booking"

class ScrapeProgress(BaseModel):
    type: str
    current: int
    total: int
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

class HistoryListQuery(BaseModel):
    page: int = 1
    page_size: int = 10
    source_filter: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None

class ApiDataQuery(BaseModel):
    mode: str = "latest"
    source: Optional[str] = None
    history_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
