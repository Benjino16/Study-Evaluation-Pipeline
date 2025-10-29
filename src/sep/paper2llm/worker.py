import threading
import time
import traceback
from sep.paper2llm.process_paper import process_paper
from sep.logger import setup_logger
from .models import Run, RunStatus

log = setup_logger(__name__)

def run_paper(run: Run, delay=15, temp=1.0, single_process=False, pdf_reader=False, stop_event: threading.Event = None):
    run.status = RunStatus.RUNNING
    try:
        for file in run.files:
            if stop_event and stop_event.is_set():
                run.status = RunStatus.CANCELLED
                log.warning(f"Run {run.id} cancelled.")
                return

            last_output, save_folder = process_paper(
                run.prompt, run.model, file, delay, temp, single_process, pdf_reader, same_run=True
            )
            run.progress += 1 / len(run.files)
            run.result_path = save_folder
            if delay > 0:
                time.sleep(delay)

        run.status = RunStatus.FINISHED
    except Exception as e:
        run.status = RunStatus.FAILED
        run.message = traceback.format_exc()
        log.error(f"Error in run {run.id}: {run.message}")