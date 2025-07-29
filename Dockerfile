# Dockerfile
FROM python:3.12-slim

# Tạo thư mục làm việc trong container
WORKDIR /app

# Cài đặt các gói cần thiết
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Cổng chạy uvicorn
EXPOSE 8000

# Lệnh chạy FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
