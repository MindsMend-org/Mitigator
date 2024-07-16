# M@FC 2024
import pandas as pd
import plotly.express as px
from plotly.offline import plot
from datetime import datetime, timedelta
import os
import warnings

__version__ = "0.0.0005"
print(f'html_analysis.py {__version__}')

# Suppress the specific pandas FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")

def html_analysis(trade_tracker, output_file='trade_analysis_report.html'):
    # Check if the file already exists to append or create a new one
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            html_content = f.read()
        insert_index = html_content.rfind('</body>')
        html_content = html_content[:insert_index]
    else:
        html_content = '<html><head><script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head><body>'
        html_content += f'<h1>Trade Analysis Report</h1>'
        html_content += f'<p id="trade_count">Total Trades: 0</p>'
        html_content += f'<p id="correct_count">Initially Correct Trades: 0 (0%)</p>'
        insert_index = len(html_content)

    # Generate the new trade plot
    timestamps = [entry['time'] if isinstance(entry['time'], datetime) else datetime.fromtimestamp(entry['time']) for entry in trade_tracker['close_history']]
    close_values = [entry['close_value'] for entry in trade_tracker['close_history']]
    fig = px.line(x=timestamps, y=close_values, title=f"Trade {trade_tracker['trade_code']} ({trade_tracker['trade_type'].upper()})")
    fig.update_xaxes(title_text='Time')
    fig.update_yaxes(title_text='Price')
    trade_plot = plot(fig, output_type='div', include_plotlyjs='cdn')

    html_content += f'<h2>Trade {trade_tracker["trade_code"]} ({trade_tracker["trade_type"].upper()}) Analysis</h2>'
    html_content += trade_plot

    # Recalculate summary statistics
    if os.path.exists('trade_summaries.json') and os.path.getsize('trade_summaries.json') > 0:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")
            summaries = pd.read_json('trade_summaries.json', orient='records')
    else:
        summaries = pd.DataFrame(columns=[
            'trade_code', 'symbol', 'open_time', 'close_time', 'entry_price',
            'close_price', 'quantity', 'initial_correct', 'close_history', 'trade_type'
        ])

    new_summary = {
        'trade_code': trade_tracker['trade_code'],
        'symbol': trade_tracker['symbol'],
        'open_time': trade_tracker['open_time'],
        'close_time': trade_tracker['close_time'],
        'entry_price': trade_tracker['price'],
        'close_price': trade_tracker['close_history'][-1]['close_value'],
        'quantity': trade_tracker['quantity'],
        'initial_correct': trade_tracker['close_history'][1]['close_value'] > trade_tracker['price'],
        'close_history': trade_tracker['close_history'],
        'trade_type': trade_tracker['trade_type']
    }

    # Concatenate without warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")
        summaries = pd.concat([summaries, pd.DataFrame([new_summary])], ignore_index=True)

    summaries.to_json('trade_summaries.json', orient='records')

    total_trades = len(summaries)
    initial_correct_count = summaries['initial_correct'].sum()
    initial_correct_percentage = (initial_correct_count / total_trades) * 100

    # Replace summary statistics in the HTML content
    html_content = html_content.replace(
        '<p id="trade_count">Total Trades: 0</p>',
        f'<p id="trade_count">Total Trades: {total_trades}</p>'
    )
    html_content = html_content.replace(
        '<p id="correct_count">Initially Correct Trades: 0 (0%)</p>',
        f'<p id="correct_count">Initially Correct Trades: {initial_correct_count} ({initial_correct_percentage:.2f}%)</p>'
    )

    # Gather sentiment data and calculate profit/loss over time
    all_sentiments = []
    for index, row in summaries.iterrows():
        initial_price = row['entry_price']
        quantity = row['quantity']
        trade_type_multiplier = 1 if row['trade_type'] == 'buy' else -1
        for entry in row['close_history']:
            close_value = entry['close_value']
            profit_loss = (close_value - initial_price) * quantity * trade_type_multiplier
            all_sentiments.append({'time': entry['time'], 'profit_loss': profit_loss})

    sentiment_df = pd.DataFrame(all_sentiments, columns=['time', 'profit_loss'])
    # Ensure the 'time' column is in datetime format
    sentiment_df['time'] = pd.to_datetime(sentiment_df['time'], errors='coerce')
    avg_sentiment = sentiment_df.groupby('time')['profit_loss'].mean().reset_index()

    # Generate sentiment plot
    sentiment_fig = px.line(avg_sentiment, x='time', y='profit_loss', title='Average Sentiment Change Over Time')
    sentiment_plot = plot(sentiment_fig, output_type='div', include_plotlyjs='cdn')

    html_content += f'<h2>Average Sentiment Change Over Time</h2>'
    html_content += sentiment_plot
    html_content += '</body></html>'

    # Write to the HTML file
    with open(output_file, 'w') as f:
        f.write(html_content)

# Testing block
if __name__ == "__main__":
    from trade_tracker import TradeTracker
    import random

    # Initialize your trade tracker
    tracker = TradeTracker()

    # Open new trades
    trade1 = {
        'symbol': 'AAPL',
        'quantity': 10,
        'price': 150.0
    }
    trade_code1 = tracker.open_trade(trade1)

    trade2 = {
        'symbol': 'GOOGL',
        'quantity': 5,
        'price': 2800.0
    }
    trade_code2 = tracker.open_trade(trade2)

    # Manually update close values for the trades
    tracker.update_close_value(trade_code1, 152.0)
    tracker.update_close_value(trade_code2, 2820.0)

    # Close trades and call the html_analysis function
    closed_trade1 = tracker.close_trade(trade_code1)
    html_analysis(closed_trade1)

    closed_trade2 = tracker.close_trade(trade_code2)
    html_analysis(closed_trade2)
