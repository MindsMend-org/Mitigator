# useage: python analyze_trade_history.py --file trade_history.json
import json
import pandas as pd
import matplotlib.pyplot as plt

def load_trade_history(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def analyze_trade_history(file_path):
    trade_history = load_trade_history(file_path)

    # Convert trade history to DataFrame
    df = pd.DataFrame(trade_history)

    # Ensure that the 'timestamp' column is converted to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Plotting the trade history
    plt.figure(figsize=(10, 6))

    # Plotting returns over time
    plt.subplot(2, 1, 1)
    plt.plot(df['timestamp'], df['return'], label='Return')
    plt.xlabel('Date')
    plt.ylabel('Return')
    plt.title('Return Over Time')
    plt.legend()

    # Plotting the balance over time
    plt.subplot(2, 1, 2)
    plt.plot(df['timestamp'], df['balance'], label='Balance', color='orange')
    plt.xlabel('Date')
    plt.ylabel('Balance')
    plt.title('Balance Over Time')
    plt.legend()

    plt.tight_layout()
    plt.show()

    # Print summary statistics
    print("Summary Statistics:")
    print(df.describe())

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Analyze trade history and generate visualizations.')
    parser.add_argument('--file', type=str, required=True, help='Path to the trade history JSON file.')
    args = parser.parse_args()

    analyze_trade_history(args.file)
