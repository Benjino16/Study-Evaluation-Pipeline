import threading
import uuid
from sep.runner.models import Run
from sep.runner.worker import run_paper

class RunManager:
    def __init__(self):
        self.runs: dict[str, Run] = {}
        self.threads: dict[str, threading.Thread] = {}
        self.stop_events: dict[str, threading.Event] = {}

    def start_run(self, prompt, model, files, **kwargs) -> Run:
        run_id = str(uuid.uuid4())
        run = Run(id=run_id, prompt=prompt, model=model, files=files)
        self.runs[run_id] = run

        stop_event = threading.Event()
        self.stop_events[run_id] = stop_event

        thread = threading.Thread(target=run_paper, args=(run,), kwargs={**kwargs, "stop_event": stop_event}, daemon=True)
        self.threads[run_id] = thread
        thread.start()

        return run

    def stop_run(self, run_id: str):
        if run_id in self.stop_events:
            self.stop_events[run_id].set()

    def get_run(self, run_id: str) -> Run:
        return self.runs.get(run_id)

    def list_runs(self) -> list[Run]:
        return list(self.runs.values())
