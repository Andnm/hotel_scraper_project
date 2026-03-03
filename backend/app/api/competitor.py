from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import List, Optional
from pydantic import BaseModel
from app.database.repositories import CompetitorListRepository
import openpyxl
import io

router = APIRouter(prefix="/api/competitors", tags=["competitors"])

class CompetitorData(BaseModel):
    hotel_name: Optional[str] = None
    hotel_link: Optional[str] = None
    room_type: Optional[str] = None
    num_people: Optional[int] = None
    bed_info: Optional[str] = None
    room_area: Optional[str] = None
    room_choices: Optional[str] = None
    popular_facilities: Optional[str] = None
    market: Optional[str] = None
    cluster: Optional[str] = None
    competitor_level: Optional[str] = None
    breakfast_included: Optional[str] = None
    room_group: Optional[str] = None
    level: Optional[str] = None

@router.get("")
async def get_all_competitors(limit: int = 1000, offset: int = 0):
    """Get all competitors with pagination"""
    try:
        repo = CompetitorListRepository()
        competitors = repo.get_all_competitors(limit, offset)
        total = repo.get_total_count()
        return {
            "data": competitors,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{competitor_id}")
async def get_competitor_by_id(competitor_id: int):
    """Get competitor by ID"""
    try:
        repo = CompetitorListRepository()
        competitor = repo.get_competitor_by_id(competitor_id)
        if competitor:
            return competitor
        else:
            raise HTTPException(status_code=404, detail="Competitor not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_competitor(data: CompetitorData):
    """Create a new competitor"""
    try:
        repo = CompetitorListRepository()
        competitor_id = repo.create_competitor(data.dict())
        return {"id": competitor_id, "message": "Competitor created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{competitor_id}")
async def update_competitor(competitor_id: int, data: CompetitorData):
    """Update an existing competitor"""
    try:
        repo = CompetitorListRepository()
        success = repo.update_competitor(competitor_id, data.dict())
        if success:
            return {"message": "Competitor updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Competitor not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{competitor_id}")
async def delete_competitor(competitor_id: int):
    """Delete a competitor"""
    try:
        repo = CompetitorListRepository()
        success = repo.delete_competitor(competitor_id)
        if success:
            return {"message": "Competitor deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Competitor not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_from_excel(file: UploadFile = File(...)):
    """Import competitors from Excel file"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File must be Excel format")
        
        contents = await file.read()
        workbook = openpyxl.load_workbook(io.BytesIO(contents))
        sheet = workbook.active
        
        repo = CompetitorListRepository()
        created_count = 0
        updated_count = 0
        errors = []
        
        # Expected columns: A=Tên khách sạn, B=Link, C=Tên hạng phòng, D=Số người, 
        # E=Giường, F=Diện tích, G=Các lựa chọn, H=Tiện nghi, 
        # I=Market, J=Cluster, K=Level đối thủ, L=Giá bao gồm bữa sáng, M=Nhóm hạng phòng, N=Level
        
        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            try:
                if not row[0] or not row[2]:  # Skip if no hotel name or room type
                    continue
                
                data = {
                    'hotel_name': str(row[0]) if row[0] else None,
                    'hotel_link': str(row[1]) if row[1] else None,
                    'room_type': str(row[2]) if row[2] else None,
                    'num_people': int(row[3]) if row[3] else None,
                    'bed_info': str(row[4]) if row[4] else None,
                    'room_area': str(row[5]) if row[5] else None,
                    'room_choices': str(row[6]) if row[6] else None,
                    'popular_facilities': str(row[7]) if row[7] else None,
                    'market': str(row[8]) if row[8] else None,
                    'cluster': str(row[9]) if row[9] else None,
                    'competitor_level': str(row[10]) if row[10] else None,
                    'breakfast_included': str(row[11]) if row[11] else None,
                    'room_group': str(row[12]) if row[12] else None,
                    'level': str(row[13]) if row[13] else None,
                }
                
                # Use upsert_competitor which handles find + create/update automatically
                result = repo.upsert_competitor(data)
                if result['action'] == 'updated':
                    updated_count += 1
                else:
                    created_count += 1
                    
            except Exception as e:
                errors.append(f"Row {row_idx}: {str(e)}")
        
        return {
            "message": "Import completed",
            "created": created_count,
            "updated": updated_count,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
