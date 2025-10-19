import pytest
from unittest.mock import patch
from sep.prompt_designer import run_prompt_design

def test_run_prompt_designer_flow(tmp_path):
    base_prompt_json = tmp_path / "base_prompt.json"
    base_prompt_json.write_text('{"prompt": "BASE"}', encoding="utf-8")

    fake_data = [{"dummy": 1}]
    fake_compare_result = {"global_accuracy": 0.5}

    with patch.object(run_prompt_design, "load_json", return_value={"prompt": "BASE"}) as mock_load_json, \
         patch.object(run_prompt_design, "adjust_prompt", side_effect=lambda p, f, m, t: f"{p}_ADJ") as mock_adjust, \
         patch.object(run_prompt_design, "process_paper", return_value=("ANSWER", str(tmp_path / "run1/"))) as mock_proc, \
         patch.object(run_prompt_design, "load_saved_jsons", return_value=fake_data) as mock_load_saved, \
         patch.object(run_prompt_design, "compare_data", return_value=fake_compare_result) as mock_compare, \
         patch.object(run_prompt_design, "init_log") as mock_init_log, \
         patch.object(run_prompt_design, "update_log") as mock_update_log, \
         patch("time.sleep", return_value=None):  # verhindert echte Wartezeit

        run_prompt_design.run_prompt_designer(
            base_prompt_json=str(base_prompt_json),
            loop=2,
            test_paper=1,
            papers=["paper1.pdf", "paper2.pdf"],
            model="mock-model",
            temp=0.7,
            csv="mock.csv",
            delay=0
        )

    # --- Assertions ---
    mock_load_json.assert_called_once_with(str(base_prompt_json))
    assert mock_adjust.call_count == 2
    assert mock_proc.call_count >= 2  # Baseline + Adjusted Loops
    mock_load_saved.assert_called()
    mock_compare.assert_called()
    mock_init_log.assert_called_once()
    assert mock_update_log.call_count == 2  # zwei Loops

    # Optionale Validierung: update_log Inhalt prüfen
    last_call = mock_update_log.call_args_list[-1][0][0]  # erster Arg (dict)
    assert "accuracy" in last_call
    assert isinstance(last_call["accuracy"], float)
