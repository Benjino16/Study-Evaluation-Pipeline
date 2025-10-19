import pytest
from unittest.mock import patch
from sep.evaluation import load_saved_json

def test_load_json_version_1():
    result_json_data = load_saved_json.load_json("tests/test_data/test_results/raw-0005-20250115-130435.json")
    check_json_data(result_json_data, 1)

def test_load_json_version_2():
    result_json_data = load_saved_json.load_json("tests/test_data/test_results/raw-0005-20250508-135152.json")
    check_json_data(result_json_data, 2)

def test_load_jsons():
    result_json_data = load_saved_json.load_saved_jsons("tests/test_data/test_results/*.json")

    check_json_data(result_json_data[0], 1)
    check_json_data(result_json_data[1], 2)

    
def check_json_data(json_data, version):
    
    assert json_data["Date"] == "2025-05-08T11:51:52Z"
    assert json_data["Model_Name"] == "gpt-4o-2024-08-06"
    assert json_data["Temperature"] == 0.2
    assert json_data["PDF_Name"] == "0005"
    assert json_data["PDF_Reader"] is False
    assert json_data["PDF_Reader_Version"] == "-"
    assert json_data["Process_Mode"] == "process full pdf in single request"

    assert json_data["Raw_Data"] == "Raw Data"

    if version == 1:
        assert json_data["Version"] == 1
        assert json_data["Prompt"] == "-"
    if version == 2.0:
        assert json_data["Version"] == 2.0
        assert json_data["Prompt"] == "Test Prompt"