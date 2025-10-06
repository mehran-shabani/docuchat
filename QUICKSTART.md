# DocuChat Quick Start Guide

Get up and running with DocuChat in under 5 minutes!

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) v2
- [OpenAI API Key](https://platform.openai.com/api-keys) (optional for basic testing)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/docuchat.git
cd docuchat
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp backend/.env.example backend/.env

# Edit backend/.env and add your OpenAI API key
# nano backend/.env
# or
# vim backend/.env
```

**backend/.env:**
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
DATABASE_URL=postgresql://docuchat:docuchat_pass@postgres:5432/docuchat
```

### 3. Start All Services

```bash
cd infra
docker compose up
```

Wait for all services to start (approximately 2-3 minutes on first run).

### 4. Verify Installation

Open your browser and visit:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/healthz

You should see:
- Frontend: Beautiful RTL Persian interface saying "DocuChat is live"
- Health Check: `{"status":"ok"}`

### 5. Test the Demo Endpoint

```bash
# Test the health endpoint
curl http://localhost:8000/healthz

# Test the AI chat demo (requires OPENAI_API_KEY)
curl http://localhost:8000/v1/chat/demo
```

Expected response:
```json
{"reply": "pong"}
```

## 🛠️ Development Mode

### Backend Development

```bash
cd backend

# Create virtual environment (if venv package is installed)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for interactive API documentation.

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server with hot reload
npm run dev
```

Visit http://localhost:3000 to see your changes live.

## 🧪 Running Tests

### Backend Tests

```bash
cd backend
pytest -q
```

### Linting

```bash
# Backend
cd backend
ruff check .
ruff format --check .

# Frontend
cd frontend
npm run lint
```

## 📁 Project Structure

```
docuchat/
├── backend/              # FastAPI application
│   ├── app/             # Application code
│   │   └── main.py      # Main FastAPI app
│   ├── tests/           # Test suite
│   ├── Dockerfile       # Backend container
│   └── requirements.txt # Python dependencies
├── frontend/            # Next.js 14 application
│   ├── src/            # Source code
│   │   ├── pages/      # Next.js pages
│   │   └── styles/     # CSS styles
│   ├── Dockerfile      # Frontend container
│   └── package.json    # Node dependencies
├── infra/              # Infrastructure
│   ├── docker-compose.yml  # Docker Compose config
│   ├── helm/          # Kubernetes Helm charts
│   └── terraform/     # Terraform IaC
└── docs/              # Documentation
    ├── en/            # English docs
    └── fa/            # Persian docs
```

## 🐳 Docker Commands

```bash
# Start all services in background
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Rebuild and restart
docker compose up --build

# Stop and remove volumes (fresh start)
docker compose down -v
```

## 🔧 Common Issues

### Port Already in Use

If ports 3000, 5432, or 8000 are already in use:

```bash
# Check what's using the port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Option 1: Stop the conflicting service
# Option 2: Change ports in docker-compose.yml
```

### OpenAI API Key Not Working

```bash
# Verify your API key is set
cat backend/.env | grep OPENAI_API_KEY

# Test without OpenAI (health check only)
curl http://localhost:8000/healthz
```

### Docker Permission Denied

```bash
# Add your user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in
```

## 📚 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Read the Documentation**: Check [docs/en/README.md](./docs/en/README.md)
3. **Customize the Frontend**: Edit `frontend/src/pages/index.tsx`
4. **Add Endpoints**: Edit `backend/app/main.py`
5. **Deploy to Production**: See [docs/en/DEPLOYMENT.md](./docs/en/DEPLOYMENT.md)

## 🤝 Getting Help

- **Documentation**: [docs/en/README.md](./docs/en/README.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/docuchat/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/docuchat/discussions)

## 🎉 You're Ready!

You now have a fully functional DocuChat instance running locally. Happy coding!

---

**Need more help?** Check out the [full documentation](./docs/en/README.md) or open an [issue](https://github.com/your-org/docuchat/issues).
