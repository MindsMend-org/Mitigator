# PRIVATE AND CONFIDENTIAL [Intellectual Property Of Brett Palmer mince@foldingcircles.co.uk]
# [No Copying Or Reading Or Use Permitted !]
"""
Copyright (c) 2023, Brett Palmer (Mince@foldingcircles.co.uk)

All rights reserved. No permission is granted for anyone, except the software owner, Brett Palmer, to use, copy, modify,
distribute, sublicense, or otherwise deal with the software in any manner.

Any unauthorized use, copying, or distribution of this software without the explicit written consent of the software
owner is strictly prohibited.

For permission requests, please contact the software owner, Brett Palmer, at Mince@foldingcircles.co.uk.
"""

# FoldingCircles Making The Unknown Known


__version__ = "0.0.0005"
print(f'trade_transactions.py {__version__}')



# trade_transactions.py

import time
from datetime import datetime, timezone, timedelta


def format_time_zone(timestamp):
    # Convert the timestamp to a datetime object in UTC
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt.strftime('%H:%M:%S')
class TradeTransaction:
    def __init__(self, trade_type, entry_price, quantity, trade_code=None):
        self.u_code = trade_code
        self.entry_price = entry_price
        self.trade_type = trade_type
        self.quantity = quantity
        self.status = 'open'
        self.open_time = time.time()
        self.close_time = None
        self.exit_price = None
        self.profit_loss = 0.00
        self.mitigated = False
        self.failed = False
        self.successful = False
        self.close_history = []  # Initialize the close_history attribute

    def __str__(self):
        duration = timedelta(seconds=(time.time() - self.open_time) if self.status == 'open' else (self.close_time - self.open_time))
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
        profit = self.profit_loss
        return (f'M-it({self.trade_type.upper()}, Entry: {self.entry_price:.3f}, Quantity: {self.quantity:.4f}, '
                f'Status: {self.status})  E Time: {format_time_zone(self.open_time)}   Profit £{profit:.2f}  Duration: {duration_str}')

    def close_trade(self, exit_price):
        if self.status == 'open':
            self.exit_price = exit_price
            self.status = 'closed'
            self.close_time = time.time()
            self.calculate_profit_loss()

    def update_value(self, current_price):
        if self.status == 'open':
            self.profit_loss = (current_price - self.entry_price) * self.quantity
            if self.trade_type == 'sell':
                self.profit_loss *= -1

            # Append the current price to close_history able to limit history length > expired trades
            self.close_history.append(current_price)

    def calculate_profit_loss(self):
        if self.status == 'closed':
            self.profit_loss = (self.exit_price - self.entry_price) * self.quantity
            if self.trade_type == 'sell':
                self.profit_loss *= -1

    def get_profit_loss(self):
        return self.profit_loss





