# ⚡ Quick Start Guide

## 🎯 Chạy nhanh trong 5 phút

### 1️⃣ Chuẩn bị
- ✅ Python 3.8+ đã cài
- ✅ Node.js 20+ đã cài
- ✅ MySQL 8.0+ đã cài và đang chạy

### 2️⃣ Setup Database (1 phút)
```powershell
# Tạo database
mysql -u root -p -e "CREATE DATABASE hotel_scraper"

# Import schema
mysql -u root -p hotel_scraper < backend\app\database\setup.sql
```

### 3️⃣ Setup Backend (1 phút)
```powershell
cd backend
.\setup.ps1
# Sửa file .env với MySQL password
notepad .env
```

### 4️⃣ Setup Frontend (1 phút)
```powershell
cd frontend
.\setup.ps1
```

### 5️⃣ Chạy Application (1 phút)
```powershell
# Từ thư mục gốc
.\start.ps1
```

### 6️⃣ Truy cập
🌐 Mở trình duyệt: **http://localhost:5173**

---

## 🔥 Lần sau chạy lại (30 giây)
```powershell
.\start.ps1
```
Xong! 🎉

---

## 📝 Sử dụng

### Upload file Excel
1. Mở Tab "Booking.com"
2. Click "Chọn file Excel"
3. Chọn file chứa link Booking.com (trong cột A, B, hoặc C)

### Chọn ngày
1. Chọn ngày Check-in
2. Chọn ngày Check-out
3. Click "➕ Thêm"
4. Có thể thêm nhiều cặp ngày

### Bắt đầu cào
1. Click "🚀 Bắt đầu cào dữ liệu"
2. Xem progress bar real-time
3. Đợi hoàn thành
4. Xem kết quả

### Xem lịch sử
1. Click tab "Lịch sử"
2. Xem danh sách các lần cào trước
3. Click "👁️" để xem chi tiết
4. Click "📥" để download Excel

---

## ❌ Lỗi thường gặp

### "Execution Policy" error
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Backend không chạy
- Kiểm tra MySQL đang chạy
- Kiểm tra password trong `backend\.env`
- Kiểm tra database đã tạo chưa

### Frontend không chạy
```powershell
cd frontend
rm -r node_modules
npm install
npm run dev
```

### Port đã được sử dụng
- Backend cần port 8000 trống
- Frontend cần port 5173 trống
- Tắt ứng dụng đang dùng port đó

---

## 📞 Cần thêm help?

1. Xem file [README.md](README.md) chi tiết hơn
2. Check backend logs trong terminal Backend
3. Check frontend logs trong terminal Frontend
4. Check browser console (F12)

---

## 🎓 Cấu trúc file Excel

File Excel cần có:
- Link Booking.com trong 3 cột đầu (A, B, hoặc C)
- Link có dạng: `https://www.booking.com/hotel/vn/...`
- Có thể có nhiều sheet (chỉ đọc sheet đầu)

Ví dụ:
```
| A                                      | B           | C         |
|----------------------------------------|-------------|-----------|
| https://booking.com/hotel/vn/abc       | Hotel ABC   | Hanoi     |
| https://booking.com/hotel/vn/xyz       | Hotel XYZ   | HCMC      |
```

---

**Happy Scraping! 🎉**
