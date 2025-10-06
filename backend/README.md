# DocuChat Backend

Multi-tenant FastAPI backend with OpenAI RAG (Retrieval-Augmented Generation) capabilities.

## Features

- ✅ **Multi-tenancy** with tenant isolation via `X-Tenant-ID` header
- ✅ **Email + Code Authentication** with JWT tokens
- ✅ **PDF Upload & Processing** with automatic text extraction and chunking
- ✅ **Vector Search** using PostgreSQL with pgvector extension
- ✅ **RAG (Retrieval-Augmented Generation)** with OpenAI GPT models
- ✅ **WebSocket Chat** with streaming responses
- ✅ **Token Usage Tracking** and rate limiting
- ✅ **Async/Await** throughout for high performance

## Tech Stack

- **FastAPI** - Modern async web framework
- **SQLModel** - SQL databases in Python with type annotations
- **PostgreSQL + pgvector** - Vector database for embeddings
- **Redis** - Cache and rate limiting
- **OpenAI API** - Embeddings and chat completions
- **Alembic** - Database migrations
- **Pytest** - Testing framework

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Docker and Docker Compose
- OpenAI API key

### 2. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### 3. Start Services

```bash
# Start database and Redis
cd ../infra
docker compose up -d db redis

# Return to backend
cd ../backend
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Migrations

```bash
alembic upgrade head
```

### 6. Start Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

- `POST /v1/auth/request-code` - Request verification code
- `POST /v1/auth/verify-code` - Verify code and get JWT token

### Files

- `POST /v1/files` - Upload PDF file (requires auth)

### Chat

- `WS /ws/chat` - WebSocket endpoint for chat with streaming

### Usage

- `GET /v1/usage` - Get token usage statistics (requires auth)

### Health

- `GET /healthz` - Health check

## Multi-tenancy

All requests must include the `X-Tenant-ID` header:

```bash
curl -H "X-Tenant-ID: 1" http://localhost:8000/healthz
```

## Authentication Flow

### Step 1: Request verification code

```bash
curl -X POST http://localhost:8000/v1/auth/request-code \
  -H "X-Tenant-ID: 1" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### Step 2: Check server logs

Check server logs for the code (in production, this would be sent via email)

### Step 3: Verify code

```bash
curl -X POST http://localhost:8000/v1/auth/verify-code \
  -H "X-Tenant-ID: 1" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "code": "123456"}'
```

### Step 4: Use the JWT token

```bash
curl http://localhost:8000/v1/usage \
  -H "X-Tenant-ID: 1" \
  -H "Authorization: Bearer <your-token>"
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## Development

### Project Structure

```text
app/
├── main.py              # Application entry point
├── core/                # Core configuration
├── db/                  # Database setup and migrations
├── models/              # SQLModel models
├── schemas/             # Pydantic schemas
├── api/                 # API routes and dependencies
├── services/            # Business logic
└── ws/                  # WebSocket handlers
```

### Code Quality

```bash
# Format code
ruff format .

# Lint
ruff check .
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `OPENAI_API_KEY` - Your OpenAI API key
- `OPENAI_MODEL` - Model to use (gpt-4o-mini, gpt-4o, etc.)
- `JWT_SECRET` - Secret key for JWT tokens
- `FRONTEND_ORIGIN` - CORS origin for frontend

## Production Considerations

1. Use a strong `JWT_SECRET`
2. Set appropriate `RATE_LIMIT_PER_MINUTE`
3. Configure proper logging
4. Use connection pooling for database
5. Enable Redis persistence
6. Run with multiple workers:

   ```bash
   uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
   ```

## License

See LICENSE file in the root directory.

## Documentation

For detailed setup and usage instructions in Persian, see:

- [راهنمای سریع فارسی](../docs/fa/backend-quickstart.md)
