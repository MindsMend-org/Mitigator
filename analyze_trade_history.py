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
    print(f"Columns in the DataFrame: {df.columns}")

    # Ensure required columns are present
    required_columns = {'entry_price', 'trade_type', 'quantity', 'status', 'open_time', 'close_time', 'exit_price', 'profit_loss'}
    if not required_columns.issubset(df.columns):
        print("Missing required data columns.")
        return

    # Check for any null values in the close_time and open_time columns
    if df['close_time'].isnull().any() or df['open_time'].isnull().any():
        print("Null values detected in 'close_time' or 'open_time'.")
        df = df.dropna(subset=['close_time', 'open_time'])

    # Convert time columns to datetime
    df['close_time'] = pd.to_datetime(df['close_time'], unit='s', errors='coerce')
    df['open_time'] = pd.to_datetime(df['open_time'], unit='s', errors='coerce')

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

    # Visualization of Profit/Loss Distribution
    plt.figure(figsize=(10, 5))
    plt.hist(df['profit_loss'], bins=50, alpha=0.75, color='blue')
    plt.xlabel('Profit/Loss')
    plt.ylabel('Frequency')
    plt.title('Profit/Loss Distribution')
    plt.grid(True)
    plt.savefig('analysis/profit_loss_distribution.png')
    plt.show()

    # Cumulative Profit Over Time
    df.set_index('close_time', inplace=True)
    df['cumulative_profit'] = df['profit_loss'].cumsum()

    plt.figure(figsize=(10, 5))
    df['cumulative_profit'].plot(color='green')
    plt.xlabel('Time')
    plt.ylabel('Cumulative Profit')
    plt.title('Cumulative Profit Over Time')
    plt.grid(True)
    plt.savefig('analysis/cumulative_profit_over_time.png')
    plt.show()

    # Bar chart of trade performance metrics
    metrics = {
        'Total Trades': total_trades,
        'Winning Trades': winning_trades,
        'Losing Trades': losing_trades,
        'Win Rate (%)': win_rate
    }
    names = list(metrics.keys())
    values = list(metrics.values())

    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.bar(names[:-1], values[:-1], color=['blue', 'green', 'red'])
    ax1.set_ylabel('Count')
    ax1.set_title('Trade Performance Metrics')

    ax2 = ax1.twinx()
    ax2.plot(names[-1:], values[-1:], color='orange', marker='o', linestyle='-')
    ax2.set_ylabel('Win Rate (%)')

    plt.savefig('analysis/trade_performance_metrics.png')
    plt.show()

    # Trade Duration Analysis
    df['trade_duration'] = (df.index - df['open_time']).dt.total_seconds() / 3600  # Convert duration to hours

    plt.figure(figsize=(10, 5))
    plt.hist(df['trade_duration'], bins=50, alpha=0.75)
    plt.xlabel('Duration (hours)')
    plt.ylabel('Count')
    plt.title('Trade Duration Distribution')
    plt.savefig('analysis/trade_duration_distribution.png')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze trade history.')
    parser.add_argument('--file', type=str, required=True, help='Path to the trade history JSON file.')
    args = parser.parse_args()

    analyze_trade_history(file_path=args.file)
