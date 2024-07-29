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

__version__ = "0.0.0009"
print(f'game.py {__version__}')

import datetime
import time
import random
import json
from strategy import analyze_data, D_calculate_bollinger_bands, calculate_bollinger_crossovers, get_trade_signal, calculate_trading_costs, non_zero
from time_step import TIME_STEP  # Import here to avoid circular dependencies
from forex_data_loader import DataLoader
from forex_playback_sim import PlaybackSimulator
from forex_data_loader import pull_forex_data
from fc_color import reset_color, rgb_color
from trade_tracker import TradeTracker

tracker = TradeTracker()  # used to track all trades

UPDATE_FOREX = False
if UPDATE_FOREX: pull_forex_data()

# GLOBAL
BABY = False
GAME_SCORE = 0
GAME_TARGET_SCORE = 0.9


def _serialize_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def serialize_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    else:
        print(f"Non-serializable type: {type(obj)}")
        raise TypeError("Type not serializable")

def deserialize_datetime(date_str):
    return datetime.datetime.fromisoformat(date_str)


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


class Game:
    def __init__(self, currency_pairs):
        self.currency_pairs = currency_pairs
        self.simulators = {}
        self.last_close_prices = {pair: None for pair in self.currency_pairs}
        self.state_size = 60  # AI
        self.action_size = 11  # AI
        self.state = [0] * self.state_size  # AI
        self.score = 0  # AI
        self.target_score = GAME_TARGET_SCORE  # AI
        self.action_history = []  # AI
        self.state_history = []  # AI
        self.action_frequencies = [0] * self.action_size  # AI
        self.last_repeated = [False] * self.action_size  # AI
        self.current_forex_data = None
        self.step = 0  # SIM/REAL Cycles & # AI
        self.start_bank = 30000.0
        self.bank = self.start_bank
        self.invested = 0.0
        self.wager = 5.25
        self.min_bank_limit = 90.0  # will not open trades if (bank-trade_cost) < this value
        self.bank_share = 6  # bank_share=50
        self.cap = self.bank + self.invested
        self.open_trades = 0  # pair
        self.all_pairs_open_trades = 0
        self.max_history_length = 33  # Set max history length > close expired [time & length]
        self.game_close_after = 33  # days/mins/hours & steps if in sim mode [wip]
        self.game_archive_time = 2
        self.trades_limit_trade_count = True
        self.trades_max_count = 700  # if trades_limit_trade_count use this as limit [pair] keeps open possible per pair
        self.open_sell_cost = 0.0  # Track the cost of open sell trades
        # Sim Trading cost parameters
        self.spread = 1.2  # Example spread in pips
        self.commission_per_unit = 0.2 # 5  # Example commission per unit
        self.pip_value = 1.56  # Set pip value for 100,000 units of USD/JPY
        self.reset = reset_color()
        self.red = rgb_color(220, 40, 60)
        self.green = rgb_color(0, 255, 0)
        self.sim_wait = True
        self.sim_wait_time = 0.3
        self.game_type = "M-Trader"
        self.game_mode = ""
        self.game_temporal_step_ratio = (10 * 7) * 1
        self.game_flag = False
        self.game_since = -1
        self.game_next = self.game_temporal_step_ratio
        self.game_show_details = False
        self.game_live_mode = False
        self.game_step = self.step
        self.game_temporal_step = -1
        self.game_time_start = None
        self.game_time_to = 0.0
        self.game_time_total = 0.0
        self.game_realtime_per_step = 0.0
        self.game_time_total_reset_at = 99999999.999
        self.vis_window = None  # Link to the visualization window instance call set from main

        # Add counters for trades and mitigations
        self.closed_trades_count = 0
        self.mitigated_trades_count = 0
        self.failed_trades_count = 0
        self.initial_successful_open = 0
        self.initial_failed_open = 0
        self.successful_trades_count = 0
        self.successful_mitigated_trades_count = 0

        for pair, file in currency_pairs.items():
            data_loader = DataLoader(file)
            historical_data = data_loader.load_data()
            self.simulators[pair] = PlaybackSimulator(historical_data)

    def set_vis_window(self, vis_window):
        """Set the visualization window instance."""
        self.vis_window = vis_window

    def update_vis(self):
        """Update the visualization window with the current game values."""
        if self.vis_window:
            print(f'-')
            print(f'--- Update Visualization Window  ---')
            print(f'-')
            self.vis_window.set_bank(self.bank)
            self.vis_window.set_cap(self.cap)
            self.vis_window.set_trades_total(len(tracker.get_trades()))
            self.vis_window.set_trades_open(self.open_trades)
            self.vis_window.set_avg_profit(self.invested / max(1, self.open_trades))  # Prevent division by zero
            self.vis_window.set_trades_closed(self.closed_trades_count)
            self.vis_window.set_trades_mitigated(self.mitigated_trades_count)
            self.vis_window.set_trades_failed(self.failed_trades_count)
            self.vis_window.set_trades_successful(self.successful_trades_count)
            self.vis_window.set_trades_successful_mitigated(self.successful_mitigated_trades_count)
            self.vis_window.set_mitigation_lives_per_trade(self.calculate_mitigation_lives_per_trade())
            self.vis_window.set_mitigation_total_lives(self.calculate_mitigation_total_lives())
        else:
            print(f'-')
            print(f'--- No Visualization Window ! ---')
            print(f'-')

    def calculate_mitigation_lives_per_trade(self):
        # Placeholder calculation for mitigation lives per trade
        return 8  # Replace with actual calculation logic

    def calculate_mitigation_total_lives(self):
        # Placeholder calculation for mitigation total lives
        return 50  # Replace with actual calculation logic

    def open_trade(self, pair, trade_type, quantity):
        current_price = self.simulators[pair].data[self.simulators[pair].index]['close']
        trade_details = {
            'symbol': pair,
            'type': trade_type,
            'quantity': quantity,
            'price': current_price
        }

        cost = current_price * quantity
        trade_size = quantity * 100  # will match prob try OANDA / etoro  [100000 Assuming standard lot size for simplicity]
        print('--New Trade--')
        print(f'bank:[£{self.bank:.2f}]    cap £{self.cap:.2f}')
        print(f' Pos:{trade_type}  Pair:{pair}  * {quantity}  at £{current_price}  TOT-fees £{quantity*current_price}')
        total_cost = calculate_trading_costs(trade_size, self.spread, self.commission_per_unit, self.pip_value)
        total_cost += cost
        print(f'Sub Total £{total_cost}')

        #if trade_type == 'buy':
        #    total_cost += cost
        # we will switch to allways take cost and on close work out overnight fees and sell+/-

        if self.bank - total_cost > self.min_bank_limit:
            self.bank -= total_cost
            tracker.open_trade(trade_details, tradetype=trade_type)
            print(f'- £ {total_cost:.2f}  bank:[£{self.bank:.2f}]    cap £{self.cap:.2f}  ucode:{trade_details["trade_code"]}')
        else:
            print(f'Insufficient funds to open trade. Bank balance: £{self.bank:.2f}, Required: £{total_cost:.2f}  min Bank needed to open £{self.min_bank_limit}')

    def close_trade(self, trade_code):
        trade = tracker.get_trade(trade_code)
        if trade and trade['status'] == 'open':

            current_price = self.simulators[trade['symbol']].data[self.simulators[trade['symbol']].index]['close']
            profit_loss = (current_price - trade['price']) * trade['quantity'] if trade['type'] == 'buy' else (trade['price'] - current_price) * trade['quantity']
            trade_size = trade['quantity'] * 100000  # Assuming standard lot size for simplicity
            trading_cost = 0.0 # calculate_trading_costs(trade_size, self.spread, self.commission_per_unit, self.pip_value)

            if trade['type'] == 'buy':
                self.bank += (profit_loss - trading_cost)
            else:
                self.bank += (profit_loss - trading_cost)
                self.open_sell_cost -= trading_cost
            # now as we have the sell/buy profit we only need to add the entry cost

            entry_value = trade['price'] * trade['quantity']
            self.bank += entry_value

            self.cap = self.bank + self.invested
            tracker.close_trade(trade_code)
            self.closed_trades_count += 1
            print(f'Closed Trade:ucode:{trade_code} {trade["type"].upper()} - Profit/Loss: £{profit_loss:.2f}, New Bank Balance: £{self.bank:.2f}')
            """
            if t['mitigated']:
                self.mitigated_trades_count += 1
            if t['failed']:
                self.failed_trades_count += 1
            if t['successful']:
                self.successful_trades_count += 1
                if t['mitigated']:
                    self.successful_mitigated_trades_count += 1
            """
            # stats
            # Determine if the initial movement was correct
            if len(trade['close_history']) > 1:
                first_close_price = trade['close_history'][1]['close_value']
                if (trade['type'] == 'buy' and first_close_price > trade['price']) or \
                        (trade['type'] == 'sell' and first_close_price < trade['price']):
                    trade['initial_correct'] = True
                    self.initial_successful_open += 1
                else:
                    trade['initial_correct'] = False
                    self.initial_failed_open += 1

            # Determine if the trade was ultimately successful
            if profit_loss > 0:
                self.successful_trades_count += 1
            else:
                self.failed_trades_count += 1

            if len(trade['close_history']) > 1:
                open_correct = trade.get('initial_correct', 'N/A')  # trade['initial_correct']
            else:
                open_correct = None

            print(f"Stats Trade [{trade_code}]  open correct [{open_correct}]   winner:[{profit_loss > 0}]")

    def close_all_open_trades(self, pair, keep_trade_type):
        for trade in tracker.get_open_trades():
            if trade['symbol'] == pair and trade['type'] != keep_trade_type:
                self.close_trade(trade['trade_code'])

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

                # update link to vis instance
                self.update_vis()

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

            # Update the current price in the TradeTracker
            tracker.update_current_prices(pair, current_close)

            signal = get_trade_signal(simulator.data, self.step, debug=False, debug_graph=False)
            self.wager = self.bank / self.bank_share  # bank_share=50
            current_price = current_close
            quantity = self.wager / current_price

            if signal == "buy":
                self.close_all_open_trades(pair, "buy")
            elif signal == "sell":
                self.close_all_open_trades(pair, "sell")

            if signal == "buy":
                if self.trades_limit_trade_count:
                    if len(tracker.get_open_trades()) < self.trades_max_count:
                        self.open_trade(pair, "buy", quantity)
            elif signal == "sell":
                if self.trades_limit_trade_count:
                    if len(tracker.get_open_trades()) < self.trades_max_count:
                        self.open_trade(pair, "sell", quantity)

            self.game_logic()
            self.last_close_prices[pair] = current_close
            self.update_transactions(pair, current_forex_data)
            self.capital()

        if self.step % 10 == 0:
            print(f'Average time per step: {self.game_realtime_per_step:.6f}')

    def update_transactions(self, pair, market_data, show_value=True):
        _open_trade_count = 0
        _investments_value = 0.0
        for trade in tracker.get_open_trades():
            if trade['symbol'] == pair:
                _open_trade_count += 1
                current_value = market_data['close'] * trade['quantity']
                entry_value = trade['price'] * trade['quantity']
                if show_value:
                    _investments_value += current_value
                else:
                    _investments_value += (current_value - entry_value)

        self.invested += _investments_value
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

                if self.trades_limit_trade_count:
                    if len(tracker.get_open_trades()) < self.trades_max_count:
                        self.open_trade(pair, "sell", self.wager / current_price)

            self.archive_old_trades()

            if self.open_trades > 0:
                longest_trade = self.Longest_Trade()
                if longest_trade:
                    print(f"Longest Open Trade: {longest_trade}")
            else:
                print('----------')
                print('No Trades OPEN--------------------------------------------------------------------')
                print('----------')

            self.close_expired_trades()

        if show_details or self.game_show_details:
            self.show_internals()
        self.internal_end()

    # Internals
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

    # TRADE
    def Longest_Trade(self):
        open_trades = tracker.get_open_trades()
        open_trades.sort(key=lambda x: x['open_time'])
        if open_trades:
            return open_trades[0]
        return None

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

            # old time_limit = (self.game_close_after * sub_time_frame) / self.game_realtime_per_step if self.game_realtime_per_step > 0 else self.game_close_after * sub_time_frame
            time_limit = (self.game_close_after * 1.01) / self.game_realtime_per_step if self.game_realtime_per_step > 0 else self.game_close_after * sub_time_frame
            print(f'setting time_limit to [{time_limit}]')
        if debug:
            print(f'----')
            print('Duration Limit Check All Trades:')
        current_time = time.time()
        for trade in tracker.get_open_trades():
            trade_duration = current_time - trade['open_time'].timestamp()
            if trade_duration > time_limit or len(trade['close_history']) > self.max_history_length:
                if debug:
                    formatted_duration = self.format_duration(trade_duration)
                    print(f"Closing trade {trade['trade_code']} which has been open for {formatted_duration}")
                self.close_trade(trade['trade_code'])
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

        for trade in tracker.get_trades():
            if trade['status'] == 'closed' and (current_time - trade['close_time'].timestamp()) >= archive_after:
                trade_copy = trade.copy()  # Make a copy of the trade serialize error
                trade_copy['open_time'] = serialize_datetime(trade_copy['open_time'])
                trade_copy['close_time'] = serialize_datetime(trade_copy['close_time'])
                trades_to_archive.append(trade_copy)
                tracker.get_trades().remove(trade)
                #trades_to_archive.append(trade)
                #tracker.get_trades().remove(trade)

        if trades_to_archive:
            self.save_trades_to_history_file(trades_to_archive)
            print(f"Archived {len(trades_to_archive)} trades.")


    def save_trades_to_history_file(self,trades):
        try:
            with open('trade_history.json', 'a') as file:
                for trade in trades:
                    trade_copy = trade.copy()
                    try:
                        trade_copy['open_time'] = serialize_datetime(trade_copy['open_time'])
                        if 'close_time' in trade_copy:
                            trade_copy['close_time'] = serialize_datetime(trade_copy['close_time'])

                        # Ensure all keys and values in trade_copy are serializable
                        for key, value in trade_copy.items():
                            if not isinstance(value, (str, int, float, bool, type(None))):
                                trade_copy[key] = str(value)

                        file.write(json.dumps(trade_copy) + '\n')
                    except TypeError as e:
                        print(f"Serialization error for trade: {trade_copy}")
                        print(f"Error: {e}")
        except Exception as e:
            print(f"Failed to write to history file: {e}")


    def display_trades(self, status='open'):
        tracker.print_trades(status=status)

    # DEEP
    def get_state(self):
        distance_to_target = (self.target_score - self.score) / self.target_score
        self.state[-1] = distance_to_target
        return self.state

    def action_repeated(self, action):
        return self.action_history and action == self.action_history[-1]

    def get_action_reward(self, action):
        return 0.00

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
        return self.step >5000

    def should_save_model(self):
        ts = TIME_STEP()
        return ts % 10000 == 0 or self.cap > 300000
