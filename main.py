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

__version__ = "0.0.0001"
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
from game import Game, get_score, get_target_score
from brain import Brain
from time_step import time_step


def main():
    currency_pairs = {
        'EURUSD':'EURUSD_data.csv', 'USDJPY': 'USDJPY_data.csv', 'GBPUSD':'GBPUSD_data.csv',
        'AUDUSD':'AUDUSD_data.csv', 'USDCAD':'USDCAD_data.csv' , 'USDCHF':'USDCHF_data.csv',
        'AUDJPY': 'AUDJPY_data.csv', 'NZDUSD':'NZDUSD_data.csv'
    }
    game = Game(currency_pairs)
    game.forex_step()
    brain = Brain(num_sensors=game.state_size, num_actions=game.action_size, Load_Model=True, Find=True)

    while not game.is_over():

        state = game.get_state()
        action = brain.decide_action(state)
        reward, done = game.update(action)

        current_score = get_score()  # Get the current score

        # brain.action_learn(state, action, reward, done, current_score, score_target=score_target)
        brain.learn(state, action, reward, done, current_score)

        time_step(simulate=True)  # Simulate time passing
        game.forex_step(sim_wait=True)  # Get data for new step sim 1 min intervals

        if game.should_save_model():
            brain.save_model('model.pth')

        if done:
            break  # End the loop if the game is over


if __name__ == "__main__":
    main()
