# 🏨 Hotel Scraper Project

Ứng dụng web cào dữ liệu khách sạn từ Booking.com với giao diện Vue.js và backend FastAPI.

## 📋 Yêu cầu hệ thống

- **Python**: 3.8 trở lên
- **Node.js**: 20.x trở lên
- **MySQL**: 8.0 trở lên
- **Microsoft Edge**: Phiên bản mới nhất (cho Selenium WebDriver)

## 🚀 Hướng dẫn cài đặt nhanh

### Bước 1: Clone và setup Database

```powershell
# Tạo database MySQL
mysql -u root -p
```

```sql
CREATE DATABASE hotel_scraper CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

```powershell
# Import schema
mysql -u root -p hotel_scraper < backend/app/database/setup.sql
```

### Bước 2: Setup Backend

```powershell
cd backend
.\setup.ps1
```

**Sửa file `.env`** với MySQL password của bạn:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=hotel_scraper
```

### Bước 3: Setup Frontend

```powershell
cd frontend
.\setup.ps1
```

### Bước 4: Chạy ứng dụng

**Cách 1: Tự động (khuyên dùng)**
```powershell
# Từ thư mục gốc
.\start.ps1
```

**Cách 2: Thủ công**
```powershell
# Terminal 1 - Backend
cd backend
.\venv\Scripts\Activate.ps1
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Bước 5: Truy cập

- 🌐 **Ứng dụng**: http://localhost:5173
- 📚 **API Docs**: http://localhost:8000/docs

## 📁 Cấu trúc project

```
hotel_scraper_project/
├── backend/                  # FastAPI Backend
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   ├── core/            # Config, database
│   │   ├── database/        # Repositories
│   │   ├── schemas/         # Pydantic models
│   │   └── services/        # Scraper logic
│   ├── main.py              # Entry point
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example
│   └── setup.ps1
│
├── frontend/                # Vue.js Frontend
│   ├── src/
│   │   ├── components/      # Vue components
│   │   ├── services/        # API & WebSocket
│   │   ├── stores/          # Pinia state
│   │   ├── types/           # TypeScript types
│   │   └── views/           # Page views
│   ├── package.json
│   └── setup.ps1
│
├── start.ps1               # Script chạy cả 2 servers
└── README.md
```

## 🔧 Troubleshooting

### Lỗi PowerShell Execution Policy
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Lỗi kết nối MySQL
- Kiểm tra MySQL service đã chạy chưa
- Kiểm tra username/password trong `backend/.env`
- Đảm bảo database `hotel_scraper` đã được tạo

### Lỗi Frontend không build
```powershell
cd frontend
rm -r node_modules, package-lock.json
npm install
npm run dev
```

### Lỗi Backend không chạy
```powershell
cd backend
rm -r venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## 💡 Tính năng

### ✅ Đã hoàn thành
- Upload file Excel chứa link Booking.com
- Chọn nhiều cặp ngày check-in/check-out
- Cào dữ liệu real-time với WebSocket
- Hiển thị progress bar và trạng thái
- Lưu lịch sử cào vào database
- Xem lại dữ liệu đã cào
- Export dữ liệu

### 🔄 Đang phát triển
- Hỗ trợ Agoda.com
- Google Sheets integration
- Export Excel từ frontend
- Dashboard analytics

## 📝 Ghi chú

- File Excel cần chứa link Booking.com trong 3 cột đầu (A, B, C)
- Link phải có định dạng: `https://www.booking.com/hotel/...`
- Selenium sử dụng Edge WebDriver (tự động tải)
- WebSocket endpoint: `ws://localhost:8000/ws/scrape`

## 📄 License

MIT License

## 👨‍💻 Author

Hotel Scraper Team
