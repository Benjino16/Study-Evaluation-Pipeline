import argparse
import pandas as pd
from sep.evaluation.load_saved_json import load_saved_jsons
from sep.evaluation.parse_csv_answers import clean_study_number
from sep.evaluation.parse_csv_answers import parse_json_answer
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, matthews_corrcoef
from sep.env_manager import DEFAULT_CSV
import logging

logging.basicConfig(level=logging.INFO)

# Papers that should be in the run
papers = [
    "0005", "0013", "0019", "0031", "0054", "0094", "0098", "0100", "0110", "0124", "0125", "0129", "0172",
    "0191", "0214", "0223", "0226", "0280", "0317", "0379", "0400", "0424", "0435", "0480", "0491", "0535",
    "0541", "0646", "0665", "0705", "0714", "0732", "0760", "0819", "0827", "0837", "0887", "0891", "0935"
]

def load_correct_answers(csv_file):
    """Load correct answers from the CSV file into a pandas DataFrame."""
    df = pd.read_csv(csv_file, delimiter=';', dtype={'answer': str})

    # clean study_number
    df['study_number'] = df['study_number'].apply(clean_study_number)

    df = df[df["answer"] != "NA"]
    return df

def convert_model_prediction_df(data):
    """Convert the model prediction dictionary into a DataFrame."""
    records = []

    for entry in data:
        pdf_name = entry.get('PDF_Name')
        for response in entry.get('Prompts', []):
            prompt_number = str(response.get('number'))
            json_answer = parse_json_answer(response.get('answer'))

            records.append({
                "study_number": clean_study_number(pdf_name),
                "prompt_number": prompt_number,
                "model_answer": json_answer
            })

    df = pd.DataFrame(records)
    return df


def compare_data(data, csv: str, ignore_na: bool = False):
    """
    Vergleicht die Daten aus einem Run mit den Antworten aus einer CSV-Datei.
    Gibt Gesamtmetriken und Genauigkeiten pro Frage & pro Paper zurück.
    """
    prediction_df = convert_model_prediction_df(data)
    correct_answers_df = load_correct_answers(csv)

    # Zusammenführen
    df_merged = pd.merge(
        correct_answers_df,
        prediction_df,
        on=['study_number', 'prompt_number'],
        how='left',
        suffixes=('_correct', '_pred')
    )

    # Fehlende Werte ignorieren
    if ignore_na:
        df_merged = df_merged.dropna(subset=['answer', 'model_answer'])

    # True/Pred extrahieren
    y_true = df_merged['answer']
    y_pred = df_merged['model_answer']

    # --- Gesamtmetriken ---
    results = {
        "overall": {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, average='weighted', zero_division=0),
            "recall": recall_score(y_true, y_pred, average='weighted', zero_division=0),
            "f1": f1_score(y_true, y_pred, average='weighted', zero_division=0),
            "n_samples": len(df_merged),
        },
    }

    # --- Genauigkeit pro Frage (alphabetisch sortiert) ---
    acc_by_question = (
        df_merged.groupby('prompt_number')
        .apply(lambda g: accuracy_score(g['answer'], g['model_answer']))
        .sort_index()  # sortiert alphabetisch/numerisch nach prompt_number
        .to_dict()
    )
    results["per_question"] = acc_by_question

    # --- Genauigkeit pro Paper (nach Accuracy sortiert, absteigend) ---
    acc_by_paper = (
        df_merged.groupby('study_number')
        .apply(lambda g: accuracy_score(g['answer'], g['model_answer']))
        .sort_values(ascending=False)  # sortiert nach Genauigkeit
        .to_dict()
    )
    results["per_paper"] = acc_by_paper

    # --- Confusion Matrix separat ---
    results["confusion_matrix"] = confusion_matrix(y_true, y_pred)

    return results
