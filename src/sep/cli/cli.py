import typer
import requests
from sep.core.file_manager.file_manager import get_papers_from_schema
from sep.prompt_manager import getPrompt
from sep.env_manager import PROMPT_PATH

API_URL = "http://127.0.0.1:8000"

app = typer.Typer(help="CLI client for the persistent RunManager API.")

@app.command("start")
def start(
    model: str = typer.Option(..., "-m"),
    files: list[str] = typer.Option(None, "-f"),
    delay: int = 15,
    temp: float = 1.0,
    prompt_path: str = None,
):
    """Start a new run via the API."""
    pdf_paths = files or get_papers_from_schema("main")
    prompt = getPrompt(prompt_path or PROMPT_PATH)

    data = {
        "model": model,
        "prompt": prompt,
        "files": pdf_paths,
        "delay": delay,
        "temp": temp,
    }

    r = requests.post(f"{API_URL}/runs/", json=data)
    if r.status_code == 200:
        run = r.json()
        typer.echo(f"✅ Started run {run['id']} ({len(pdf_paths)} files).")
    else:
        typer.echo(f"❌ Error: {r.text}")

@app.command("list")
def list_runs():
    """List all runs."""
    r = requests.get(f"{API_URL}/runs/")
    runs = r.json()
    if not runs:
        typer.echo("No runs found.")
        return
    for run in runs:
        typer.echo(f"{run['id']} | {run['status']} | {run['progress']*100:.0f}% | {run['model']}")

@app.command("status")
def status(run_id: str):
    """Show status of a specific run."""
    r = requests.get(f"{API_URL}/runs/{run_id}")
    if r.status_code == 404 or not r.json():
        typer.echo("Run not found.")
        return
    run = r.json()
    typer.echo(f"{run['id']}: {run['status']} ({run['progress']*100:.1f}%)")

@app.command("stop")
def stop(run_id: str):
    """Stop a running run."""
    r = requests.post(f"{API_URL}/runs/{run_id}/stop")
    if r.status_code == 200:
        typer.echo(f"🛑 Stopping run {run_id}...")
    else:
        typer.echo(f"❌ Error: {r.text}")

@app.command("serve")
def serve(
    host: str = "127.0.0.1",
    port: int = 8000,
):
    """Start the RunManager API service."""
    import uvicorn
    from sep.api.run_api import app as api_app
    typer.echo(f"🚀 Starting RunManager API on http://{host}:{port}")
    uvicorn.run(api_app, host=host, port=port)

if __name__ == "__main__":
    app()
 