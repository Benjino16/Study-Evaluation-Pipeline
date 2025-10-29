from fastapi import FastAPI
from pydantic import BaseModel
from sep.paper2llm.manager import RunManager
from sep.paper2llm.models import Run

app = FastAPI(title="Study Evaluation Runner API")
manager = RunManager()

# Eingabe-Model für /runs/
class RunRequest(BaseModel):
    prompt: str
    model: str
    files: list[str]
    delay: int = 15
    temp: float = 1.0
    single_process: bool = False
    pdf_reader: bool = False

@app.post("/runs/", response_model=Run)
def start_run(request: RunRequest):
    run = manager.start_run(
        prompt=request.prompt,
        model=request.model,
        files=request.files,
        delay=request.delay,
        temp=request.temp,
        single_process=request.single_process,
        pdf_reader=request.pdf_reader,
    )
    return run

@app.get("/runs/", response_model=list[Run])
def list_runs():
    return manager.list_runs()

@app.get("/runs/{run_id}", response_model=Run | None)
def get_run(run_id: str):
    return manager.get_run(run_id)

@app.post("/runs/{run_id}/stop")
def stop_run(run_id: str):
    manager.stop_run(run_id)
    return {"status": "stopping"}
