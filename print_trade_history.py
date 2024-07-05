import json
import argparse

def load_and_print_trade_history(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        print(content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load and print trade history JSON content.')
    parser.add_argument('--file', type=str, required=True, help='Path to the trade history JSON file.')
    args = parser.parse_args()

    load_and_print_trade_history(args.file)
