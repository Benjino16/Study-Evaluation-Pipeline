import pytest
from evaluation import parse_json_answer, clean_study_number, parse_csv_string_to_json

def test_parse_json_answer():
    assert parse_json_answer("yes") == '1'
    assert parse_json_answer("Yes") == '1'
    assert parse_json_answer("1") == '1'
    assert parse_json_answer(1) == '1'
    assert parse_json_answer("no") == '0'
    assert parse_json_answer("No") == '0'
    assert parse_json_answer("0") == '0'
    assert parse_json_answer(0) == '0'

def test_clean_study_number():
    assert clean_study_number("1234.pdf") == "1234"
    assert clean_study_number("1234") == "1234"
    assert clean_study_number("0034") == "34"
    assert clean_study_number("0034.pdf") == "34"

def test_parse_csv_to_json_without_combination():
    csv_string = (
        "1;yes;answer to question 1\n"
        "2;no;answer to question 2\n"
        "3;no;answer to question 3\n"
        "5;yes;test\n"
        "7a;yes;answer to question 7a\n"
        "7b;yes;answer to question 7b\n"
        "7c;yes;answer to question 7c\n"
        "8;yes;answer to question 8\n"
        "9;yes;answer to question 9\n"
        "10;no;answer to question 10\n"
        "11;yes;answer to question 11\n"
        "12;yes;answer to question 12"
    )

    result = parse_csv_string_to_json(csv_string, combine_7abc=False)

    q1 = next((item for item in result if item["number"] == "1"), None)
    assert q1["answer"] == "yes"
    assert q1["quote"] == "answer to question 1"

    q7b = next((item for item in result if item["number"] == "7b"), None)
    assert q7b["answer"] == "yes"
    assert q7b["quote"] == "answer to question 7b"

def test_parse_csv_to_json_with_combination():
    csv_string = (
        "1;yes;answer to question 1\n"
        "7a;yes;quote 7a\n"
        "7b;no;quote 7b\n"
        "7c;yes;quote 7c"
    )

    result = parse_csv_string_to_json(csv_string, combine_7abc=True)

    numbers = [item["number"] for item in result]
    assert "7b" not in numbers
    assert "7c" not in numbers

    q7 = next((item for item in result if item["number"] == "7"), None)
    assert q7 is not None
    assert q7["answer"] == "no"
    assert "combined 7a, 7b, 7c" in q7["quote"]
