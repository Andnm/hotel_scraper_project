#!/bin/bash

# ========================================
# Health Check Script - Production
# ========================================
# Kiểm tra tất cả services có hoạt động không
# Usage: ./health-check.sh
# ========================================

echo "🏥 Starting health check..."
echo ""

# Màu sắc cho terminal
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter
PASS=0
FAIL=0

# Function to check
check_service() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $1"
        ((FAIL++))
    fi
}

# 1. Check Docker
echo "1️⃣ Checking Docker..."
docker --version > /dev/null 2>&1
check_service "Docker is installed"

docker compose version > /dev/null 2>&1
check_service "Docker Compose is installed"
echo ""

# 2. Check Containers
echo "2️⃣ Checking Containers..."
docker compose ps | grep -q "hotel_db.*Up"
check_service "MySQL container is running"

docker compose ps | grep -q "hotel_backend.*Up"
check_service "Backend container is running"

docker compose ps | grep -q "hotel_frontend.*Up"
check_service "Frontend container is running"
echo ""

# 3. Check Network connectivity
echo "3️⃣ Checking Network..."
docker compose exec -T backend curl -s http://localhost:8000 > /dev/null 2>&1
check_service "Backend is responding on port 8000"

curl -s http://localhost:80 > /dev/null 2>&1
check_service "Nginx is responding on port 80"
echo ""

# 4. Check Database
echo "4️⃣ Checking Database..."
docker compose exec -T db mysql -u root -p${DB_ROOT_PASSWORD} -e "SELECT 1" > /dev/null 2>&1
check_service "MySQL is accepting connections"

docker compose exec -T db mysql -u root -p${DB_ROOT_PASSWORD} -e "USE hotel_scraper; SHOW TABLES;" > /dev/null 2>&1
check_service "Database 'hotel_scraper' exists"
echo ""

# 5. Check Backend Services
echo "5️⃣ Checking Backend Services..."
docker compose exec -T backend bash -c "google-chrome --version" > /dev/null 2>&1
check_service "Google Chrome is installed"

docker compose exec -T backend bash -c "python -c 'import selenium'" > /dev/null 2>&1
check_service "Selenium is installed"
echo ""

# 6. Check API Endpoints
echo "6️⃣ Checking API Endpoints..."
curl -s http://localhost:80/api/sources/history > /dev/null 2>&1
check_service "API endpoint /api/sources/history is accessible"
echo ""

# 7. Check SSL (if applicable)
echo "7️⃣ Checking SSL..."
if [ -f "./certbot/conf/live/projecthub.io.vn/fullchain.pem" ]; then
    echo -e "${GREEN}✓${NC} SSL certificate exists"
    ((PASS++))
    
    # Check certificate expiry
    EXPIRY=$(openssl x509 -enddate -noout -in ./certbot/conf/live/projecthub.io.vn/fullchain.pem | cut -d= -f2)
    echo "   Certificate expires: $EXPIRY"
else
    echo -e "${YELLOW}⚠${NC} SSL certificate not found (HTTP-only mode)"
fi
echo ""

# 8. Check Disk Space
echo "8️⃣ Checking System Resources..."
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo -e "${GREEN}✓${NC} Disk usage: ${DISK_USAGE}%"
    ((PASS++))
else
    echo -e "${RED}✗${NC} Disk usage: ${DISK_USAGE}% (>80%)"
    ((FAIL++))
fi

# Check memory
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEMORY_USAGE -lt 90 ]; then
    echo -e "${GREEN}✓${NC} Memory usage: ${MEMORY_USAGE}%"
    ((PASS++))
else
    echo -e "${RED}✗${NC} Memory usage: ${MEMORY_USAGE}% (>90%)"
    ((FAIL++))
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Health Check Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${GREEN}Passed: $PASS${NC}"
echo -e "  ${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! System is healthy.${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some checks failed. Please investigate.${NC}"
    echo ""
    echo "💡 Tips:"
    echo "  - Check logs: docker compose logs -f"
    echo "  - Restart services: docker compose restart"
    echo "  - See troubleshooting: cat TROUBLESHOOTING.md"
    exit 1
fi
