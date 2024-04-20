# Brett Palmer mince@foldingcircles.co.uk

# pip install numpy
# Deep Learn [try] lets create a curious brian.
# gen requirements file pip freeze > requirements.txt

__version__ = "0.0.0003"
import fc_color
from dataframe_validator import validate_and_correct_data
print(f'main.py {__version__}')

print(f'FoldingCircles 2024  A Play with [ Deep Learning Part 2 ]  -M-')
print(f'')
print(f'Forex Trade-Bot The Mitigator Ver:{__version__}')
print(f'Majors:   '
      f'\nEUR/USD (Euro/US Dollar)'
      f'\nUSD/JPY (US Dollar/Japanese Yen)'
      f'\nGBP/USD (British Pound/US Dollar)'
      f'\nAUD/USD (Australian Dollar/US Dollar)'
      f'\nUSD/CAD (US Dollar/Canadian Dollar)'
      f'\nUSD/CHF (US Dollar/Swiss Franc)'
      f'\nNZD/USD (New Zealand Dollar/US Dollar)')
print(f'')
print(f'Minors:   '
      f'\nEUR/GBP (Euro/British Pound)'
      f'\nEUR/AUD (Euro/Australian Dollar)'
      f'\nGBP/JPY (British Pound/Japanese Yen)')
print(f'')
print(f'Exotic Pairs:   '
      f'\nUSD/SGD (US Dollar/Singapore Dollar)'
      f'\nUSD/HKD (US Dollar/Hong Kong Dollar)'
      f'\nEUR/TRY (Euro/Turkish Lira)')
print(f'')
print(f'')

# main.py
from game import Game, get_score, get_target_score
from brain import Brain
from time_step import time_step
from render_weights import WeightRenderer


# This may be an un-necessary step but for me needed.
Validate_currency_pairs = {
    'EURUSD': 'EURUSD_data.csv', 'USDJPY': 'USDJPY_data.csv', 'GBPUSD': 'GBPUSD_data.csv',
    'AUDUSD': 'AUDUSD_data.csv', 'USDCAD': 'USDCAD_data.csv', 'USDCHF': 'USDCHF_data.csv',
    'AUDJPY': 'AUDJPY_data.csv', 'NZDUSD': 'NZDUSD_data.csv'
}
# Let's validate and fix the data as needed
for pair, file_path in Validate_currency_pairs.items():
    print(f'Validating {pair} File: {file_path}')
    v_df, corrected_file_name = validate_and_correct_data(file_path)

def main():
    # initialize neuron renderer
    neuron_renderer = WeightRenderer(width=400, height=400)

    # Define OUR Pairs
    currency_pairs = {
        'EURUSD':'EURUSD_data_corrected.csv', 'USDJPY': 'USDJPY_data_corrected.csv', 'GBPUSD':'GBPUSD_data_corrected.csv',
        'AUDUSD':'AUDUSD_data_corrected.csv', 'USDCAD':'USDCAD_data_corrected.csv' , 'USDCHF':'USDCHF_data_corrected.csv',
        'AUDJPY': 'AUDJPY_data_corrected.csv', 'NZDUSD':'NZDUSD_data_corrected.csv'
    }

    # Init Game
    game = Game(currency_pairs)
    game.forex_step()

    # Init Brain Type
    brain = Brain(use_cuda=False, num_sensors=game.state_size, num_actions=game.action_size, Load_Model=True, Find=True)

    # Simulate Time ?
    sim_time = True  # simulate time scale? if true default time settings = Game.sim_wait = True Game.sim_wait_time = 3

    # TODO  
    # Attention To Sensors
    # AttentionConvMatrix = [P[n] X P[-n]] = 1,0,-1
    # UI
    # AI Controls
    # Q > learn
    # Live Data
    # Save 

    # The Loop
    while not game.is_over():

        state = game.get_state()

        action_index, action_matrix, action_probabilities = brain.decide_action(state)  # for clarity

        action = action_index
        reward, done = game.update(action)

        current_score = get_score()  # Get the current score

        # brain.action_learn(state, action, reward, done, current_score, score_target=score_target)
        brain.learn(state, action, reward, done, current_score)

        time_step(simulate=sim_time)  # Simulate time passing
        game.forex_step(sim_wait=sim_time)  # Get data for new step sim 1 min intervals: quiet/expose internals & logic?

        if game.should_save_model():
            brain.save_model('model.pth')

        if done:
            break  # End the loop if the game is over

        # vis the Brain
        neuron_renderer.update(weight_matrix=brain.get_weights())


if __name__ == "__main__":
    main()
