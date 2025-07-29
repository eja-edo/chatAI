### 📁 `app/`

Thư mục chính chứa toàn bộ mã nguồn của ứng dụng FastAPI.

---

### 📁 `api/`

Chứa logic điều hướng (routing) và phụ trợ cho API.

#### 📁 `routes/`

* Nơi định nghĩa **các route chính** của ứng dụng (GET, POST, PUT, DELETE...).
* Mỗi file trong đây đại diện cho một module API (ví dụ: `users.py`, `auth.py`, `products.py`…).

#### `__init__.py`

* Đảm bảo `routes/` là một Python package.
* Có thể sử dụng để import tất cả các router con vào một router lớn.

#### `deps.py`

* Chứa các **dependency** dùng cho các endpoint (ví dụ: xác thực người dùng, lấy `db_session`...).
* Ví dụ:

  ```python
  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()
  ```

---

### 📁 `core/`

Chứa các cấu hình chính của hệ thống.

#### `config.py`

* Cấu hình các giá trị như:

  * `DATABASE_URL`
  * `SECRET_KEY`, `ALGORITHM`
  * `ACCESS_TOKEN_EXPIRE_MINUTES`
  * Đọc từ `.env`

#### `security.py`

* Logic liên quan đến bảo mật:

  * Mã hóa mật khẩu (`bcrypt`)
  * Sinh và kiểm tra JWT token
  * Middleware bảo vệ route

---

### 📁 `crud/`

* CRUD = Create, Read, Update, Delete
* Nơi viết **logic thao tác dữ liệu với database** (thường sử dụng SQLAlchemy)
* Ví dụ: `get_user_by_email()`, `create_user()`, `update_item()`,...

---

### 📁 `db/`

* Cấu hình cơ bản cho database.

#### `base.py`

* Chứa lệnh để import tất cả các model để `Base.metadata.create_all(bind=engine)` có thể hoạt động.

  ```python
  from app.models.user import User
  ```

#### `session.py`

* Nơi cấu hình kết nối database bằng SQLAlchemy:

  ```python
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker

  SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
  engine = create_engine(SQLALCHEMY_DATABASE_URL)
  SessionLocal = sessionmaker(bind=engine)
  ```

---

### 📁 `models/`

* Chứa các **ORM model** mô tả bảng trong CSDL bằng SQLAlchemy.

---

### 📁 `schemas/`

* Chứa các **Pydantic models** để kiểm tra và validate dữ liệu vào/ra API.
* Tách biệt với `models` (ORM) vì `models` dùng cho DB, còn `schemas` dùng cho API.

---

### 🗂 `main.py`

* File chính chạy ứng dụng FastAPI.
* Khởi tạo app, include các router từ `api/routes`, cấu hình middleware, exception handler...

```python
from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI()

app.include_router(api_router)
```

---

### 🗂 `.env`

* Chứa các biến môi trường như:

  ```
  DATABASE_URL=postgresql://user:pass@localhost/db
  SECRET_KEY=supersecret
  ```

---

### 🗂 `requirements.txt`

* Danh sách các thư viện cần cài đặt:

  ```
  fastapi
  uvicorn
  sqlalchemy
  python-dotenv
  passlib[bcrypt]
  ```
docker exec -it ChatAI_app bash
docker exec -it chatAI_db psql -U postgres -d chatAI_database
---
