# Sử dụng Python 3.10 slim để nhẹ máy
FROM python:3.10-slim

# Thiết lập biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

# Đặt thư mục làm việc
WORKDIR $APP_HOME

# Cài đặt các gói hệ thống cần thiết và TRÌNH DUYỆT CHROME (Thay vì Edge để ổn định hơn trên Linux Server)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && wget -q -O - https://dl-google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements và cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code
COPY . .

# Tạo thư mục cho debug html
RUN mkdir -p debug_html

# Mở port 8000
EXPOSE 8000

# Lệnh chạy server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
