import csv
import argparse

def flip_answers(csv_path, output_path):
    flipped = []
    with open(csv_path, newline='', encoding='utf-8') as infile:
        reader = list(csv.reader(infile, delimiter=';'))
        
        # keep header as is
        header, *rows = reader
        flipped.append(header)
        
        for row in rows:
            if row[-1] == "1":
                row[-1] = "0"
            elif row[-1] == "0":
                row[-1] = "1"
            # leave NA or others unchanged
            flipped.append(row)
    
    with open(output_path, "w", newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerows(flipped)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Flip the values in the 'answer' column of a semicolon-delimited CSV (1↔0, NA unchanged)."
    )
    parser.add_argument("input_csv", help="Path to the input CSV file")
    parser.add_argument("output_csv", help="Path to save the modified CSV file")
    
    args = parser.parse_args()
    flip_answers(args.input_csv, args.output_csv)
