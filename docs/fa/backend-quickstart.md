# راهنمای سریع بک‌اند DocuChat

## معماری
بک‌اند DocuChat یک سیستم FastAPI چندمستاجری با قابلیت RAG است که از OpenAI برای embedding و چت استفاده می‌کند.

### فناوری‌های استفاده شده
- **FastAPI** - فریمورک وب
- **SQLModel** - ORM
- **PostgreSQL** با **pgvector** - ذخیره بردارها
- **Redis** - ذخیره کدهای احراز هویت و rate limiting
- **OpenAI API** - embeddings و chat completion
- **Alembic** - مدیریت migrations

## پیش‌نیازها
- Python 3.11+
- Docker و Docker Compose
- کلید API OpenAI

## راه‌اندازی سریع

### 1. تنظیمات محیطی
ابتدا فایل `.env` را در پوشه `backend/` بسازید:

```bash
cp .env.example .env
```

سپس مقادیر زیر را تنظیم کنید:
```env
OPENAI_API_KEY=sk-your-openai-key-here
JWT_SECRET=your-secret-key-here
```

### 2. اجرای سرویس‌ها با Docker Compose
از پوشه `infra/` دستور زیر را اجرا کنید:

```bash
cd infra
docker compose up -d db redis
```

این دستور PostgreSQL با pgvector و Redis را اجرا می‌کند.

### 3. نصب وابستگی‌ها
```bash
cd ../backend
pip install -r requirements.txt
```

### 4. اجرای Migrations
```bash
# ساخت migration اولیه
alembic revision --autogenerate -m "Initial migration"

# اعمال migrations
alembic upgrade head
```

### 5. اجرای سرور
```bash
uvicorn app.main:app --reload
```

سرور در آدرس `http://localhost:8000` اجرا می‌شود.

## ساختار پروژه

```
backend/
├── app/
│   ├── main.py                 # نقطه ورود اصلی
│   ├── core/                   # تنظیمات و امنیت
│   │   ├── config.py          # تنظیمات از .env
│   │   └── security.py        # JWT utilities
│   ├── db/                     # دیتابیس
│   │   ├── session.py         # async session
│   │   ├── init.py            # راه‌اندازی pgvector
│   │   └── migrations/        # Alembic migrations
│   ├── models/                 # مدل‌های SQLModel
│   │   ├── tenant.py
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── chunk.py
│   │   ├── chat.py
│   │   └── quota.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py
│   │   ├── files.py
│   │   ├── chat.py
│   │   └── usage.py
│   ├── api/                    # API routes
│   │   ├── deps.py            # وابستگی‌های احراز هویت
│   │   └── routes/
│   │       ├── health.py
│   │       ├── auth.py
│   │       ├── files.py
│   │       └── usage.py
│   ├── services/               # Business logic
│   │   ├── pdf_ingest.py      # استخراج متن PDF
│   │   ├── chunker.py         # برش متن با tiktoken
│   │   ├── embedder.py        # OpenAI embeddings
│   │   ├── retriever.py       # جستجوی برداری
│   │   ├── rag.py             # ساخت prompt
│   │   ├── ratelimit.py       # محدودسازی نرخ
│   │   └── tokens_meter.py    # شمارش توکن‌ها
│   └── ws/                     # WebSocket handlers
│       └── chat.py            # چت با استریم
├── tests/                      # تست‌ها
└── requirements.txt
```

## APIهای موجود

### احراز هویت
- `POST /v1/auth/request-code` - درخواست کد احراز هویت
- `POST /v1/auth/verify-code` - تأیید کد و دریافت JWT

### فایل‌ها
- `POST /v1/files` - آپلود PDF (نیاز به احراز هویت)

### چت
- `WS /ws/chat` - WebSocket برای چت با استریم

### آمار
- `GET /v1/usage` - مشاهده مصرف توکن‌ها

### سلامت
- `GET /healthz` - بررسی سلامت سرویس

## چندمستاجری (Multi-tenancy)

تمام درخواست‌ها باید هدر `X-Tenant-ID` داشته باشند:

```bash
curl -H "X-Tenant-ID: 1" http://localhost:8000/healthz
```

## احراز هویت

### فرآیند:
1. کاربر ایمیل خود را ارسال می‌کند → کد 6 رقمی دریافت می‌کند
2. کد را تأیید می‌کند → JWT token دریافت می‌کند  
3. از token در هدر `Authorization: Bearer <token>` استفاده می‌کند

### مثال:
```bash
# درخواست کد
curl -X POST http://localhost:8000/v1/auth/request-code \
  -H "X-Tenant-ID: 1" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# تأیید کد (کد را از لاگ سرور بردارید)
curl -X POST http://localhost:8000/v1/auth/verify-code \
  -H "X-Tenant-ID: 1" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "code": "123456"}'

# استفاده از token
curl http://localhost:8000/v1/usage \
  -H "X-Tenant-ID: 1" \
  -H "Authorization: Bearer <your-token>"
```

## آپلود PDF و RAG

### فرآیند:
1. PDF آپلود می‌شود
2. متن استخراج می‌شود (pypdf)
3. به chunk های کوچکتر تقسیم می‌شود (tiktoken)
4. embedding ساخته می‌شود (OpenAI)
5. در pgvector ذخیره می‌شود

### مثال آپلود:
```bash
curl -X POST http://localhost:8000/v1/files \
  -H "X-Tenant-ID: 1" \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "title=My Document"
```

## چت WebSocket

### اتصال:
```javascript
const ws = new WebSocket(
  'ws://localhost:8000/ws/chat?token=<your-token>',
  { headers: { 'X-Tenant-ID': '1' } }
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'start') {
    console.log('Session:', data.session_id);
  }
  else if (data.type === 'delta') {
    console.log('Token:', data.token);
  }
  else if (data.type === 'end') {
    console.log('Usage:', data.usage);
  }
  else if (data.type === 'error') {
    console.error('Error:', data.message);
  }
};

// ارسال پیام
ws.send(JSON.stringify({
  message: 'سؤال من چیست؟',
  session_id: 123  // اختیاری
}));
```

## تست‌ها

### اجرای تست‌ها:
```bash
# همه تست‌ها
pytest

# با coverage
pytest --cov=app --cov-report=html

# فقط یک فایل
pytest tests/test_auth.py
```

### پیش‌نیاز برای تست‌ها:
دیتابیس تست باید وجود داشته باشد:
```bash
createdb docuchat_test
```

## تنظیمات تولید

### متغیرهای مهم:
- `JWT_SECRET` - یک کلید تصادفی قوی
- `OPENAI_API_KEY` - کلید واقعی OpenAI
- `RATE_LIMIT_PER_MINUTE` - محدودیت نرخ (پیش‌فرض: 50)
- `MAX_FILE_SIZE_MB` - حداکثر اندازه فایل (پیش‌فرض: 25)
- `MAX_PDF_PAGES` - حداکثر صفحات PDF (پیش‌فرض: 500)

### بهینه‌سازی‌ها:
1. استفاده از connection pooling برای دیتابیس
2. فعال کردن Redis persistence
3. تنظیم workers در uvicorn:
   ```bash
   uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
   ```

## مشکلات رایج

### خطای "vector extension not found"
```sql
-- اجرا در psql:
CREATE EXTENSION vector;
```

### خطای rate limit
Redis باید در حال اجرا باشد:
```bash
docker compose up -d redis
```

### خطای OpenAI API
بررسی کنید که `OPENAI_API_KEY` صحیح است و اعتبار دارد.

## منابع بیشتر
- [مستندات FastAPI](https://fastapi.tiangolo.com/)
- [مستندات OpenAI](https://platform.openai.com/docs)
- [pgvector](https://github.com/pgvector/pgvector)
- [SQLModel](https://sqlmodel.tiangolo.com/)
