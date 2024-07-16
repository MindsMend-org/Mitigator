import datetime
from html_analysis import html_analysis

__version__ = "0.0.0005"
print(f'trade_tracker.py {__version__}')

class TradeTracker:
    def __init__(self):
        self.trades = []
        self.current_prices = {}  # Dictionary to store the current close prices

    def generate_unique_code(self, open_time):
        return open_time.strftime("%d.%m.%Y.%H.%M.%S") + f".{open_time.microsecond // 1000:03d}"

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
        for trade in self.trades:
            if trade['trade_code'] == trade_code and trade['status'] == 'open':
                close_time = datetime.datetime.now()
                trade['status'] = 'closed'  # Fix status typo from 'close' to 'closed'
                trade['close_time'] = close_time
                # Call method to get the current close value
                close_value = self.get_close_value(trade['symbol'])
                trade['close_history'].append({'time': close_time, 'close_value': close_value})
                print(f"Trade closed with code: {trade_code} history len: {len(trade['close_history'])}")
                html_analysis(trade)  # Call html_analysis here
                return trade
        print(f"Trade not found or already closed: {trade_code}")
        return None

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
        print(f'-tracker-     ALL-EVER:{len(self.trades)}     closed: [{len([trade for trade in self.trades if trade["status"] == "closed"])}]')

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

    # Close a trade
    tracker.close_trade(new_trade['trade_code'])

    # Print open trades after closing one
    print("Open trades after closing one:", tracker.get_open_trades())

    # Print all trades after closing one
    print("All trades after closing one:", tracker.get_trades())
