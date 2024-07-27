import json
import argparse
import pandas as pd
import matplotlib.pyplot as plt

__version__ = "0.0.0008"
print(f'analyze_trade_summaries.py {__version__}')

"""
Generate Charts and fast mitigation deep learn data.
cmd-line
 python analyze_trade_summaries.py --file trade_summaries.json
"""

def load_trade_summaries(file_path):
    with open(file_path, 'r') as file:
        try:
            trade_summaries = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    return trade_summaries

def analyze_trade_summaries(file_path):
    trade_summaries = load_trade_summaries(file_path)

    if not trade_summaries:
        print("No valid trade data found.")
        return

    df = pd.DataFrame(trade_summaries)
    print(f"Columns in the DataFrame: {df.columns}")

    # Ensure required columns are present
    required_columns = {'entry_price', 'trade_type', 'quantity', 'open_time', 'close_time', 'close_price', 'initial_correct'}
    if not required_columns.issubset(df.columns):
        print("Missing required data columns.")
        return

    # Calculate profit_loss
    df['profit_loss'] = (df['close_price'] - df['entry_price']) * df['quantity']
    df.loc[df['trade_type'] == 'sell', 'profit_loss'] *= -1  # Adjust for sell trades
    df['status'] = 'closed'

    # Convert time columns to datetime
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms', errors='coerce')
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', errors='coerce')

    # Sort dataframe by close_time
    df = df.sort_values(by='close_time')

    # Analysis and visualization
    profit_loss = df['profit_loss'].sum()
    total_trades = len(df)
    winning_trades = df[df['profit_loss'] > 0].shape[0]
    losing_trades = df[df['profit_loss'] <= 0].shape[0]
    win_rate = winning_trades / total_trades * 100
    initially_correct = df[df['initial_correct'] == True].shape[0]
    initially_wrong = df[df['initial_correct'] == False].shape[0]

    print(f"Total Profit/Loss: {profit_loss}")
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades}")
    print(f"Losing Trades: {losing_trades}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Initially Correct Trades: {initially_correct}")
    print(f"Initially Wrong Trades: {initially_wrong}")

    # Debug: Verify individual records for consistency
    print("Sample of winning trades:")
    print(df[df['profit_loss'] > 0].head())

    print("Sample of losing trades:")
    print(df[df['profit_loss'] <= 0].head())

    print("Sample of initially correct trades:")
    print(df[df['initial_correct'] == True].head())

    print("Sample of initially wrong trades:")
    print(df[df['initial_correct'] == False].head())

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
        'Win Rate (%)': win_rate,
        'Initially Correct': initially_correct,
        'Initially Wrong': initially_wrong
    }
    names = list(metrics.keys())
    values = list(metrics.values())

    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.bar(names[:-2], values[:-2], color=['blue', 'green', 'red'])
    ax1.set_ylabel('Count')
    ax1.set_title('Trade Performance Metrics')

    ax2 = ax1.twinx()
    ax2.plot(names[-2:], values[-2:], color='orange', marker='o', linestyle='-')
    ax2.set_ylabel('Count')

    plt.savefig('analysis/trade_performance_metrics.png')
    plt.show()

    # Initially Correct vs. Initially Wrong Trades
    plt.figure(figsize=(10, 5))
    plt.bar(['Initially Correct', 'Initially Wrong'], [initially_correct, initially_wrong], color=['green', 'red'])
    plt.xlabel('Trade Outcome')
    plt.ylabel('Count')
    plt.title('Initially Correct vs. Initially Wrong Trades')
    plt.grid(True)
    plt.savefig('analysis/initially_correct_vs_wrong.png')
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
    parser = argparse.ArgumentParser(description='Analyze trade summaries.')
    parser.add_argument('--file', type=str, required=True, help='Path to the trade summaries JSON file.')
    args = parser.parse_args()

    analyze_trade_summaries(file_path=args.file)
