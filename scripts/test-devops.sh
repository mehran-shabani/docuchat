#!/bin/bash
# Test script for DevOps infrastructure

set -e

echo "==========================================="
echo "🧪 Testing DocuChat DevOps Infrastructure"
echo "==========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if services are running
echo "📍 Step 1: Checking if services are running..."
echo ""

check_service() {
    local name=$1
    local url=$2
    
    if curl -sf "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name is running${NC}"
        return 0
    else
        echo -e "${RED}❌ $name is not running${NC}"
        return 1
    fi
}

check_service "Backend API" "http://localhost:8000/api/v1/health"
check_service "Metrics Endpoint" "http://localhost:8000/api/v1/metrics"
check_service "Prometheus" "http://localhost:9090/-/healthy"
check_service "Grafana" "http://localhost:3001/api/health"

echo ""
echo "📊 Step 2: Checking Prometheus metrics..."
echo ""

# Fetch metrics and check for our custom metrics
METRICS=$(curl -s http://localhost:8000/api/v1/metrics)

check_metric() {
    local metric=$1
    if echo "$METRICS" | grep -q "^${metric}"; then
        echo -e "${GREEN}✅ Metric '${metric}' is present${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Metric '${metric}' not found (may appear after first usage)${NC}"
        return 1
    fi
}

check_metric "openai_tokens_total"
check_metric "ml_fallback_total"
check_metric "http_request_duration_seconds"
check_metric "openai_request_total"
check_metric "rag_query_total"
check_metric "document_chunks_total"

echo ""
echo "🔍 Step 3: Checking Prometheus targets..."
echo ""

# Check if Prometheus can scrape our backend
TARGETS=$(curl -s http://localhost:9090/api/v1/targets | grep -c "backend:8000" || echo "0")
if [ "$TARGETS" -gt 0 ]; then
    echo -e "${GREEN}✅ Prometheus is configured to scrape backend${NC}"
else
    echo -e "${YELLOW}⚠️  Prometheus target configuration not found (expected in K8s)${NC}"
fi

echo ""
echo "📈 Step 4: Testing Prometheus query..."
echo ""

# Test a simple Prometheus query
QUERY_RESULT=$(curl -s "http://localhost:9090/api/v1/query?query=up" | grep -c '"status":"success"' || echo "0")
if [ "$QUERY_RESULT" -gt 0 ]; then
    echo -e "${GREEN}✅ Prometheus queries are working${NC}"
else
    echo -e "${RED}❌ Prometheus queries failed${NC}"
fi

echo ""
echo "📊 Step 5: Checking Grafana datasource..."
echo ""

# Check if Grafana has Prometheus datasource
DATASOURCE=$(curl -s -u admin:admin http://localhost:3001/api/datasources | grep -c '"type":"prometheus"' || echo "0")
if [ "$DATASOURCE" -gt 0 ]; then
    echo -e "${GREEN}✅ Grafana has Prometheus datasource configured${NC}"
else
    echo -e "${YELLOW}⚠️  Grafana datasource not configured (may need manual setup)${NC}"
fi

echo ""
echo "🐳 Step 6: Checking Docker containers..."
echo ""

CONTAINERS=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep docuchat || echo "")
if [ -n "$CONTAINERS" ]; then
    echo -e "${GREEN}✅ DocuChat containers are running:${NC}"
    echo "$CONTAINERS"
else
    echo -e "${YELLOW}⚠️  No DocuChat containers found. Run 'make devops-up' first.${NC}"
fi

echo ""
echo "📝 Step 7: Checking configuration files..."
echo ""

check_file() {
    local file=$1
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file exists${NC}"
        return 0
    else
        echo -e "${RED}❌ $file missing${NC}"
        return 1
    fi
}

check_file ".github/workflows/ci.yml"
check_file ".github/workflows/deploy.yml"
check_file "infra/docker-compose.yml"
check_file "infra/chart/Chart.yaml"
check_file "infra/chart/values.yaml"
check_file "infra/prometheus/prometheus.yml"
check_file "infra/prometheus/alerts.yml"
check_file "infra/grafana/datasources.yaml"
check_file "Makefile"

echo ""
echo "🔐 Step 8: Checking Helm chart..."
echo ""

if command -v helm &> /dev/null; then
    if helm lint infra/chart > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Helm chart is valid${NC}"
    else
        echo -e "${RED}❌ Helm chart validation failed${NC}"
        helm lint infra/chart
    fi
else
    echo -e "${YELLOW}⚠️  Helm not installed, skipping chart validation${NC}"
fi

echo ""
echo "==========================================="
echo "📊 Test Summary"
echo "==========================================="
echo ""

# Simple summary
echo "Core services:"
curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1 && echo -e "${GREEN}  ✅ Backend API${NC}" || echo -e "${RED}  ❌ Backend API${NC}"
curl -sf http://localhost:8000/api/v1/metrics > /dev/null 2>&1 && echo -e "${GREEN}  ✅ Metrics endpoint${NC}" || echo -e "${RED}  ❌ Metrics endpoint${NC}"
curl -sf http://localhost:9090/-/healthy > /dev/null 2>&1 && echo -e "${GREEN}  ✅ Prometheus${NC}" || echo -e "${RED}  ❌ Prometheus${NC}"
curl -sf http://localhost:3001/api/health > /dev/null 2>&1 && echo -e "${GREEN}  ✅ Grafana${NC}" || echo -e "${RED}  ❌ Grafana${NC}"

echo ""
echo "Configuration files:"
[ -f ".github/workflows/ci.yml" ] && echo -e "${GREEN}  ✅ CI workflow${NC}" || echo -e "${RED}  ❌ CI workflow${NC}"
[ -f ".github/workflows/deploy.yml" ] && echo -e "${GREEN}  ✅ CD workflow${NC}" || echo -e "${RED}  ❌ CD workflow${NC}"
[ -f "infra/chart/Chart.yaml" ] && echo -e "${GREEN}  ✅ Helm chart${NC}" || echo -e "${RED}  ❌ Helm chart${NC}"
[ -f "Makefile" ] && echo -e "${GREEN}  ✅ Makefile${NC}" || echo -e "${RED}  ❌ Makefile${NC}"

echo ""
echo "==========================================="
echo ""

# Final message
if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1 && \
   curl -sf http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✅ DevOps infrastructure is working!${NC}"
    echo ""
    echo "🎉 You can now:"
    echo "   • View metrics: http://localhost:9090"
    echo "   • View dashboards: http://localhost:3001 (admin/admin)"
    echo "   • Access API: http://localhost:8000/docs"
    echo ""
else
    echo -e "${YELLOW}⚠️  Some services are not running.${NC}"
    echo ""
    echo "💡 To start services, run:"
    echo "   make devops-up"
    echo ""
fi

echo "For full documentation, see:"
echo "   • docs/fa/devops-guide.md"
echo "   • infra/README.md"
echo ""
