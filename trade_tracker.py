import datetime
import os
import cProfile
import pstats
from html_analysis import html_analysis
import pandas as pd

__version__ = "0.0.0008"
print(f'trade_tracker.py {__version__}')


class TradeTracker:
    def __init__(self):
        self.trades = []
        self.current_prices = {}  # Dictionary to store the current close prices
        self.trade_counter = 0  # Counter to ensure unique trade codes
        self.summary_file = 'trade_summaries.json'
        self.summaries = self.load_summaries()  # Load summaries at initialization
        self.profile = False
        self.html_analysis_mode = False

    def load_summaries(self):
        if os.path.exists(self.summary_file) and os.path.getsize(self.summary_file) > 0:
            return pd.read_json(self.summary_file, orient='records')
        else:
            return pd.DataFrame(columns=[
                'trade_code', 'symbol', 'open_time', 'close_time', 'entry_price',
                'close_price', 'quantity', 'initial_correct', 'close_history', 'trade_type'
            ])

    def save_summaries(self):
        self.summaries.to_json(self.summary_file, orient='records')

    def generate_unique_code(self, open_time):
        self.trade_counter += 1
        return open_time.strftime("%d.%m.%Y.%H.%M.%S.%f") + f".{self.trade_counter:04d}"

    def open_trade(self, trade_details, trade_code=None, tradetype='---', silent=False):
        open_time = datetime.datetime.now()
        if not trade_code: trade_code = self.generate_unique_code(open_time)
        trade_details['trade_type'] = tradetype
        trade_details['open_time'] = open_time
        trade_details['trade_code'] = trade_code
        trade_details['status'] = 'open'
        trade_details['close_history'] = []
        self.trades.append(trade_details)
        print(f"-")
        print(f"Trade opened with code: {trade_code}")
        print(trade_details)
        print(f"-")
        return trade_code

    def update_close_value(self, trade_code, close_value):
        for trade in self.trades:
            if trade['trade_code'] == trade_code and trade['status'] == 'open':
                trade['close_history'].append({'time': datetime.datetime.now(), 'close_value': close_value})
                print(f"Trade {trade_code} updated with close value: {close_value}")
                return trade
        print(f"Trade not found or not open: {trade_code}")
        return None

    def update_current_prices(self, symbol, close_price):
        self.current_prices[symbol] = close_price
        for trade in self.trades:
            if trade['symbol'] == symbol and trade['status'] == 'open':
                self.update_close_value(trade['trade_code'], close_price)

    def close_trade(self, trade_code):
        if self.profile:
            profiler = cProfile.Profile()
            profiler.enable()

        for trade in self.trades:
            if trade['trade_code'] == trade_code and trade['status'] == 'open':
                close_time = datetime.datetime.now()
                trade['status'] = 'closed'
                trade['close_time'] = close_time
                # Call method to get the current close value
                close_value = self.get_close_value(trade['symbol'])
                trade['close_history'].append({'time': close_time, 'close_value': close_value})
                print(f"Trade closed with code: {trade_code} history len: {len(trade['close_history'])}")

                # Update summaries
                initial_correct = self.is_initial_correct(trade)
                new_summary = {
                    'trade_code': trade['trade_code'],
                    'symbol': trade['symbol'],
                    'open_time': trade['open_time'],
                    'close_time': trade['close_time'],
                    'entry_price': trade['price'],
                    'close_price': trade['close_history'][-1]['close_value'],
                    'quantity': trade['quantity'],
                    'initial_correct': initial_correct,
                    'close_history': trade['close_history'],
                    'trade_type': trade['trade_type']
                }
                self.summaries = pd.concat([self.summaries, pd.DataFrame([new_summary])], ignore_index=True)

                # Call html_analysis
                if self.html_analysis_mode:
                    html_analysis(trade)  # Call html_analysis here

                if self.profile:
                    profiler.disable()
                    profiler.dump_stats(f'profile_output_{trade_code}.prof')

                    # Analyze the profile
                    with open(f'profile_output_{trade_code}.txt', 'w') as f:
                        ps = pstats.Stats(f'profile_output_{trade_code}.prof', stream=f)
                        ps.strip_dirs().sort_stats('cumulative').print_stats(20)

                    print(f'Profiling complete for {trade_code}. Results saved to profile_output_{trade_code}.txt.')

                # Save summaries
                self.save_summaries()
                return trade
        print(f"Trade not found or already closed: {trade_code}")
        return None

    def is_initial_correct(self, trade):
        if len(trade['close_history']) > 1:  # Ensure there are at least two close values
            if trade['trade_type'] == 'buy':
                return trade['close_history'][1]['close_value'] > trade['price']
            else:  # sell trade
                return trade['close_history'][1]['close_value'] < trade['price']
        else:
            print(f"Insufficient close history for trade {trade['trade_code']} to determine initial correctness.")
            return False  # or handle it as appropriate

    def get_close_value(self, symbol):
        # Retrieve the current close value for the given symbol from the stored data
        return self.current_prices.get(symbol, 0.0)  # Default to 0.0 if the symbol is not found

    def get_open_trades(self):
        return [trade for trade in self.trades if trade['status'] == 'open']

    def get_trades(self):
        return self.trades

    def print_trades(self, status='all'):
        """
        TradeTracker print_trades
        :param status: 'open'/'close'/'all'
        :return:
        """
        print('-begin')
        print(
            f'-tracker-     ALL-EVER:{len(self.trades)}     closed: [{len([trade for trade in self.trades if trade["status"] == "closed"])}]')

        if status == 'all':
            trades_to_print = self.trades
        elif status == 'open':
            trades_to_print = self.get_open_trades()
        elif status == 'closed':
            trades_to_print = [trade for trade in self.trades if trade['status'] == 'closed']
        else:
            print("Invalid status specified.")
            return

        print(f'show {status}')
        for trade in trades_to_print:
            print(trade)
        print('-end-')


# Example usage
if __name__ == "__main__":
    tracker = TradeTracker()

    # Open a new trade
    new_trade = {
        'symbol': 'AAPL',
        'quantity': 10,
        'price': 150.0
    }
    tracker.open_trade(new_trade)

    # Open another trade
    new_trade_2 = {
        'symbol': 'GOOGL',
        'quantity': 5,
        'price': 2800.0
    }
    tracker.open_trade(new_trade_2)

    # Manually update close values for the trades
    tracker.update_close_value(new_trade['trade_code'], 152.0)
    tracker.update_close_value(new_trade_2['trade_code'], 2820.0)

    # Print all trades
    print("All trades:", tracker.get_trades())

    # Print open trades
    print("Open trades:", tracker.get_open_trades())

    # Enable profiling
    tracker.profile = True

    # Close a trade
    tracker.close_trade(new_trade['trade_code'])

    # Disable profiling
    tracker.profile = False

    # Print open trades after closing one
    print("Open trades after closing one:", tracker.get_open_trades())

    # Print all trades after closing one
    print("All trades after closing one:", tracker.get_trades())
