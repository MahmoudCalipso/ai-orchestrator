# AI Orchestrator - Start Script (Backend Only)
# This script starts the AI Orchestrator backend

Write-Host "🤖 Starting AI Orchestrator..." -ForegroundColor Cyan
Write-Host ""

# Check if Docker services are running
Write-Host "Checking Docker services..." -ForegroundColor Yellow
$redisRunning = docker ps --filter "name=redis" --format "{{.Names}}" | Select-String "redis"
$postgresRunning = docker ps --filter "name=postgres" --format "{{.Names}}" | Select-String "postgres"

if (-not $redisRunning -or -not $postgresRunning) {
    Write-Host "⚠ Docker services not running. Starting..."-ForegroundColor Yellow
    docker-compose up -d redis postgres
    Start-Sleep -Seconds 5
}

# Check for Ollama
$ollamaPath = "C:\Users\CALIPSO\AppData\Local\Programs\Ollama\ollama.exe"
if (-not (Test-Path $ollamaPath)) {
    Write-Host "⚠ Warning: Ollama not found at $ollamaPath" -ForegroundColor Yellow
    Write-Host "Please install Ollama from https://ollama.ai" -ForegroundColor Yellow
    Write-Host ""
}
else {
    Write-Host "✓ Ollama found" -ForegroundColor Green
    # Check if models are downloaded
    $models = & $ollamaPath list 2>$null
    if ($models -match "qwen2.5-coder") {
        Write-Host "✓ AI models ready" -ForegroundColor Green
    }
    else {
        Write-Host "⚠ No AI models found. Download with:" -ForegroundColor Yellow
        Write-Host "  $ollamaPath pull qwen2.5-coder:7b" -ForegroundColor Gray
    }
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
