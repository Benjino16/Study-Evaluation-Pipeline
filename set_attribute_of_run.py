import argparse
import json
import glob

def process_file(file_path, attribute, value):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Add or update the ID
        data[attribute] = value

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"Processed: {file_path}")
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Adds an ID to JSON files.")
    parser.add_argument("--run", required=True, help="Glob pattern for JSON files (e.g. './data/*.json')")
    parser.add_argument("--id", type=int, required=False, help="Value for the ID (e.g. 1234)")
    parser.add_argument("--model", type=str, required=False, help="Value for the ID (e.g. 1234)")

    args = parser.parse_args()

    files = glob.glob(args.run)
    if not files:
        print("No matching files found.")
        return

    attributChanged = False
    for file_path in files:
        if args.id:
            process_file(file_path, "ID", args.id)
            attributChanged = True
        if args.model:
            process_file(file_path, "Model_Name", args.model)
            attributChanged = True
        else:
            if attributChanged is False:
                raise Exception(f"At least one attribute has to be updated!")

if __name__ == "__main__":
    main()
