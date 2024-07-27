import json
import argparse
import pandas as pd

__version__ = "0.0.0006"
print(f'compare_summaries_history.py {__version__}')


# python compare_summaries_history.py --summary_file trade_summaries.json --history_file trade_history.json
# python compare_summaries_history.py --summary_file trade_summaries.json --history_file trade_history.json --balance

def load_json_lines(file_path):
    data = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    data.append(json.loads(line.strip()))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from {file_path}: {e}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return data


def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return None


def add_missing_trades(missing_file, history_file):
    with open(missing_file, 'r') as file:
        missing_trades = json.load(file)

    with open(history_file, 'a') as file:
        for trade in missing_trades:
            file.write(json.dumps(trade) + '\n')


def compare_summaries_history(summary_file, history_file, balance=False):
    trade_summaries = load_json(summary_file)
    trade_history = load_json_lines(history_file)

    if not trade_summaries or not trade_history:
        print("Invalid data in one or both files.")
        return

    # If trade_summaries is a list of single-element dictionaries, we need to extract the values
    if isinstance(trade_summaries, list) and isinstance(trade_summaries[0], dict) and len(trade_summaries[0]) == 1:
        trade_summaries = [list(item.values())[0] for item in trade_summaries]

    df_summaries = pd.DataFrame(trade_summaries)
    df_history = pd.DataFrame(trade_history)

    print(f"Columns in Summaries DataFrame: {df_summaries.columns}")
    print(f"Columns in History DataFrame: {df_history.columns}")

    # Rename 'u_code' to 'trade_code' in history DataFrame for consistent comparison
    df_history.rename(columns={'u_code': 'trade_code'}, inplace=True)

    # Ensure 'trade_code' exists in both DataFrames
    if 'trade_code' not in df_summaries.columns:
        print("Error: 'trade_code' not found in trade_summaries DataFrame")
        print(f"Sample rows from trade_summaries DataFrame: {df_summaries.head()}")
        return

    if 'trade_code' not in df_history.columns:
        print("Error: 'trade_code' not found in trade_history DataFrame")
        print(f"Sample rows from trade_history DataFrame: {df_history.head()}")
        return

    # Ensure both DataFrames have the same columns for comparison
    common_columns = list(set(df_summaries.columns).intersection(set(df_history.columns)))
    df_summaries = df_summaries[common_columns].sort_values(by='trade_code').reset_index(drop=True)
    df_history = df_history[common_columns].sort_values(by='trade_code').reset_index(drop=True)

    # Compare DataFrames
    comparison_df = df_summaries.merge(df_history, on='trade_code', suffixes=('_summary', '_history'), how='outer',
                                       indicator=True)

    # Print mismatched records
    mismatched_records = comparison_df[comparison_df['_merge'] != 'both']
    if not mismatched_records.empty:
        print("Mismatched records between summaries and history:")
        print(mismatched_records)

        # Detailed mismatched records information
        print("Detailed mismatched records:")
        for index, row in mismatched_records.iterrows():
            print(f"Trade Code: {row['trade_code']}")
            for col in common_columns:
                val_summary = row.get(f"{col}_summary", "N/A")
                val_history = row.get(f"{col}_history", "N/A")
                if val_summary != val_history:
                    print(f"  {col}: Summary -> {val_summary}, History -> {val_history}")

        # Log missing trades
        missing_trades = mismatched_records[mismatched_records['_merge'] == 'left_only']
        if not missing_trades.empty:
            missing_trades_dicts = missing_trades.drop(columns=['_merge']).to_dict(orient='records')
            with open('missing_trades.json', 'w') as file:
                json.dump(missing_trades_dicts, file, indent=4)
            print(f"Missing trades have been logged to 'missing_trades.json'.")
            if balance:
                add_missing_trades('missing_trades.json', history_file=history_file)


    else:
        print("No mismatched records found between summaries and history.")

    # Print records present in both
    matched_records = comparison_df[comparison_df['_merge'] == 'both']
    if not matched_records.empty:
        print("Records present in both summaries and history:")
        print(matched_records)
    else:
        print("No matching records found between summaries and history.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare trade summaries with trade history.')
    parser.add_argument('--summary_file', type=str, required=True, help='Path to the trade summaries JSON file.')
    parser.add_argument('--history_file', type=str, required=True, help='Path to the trade history JSON file.')
    parser.add_argument('--balance', action='store_true', help='Add missing trades to history if this flag is set.')
    args = parser.parse_args()

    compare_summaries_history(summary_file=args.summary_file, history_file=args.history_file, balance=args.balance)
