# Hướng dẫn Import Google Sheets

## Vấn đề hiện tại
Lỗi **"Không tìm thấy link nào trong tất cả các sheets"** với 400 Bad Request thường do:

### 1. Sheet chưa được share công khai ✋

**Cách fix:**
1. Mở Google Sheet của bạn
2. Click nút **"Share"** (góc trên bên phải)
3. Chọn **"Change to anyone with the link"**
4. Đảm bảo quyền là **"Viewer"** (đọc)
5. Copy link và thử lại

### 2. Format dữ liệu không đúng 📊

**Định dạng yêu cầu:**
- **Cột A**: Tên khách sạn
- **Cột B**: Link Booking.com

Ví dụ:
```
A                           | B
---------------------------|------------------------------------------
Khách sạn ABC              | https://www.booking.com/hotel/vn/abc.html
Resort XYZ                 | https://www.booking.com/hotel/vn/xyz.html
```

### 3. Sheet names bị lỗi 🏷️

Nếu có nhiều sheets trong file, tên sheet phải:
- Dài 3-50 ký tự
- Không chứa ký tự đặc biệt: `< > { } [ ] | \`
- Không chứa từ khóa kỹ thuật: `docs.`, `security`, `api`, etc.
- ✅ Tốt: `Vũng Tàu`, `Đà Lạt`, `Phú Quốc`
- ❌ Xấu: `tf`, `docs.security.access_capabilities`

## Cách test nhanh

### Test 1: Kiểm tra quyền truy cập
Mở trình duyệt **ẩn danh** (Incognito) và paste link Google Sheet vào. 
- ✅ Nếu mở được → Sheet đã public
- ❌ Nếu báo "Request access" → Sheet chưa public

### Test 2: Kiểm tra export CSV
Thay cấu trúc URL:
```
From: https://docs.google.com/spreadsheets/d/YOUR_ID/edit
To:   https://docs.google.com/spreadsheets/d/YOUR_ID/export?format=csv
```
Paste vào browser:
- ✅ Nếu download file CSV → OK
- ❌ Nếu báo 400 Bad Request → Chưa public

## Troubleshooting

### Nếu masih lỗi sau khi share public:
1. Check console trong browser (F12)
2. Xem terminal backend để thấy logs chi tiết
3. Đảm bảo có link trong cột B (không được để trống)
4. Thử với file Excel trước để verify format

### Alternative: Dùng Excel thay vì Google Sheets
Nếu Google Sheets quá phức tạp:
1. Download Sheet as Excel (.xlsx)
2. Upload trực tiếp Excel file
3. System sẽ tự động detect multiple sheets
