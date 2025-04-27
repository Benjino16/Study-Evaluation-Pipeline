import os
import platform
import argparse
import json

def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")



def main():
    parser = argparse.ArgumentParser(description='Process files with specified model (gpt or gemini).')
    parser.add_argument('--data', required=True, help='The data that should be processed.')

    args = parser.parse_args()

if __name__ == "__main__":
    main()