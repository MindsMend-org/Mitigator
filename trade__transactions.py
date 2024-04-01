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


__version__ = "0.0.0001"
print(f'trade_transactions.py {__version__}')



# trade_transactions.py
import time

class TradeTransaction:
    def __init__(self, trade_type, entry_price, quantity):
        self.entry_price = entry_price
        self.trade_type = trade_type
        self.quantity = quantity
        self.status = 'open'
        self.open_time = time.time()
        self.exit_price = None
        self.profit_loss = 0

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
            self.calculate_profit_loss()

    def update_value(self, current_price):
        if self.status == 'open':
            self.profit_loss = (current_price - self.entry_price) * self.quantity
            if self.trade_type == 'sell':
                self.profit_loss *= -1

    def calculate_profit_loss(self):
        if self.status == 'closed':
            self.profit_loss = (self.exit_price - self.entry_price) * self.quantity
            if self.trade_type == 'sell':
                self.profit_loss *= -1

    def get_profit_loss(self):
        return self.profit_loss
