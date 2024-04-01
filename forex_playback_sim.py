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
print(f'forex_playback_sim.py {__version__}')



# forex_playback_sim.py

import time

class PlaybackSimulator:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def start(self):
        while self.index < len(self.data):
            current_data = self.data[self.index]
            print(f"Time: {current_data['timestamp']}, Price: {current_data['price']}, Volume: {current_data['volume']}")
            self.index += 1
            time.sleep(60)  # Wait for 1 minute

    def get_sim_index(self, index, wait=True, wait_time=3):   # df.columns = ['Date', 'Open', 'Close', 'High', 'Low']
        if 0 <= index < len(self.data):  # Ensure index is within the range
            current_data = self.data[index]  # Use the passed index to get the current data
            print(
                f"Time: {current_data['timestamp']}, Open: {current_data['open']}, Close: {current_data['close']}, High: {current_data['high']}, Low: {current_data['low']}")
            self.index = index + 1  # Move to the next index after printing
            if wait:
                time.sleep(wait_time)  # Wait for 1 minute
            return current_data
        else:
            print("Index out of range")  # Print error message if index is out of range
            return None