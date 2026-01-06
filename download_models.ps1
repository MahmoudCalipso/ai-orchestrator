# Quick Download Script for 2026 Models
# Run this to download all recommended models

Write-Host "🤖 Downloading 2026 State-of-the-Art AI Models..." -ForegroundColor Cyan
Write-Host ""

# Check if Ollama is installed
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✓ Ollama installed: $ollamaVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ Ollama not found. Please install:" -ForegroundColor Red
    Write-Host "  winget install Ollama.Ollama" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Select model tier to download:" -ForegroundColor Cyan
Write-Host "1. Minimal (16GB RAM) - Fast, efficient" -ForegroundColor White
Write-Host "2. Balanced (32GB RAM) - Recommended" -ForegroundColor Green
Write-Host "3. Full Power (64GB+ RAM) - Best quality" -ForegroundColor Yellow
Write-Host "4. Custom selection" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

$models = @()

switch ($choice) {
    "1" {
        Write-Host "Downloading Minimal tier..." -ForegroundColor Cyan
        $models = @(
            "qwen2.5-coder:14b",
            "qwen2.5-coder:7b",
            "glm4:9b"
        )
    }
    "2" {
        Write-Host "Downloading Balanced tier (Recommended)..." -ForegroundColor Green
        $models = @(
            "qwen2.5-coder:32b",
            "deepseek-r1:32b-q4",
            "qwen2.5-coder:14b",
            "glm4:9b",
            "codellama:13b"
        )
    }
    "3" {
        Write-Host "Downloading Full Power tier..." -ForegroundColor Yellow
        $models = @(
            "qwen3:235b-q4",
            "deepseek-r1:70b-q4",
            "qwen2.5-coder:32b",
            "glm4:9b",
            "deepseek-v3.2:671b-q4"
        )
    }
    "4" {
        Write-Host "Available models:" -ForegroundColor Cyan
        Write-Host "  qwen3:235b-q4 - #1 Coder (140GB)" -ForegroundColor White
        Write-Host "  deepseek-r1:70b-q4 - Best Reasoner (40GB)" -ForegroundColor White
        Write-Host "  qwen2.5-coder:32b - Dense Coding (20GB)" -ForegroundColor White
        Write-Host "  qwen2.5-coder:14b - Balanced (10GB)" -ForegroundColor White
        Write-Host "  qwen2.5-coder:7b - Fast (5GB)" -ForegroundColor White
        Write-Host "  glm4:9b - Frontend Specialist (6GB)" -ForegroundColor White
        Write-Host "  codellama:13b - Reliable Fallback (8GB)" -ForegroundColor White
        Write-Host ""
        $customModels = Read-Host "Enter model names (comma-separated)"
        $models = $customModels -split "," | ForEach-Object { $_.Trim() }
    }
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Downloading $($models.Count) models..." -ForegroundColor Cyan
Write-Host ""

$downloaded = 0
$failed = 0

foreach ($model in $models) {
    Write-Host "[$($downloaded + $failed + 1)/$($models.Count)] Downloading $model..." -ForegroundColor Yellow
    
    try {
        ollama pull $model
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $model downloaded successfully" -ForegroundColor Green
            $downloaded++
        }
        else {
            Write-Host "  ✗ Failed to download $model" -ForegroundColor Red
            $failed++
        }
    }
    catch {
        Write-Host "  ✗ Error downloading $model : $_" -ForegroundColor Red
        $failed++
    }
    
    Write-Host ""
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Download Summary:" -ForegroundColor Cyan
Write-Host "  ✓ Downloaded: $downloaded" -ForegroundColor Green
Write-Host "  ✗ Failed: $failed" -ForegroundColor Red
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

if ($downloaded -gt 0) {
    Write-Host "✅ Models ready to use!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Copy .env.example to .env" -ForegroundColor White
    Write-Host "2. Set LLM_PROVIDER=ollama in .env" -ForegroundColor White
    Write-Host "3. Run: .\start.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "List downloaded models: ollama list" -ForegroundColor Gray
}
