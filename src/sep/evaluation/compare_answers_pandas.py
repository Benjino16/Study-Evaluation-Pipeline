import pandas as pd
from sep.evaluation.parse_csv_answers import clean_study_number
from sep.evaluation.parse_csv_answers import parse_json_answer
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, matthews_corrcoef
import sep.logger

log = sep.logger.setup_logger(__name__)

def load_correct_answers(csv_file):
    """Load correct answers from the CSV file into a pandas DataFrame."""
    df = pd.read_csv(csv_file, delimiter=';', dtype={'answer': str})

    # clean study_number
    df['study_number'] = df['study_number'].apply(clean_study_number)

    #remove rows with NA
    df = df.dropna(subset=['answer'])

    print(df)
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

    #remove rows with NA
    df = df.dropna(subset=['model_answer'])
    print(df)
    return df


def merge_dataframes(correct, prediction):
    """Merge two pandas DataFrames on the 'study_number' and 'prompt_number' columns."""
    # merge dataframes
    df_merged = pd.merge(
        correct,
        prediction,
        on=['study_number', 'prompt_number'],
        how='left',
        suffixes=('_correct', '_pred')
    )


    df_merged = df_merged.dropna(subset=['answer', 'model_answer'])

    log.warning(f"Merged dataframe dropped {len(df_merged)} NAs.")

    return df_merged


def compare_data(data, csv: str, ignore_na: bool = False):
    """
    Vergleicht die Daten aus einem Run mit den Antworten aus einer CSV-Datei.
    Gibt Gesamtmetriken und Genauigkeiten pro Frage & pro Paper zurück.
    """
    prediction_df = convert_model_prediction_df(data)
    correct_answers_df = load_correct_answers(csv)

    df_merged = merge_dataframes(correct_answers_df, prediction_df)

    y_true = df_merged['answer']
    y_pred = df_merged['model_answer']
    y_true = y_true.astype(int)
    y_pred = y_pred.astype(int)

    # --- general metrics ---
    results = {
        "overall": {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1": f1_score(y_true, y_pred, zero_division=0),
            "n_samples": len(df_merged),
        },
    }

    # --- accuracy per question ---
    acc_by_question = (
        df_merged.groupby('prompt_number')
        .apply(lambda g: accuracy_score(g['answer'], g['model_answer']))
        .to_dict()
    )
    results["per_question"] = acc_by_question

    # --- accuracy per paper ---
    acc_by_paper = (
        df_merged.groupby('study_number')
        .apply(lambda g: accuracy_score(g['answer'], g['model_answer']))
        .to_dict()
    )
    results["per_paper"] = acc_by_paper

    results["confusion_matrix"] = confusion_matrix(y_true, y_pred)

    return results
