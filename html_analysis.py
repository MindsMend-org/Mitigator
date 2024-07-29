import pandas as pd
import plotly.express as px
from plotly.offline import plot
from datetime import datetime, timedelta
import os
import warnings

__version__ = "0.0.0009"
print(f'html_analysis.py {__version__}')

# Suppress the specific pandas FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")

def html_analysis(trade_tracker, output_dir='html_trade_analysis_reports', page_limit=400):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    main_report_path = 'trade_analysis_report.html'

    # Initialize or read the existing main report content
    if os.path.exists(main_report_path):
        with open(main_report_path, 'r') as f:
            main_html_content = f.read()
        insert_index = main_html_content.rfind('</body>')
        main_html_content = main_html_content[:insert_index]
    else:
        main_html_content = '<html><head><title>Trade Analysis Report</title></head><body>'
        main_html_content += '<h1>Trade Analysis Report</h1>'
        main_html_content += '<p id="trade_count">Total Trades: 0</p>'
        main_html_content += '<p id="correct_count">Initially Correct Trades: 0 (0%)</p>'
        main_html_content += '<h2>Pages</h2>'
        main_html_content += '<ul>'
        insert_index = len(main_html_content)

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

    # Remove the last trade if it is incomplete
    if not summaries.empty:
        last_trade = summaries.iloc[-1]
        if len(last_trade['close_history']) < 2:
            summaries = summaries[:-1]

    # Check if close_history has enough data points
    if len(trade_tracker['close_history']) < 2:
        print(f"Trade {trade_tracker['trade_code']} is incomplete and will not be processed.")
        return

    # Determine if the trade was initially correct
    if trade_tracker['trade_type'] == 'buy':
        initial_correct = trade_tracker['close_history'][1]['close_value'] > trade_tracker['entry_price']
    else:  # sell trade
        initial_correct = trade_tracker['close_history'][1]['close_value'] < trade_tracker['entry_price']

    # Generate the new trade plot
    #timestamps = [entry['time'] if isinstance(entry['time'], datetime) else datetime.fromtimestamp(entry['time']) for entry in trade_tracker['close_history']]
    timestamps = [
        entry['time'] if isinstance(entry['time'], datetime)
        else datetime.fromtimestamp(entry['time'] / 1000)  # Divide by 1000 to convert from ms to s
        for entry in trade_tracker['close_history']
    ]



    close_values = [entry['close_value'] for entry in trade_tracker['close_history']]

    # Include the entry price as the first point in the graph
    timestamps.insert(0, datetime.fromtimestamp(trade_tracker["close_history"][0]["time"] / 1000 - 1))  # Adding a point just before the first close history for visualization
    close_values.insert(0, trade_tracker["entry_price"])


    fig = px.line(x=timestamps, y=close_values, title=f"Trade {trade_tracker['trade_code']} ({trade_tracker['trade_type'].upper()})", markers=True)
    fig.update_xaxes(title_text='Time')
    fig.update_yaxes(title_text='Price')
    # Add markers to the plot
    fig.add_scatter(x=timestamps, y=close_values, mode='markers', marker=dict(color='black', size=5), name='Close Positions')
    trade_plot = plot(fig, output_type='div', include_plotlyjs='cdn')

    # Add the new trade plot to the main report
    main_html_content += f'<h2>Trade {trade_tracker["trade_code"]} ({trade_tracker["trade_type"].upper()}) Analysis</h2>'
    main_html_content += trade_plot

    new_summary = {
        'trade_code': trade_tracker['trade_code'],
        'symbol': trade_tracker['symbol'],
        'open_time': trade_tracker['open_time'],
        'close_time': trade_tracker['close_time'],
        'entry_price': trade_tracker['entry_price'],
        'close_price': trade_tracker['close_history'][-1]['close_value'],
        'quantity': trade_tracker['quantity'],
        'initial_correct': initial_correct,
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

    # Paginate the summaries
    num_pages = (total_trades // page_limit) + 1

    for page_num in range(1, num_pages + 1):
        start_idx = (page_num - 1) * page_limit
        end_idx = min(page_num * page_limit, total_trades)

        page_summaries = summaries.iloc[start_idx:end_idx]

        page_html_content = '<html><head><script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head><body>'
        page_html_content += f'<h1>Trade Analysis Report - Page {page_num}</h1>'
        page_html_content += f'<p id="trade_count">Total Trades: {total_trades}</p>'
        page_html_content += f'<p id="correct_count">Initially Correct Trades: {initial_correct_count} ({initial_correct_percentage:.2f}%)</p>'

        # Gather sentiment data and calculate profit/loss over time
        all_sentiments = []
        for index, row in page_summaries.iterrows():
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

        page_html_content += f'<h2>Average Sentiment Change Over Time</h2>'
        page_html_content += sentiment_plot
        page_html_content += '</body></html>'

        # Save the HTML file for the current page
        page_file_path = os.path.join(output_dir, f'trade_analysis_report_page_{page_num}.html')
        with open(page_file_path, 'w') as f:
            f.write(page_html_content)

        # Add a link to the current page in the main report
        main_html_content += f'<li><a href="{os.path.join(output_dir, f"trade_analysis_report_page_{page_num}.html")}">Page {page_num}</a></li>'

    main_html_content += '</ul></body></html>'

    # Write the main report HTML file
    with open(main_report_path, 'w') as f:
        f.write(main_html_content)

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
    # Manually update close values for the trades
    tracker.update_close_value(trade_code1, 153.0)
    tracker.update_close_value(trade_code2, 2824.0)
    # Manually update close values for the trades
    tracker.update_close_value(trade_code1, 154.0)
    tracker.update_close_value(trade_code2, 2810.0)

    # Close trades and call the html_analysis function
    closed_trade1 = tracker.close_trade(trade_code1)
    html_analysis(closed_trade1, page_limit=400)

    closed_trade2 = tracker.close_trade(trade_code2)
    html_analysis(closed_trade2, page_limit=400)
