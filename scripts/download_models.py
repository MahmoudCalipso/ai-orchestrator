import os
import json
import time
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

console = Console()

def download_model(model_name, ollama_host):
    url = f"{ollama_host}/api/pull"
    payload = {"name": model_name}
    
    with requests.post(url, json=payload, stream=True) as response:
        if response.status_code != 200:
            console.print(f"[red]❌ Error: Failed to start download for {model_name} (Status: {response.status_code})[/red]")
            return False
            
        # Initialize progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=True
        ) as progress:
            
            task_id = progress.add_task(f"Downloading {model_name}...", total=100)
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    status = data.get("status", "")
                    
                    if status == "pulling manifest":
                        continue
                        
                    completed = data.get("completed", 0)
                    total = data.get("total", 0)
                    
                    if total > 0:
                        progress.update(task_id, completed=completed, total=total, description=f"Downloading {model_name} ({status})")
                    else:
                        progress.update(task_id, description=f"Status: {status}")
                        
                    if status == "success":
                        return True
    return False

def wait_for_ollama(ollama_host):
    console.print(f"[cyan]⏳ Waiting for Ollama service at {ollama_host}...[/cyan]")
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get(f"{ollama_host}/api/tags")
            if response.status_code == 200:
                console.print("[green]✓ Ollama is ready![/green]")
                return True
        except:
            pass
        time.sleep(2)
        console.print(f"  Attempt {i+1}/{max_attempts}...")
    return False

def main():
    ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    model_tier = os.getenv("MODEL_TIER", "minimal")
    
    # Define model tiers (sync with download_models.sh if possible)
    TIERS = {
        "minimal": ["qwen2.5-coder:7b", "glm4:9b"],
        "balanced": ["qwen2.5-coder:14b", "qwen2.5-coder:7b", "glm4:9b", "codellama:13b"],
        "full": ["qwen2.5-coder:32b", "deepseek-r1:32b-q4", "qwen2.5-coder:14b", "glm4:9b"],
        "ultra": ["qwen3:235b-q4", "deepseek-r1:70b-q4", "qwen2.5-coder:32b", "glm4:9b"]
    }
    
    selected_models = TIERS.get(model_tier, TIERS["minimal"])
    
    console.print(f"\n[bold cyan]🤖 IA-Orchestrator 2026 - Ultimate Model Downloader[/bold cyan]")
    console.print(f"[bold cyan]================================================[/bold cyan]\n")
    
    if not wait_for_ollama(ollama_host):
        console.print("[red]❌ Error: Ollama service timed out.[/red]")
        return

    console.print(f"[yellow]📦 Tier Selected:[/yellow] [bold white]{model_tier}[/bold white]")
    console.print(f"[yellow]📦 Models to acquire:[/yellow] [bold white]{', '.join(selected_models)}[/bold white]\n")

    summary_table = Table(title="Download Summary", show_header=True, header_style="bold magenta")
    summary_table.add_column("Model", style="cyan")
    summary_table.add_column("Status", style="green")

    with Live(summary_table, console=console, refresh_per_second=4):
        for model in selected_models:
            # We need to render the progress separately but show the table simultaneously?
            # Actually, let's just do them sequentially but keep the table updated.
            pass

    # Better approach for Live:
    overall_status = []
    
    for i, model in enumerate(selected_models):
        console.print(f"\n[bold blue][{i+1}/{len(selected_models)}] Processing {model}...[/bold blue]")
        success = download_model(model, ollama_host)
        if success:
            console.print(f"[bold green]✓ {model} is ready![/bold green]")
            overall_status.append((model, "✅ Success"))
        else:
            console.print(f"[bold red]✗ {model} failed![/bold red]")
            overall_status.append((model, "❌ Failed"))

    console.print(f"\n[bold cyan]================================================[/bold cyan]")
    final_table = Table(title="Final Status Report", show_header=True, header_style="bold magenta")
    final_table.add_column("Model", style="cyan")
    final_table.add_column("Result", style="green")
    for m, s in overall_status:
        final_table.add_row(m, s)
    console.print(final_table)
    console.print(f"\n[bold green]🚀 All set! IA-Orchestrator is ready to dominate.[/bold green]\n")

if __name__ == "__main__":
    main()
