# useage: python analyze_trade_history.py --file trade_history.json
import json
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def load_trade_history(file_path):
    trade_history = []
    with open(file_path, 'r') as file:
        for line in file:
            try:
                trade_history.append(json.loads(line.strip()))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
    return trade_history


def analyze_trade_history(file_path):
    trade_history = load_trade_history(file_path)

    if not trade_history:
        print("No valid trade data found.")
        return

    df = pd.DataFrame(trade_history)

    # Ensure required columns are present
    required_columns = {'entry_price', 'trade_type', 'quantity', 'status', 'open_time', 'close_time', 'exit_price',
                        'profit_loss'}
    if not required_columns.issubset(df.columns):
        print("Missing required data columns.")
        return

    # Analysis and visualization
    profit_loss = df['profit_loss'].sum()
    total_trades = len(df)
    winning_trades = df[df['profit_loss'] > 0].shape[0]
    losing_trades = df[df['profit_loss'] <= 0].shape[0]
    win_rate = winning_trades / total_trades * 100

    print(f"Total Profit/Loss: {profit_loss}")
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades}")
    print(f"Losing Trades: {losing_trades}")
    print(f"Win Rate: {win_rate:.2f}%")

    # Visualization
    plt.figure(figsize=(10, 5))
    plt.hist(df['profit_loss'], bins=50, alpha=0.75)
    plt.xlabel('Profit/Loss')
    plt.ylabel('Frequency')
    plt.title('Profit/Loss Distribution')
    plt.show()

    df['close_time'] = pd.to_datetime(df['close_time'], unit='s')
    df.set_index('close_time', inplace=True)
    df['cumulative_profit'] = df['profit_loss'].cumsum()

    plt.figure(figsize=(10, 5))
    df['cumulative_profit'].plot()
    plt.xlabel('Time')
    plt.ylabel('Cumulative Profit')
    plt.title('Cumulative Profit Over Time')
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze trade history.')
    parser.add_argument('--file', type=str, required=True, help='Path to the trade history JSON file.')
    args = parser.parse_args()

    analyze_trade_history(file_path=args.file)
