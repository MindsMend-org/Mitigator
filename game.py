# FoldingCircles 2024
# Brett Palmer mince@foldingcircles.co.uk

__version__ = "0.0.0003"
print(f'game.py {__version__}')

# game.py
from time_step import TIME_STEP  # Import here to avoid circular dependencies
import time
from forex_data_loader import DataLoader
from forex_playback_sim import PlaybackSimulator
from forex_data_loader import pull_forex_data
from trade__transactions import TradeTransaction
from fc_color import reset_color, rgb_color

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

#self.action_mappings = {0: 'action1', 1: 'action2'}
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
        self.bank = 120000
        self.wager = 100
        self.reset = reset_color()
        self.red = rgb_color(220, 40, 60)
        self.green = rgb_color(0, 255, 0)
        self.sim_wait = True
        self.sim_wait_time = 3               # seconds or steps
        # desc std all game types > make into a class
        self.game_type = "M-Trader"          # Game Description
        self.game_mode = "AUTO_OPEN_SHORT"   # set to auto open / short / per temporal step
        self.game_temporal_step_ratio = 10 * 7      # [10 * Pair Count] steps to one temporal step [logic]
        self.game_flag = False                           # used for internal logic flag/counters
        self.game_since = -1                              # used for internal logic flag/counters
        self.game_next = self.game_temporal_step_ratio   # used for internal logic flag/counters
        self.game_show_details = False                   # used for internal logic flag/counters


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

    # game: game-trade and game-logic update
    def forex_step(self, sim_wait=None, wait_time=None):
        if wait_time == None:
            wait_time = self.sim_wait_time
        if sim_wait == None:
            sim_wait = self.sim_wait

        STEPPED = False
        pairs_count = len(self.simulators)
        counter = 0
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

    def show_internals(self):
        print(f'self.game_type = {self.game_type}')
        print(f'self.game_mode = {self.game_mode}')
        print(f'self.game_temporal_step_ratio = {self.game_temporal_step_ratio}')
        print(f'self.game_since = {self.game_since}')
        print(f'self.game_next = {self.game_next}')
        print(f'self.game_flag = {self.game_flag}')
        print(f'self.game_show_details = {self.game_show_details}')

    def internal_flag(self):
        self.game_since += 1
        self.game_next = self.game_temporal_step_ratio - self.game_since
        if self.game_since >= self.game_temporal_step_ratio+1:
            self.game_since = -1
            self.game_flag = True
        return self.game_flag

    def internal_end(self):
        self.game_flag = False
    def game_logic(self, show_details=False):
        # [1]
        if self.internal_flag():
            if self.game_mode == "AUTO_OPEN_SHORT":
                print(f'Flagged:')
        # [2]
        if show_details or self.game_show_details:
            self.show_internals()
        # [3]
        self.internal_end()


    # trade Transactions: update_transactions > called from game.forex_step()
    def update_transactions(self, pair, market_data):
        for transaction in self.transactions[pair]:
            if transaction.status == 'open':
                transaction.update_value(market_data['close'])

    def open_trade(self, pair, trade_type, quantity):
        if pair in self.simulators:
            current_price = self.simulators[pair].data[self.simulators[pair].index]['close']
            new_transaction = TradeTransaction(trade_type, current_price, quantity)
            self.transactions[pair].append(new_transaction)

    def close_trade(self, pair, transaction_index):
        if pair in self.transactions and 0 <= transaction_index < len(self.transactions[pair]):
            transaction = self.transactions[pair][transaction_index]
            current_price = self.simulators[pair].data[self.simulators[pair].index]['close']
            transaction.close_trade(current_price)

    def get_state(self):
        # Normalized distance to target score as part of the state
        distance_to_target = (self.target_score - self.score) / self.target_score
        self.state[-1] = distance_to_target  # Set the last element of the state to the distance
        return self.state

    def action_repeated(self, action):
        return self.action_history and action == self.action_history[-1]

    def get_action_reward(self, action):
        return 0.00

    # display game information to console: update > called from game.forex_step()
    def update(self, action, Debug=True):
        reward = 0.0
        bonus = 0.0

        # display forex at step TIME_STEP() auto from main call in main.py

        print(f'Trades:{self.transactions}')

        # Initialize is_repeated based on the immediate history
        is_repeated = False if not self.action_history else action == self.action_history[-1]

        # Append the current action's repeated status
        if self.action_history:
            self.last_repeated.append(is_repeated)
            if Debug:
                print(f'This: {action} Last Action Taken: {self.action_history[-1]} Repeated: {is_repeated}', end='  ')

        reward += self.get_action_reward(action) + bonus
        self.score += reward
        set_score(self.score)

        # Debug output
        if Debug:
            print(
                f'Action: {action} Repeated: {is_repeated}  Reward: {reward:.2f} Score: {self.score:.2f}  Distance:{get_target_score() - self.score}',
                end='  ')

        # Update the state and score
        self.state[action % self.state_size] = self.score
        self.action_history.append(action)
        self.state_history.append(self.state.copy())

        # Maintain the length of histories
        if len(self.action_history) > self.action_size:
            self.action_history.pop(0)
            self.last_repeated.pop(0)

        if len(self.state_history) > 60:
            self.state_history.pop(0)

        return reward, self.is_over()

    def is_over(self):
        # Example condition to end the game
        return self.bank <= 0

    def should_save_model(self):
        ts = TIME_STEP()
        # Example condition to save model
        return ts % 10000 == 0 and self.score > 3000
