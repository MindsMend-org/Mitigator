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


__version__ = "0.0.0003"
print(f'game.py {__version__}')

# game.py
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
        self.currency_pairs = currency_pairs  # Example: currency_pairs = {'EURUSD':'EURUSD_data.csv', 'USDJPY': 'USDJPY_data.csv'}
        self.simulators = {}
        self.transactions = {}  # Transactions for each currency pair

        for pair, file in currency_pairs.items():  # Iterate through dictionary if using a dictionary
            data_loader = DataLoader(file)
            historical_data = data_loader.load_data()
            self.simulators[pair] = PlaybackSimulator(historical_data)
            self.transactions[pair] = []  # List to store active and closed transactions

        self.last_close_prices = {pair: None for pair in self.currency_pairs}

        self.state_size = 60  # State size> the len of .state Ideally for Trading Game need min Pair^2 for matrix
        self.action_size = 11  # Number of Game actions 9 dir 2 buttons [any game]
        self.state = [0] * self.state_size
        self.score = 0
        self.target_score = GAME_TARGET_SCORE  # Define the target score
        self.action_history = []  # Store last actions
        self.state_history = []  # Store last states
        self.action_frequencies = [0] * self.action_size  # Track how often each action is taken [DEBUG]
        self.last_repeated = [False] * self.action_size  # Track if the last instance of an action was repeated [DEBUG]
        self.current_forex_data = None
        self.step = 0
        self.start_bank = 1200000.0  # boost as some positions stay open too long , I need to work on stack control for Mitigation system to start work[05/07/24]
        self.bank = self.start_bank
        self.invested = 0.0
        self.wager = 395.25
        self.cap = self.bank + self.invested
        self.open_trades = 0
        self.reset = reset_color()
        self.red = rgb_color(220, 40, 60)
        self.green = rgb_color(0, 255, 0)
        self.sim_wait = True
        self.sim_wait_time = 0.1  # seconds or steps
        # desc std all game types > make into a class
        self.game_type = "M-Trader"  # Game Description
        self.game_mode = "AUTO_OPEN_SHORT"  # set to auto open / short / per temporal step
        self.game_temporal_step_ratio = (10 * 7) * 3  # [10 * Pair Count] steps to one temporal step [logic]
        self.game_flag = False  # used for internal logic flag/counters
        self.game_since = -1  # used for internal logic flag/counters
        self.game_next = self.game_temporal_step_ratio  # used for internal logic flag/counters
        self.game_show_details = False  # used for internal logic flag/counters
        self.game_live_mode = False
        self.game_close_after = 60  # for random close 1 min
        self.game_archive_time = self.game_close_after + 9  # 2592000  # Default is 30 days (30*24*60*60 seconds) > archive
        self.game_step = self.step
        self.game_temporal_step = -1

    def start_forex_simulations(self):
        if self.simulators:
            try:
                print("Starting simulation...")
                for pair, simulator in self.simulators.items():
                    simulator.start()  # disabled for now
            except KeyboardInterrupt:
                print("Simulation stopped.")
        else:
            print("Data not loaded. Call load_data() first.")

    def display_trades(self):
        for currency_pair, trades in self.transactions.items():
            print(f'Currency Pair: {currency_pair} [{len(trades)}]')
            for trade in trades:
                print(f'{currency_pair}: {trade}')  # This will use the __str__ method of TradeTransaction

    # game: game-trade and game-logic update
    def _forex_step(self, sim_wait=None, wait_time=None):
        """
        Modify the forex_step method to include
        Bollinger Bands analysis and pattern detection. This will guide the trade opening decisions:
        :param sim_wait:
        :param wait_time:
        :return:
        """
        if wait_time == None:
            wait_time = self.sim_wait_time
        if sim_wait == None:
            sim_wait = self.sim_wait

        if sim_wait: time.sleep(wait_time)  # Simulate time delay for each step

        STEPPED = False
        pairs_count = len(self.simulators)
        counter = 0

        # !!!!!!!!!!!!!!!!!!!!!!!!
        self.invested = 0.0  # !!
        self.open_trades = 0  # !!
        # !!!!!!!!!!!!!!!!!!!!!!!!
        for pair, simulator in self.simulators.items():
            if self.simulators:
                if not STEPPED:
                    self.step += 1
                    STEPPED = True
                print(f"Step {self.step} for {pair}  ", end=' ')
                # Ensure sim_wait is True only for the last item in the loop
                current_wait = sim_wait if counter == pairs_count else False
                current_forex_data = simulator.get_sim_index(simulator.index, wait=current_wait, wait_time=wait_time)

                last_close = self.last_close_prices[pair]
                current_close = current_forex_data['close']

                change = 0.0

                # Determine the color based on price movement
                if last_close is not None:
                    color = self.green if current_close > last_close else self.red
                    change = current_close - last_close
                else:
                    color = self.reset

                # ui
                print(
                    f"{color}Time: {current_forex_data['timestamp']}, Close: {current_close}  {change:.6f}{self.reset}")

                # game logic
                self.game_logic()
                # update last_close
                self.last_close_prices[pair] = current_close
                # update trade transactions
                self.update_transactions(pair, current_forex_data)
                # update cap
                self.capital()


# new opener M-mod_bolinger
    def forex_step(self, sim_wait=None, wait_time=None):
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
            if self.simulators:
                if not STEPPED:
                    self.step += 1
                    STEPPED = True
                print(f"Step {self.step} for {pair}  ", end=' ')
                current_wait = sim_wait if counter == pairs_count else False
                current_forex_data = simulator.get_sim_index(simulator.index, wait=current_wait, wait_time=wait_time)

                last_close = self.last_close_prices[pair]
                current_close = current_forex_data['close']

                change = 0.0
                if last_close is not None:
                    color = self.green if current_close > last_close else self.red
                    change = current_close - last_close
                else:
                    color = self.reset

                print(
                    f"{color}Time: {current_forex_data['timestamp']}, Close: {current_close}  {change:.6f}{self.reset}")

                # Run analysis on current Forex data
                signal = get_trade_signal(simulator.data)

                # Act based on the trade signal
                if signal == "buy":
                    self.open_trade(pair, "buy", self.wager / current_close)
                elif signal == "sell":
                    self.open_trade(pair, "sell", self.wager / current_close)

                self.game_logic()
                self.last_close_prices[pair] = current_close
                self.update_transactions(pair, current_forex_data)
                self.capital()

    def _run_analysis(self, pair, data): # remove encaplsulate it into strat
        window_size = 20  # Adjust as needed
        num_std = 2  # Adjust as needed

        # Ensure the data is structured correctly
        b_band_window = np.array(data[-window_size:], dtype=[('o', 'f8'), ('h', 'f8'), ('l', 'f8'), ('c', 'f8')])

        upper_band, lower_band = D_calculate_bollinger_bands(b_band_window, smoothing_window=window_size,
                                                             num_std=num_std)
        upper_crossovers, lower_crossovers = calculate_bollinger_crossovers(b_band_window, upper_band, lower_band)

        # Check for signals and open trades accordingly
        if upper_crossovers:
            self.open_trade(pair, "sell", self.wager / b_band_window['c'][-1])
        elif lower_crossovers:
            self.open_trade(pair, "buy", self.wager / b_band_window['c'][-1])
#------------------------------------ opener added - M modified Bolinger
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
        # Filter to get only open trades
        open_trades = [trade for pair_trades in self.transactions.values() for trade in pair_trades if
                       trade.status == 'open']
        # Sort the trades by their open_time, the oldest first
        open_trades.sort(key=lambda x: x.open_time)
        # Return the oldest trade if any are open
        if open_trades:
            return open_trades[0]
        return None

    # Game:Mitigation AI [[internal]:[1] [2] [3] ]
    def game_logic(self, show_details=False):
        # [1] call internal_flag update internal timers
        if self.internal_flag():
            # use the flag:True for logic.
            if self.game_mode == "AUTO_OPEN_SHORT":
                print(f'self.game_mode = {self.game_mode} [Flagged:]')
                # ok here the game will auto short a trade

                # Get a list of the dictionary keys
                keys = list(self.currency_pairs.keys())

                # Select a random key from the forex pairs list
                random_key = random.choice(keys)

                pair = random_key
                if pair in self.simulators:
                    # use a simulation pair
                    current_price = self.simulators[pair].data[self.simulators[pair].index]['close']
                else:
                    # use a live pair
                    current_price = self.last_close_prices[pair]

                # set trade type
                trade_type = "sell"
                # set wager using bank/50
                self.wager = self.bank/50
                # update quantity using wager at current price
                quantity = self.wager / current_price
                # perform open trade
                self.open_trade(pair, trade_type, quantity)
                # update any sensors or logs for clear historic path to action and current state.

                # update console
                print(
                    f'>TRADE: Pair:{pair}    Type:{trade_type}    Cost:£{quantity * current_price:.3f}    qty:{quantity:.3f}')

            # free memory move old trades to archive [only closed trades]
            self.archive_old_trades()

            if self.open_trades > 0:
                longest_trade = self.Longest_Trade()
                if longest_trade:
                    print(f"Longest Open Trade: {longest_trade}")

                    # if trade > time_limit close
                    self.close_expired_trades()

        # [2]
        if show_details or self.game_show_details:
            self.show_internals()
        # [3]
        self.internal_end()

    # trade Transactions: update_transactions > called from game.forex_step()
    def update_transactions(self, pair, market_data):
        _open_trade_count = 0
        investments_value = 0.0
        for transaction in self.transactions[pair]:
            if transaction.status == 'open':
                _open_trade_count += 1
                transaction.update_value(market_data['close'])
                investments_value += transaction.get_profit_loss()
        # update game var
        self.invested += investments_value
        self.open_trades += _open_trade_count

    # trade Transactions:
    def open_trade(self, pair, trade_type, quantity):
        if pair in self.simulators:
            current_price = self.simulators[pair].data[self.simulators[pair].index]['close']
            new_transaction = TradeTransaction(trade_type, current_price, quantity)
            self.transactions[pair].append(new_transaction)
            cost = current_price * quantity
            if trade_type == 'buy':
                self.bank -= cost
            print(f'- £ {cost:.2f}  bank:[£{self.bank:.2f}]    cap £{self.cap:.2f}p')

    # trade Transactions:
    def close_trade(self, pair, transaction_index):
        if pair in self.transactions and 0 <= transaction_index < len(self.transactions[pair]):
            transaction = self.transactions[pair][transaction_index]

            if transaction.status == 'open':  # Check if the trade is still open
                current_price = self.simulators[pair].data[self.simulators[pair].index]['close']
                transaction.close_trade(current_price)
                total_position_value = transaction.entry_price * transaction.quantity

                # Retrieve profit or loss from the transaction
                profit_loss = transaction.get_profit_loss()

                # Update the bank balance
                if transaction.trade_type == 'buy':
                    self.bank += total_position_value + profit_loss
                elif transaction.trade_type == 'sell':
                    self.bank += profit_loss  # For short selling, profit or loss is the only financial change

                # Output the result of the closing trade
                print(f'Closed Trade: {transaction.trade_type.upper()} - Profit/Loss: £{profit_loss:.2f},'
                      f'New Bank Balance: £{self.bank:.2f}')

    # trade Transactions: expired
    def close_expired_trades(self, _time_limit=None):  # Default time_limit set to 5400 seconds (90 minutes)
        if _time_limit is not None:
            time_limit = _time_limit
        else:
            time_limit = self.game_close_after

        current_time = time.time()
        for pair, trades in self.transactions.items():
            # Create a copy of the list of trades as we might be modifying it during iteration
            for trade_index, trade in enumerate(
                    trades.copy()):  # Using copy() to safely modify the list while iterating
                if trade.status == 'open':
                    trade_duration = current_time - trade.open_time
                    if trade_duration > time_limit:
                        # Call the close_trade method using the pair and the index of the trade
                        self.close_trade(pair, trade_index)

    # trade Transactions:
    def archive_old_trades(self, _archive_after=None):  # Default is 30 days (30*24*60*60 seconds) 2592000
        if _archive_after is not None:
            archive_after = _archive_after
        else:
            archive_after = self.game_archive_time

        current_time = time.time()
        trades_to_archive = []

        for pair, trades in list(self.transactions.items()):
            for trade in trades[:]:  # iterate over a shallow copy of the list
                if trade.status == 'closed' and (current_time - trade.close_time) >= archive_after:
                    trades_to_archive.append(trade)
                    trades.remove(trade)  # Remove trade from active list

        if trades_to_archive:
            self.save_trades_to_history_file(trades_to_archive)
            print(f"Archived {len(trades_to_archive)} trades.")

    # trade Transactions: history
    def save_trades_to_history_file(self, trades):
        try:
            # Assuming trade data is serializable; otherwise, adjust serialization method
            with open('trade_history.json', 'a') as file:  # Appends to the existing file
                for trade in trades:
                    file.write(json.dumps(trade.__dict__) + '\n')
        except Exception as e:
            print(f"Failed to write to history file: {e}")

    # Mitigation AI
    def get_state(self):
        # Normalized distance to target score as part of the state
        distance_to_target = (self.target_score - self.score) / self.target_score
        self.state[-1] = distance_to_target  # Set the last element of the state to the distance
        return self.state

    # Mitigation AI
    def action_repeated(self, action):
        return self.action_history and action == self.action_history[-1]

    # Mitigation AI
    def get_action_reward(self, action):
        return 0.00

    # Console
    # display game information to console: update > called from game.forex_step() [singular] todo [sequence]
    def update(self, action, Debug=True):
        reward = 0.0
        bonus = 0.0
        self.display_trades()
        if self.cap >= self.start_bank:
            col = self.green
        else:
            col = self.red
        print(
            f'Bank: £{self.bank:.2f}    Positions Invested: #[{self.open_trades}] [Profit £{self.invested:.2f}]    CAPITAL £{self.reset}{col}{self.cap:.2f}{self.reset}p')

        # Initialize is_repeated based on the immediate history
        is_repeated = False if not self.action_history else action == self.action_history[-1]

        # Mitigation AI
        # Append the current action's repeated status
        if self.action_history:
            self.last_repeated.append(is_repeated)
            if Debug:
                print(f'This: {action} Last Action Taken: {self.action_history[-1]} Repeated: {is_repeated}', end='  ')

        reward += self.get_action_reward(action) + bonus
        self.score += reward
        set_score(self.score)

        # Mitigation AI
        # Debug output
        if Debug:
            print(
                f'Action: {action} Repeated: {is_repeated}  Reward: {reward:.2f} Score: {self.score:.2f}  Distance:{get_target_score() - self.score}',
                end='  ')

        # Mitigation AI
        # Update the state and score
        self.state[action % self.state_size] = self.score
        self.action_history.append(action)
        self.state_history.append(self.state.copy())

        # Mitigation AI
        # Maintain the length of histories
        if len(self.action_history) > self.action_size:
            self.action_history.pop(0)
            self.last_repeated.pop(0)

        if len(self.state_history) > 60:
            self.state_history.pop(0)

        # Mitigation AI
        return reward, self.is_over()

    # Game:Mitigation AI
    def capital(self):
        self.cap = self.bank + self.invested
        return self.cap

    # Game:Mitigation AI
    def is_over(self):
        # Example condition to end the game
        return self.cap <= 100.00

    # Game:Mitigation AI
    def should_save_model(self):
        ts = TIME_STEP()
        # Example condition to save model £$ 3 mill $£
        # Mitigation AI [update this to a rolling value based upon starting capital]
        return ts % 10000 == 0 or self.cap > 300000
