# Brett Palmer mince@foldingcircles.co.uk]
# FoldingCircles 

__version__ = "0.0.001"
print(f'time_step.py {__version__}')

# time_step.py
import time

GLOBAL_TIME_STEP = 0

def TIME_STEP():
    global GLOBAL_TIME_STEP
    return GLOBAL_TIME_STEP

# we need to attend to  # Poll for and process events
#                     glfw.poll_events()
def time_step(simulate=True, wait_time=0.02, newline=True):
    global GLOBAL_TIME_STEP
    GLOBAL_TIME_STEP += 1

    if simulate: time.sleep(wait_time)  # Simulate time delay for each step

    print(f'\rTime Step:{GLOBAL_TIME_STEP}', end=' ')
    if newline: print()
