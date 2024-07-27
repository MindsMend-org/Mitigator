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
print(f'game.py {__version__}')

# game.py
import datetime
import time
from strategy import analyze_data, D_calculate_bollinger_bands, calculate_bollinger_crossovers, get_trade_signal
from time_step import TIME_STEP  # Import here to avoid circular dependencies
from forex_data_loader import DataLoader
from forex_playback_sim import PlaybackSimulator
from forex_data_loader import pull_forex_data
from trade__transactions import TradeTransaction
from fc_color import reset_color, rgb_color
import random
import json
from trade_tracker import TradeTracker
tracker = TradeTracker()  # used to track all trades

UPDATE_FOREX = False
if UPDATE_FOREX: pull_forex_data()

# GLOBAL
BABY = False
GAME_SCORE = 0
GAME_TARGET_SCORE = 0.9


def get_score():
    global GAME_SCORE
    return GAME_SCORE


def set_score(set):
    global GAME_SCORE
    GAME_SCORE = set


def get_target_score():
    global GAME_TARGET_SCORE
    return GAME_TARGET_SCORE


def set_target_score(set):
    global GAME_TARGET_SCORE
    GAME_TARGET_SCORE = set


def distance_to_target(score):
    global GAME_TARGET_SCORE
    return GAME_TARGET_SCORE - score


# self.action_mappings = {0: 'action1', 1: 'action2'}
class Game:
    def __init__(self, currency_pairs):
        self.currency_pairs = currency_pairs
        self.simulators = {}
        self.transactions = {pair: [] for pair in currency_pairs}
        self.last_close_prices = {pair: None for pair in self.currency_pairs}
        self.state_size = 60
        self.action_size = 11
        self.state = [0] * self.state_size
        self.score = 0
        self.target_score = GAME_TARGET_SCORE
        self.action_history = []
        self.state_history = []
        self.action_frequencies = [0] * self.action_size
        self.last_repeated = [False] * self.action_size
        self.current_forex_data = None
        self.step = 0
        self.start_bank = 3000.0
        self.bank = self.start_bank
        self.invested = 0.0
        self.wager = 5.25
        self.cap = self.bank + self.invested
        self.open_trades = 0
        self.reset = reset_color()
        self.red = rgb_color(220, 40, 60)
        self.green = rgb_color(0, 255, 0)
        self.sim_wait = True
        self.sim_wait_time = 0.1
        self.game_type = "M-Trader"
        self.game_mode = ""
        self.game_temporal_step_ratio = (10 * 7) * 1
        self.game_flag = False
        self.game_since = -1
        self.game_next = self.game_temporal_step_ratio
        self.game_show_details = False
        self.game_live_mode = False
        self.game_close_after = 8  # days/mins/hours
        self.game_archive_time = 1
        self.game_step = self.step
        self.game_temporal_step = -1
        self.game_time_start = None
        self.game_time_to = 0.0
        self.game_time_total = 0.0
        self.game_realtime_per_step = 0.0
        self.game_time_total_reset_at = 99999999.999

        for pair, file in currency_pairs.items():
            data_loader = DataLoader(file)
            historical_data = data_loader.load_data()
            self.simulators[pair] = PlaybackSimulator(historical_data)
            self.transactions[pair] = []


    def generate_unique_code(self, open_time):
        return open_time.strftime("%d.%m.%Y.%H.%M.%S") + f".{open_time.microsecond // 1000:03d}"

    def open_trade(self, pair, trade_type, quantity, trade_code=None):
        current_price = self.simulators[pair].data[self.simulators[pair].index]['close']
        new_transaction = TradeTransaction(trade_type, current_price, quantity, trade_code)
        self.transactions[pair].append(new_transaction)
        cost = current_price * quantity
        if trade_type == 'buy':
            self.bank -= cost
        self.cap = self.bank + self.invested
        print(f'- £ {cost:.2f}  bank:[£{self.bank:.2f}]    cap £{self.cap:.2f}  ucode:{trade_code}')

    def close_trade(self, pair, transaction_index):
        if pair in self.transactions and 0 <= transaction_index < len(self.transactions[pair]):
            transaction = self.transactions[pair][transaction_index]
            if transaction.status == 'open':
                current_price = self.simulators[pair].data[self.simulators[pair].index]['close']
                transaction.close_trade(current_price)
                total_position_value = transaction.entry_price * transaction.quantity
                profit_loss = transaction.get_profit_loss()
                if transaction.trade_type == 'buy':
                    self.bank += total_position_value + profit_loss
                elif transaction.trade_type == 'sell':
                    self.bank += profit_loss
                self.cap = self.bank + self.invested
                print(f'Closed Trade:ucode:{transaction.u_code} {transaction.trade_type.upper()} - Profit/Loss: £{profit_loss:.2f},'
                      f'New Bank Balance: £{self.bank:.2f}')

    def close_all_open_trades(self, pair, keep_trade_type, tracker=None):
        if pair in self.transactions:
            for transaction in self.transactions[pair]:
                if transaction.status == 'open' and transaction.trade_type != keep_trade_type:
                    u_code = transaction.u_code
                    if tracker:
                        tracker.close_trade(u_code)
                    self.close_trade(pair, self.transactions[pair].index(transaction))

    def forex_step(self, sim_wait=None, wait_time=None, debug=True, show_trades=False):
        if wait_time is None:
            wait_time = self.sim_wait_time
        if sim_wait is None:
            sim_wait = self.sim_wait

        if sim_wait:
            time.sleep(wait_time)

        STEPPED = False
        pairs_count = len(self.simulators)
        counter = 0

        self.invested = 0.0
        self.open_trades = 0

        for pair, simulator in self.simulators.items():
            if not STEPPED:
                if self.game_time_start is not None:
                    step_end_time = time.time()
                    step_duration = step_end_time - self.game_time_start
                    self.game_time_total += step_duration
                    self.game_realtime_per_step = self.game_time_total / self.step if self.step > 0 else 0
                else:
                    self.game_time_start = time.time()
                self.step += 1
                STEPPED = True

                if tracker:
                    tracked_list = tracker.get_open_trades()
                    tracked_total = len(tracker.get_trades())
                    print(f'Total Tracked:{tracked_total}')
                    if debug & show_trades:
                        for trade in tracked_list:
                            print(trade)

            print(f"Step {self.step} for {pair}  ", end=' ')
            current_wait = sim_wait if counter == pairs_count else False
            current_forex_data = simulator.get_sim_index(simulator.index, wait=current_wait, wait_time=wait_time)

            last_close = self.last_close_prices[pair]
            current_close = current_forex_data['close']
            if last_close is None:
                last_close = current_close
            change = current_close - last_close if last_close is not None else 0.0
            color = self.green if current_close > last_close else self.red
            print(f"{color}Time: {current_forex_data['timestamp']}, Close: {current_close}  {change:.6f}{self.reset}")

            # Update the current price in the TradeTracker this does not append open trades for mit data that must be called seperate
            if tracker:
                tracker.update_current_prices(pair, current_close)

            signal = get_trade_signal(simulator.data, self.step, debug=False, debug_graph=False)
            self.wager = self.bank / 20
            current_price = current_close
            quantity = self.wager / current_price

            if signal == "buy":
                self.close_all_open_trades(pair, "buy", tracker=tracker)
            elif signal == "sell":
                self.close_all_open_trades(pair, "sell", tracker=tracker)

            if signal == "buy":
                u_code = self.generate_unique_code(datetime.datetime.now())
                self.open_trade(pair, "buy", quantity, u_code)
                if tracker:
                    new_trade = {'type': 'buy', 'symbol': pair, 'quantity': quantity, 'price': self.wager}
                    tracker.open_trade(new_trade, u_code, tradetype='buy')
            elif signal == "sell":
                u_code = self.generate_unique_code(datetime.datetime.now())
                self.open_trade(pair, "sell", quantity, u_code)
                if tracker:
                    new_trade = {'type': 'sell', 'symbol': pair, 'quantity': quantity, 'price': self.wager}
                    tracker.open_trade(new_trade, u_code, tradetype='sell')

            self.game_logic()
            self.last_close_prices[pair] = current_close
            self.update_transactions(pair, current_forex_data)
            self.capital()

        if self.step % 10 == 0:
            print(f'Average time per step: {self.game_realtime_per_step:.6f} seconds')

    def update_transactions(self, pair, market_data):
        _open_trade_count = 0
        investments_value = 0.0
        for transaction in self.transactions[pair]:
            if transaction.status == 'open':
                _open_trade_count += 1
                transaction.update_value(market_data['close'])
                investments_value += transaction.get_profit_loss()
        self.invested += investments_value
        self.open_trades += _open_trade_count

    def capital(self):
        self.cap = self.bank + self.invested
        return self.cap

    def game_logic(self, show_details=False):
        if self.internal_flag():
            # flagged to take action
            if self.game_mode == "AUTO_OPEN_SHORT":
                print(f'self.game_mode = {self.game_mode} [Flagged:]')

                keys = list(self.currency_pairs.keys())
                random_key = random.choice(keys)

                pair = random_key
                if pair in self.simulators:
                    current_price = self.simulators[pair].data[self.simulators[pair].index]['close']
                else:
                    current_price = self.last_close_prices[pair]

                u_code = self.generate_unique_code(datetime.datetime.now())
                trade_type = "sell"
                self.wager = self.bank / 50
                quantity = self.wager / current_price
                self.open_trade(pair, trade_type, quantity, u_code)

                if tracker:
                    new_trade = {
                        'type': trade_type,
                        'symbol': pair,
                        'quantity': quantity,
                        'price': self.wager
                    }
                    # forex step/game logic > served from config file TODO config to var set
                    # sentimant:['sell'/'buy'] /random:['r_sell']
                    tracker.open_trade(new_trade, u_code, tradetype=trade_type)  # TODO ADD [info] types/usage info for people

                print('-')
                print(f'>TRADE: Pair:{pair}    Type:{trade_type}    Cost:£{quantity * current_price:.3f}    qty:{quantity:.3f}  UCODE:{u_code}')
                print('-')

            self.archive_old_trades()

            if self.open_trades > 0:
                longest_trade = self.Longest_Trade()
                if longest_trade:
                    print(f"Longest Open Trade: {longest_trade}")
                    self.close_expired_trades()

        if show_details or self.game_show_details:
            self.show_internals()
        self.internal_end()

    def show_internals(self):
        print(f'-')
        print(f'FoldingCircles Mitigator AI Project 2024')
        print(f'')
        print(f'Internal:')
        print(f'')
        print(f'self.game_type = {self.game_type}')
        print(f'self.game_mode = {self.game_mode}')
        print(f'self.game_temporal_step_ratio = {self.game_temporal_step_ratio}')
        print(f'self.game_since = {self.game_since}')
        print(f'self.game_next = {self.game_next}')
        print(f'self.game_flag = {self.game_flag}')
        print(f'self.game_step = {self.game_step}')
        print(f'self.game_temporal_step = {self.game_temporal_step}')
        print(f'self.game_show_details = {self.game_show_details}')
        print(f'self.game_close_after = {self.game_close_after}')
        print(f'self.game_archive_time = {self.game_archive_time}')
        print(f'self.game_live_mode = {self.game_live_mode}')
        print(f'-')

    def internal_flag(self):
        self.game_step = self.step
        self.game_since += 1
        self.game_next = self.game_temporal_step_ratio - self.game_since
        if self.game_since >= self.game_temporal_step_ratio + 1:
            self.game_since = -1
            self.game_flag = True
            self.game_temporal_step += 1
        return self.game_flag

    def internal_end(self):
        self.game_flag = False

    def Longest_Trade(self):
        open_trades = [trade for pair_trades in self.transactions.values() for trade in pair_trades if trade.status == 'open']
        open_trades.sort(key=lambda x: x.open_time)
        if open_trades:
            return open_trades[0]
        return None

    # currently closed using time may switch to data length days/hours/mins depending on M=?
    def close_expired_trades(self, _time_limit=None, sub_time_frame=None, debug=True):
        if debug:
            print(f'game.py:close_expired_trades:_time_limit[{_time_limit}]')
        if _time_limit is not None:
            time_limit = _time_limit
        else:
            if sub_time_frame is None:
                sub_time_frame = self.game_realtime_per_step
                if debug:
                    print(f'sub_time_frame[{sub_time_frame}]')
            if debug:
                print(f'self.game_realtime_per_step[{self.game_realtime_per_step}]')
            time_limit = (self.game_close_after * sub_time_frame) / self.game_realtime_per_step if self.game_realtime_per_step > 0 else self.game_close_after * sub_time_frame

        if debug:
            print(f'----')
            print('Duration Limit Check All Trades:')
        current_time = time.time()
        for pair, trades in self.transactions.items():
            for trade_index, trade in enumerate(trades.copy()):
                if trade.status == 'open':
                    trade_duration = current_time - trade.open_time
                    if trade_duration > time_limit:
                        if debug:
                            formatted_duration = self.format_duration(trade_duration)
                            print(f"Closing trade {trade.u_code} which has been open for {formatted_duration}  ot:{trade.open_time}  ct:{current_time}")
                        ## tracker remove may have missed this?
                        #if tracker:
                        #    u_code = trade.u_code
                        #    tracker.close_trade(u_code)
                        self.close_trade(pair, trade_index)
        if debug:
            print('Limit Check END:')
            print(f'----')


    def format_duration(self, seconds):
        days, remainder = divmod(seconds, 86400)  # 86400 seconds in a day
        hours, remainder = divmod(remainder, 3600)
        minutes, remainder = divmod(remainder, 60)
        seconds, ms = divmod(remainder, 1)
        ms, ns = divmod(ms * 1e3, 1)
        ns *= 1e3
        return f'{int(days)}d:{int(hours):02d}h:{int(minutes):02d}m:{int(seconds):02d}s:{int(ms):03d}ms:{int(ns):03d}ns'

    def archive_old_trades(self, _archive_after=None):
        if _archive_after is not None:
            archive_after = _archive_after
        else:
            archive_after = self.game_archive_time

        current_time = time.time()
        trades_to_archive = []

        for pair, trades in list(self.transactions.items()):
            for trade in trades[:]:
                if trade.status == 'closed' and (current_time - trade.close_time) >= archive_after:
                    trades_to_archive.append(trade)
                    trades.remove(trade)

        if trades_to_archive:
            self.save_trades_to_history_file(trades_to_archive)
            print(f"Archived {len(trades_to_archive)} trades.")

    def save_trades_to_history_file(self, trades):
        try:
            with open('trade_history.json', 'a') as file:
                for trade in trades:
                    file.write(json.dumps(trade.__dict__) + '\n')
        except Exception as e:
            print(f"Failed to write to history file: {e}")

    def get_state(self):
        distance_to_target = (self.target_score - self.score) / self.target_score
        self.state[-1] = distance_to_target
        return self.state

    def action_repeated(self, action):
        return self.action_history and action == self.action_history[-1]

    def get_action_reward(self, action):
        return 0.00

    def display_trades(self, status='open'):
        # tracker
        tracker.print_trades(status=status)

        # transactions > get archived anyway
        for pair, transactions in self.transactions.items():
            for transaction in transactions:
                transaction.print_trade()

    def update(self, action, Debug=True, show_trades=False):
        reward = 0.0
        bonus = 0.0
        if Debug & show_trades:
            self.display_trades(status='open')

        col = self.green if self.cap >= self.start_bank else self.red
        print(f'>[{self.bank - self.start_bank}]<  Bank: £{self.bank:.2f}    Positions Invested: #[{self.open_trades}] [Profit £{self.invested:.2f}]    CAPITAL £{self.reset}{col}{self.cap:.2f}{self.reset}p')

        is_repeated = False if not self.action_history else action == self.action_history[-1]

        if self.action_history:
            self.last_repeated.append(is_repeated)
            if Debug:
                print(f'This: {action} Last Action Taken: {self.action_history[-1]} Repeated: {is_repeated}', end='  ')

        reward += self.get_action_reward(action) + bonus
        self.score += reward
        set_score(self.score)

        if Debug:
            print(f'Action: {action} Repeated: {is_repeated}  Reward: {reward:.2f} Score: {self.score:.2f}  Distance:{get_target_score() - self.score}', end='  ')

        self.state[action % self.state_size] = self.score
        self.action_history.append(action)
        self.state_history.append(self.state.copy())

        if len(self.action_history) > self.action_size:
            self.action_history.pop(0)
            self.last_repeated.pop(0)

        if len(self.state_history) > 60:
            self.state_history.pop(0)

        return reward, self.is_over()

    def is_over(self):
        return self.cap <= 10.00

    def should_save_model(self):
        ts = TIME_STEP()
        return ts % 10000 == 0 or self.cap > 300000
