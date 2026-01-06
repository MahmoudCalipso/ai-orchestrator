# AI Orchestrator - Start Script (Backend Only)
# This script starts the AI Orchestrator backend

Write-Host "🤖 Starting AI Orchestrator..." -ForegroundColor Cyan
Write-Host ""

# Check if Docker services are running
Write-Host "Checking Docker services..." -ForegroundColor Yellow
$redisRunning = docker ps --filter "name=redis" --format "{{.Names}}" | Select-String "redis"
$postgresRunning = docker ps --filter "name=postgres" --format "{{.Names}}" | Select-String "postgres"

if (-not $redisRunning) {
    Write-Host "⚠ Redis not running. Starting Docker services..." -ForegroundColor Yellow
    docker-compose up -d redis postgres
    Start-Sleep -Seconds 5
}

# Check for OpenAI API key
if (-not $env:OPENAI_API_KEY) {
    Write-Host "⚠ Warning: OPENAI_API_KEY not set" -ForegroundColor Yellow
    Write-Host "The Universal AI Agent will run in mock mode" -ForegroundColor Yellow
    Write-Host "To use real LLM capabilities, set:" -ForegroundColor Yellow
    Write-Host "  `$env:OPENAI_API_KEY='your-api-key-here'" -ForegroundColor Gray
    Write-Host ""
}

# Start the AI Orchestrator
Write-Host "Starting AI Orchestrator Backend..." -ForegroundColor Green
Write-Host ""
Write-Host "API Server: http://localhost:8080" -ForegroundColor White
Write-Host "API Docs:   http://localhost:8080/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python main.py
