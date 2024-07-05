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


__version__ = "0.0.0002"
print(f'trade_transactions.py {__version__}')



# trade_transactions.py

import time
from datetime import datetime, timezone, timedelta


def format_time_zone(timestamp):
    # Convert the timestamp to a datetime object in UTC
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt.strftime('%H:%M:%S')
class TradeTransaction:
    def __init__(self, trade_type, entry_price, quantity):
        self.entry_price = entry_price
        self.trade_type = trade_type
        self.quantity = quantity
        self.status = 'open'
        self.open_time = time.time()
        self.close_time = None
        self.exit_price = None
        self.profit_loss = 0.00

    def __str__(self):
        """Returns a string representation of the trade, useful for printing details."""
        if self.status == 'open':
            duration = timedelta(seconds=time.time() - self.open_time)
            profit = self.profit_loss
        else:
            duration = timedelta(seconds=self.close_time - self.open_time)
            profit = self.profit_loss

        # Proper formatting of the duration:
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        # If you need it as a float of hours, here's how you could calculate it:
        duration_in_hours = duration.total_seconds() / 3600
        duration_str = f'    Duration: {hours:02d}:{minutes:02d}:{seconds:02d}'

        return (f'M-it({self.trade_type.upper()}, Entry: {self.entry_price:.3f}, Quantity: {self.quantity:.4f}, '
                f'Status: {self.status})  E Time: {format_time_zone(self.open_time)}   Profit £{profit:.2f}'
                f'    Duration: {duration_str}')

    def open_trade(self, price, trade_type, quantity):
        self.entry_price = price
        self.trade_type = trade_type
        self.quantity = quantity
        self.status = 'open'
        self.open_time = time.time()

    def close_trade(self, exit_price):
        if self.status == 'open':
            self.exit_price = exit_price
            self.status = 'closed'
            self.close_time = time.time()
            self.calculate_profit_loss()

    # running value
    def update_value(self, current_price):
        if self.status == 'open':
            self.profit_loss = (current_price - self.entry_price) * self.quantity
            if self.trade_type == 'sell':
                self.profit_loss *= -1

    # final profit calc
    def calculate_profit_loss(self):
        if self.status == 'closed':
            self.profit_loss = (self.exit_price - self.entry_price) * self.quantity
            if self.trade_type == 'sell':
                self.profit_loss *= -1

    def get_profit_loss(self):
        return self.profit_loss




