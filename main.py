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
# pip install numpy

# Deep Learn [try] lets create a curious brian.

# gen requirements file pip freeze > requirements.txt

__version__ = "0.0.0006"
# TODO add timer system for learn timing info Done
# TODO fix the adjusted Nan issue in debug bands
# TODO remark out all Mitigator calls while we Iron-out all trade issues for speed
# TODO one buy system for all calls for open gamelogic/forex logic
# TODO FEES Done.

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

# Personal project:
# first create a baby brain tries random things lots. Done! Here We continue with new train system

# seems ai needs to see all paths to know what a path is and if the info it sees is similar to a path seen.
# mirror data in time and dimension forwards v backwards and 360/8 directions

# scores[reward/cost] / aims[goals / recover / attack / defend] / targets[ progress in steps towards a final goal]

# main.py
from vis_window import Game_Vis_Window
from game import Game, get_score, get_target_score
from brain import Brain
from time_step import time_step
from render_weights import WeightRenderer
import time

mvw = Game_Vis_Window()

# Wait for the visualization window to be ready
while not mvw.is_ready():
    time.sleep(0.1)
mvw.run()  # initiate thread call once



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
    sim_time = False  # simulate time scale? if true default time settings = Game.sim_wait = True Game.sim_wait_time = 3

    # Attention To Sensors
    # AttentionConvMatrix = [P[n] X P[-n]] = 1,0,-1

    # The Loop
    while not game.is_over():

        #state = game.get_state()

        #action_index, action_matrix, action_probabilities = brain.decide_action(state)  # for clarity

        #action = action_index
        #reward, done = game.update(action)

        current_score = get_score()  # Get the current score

        # brain.action_learn(state, action, reward, done, current_score, score_target=score_target)
        #brain.learn(state, action, reward, done, current_score)

        time_step(simulate=sim_time)  # Simulate time passing
        game.forex_step(sim_wait=sim_time)  # Get data for new step sim 1 min intervals: quiet/expose internals & logic?

        #if game.should_save_model():
        #    brain.save_model('model.pth')

        #if done:
        #    break  # End the loop if the game is over

        # vis the Brain
        neuron_renderer.update(weight_matrix=brain.get_weights())

        # M Vis Win > Game/Abstraction > Sensor/s
        # mvw.run()
        # mvw.game_loop()
    mvw.quit()


if __name__ == "__main__":
    main()
