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
print(f'time_step.py {__version__}')


# time_step.py
import time

GLOBAL_TIME_STEP = 0

def TIME_STEP():
    global GLOBAL_TIME_STEP
    return GLOBAL_TIME_STEP

def time_step(simulate=True, wait_time=3):
    global GLOBAL_TIME_STEP
    GLOBAL_TIME_STEP += 1

    if simulate: time.sleep(wait_time)  # Simulate time delay for each step

    print(f'\rTime Step:{GLOBAL_TIME_STEP}', end=' ')

