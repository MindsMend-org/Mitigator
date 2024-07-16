import json
import argparse

__version__ = "0.0.001"
print(f'inspect_trade_history.py {__version__}')

def load_trade_history(file_path):
    with open(file_path, 'r') as file:
        try:
            trade_history = json.load(file)
            return trade_history
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None


def inspect_trade_history(file_path):
    trade_history = load_trade_history(file_path)
    if trade_history is None:
        print("Failed to load trade history.")
        return

    print(f"Trade history type: {type(trade_history)}")
    if isinstance(trade_history, list) and len(trade_history) > 0:
        print(f"Sample entry: {trade_history[0]}")
    else:
        print("Trade history is empty or not a list.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Inspect trade history JSON structure.')
    parser.add_argument('--file', type=str, required=True, help='Path to the trade history JSON file.')
    args = parser.parse_args()

    inspect_trade_history(args.file)
