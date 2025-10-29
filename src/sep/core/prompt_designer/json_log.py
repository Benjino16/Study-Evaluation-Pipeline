import json
import os
from datetime import datetime
from sep.env_manager import ADJUSTED_PROMPT_FOLDER
from sep.logger import setup_logger

log = setup_logger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR + ADJUSTED_PROMPT_FOLDER, "prompt_designer_log.json")


def init_log(init_data: dict):
    """
    Creates a JSON log file with initial data.
    If the file already exists, it will be overwritten.
    """

    path = LOG_PATH
    data = {
        "date": datetime.now().isoformat(),
        "prompt_design_prompt": init_data.get("prompt_design_prompt", ""),
        "base_prompt": init_data.get("base_prompt", ""),
        "papers": init_data.get("papers", []),
        "tested_papers": init_data.get("tested_papers", []),
        "base_accuracy": init_data.get("base_accuracy", 0.0),
        "runs": []
    }

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    log.info(f"[LOG INIT] Creating log at: {LOG_PATH}")


def update_log(run_data: dict):
    """
    Adds a new run entry to the log JSON file.
    """
    path = LOG_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Log file not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        json_log = json.load(f)

    entry = {
        "date": datetime.now().isoformat(),
        "input_prompt": run_data.get("input_prompt", ""),
        "adjusted_prompt": run_data.get("adjusted_prompt", ""),
        "paper_used_for_adjustment": run_data.get("paper_used_for_adjustment", ""),
        "tested_papers": run_data.get("tested_papers", []),
        "accuracy": run_data.get("accuracy", 0.0),
    }

    json_log["runs"].append(entry)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_log, f, indent=4)
    log.info(f"[LOG UPDATE] Added new entry to log at: {path}")