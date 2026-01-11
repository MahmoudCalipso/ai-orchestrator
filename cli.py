#!/usr/bin/env python3
"""
AI Orchestrator CLI Tool
"""
import click
import requests
import json
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

console = Console()


class OrchestratorCLI:
    """CLI for interacting with AI Orchestrator"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
    
    def _request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            console.print("[red]✗ Could not connect to orchestrator[/red]")
            console.print(f"Make sure the service is running at {self.base_url}")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            console.print(f"[red]✗ HTTP Error: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            sys.exit(1)


@click.group()
@click.option('--url', default='http://localhost:8080', help='Orchestrator URL')
@click.option('--api-key', default='dev-key-12345', help='API key')
@click.pass_context
def cli(ctx, url, api_key):
    """AI Orchestrator CLI Tool"""
    ctx.obj = OrchestratorCLI(url, api_key)


@cli.command()
@click.pass_obj
def health(cli_obj):
    """Check orchestrator health"""
    response = cli_obj._request('GET', '/health')
    
    status_color = "green" if response['status'] == 'healthy' else "red"
    
    console.print(Panel(
        f"[{status_color}]Status: {response['status']}[/{status_color}]\n"
        f"Uptime: {response['uptime']:.2f}s\n"
        f"Models Loaded: {response['models_loaded']}\n"
        f"Runtimes: {', '.join(response['runtimes_available'])}",
        title="[bold]Health Check[/bold]",
        border_style=status_color
    ))


@cli.command()
@click.pass_obj
def status(cli_obj):
    """Get detailed system status"""
    response = cli_obj._request('GET', '/status')
    
    # System info
    console.print("\n[bold cyan]System Status[/bold cyan]")
    console.print(f"Status: [green]{response['status']}[/green]")
    console.print(f"Uptime: {response['uptime']:.2f}s")
    
    # Resources
    resources = response['resources']
    console.print("\n[bold cyan]Resources[/bold cyan]")
    console.print(f"CPU: {resources['cpu_percent']:.1f}%")
    console.print(f"Memory: {resources['memory_percent']:.1f}%")
    console.print(f"Disk: {resources['disk_percent']:.1f}%")
    
    # GPUs
    if resources.get('gpus'):
        console.print("\n[bold cyan]GPUs[/bold cyan]")
        for gpu in resources['gpus']:
            console.print(
                f"  {gpu['name']}: {gpu['load']:.1f}% load, "
                f"{gpu['memory_used']}MB/{gpu['memory_total']}MB"
            )
    
    # Metrics
    metrics = response.get('metrics', {})
    if metrics:
        console.print("\n[bold cyan]Metrics[/bold cyan]")
        console.print(f"Total Requests: {metrics.get('total_requests', 0)}")
        console.print(f"Success Rate: {metrics.get('success_rate', 0):.2%}")


@cli.command()
@click.pass_obj
def models(cli_obj):
    """List available models"""
    response = cli_obj._request('GET', '/models')
    
    table = Table(title="Available Models")
    table.add_column("Name", style="cyan")
    table.add_column("Family", style="magenta")
    table.add_column("Size", style="green")
    table.add_column("Specialization", style="yellow")
    table.add_column("Status", style="blue")
    
    for model in response:
        table.add_row(
            model['name'],
            model['family'],
            model['size'],
            model['specialization'],
            model['status']
        )
    
    console.print(table)


@cli.command()
@click.argument('model_name')
@click.pass_obj
def model_info(cli_obj, model_name):
    """Get detailed model information"""
    response = cli_obj._request('GET', f'/models/{model_name}')
    
    console.print(Panel(
        f"[bold]Name:[/bold] {response['name']}\n"
        f"[bold]Family:[/bold] {response['family']}\n"
        f"[bold]Size:[/bold] {response['size']}\n"
        f"[bold]Context Length:[/bold] {response['context_length']}\n"
        f"[bold]Capabilities:[/bold] {', '.join(response['capabilities'])}\n"
        f"[bold]Specialization:[/bold] {response['specialization']}\n"
        f"[bold]Memory Requirement:[/bold] {response['memory_requirement']}\n"
        f"[bold]Status:[/bold] {response['status']}",
        title=f"[bold]{model_name}[/bold]",
        border_style="cyan"
    ))


@cli.command()
@click.argument('prompt')
@click.option('--model', '-m', help='Specific model to use')
@click.option('--task', '-t', default='chat', help='Task type')
@click.option('--temperature', default=0.7, help='Temperature')
@click.option('--max-tokens', default=2048, help='Max tokens')
@click.option('--stream/--no-stream', default=False, help='Stream output')
@click.pass_obj
def infer(cli_obj, prompt, model, task, temperature, max_tokens, stream):
    """Run inference"""
    
    payload = {
        "prompt": prompt,
        "task_type": task,
        "parameters": {
            "temperature": temperature,
            "max_tokens": max_tokens
        }
    }
    
    if model:
        payload["model"] = model
    
    if stream:
        console.print("[yellow]Streaming output:[/yellow]\n")
        
        response = requests.post(
            f"{cli_obj.base_url}/inference/stream",
            headers=cli_obj.headers,
            json=payload,
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8').replace('data: ', ''))
                    if 'text' in data:
                        console.print(data['text'], end='')
                except:
                    pass
        console.print("\n")
    else:
        with Progress() as progress:
            task_id = progress.add_task("[cyan]Generating...", total=None)
            
            response = cli_obj._request('POST', '/inference', json=payload)
            
            progress.update(task_id, completed=True)
        
        console.print(Panel(
            response['output'],
            title=f"[bold]Response from {response['model']}[/bold]",
            border_style="green"
        ))
        
        console.print(f"\n[dim]Tokens: {response['tokens_used']} | "
                     f"Time: {response['processing_time']:.2f}s[/dim]")


@cli.command()
@click.argument('model_name')
@click.pass_obj
def load(cli_obj, model_name):
    """Load a model"""
    with console.status(f"[yellow]Loading {model_name}...[/yellow]"):
        response = cli_obj._request('POST', f'/models/{model_name}/load')
    
    console.print(f"[green]✓ {model_name} loaded successfully[/green]")


@cli.command()
@click.argument('model_name')
@click.pass_obj
def unload(cli_obj, model_name):
    """Unload a model"""
    with console.status(f"[yellow]Unloading {model_name}...[/yellow]"):
        response = cli_obj._request('POST', f'/models/{model_name}/unload')
    
    console.print(f"[green]✓ {model_name} unloaded successfully[/green]")


@cli.command()
@click.pass_obj
def metrics(cli_obj):
    """Show system metrics"""
    response = cli_obj._request('GET', '/metrics')
    
    table = Table(title="System Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Requests", str(response['total_requests']))
    table.add_row("Successful Requests", str(response['successful_requests']))
    table.add_row("Failed Requests", str(response['failed_requests']))
    table.add_row("Success Rate", f"{response['success_rate']:.2%}")
    table.add_row("Avg Processing Time", f"{response['average_processing_time']:.2f}s")
    table.add_row("Total Tokens", str(response['total_tokens']))
    
    console.print(table)


@cli.command()
@click.option('--num', '-n', default=5, help='Number of test requests')
@click.pass_obj
def benchmark(cli_obj, num):
    """Run performance benchmark"""
    console.print(f"\n[yellow]Running {num} test requests...[/yellow]\n")
    
    import time
    results = []
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Benchmarking...", total=num)
        
        for i in range(num):
            start = time.time()
            
            try:
                response = cli_obj._request(
                    'POST',
                    '/inference',
                    json={
                        "prompt": f"Test {i+1}",
                        "task_type": "quick_query"
                    }
                )
                
                duration = time.time() - start
                results.append({
                    "success": True,
                    "time": duration,
                    "tokens": response.get('tokens_used', 0)
                })
            except:
                results.append({"success": False})
            
            progress.update(task, advance=1)
    
    # Calculate statistics
    successful = [r for r in results if r.get('success')]
    times = [r['time'] for r in successful]
    
    console.print("\n[bold cyan]Benchmark Results[/bold cyan]")
    console.print(f"Total Requests: {num}")
    console.print(f"Successful: {len(successful)}")
    console.print(f"Failed: {num - len(successful)}")
    
    if times:
        console.print(f"Avg Response Time: {sum(times)/len(times):.2f}s")
        console.print(f"Min Response Time: {min(times):.2f}s")
        console.print(f"Max Response Time: {max(times):.2f}s")


@cli.command()
@click.pass_obj
def interactive(cli_obj):
    """Start interactive chat session"""
    console.print("[bold cyan]Interactive Chat Session[/bold cyan]")
    console.print("[dim]Type 'exit' or 'quit' to end session[/dim]\n")
    
    while True:
        try:
            prompt = console.input("[yellow]You:[/yellow] ")
            
            if prompt.lower() in ['exit', 'quit']:
                console.print("[cyan]Goodbye![/cyan]")
                break
            
            if not prompt.strip():
                continue
            
            response = cli_obj._request(
                'POST',
                '/inference',
                json={
                    "prompt": prompt,
                    "task_type": "chat"
                }
            )
            
            console.print(f"[green]Assistant:[/green] {response['output']}\n")
            
        except KeyboardInterrupt:
            console.print("\n[cyan]Goodbye![/cyan]")
            break


@cli.command()
@click.argument('file_path')
@click.option('--task', '-t', default='chat', help='Task type')
@click.pass_obj
def batch(cli_obj, file_path, task):
    """Process prompts from file"""
    try:
        with open(file_path, 'r') as f:
            prompts = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        console.print(f"[red]✗ File not found: {file_path}[/red]")
        sys.exit(1)
    
    console.print(f"[yellow]Processing {len(prompts)} prompts...[/yellow]\n")
    
    with Progress() as progress:
        task_id = progress.add_task("[cyan]Processing...", total=len(prompts))
        
        for i, prompt in enumerate(prompts, 1):
            response = cli_obj._request(
                'POST',
                '/inference',
                json={
                    "prompt": prompt,
                    "task_type": task
                }
            )
            
            console.print(f"\n[bold]Prompt {i}:[/bold] {prompt}")
            console.print(f"[bold]Response:[/bold] {response['output']}\n")
            
            progress.update(task_id, advance=1)


if __name__ == '__main__':
    # Install rich if not available
    try:
        from rich.console import Console
    except ImportError:
        print("Installing required package 'rich'...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'rich'])
        from rich.console import Console
    
    cli()