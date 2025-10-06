# DocuChat 🤖📄

[![CI/CD Pipeline](https://github.com/your-org/docuchat/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/your-org/docuchat/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/your-org/docuchat/releases)

> An AI-powered document chat application built with FastAPI, Next.js 14, and OpenAI/Claude Sonnet 4.5

[English Documentation](./docs/en/README.md) | [مستندات فارسی](./docs/fa/README.md)

## ✨ Features

- 🤖 **AI-Powered Chat** - Interact with your documents using natural language via OpenAI GPT or Claude Sonnet 4.5
- 📊 **Vector Search** - Fast semantic search powered by PostgreSQL with pgvector extension
- 🚀 **Modern Stack** - FastAPI backend (Python 3.11) + Next.js 14 frontend with RTL support
- 🐳 **Docker Ready** - Full docker-compose setup for local development
- ☸️ **Kubernetes Ready** - Helm charts included for production deployment
- 🏗️ **Infrastructure as Code** - Terraform stubs for AWS deployment
- 🔒 **Production Ready** - Security best practices, testing, and CI/CD pipelines
- 🌍 **Bilingual** - Full English and Persian (Farsi) documentation

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose v2
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)
- OpenAI API key or Claude API key

### Running with Docker Compose

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/docuchat.git
   cd docuchat
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your OPENAI_API_KEY
   ```

3. **Start all services**
   ```bash
   cd infra
   docker compose up
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/healthz

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📚 Documentation

Comprehensive documentation is available in both English and Persian:

- [Quick Start Guide](./docs/en/QUICKSTART.md) | [راهنمای شروع سریع](./docs/fa/QUICKSTART.md)
- [API Reference](./docs/en/API-REFERENCE.md)
- [Architecture Overview](./docs/en/ARCHITECTURE.md)
- [Deployment Guide](./docs/en/DEPLOYMENT.md)
- [Development Guide](./docs/en/DEVELOPMENT.md)
- [Translation Plan](./docs/translation-plan.md)

## 🏗️ Architecture

```
docuchat/
├── backend/              # FastAPI application
│   ├── app/             # Application code
│   ├── tests/           # Test suite
│   ├── Dockerfile       # Backend container
│   └── requirements.txt # Python dependencies
├── frontend/            # Next.js 14 application
│   ├── src/            # Source code
│   ├── public/         # Static assets
│   ├── Dockerfile      # Frontend container
│   └── package.json    # Node dependencies
├── infra/              # Infrastructure as Code
│   ├── docker-compose.yml
│   ├── helm/           # Kubernetes Helm charts
│   └── terraform/      # AWS Terraform modules
├── docs/               # Documentation
│   ├── en/            # English docs
│   └── fa/            # Persian docs
└── .github/           # CI/CD workflows
```

## 🧪 Testing

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

## 🚢 Deployment

### Docker Compose (Development)
```bash
cd infra
docker compose up -d
```

### Kubernetes (Production)
```bash
helm install docuchat ./infra/helm \
  --set backend.image.tag=v0.1.0 \
  --set frontend.image.tag=v0.1.0
```

### AWS with Terraform
```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

## 🔧 Configuration

### Environment Variables

#### Backend
- `OPENAI_API_KEY` - OpenAI API key (required)
- `DATABASE_URL` - PostgreSQL connection string
- For Claude Sonnet 4.5, use `model="gpt-4o-sonnet-4.5"` and log latency metrics

#### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL

See `backend/.env.example` for complete configuration options.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](./docs/en/CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Roadmap

- [x] Basic FastAPI backend with OpenAI integration
- [x] Next.js frontend with RTL support
- [x] Docker Compose setup
- [x] CI/CD pipeline
- [ ] Vector search implementation
- [ ] User authentication
- [ ] Document upload and processing
- [ ] Chat history persistence
- [ ] Multi-tenancy support
- [ ] Advanced analytics dashboard

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework
- [OpenAI](https://openai.com/) - AI models
- [pgvector](https://github.com/pgvector/pgvector) - Vector similarity search for Postgres

## 📞 Support

- 📧 Email: support@docuchat.example.com
- 💬 Discussions: [GitHub Discussions](https://github.com/your-org/docuchat/discussions)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/docuchat/issues)

---

**Version:** v0.1.0 | **Status:** Active Development | **Made with ❤️ for the open source community**