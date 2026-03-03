# MIGRATION SUMMARY - Remove Code Field & Update Matching Logic

## ✅ COMPLETED - Backend Changes

### 1. Format Import Excel/Google Sheet (✓)
**File: `backend/app/services/booking_scraper.py`**
- `extract_hyperlinks_from_excel()`: Đổi từ (A=Mã số, B=Tên KS, C=Link) → (A=Tên KS, B=Link)
- `load_google_sheet()`: Đổi format tương tự
- Bỏ field `code` khỏi tất cả returned data

### 2. Database Schema (✓)
**Files:**
- `backend/app/database/setup.sql`: Schema mới
  - Xóa bảng `market_cluster_mapping`
  - Xóa cột `code` trong `competitor_list`
  - Xóa cột `code` trong `crawl_data`
  - Thêm index mới: `idx_competitor_hotel` cho matching

- `backend/app/database/migration_remove_code.sql`: Migration script
  - Migrate market/cluster data sang `config_items`
  - DROP các tables/columns cũ

### 3. Repository Logic (✓)
**File: `backend/app/database/repositories.py`**

**CompetitorListRepository:**
- ✅ `find_competitor()`: Matching mới dựa trên:
  - **Required**: `hotel_name` + `room_type`
  - **Optional**: `num_people`, `bed_info`, `room_area`
- ✅ `get_competitor_by_id()`: Get by ID thay vì code
- ✅ `create_competitor()`: Bỏ code parameter
- ✅ `update_competitor()`: Update by ID, bỏ code
- ✅ `upsert_competitor()`: Match theo name+room thay vì code
- ✅ `delete_competitor()`: Delete by ID

**CrawlDataRepository:**
- ✅ `get_data_by_history()`: LEFT JOIN mới với competitor_list:
  ```sql
  LEFT JOIN competitor_list cl ON 
      cd.hotel_name = cl.hotel_name 
      AND cd.room_type = cl.room_type
      AND (cl.num_people IS NULL OR cd.num_people = cl.num_people)
      AND (cl.bed_info IS NULL OR cl.bed_info = '' OR cd.bed_info = cl.bed_info)
      AND (cl.room_area IS NULL OR cl.room_area = '' OR cd.room_area = cl.room_area)
  ```
- ✅ `export_data_by_history()`: JOIN logic tương tự

**Removed:**
- ✅ `MarketClusterRepository`: Đã xóa toàn bộ class (không còn dùng)

---

## ⚠️ TODO - Frontend Changes (Cần làm tiếp)

### 1. BookingTab.vue
**Đã làm:**
- ✅ Xóa cột "Mã số" trong bảng invalid links (Step 2)
- ✅ Bỏ "Mã số" khỏi Excel export của invalid links

**Cần làm tiếp:**
- [ ] Kiểm tra xem còn reference nào đến `code` field không

### 2. CompetitorListView.vue 
**Cần làm:**
- [ ] Xóa cột "Code" khỏi DataTable
- [ ] Xóa input "Code" khỏi Dialog form (create/edit)
- [ ] Xóa field `code` trong `formData` interface
- [ ] Update import Excel logic:
  - Format Excel cũ: Code | Tên KS | Link | Room Type | ...
  - Format Excel mới: Tên KS | Link | Room Type | Số người | Giường | Diện tích | ...
  - Match logic: Tên KS + Room Type (required), các field khác optional

### 3. ConfigView.vue
**Cần làm:**
- [ ] **Xóa Tab "Market & Cluster"** hoặc chuyển sang format config_items:
  - Option 1: Xóa hoàn toàn tab (đơn giản nhất)
  - Option 2: Chuyển thành 2 config categories: `market` và `cluster`
- [ ] Xóa Dialog `showMCDialog` và tất cả logic liên quan
- [ ] Xóa `mcFormData`, `mcDialogMode`
- [ ] Xóa functions: `editMarketCluster`, `deleteMarketCluster`, `saveMarketCluster`

### 4. HistoryList.vue
**Cần làm:**
- [ ] Xóa cột "Mã số" (nếu có hiển thị)  
- [ ] Kiểm tra các columns: Market, Cluster, Level đối thủ, ... đang lấy từ competitor mapping
- [ ] Đảm bảo mapping dựa trên tên KS + room details (backend đã xử lý)

### 5. API Endpoints (backend)
**Cần kiểm tra và update:**
- [ ] `app/api/sources.py`: Endpoints liên quan market-cluster
- [ ] Xóa routes `/api/market-cluster/*` nếu có
- [ ] Update các response schemas bỏ `code` field

---

## 📝 DATABASE MIGRATION STEPS

**Trước khi chạy app:**
```bash
cd backend/app/database
mysql -u root -p hotel_scraper < migration_remove_code.sql
```

**Hoặc setup lại từ đầu:**
```bash
mysql -u root -p hotel_scraper < setup.sql
```

---

## 🔄 MATCHING LOGIC SUMMARY

### Old Logic (Code-based):
```
Match: crawl_data.code = competitor_list.code
```

### New Logic (Name + Room Details):
```
Match on:
1. hotel_name (REQUIRED)
2. room_type (REQUIRED)
3. num_people (OPTIONAL - match if not null)
4. bed_info (OPTIONAL - match if not empty)
5. room_area (OPTIONAL - match if not empty)
```

**Ví dụ:**
- Crawl data: "Hotel A", "Deluxe Room", 2 people, "2 single beds", "30m²"
- Competitor: "Hotel A", "Deluxe Room", NULL, NULL, NULL → ✓ MATCH
- Competitor: "Hotel A", "Deluxe Room", 2, "2 single beds", "30m²" → ✓ MATCH
- Competitor: "Hotel A", "Superior Room", 2, ... → ✗ NO MATCH (room type khác)

---

## ⚙️ NEXT STEPS

1. **Run migration:** Chạy migration_remove_code.sql
2. **Update frontend:** Làm theo TODO list ở trên
3. **Test thoroughly:**
   - Import Excel với format mới (A=Tên KS, B=Link)
   - Import competitor list
   - Xem history data có map đúng competitor info không
   - Test create/edit/delete competitor (không có code)

4. **Remove unused code:**
   - API routes cho market-cluster
   - Frontend components/functions không dùng

---

## 📎 Files Changed

**Backend:**
- ✅ `backend/app/services/booking_scraper.py`
- ✅ `backend/app/database/repositories.py`
- ✅ `backend/app/database/setup.sql`
- ✅ `backend/app/database/migration_remove_code.sql` (NEW)
- ⚠️ `backend/app/api/*.py` (cần kiểm tra)

**Frontend:**
- ⚠️ `frontend/src/components/BookingTab.vue` (partial)
- ⚠️ `frontend/src/components/CompetitorListView.vue` (chưa làm)
- ⚠️ `frontend/src/views/ConfigView.vue` (chưa làm)
- ⚠️ `frontend/src/components/HistoryList.vue` (cần kiểm tra)
