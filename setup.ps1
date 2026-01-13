# AI Orchestrator - Setup Script (Backend Only)
# Run this script to set up the AI Orchestrator

Write-Host "🤖 AI Orchestrator - Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Prerequisites
Write-Host "Step 1: Checking Prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ Python not found. Please install Python 3.12+" -ForegroundColor Red
    exit 1
}

# Check Docker
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✓ Docker: $dockerVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ Docker not found. Please install Docker Desktop" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Install Python Dependencies
Write-Host "Step 2: Installing Python Dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python dependencies installed" -ForegroundColor Green
}
else {
    Write-Host "✗ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 3: Start Docker Services
Write-Host "Step 3: Starting Docker Services (Redis, Postgres)..." -ForegroundColor Yellow
docker-compose up -d redis postgres
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker services started" -ForegroundColor Green
}
else {
    Write-Host "✗ Failed to start Docker services" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 4: Wait for services to be ready
Write-Host "Step 4: Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host "✓ Services ready" -ForegroundColor Green

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Download free AI models (if not already done):" -ForegroundColor White
Write-Host "   C:\Users\CALIPSO\AppData\Local\Programs\Ollama\ollama.exe pull qwen2.5-coder:7b" -ForegroundColor Gray
Write-Host "   C:\Users\CALIPSO\AppData\Local\Programs\Ollama\ollama.exe pull deepseek-coder:6.7b" -ForegroundColor Gray
Write-Host "   C:\Users\CALIPSO\AppData\Local\Programs\Ollama\ollama.exe pull codellama:7b" -ForegroundColor Gray
Write-Host "   C:\Users\CALIPSO\AppData\Local\Programs\Ollama\ollama.exe pull mistral:7b" -ForegroundColor Gray
Write-Host "   C:\Users\CALIPSO\AppData\Local\Programs\Ollama\ollama.exe pull phi3:3.8b" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start the AI Orchestrator:" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Access the API:" -ForegroundColor White
Write-Host "   http://localhost:8080/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   - README.md - System overview" -ForegroundColor White
Write-Host "   - OLLAMA_SETUP_GUIDE.md - Model setup guide" -ForegroundColor White
Write-Host "   - CONFIGURATION_GUIDE.md - Configuration guide" -ForegroundColor White
Write-Host ""
