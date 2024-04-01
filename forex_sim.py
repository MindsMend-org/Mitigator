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


__version__ = "0.0.001"
print(f'forex_sim.py {__version__}')



# forex_sim.py

# pip install pandas

import time
from datetime import datetime
from forex_data_loader import DataLoader
from forex_playback_sim import PlaybackSimulator

def main():
    # Load historical data
    data_loader = DataLoader("historical_data.csv")
    historical_data = data_loader.load_data()

    # Initialize the playback simulator
    simulator = PlaybackSimulator(historical_data)

    # Start playback
    try:
        print("Starting simulation...")
        simulator.start()
    except KeyboardInterrupt:
        print("Simulation stopped.")

if __name__ == "__main__":
    main()
