import numpy as np
from debug_graph_strategy import window_plot_bollinger_bands

__version__ = "0.0.001"
print(f'strategy.py {__version__}')


def D_calculate_bollinger_bands(data, smoothing_window=20, num_std=2):
    """
    Calculate Bollinger Bands for given data.
    :param data: Structured array containing 'c' (closing prices).
    :param smoothing_window: Number of periods for the moving average.
    :param num_std: Number of standard deviations for the bands.
    :return: upper_band, lower_band
    """
    closing_prices = data['c']

    if len(closing_prices) < smoothing_window:
        return np.full(len(closing_prices), np.nan), np.full(len(closing_prices), np.nan)

    rolling_mean = np.convolve(closing_prices, np.ones(smoothing_window) / smoothing_window, mode='valid')
    rolling_std = np.array(
        [np.std(closing_prices[i:i + smoothing_window]) for i in range(len(closing_prices) - smoothing_window + 1)])

    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)

    # Ensure bands have the same length as closing prices for comparison
    upper_band = np.concatenate((np.full(smoothing_window - 1, np.nan), upper_band))
    lower_band = np.concatenate((np.full(smoothing_window - 1, np.nan), lower_band))

    return upper_band, lower_band

# Modified to only reg the last crossover
def calculate_bollinger_crossovers(windowed_data, upper_band, lower_band, recent_window_fraction=1/2):
    upper_crossovers = []
    lower_crossovers = []

    recent_window_size = int(len(windowed_data) * recent_window_fraction)
    recent_window_start = len(windowed_data) - recent_window_size

    for i in range(1, len(windowed_data)):
        if i < 1 or i >= len(upper_band) or i >= len(lower_band):
            continue

        # Detect upper band crossovers
        if windowed_data['c'][i - 1] <= upper_band[i - 1] and windowed_data['c'][i] > upper_band[i]:
            print(f'# Detect upper band crossovers at index {i}')
            upper_crossovers.append(i)

        # Detect lower band crossovers
        if windowed_data['c'][i - 1] >= lower_band[i - 1] and windowed_data['c'][i] < lower_band[i]:
            print(f'# Detect lower band crossovers at index {i}')
            lower_crossovers.append(i)

    last_upper_crossover = next((x for x in reversed(upper_crossovers) if x >= recent_window_start), None)
    last_lower_crossover = next((x for x in reversed(lower_crossovers) if x >= recent_window_start), None)

    print(f'Lower crossover at index {last_lower_crossover}, fraction of window: {recent_window_fraction}')
    print(f'Upper crossover at index {last_upper_crossover}, fraction of window: {recent_window_fraction}')

    return last_upper_crossover, last_lower_crossover


def get_trade_signal(data, current_step, window_size=30, num_std=1.35, recent_window_fraction=1/3,
                     lead_in_length=10, future_estimates=10,
                     debug=False, debug_graph=False):
    """
    Mitigator: Function: can work alongside game mode or replace not sure yet
    Used when simulating or Live the rolling data of length window_size will trigger buy/sell/none
    :param debug_graph: use to adjust bands for detection [offset]
    :param data: Forex Pair Data.
    :param current_step: Mitigator Temporal step Sim or Live.
    :param window_size:
    :param num_std:
    :param recent_window_fraction:
    :param future_estimates: Number of future estimates to include.[extend]
    :param debug: [True/False] Show Debug In Console?
    :return: > buy/sell/none
    """
    if debug:
        print(f'DEBUG:strategy.py:start')

    if len(data) < window_size:
        if debug:
            print(f'TRUE:len(data) < window_size:')
            print(f'return none')
            print(f'DEBUG:strategy.py:end')
        return "none"

    if current_step < window_size:
        if debug:
            print('TRUE:current_step < window_size:')
            print('> Not enough time past to gen bands')
            print('return none')
            print('DEBUG:strategy.py:end')
        return "none"

    # Use only the last `window_size` data points up to the current step
    data_to_use = data[max(0, current_step - window_size):current_step]

    # Extract fields and create a structured array
    dtype = [('o', 'f8'), ('h', 'f8'), ('l', 'f8'), ('c', 'f8')]
    windowed_data = np.array(
        [(item['open'], item['high'], item['low'], item['close']) for item in data_to_use],
        dtype=dtype
    )

    # Extend the windowed data with future estimates
    if len(windowed_data) > 0:
        last_close = windowed_data['c'][-1]
        future_estimates_data = np.full((future_estimates,), last_close, dtype=dtype)
        windowed_data = np.concatenate((windowed_data, future_estimates_data))

        # Extend the windowed data with past estimates
    if len(windowed_data) > 0:
        first_close = windowed_data['c'][0]
        lead_in_data = np.full((lead_in_length,), first_close, dtype=dtype)
        windowed_data = np.concatenate((lead_in_data, windowed_data))

    #------------------------------------------------------------------------------------------------------------------
    # bands
    upper_band, lower_band = D_calculate_bollinger_bands(windowed_data, smoothing_window=window_size, num_std=num_std)

    # plot the bollinger
    # debug_graph:debug: [call] debug_graph_strategy.py:
    # [def plot_bollinger_bands(data, window_size=20, num_std=2, recent_window_fraction=1/2, future_estimates=5)]
    if debug and debug_graph:
        window_plot_bollinger_bands(windowed_data,upper_band=upper_band,lower_band=lower_band)
    #------------------------------------------------------------------------------------------------------------------

    # offset=-10 found using debug:debug_graph
    offset = -10

    # Adjust the bands' position using the offset
    upper_band = band_offset(upper_band, offset)
    lower_band = band_offset(lower_band, offset)

    if upper_band is None or lower_band is None:
        if debug:
            print(f'TRUE:upper_band or lower_band is None:')
            print(f'return none')
            print(f'DEBUG:strategy.py:end')
        return "none"

    recent_window_size = int(window_size * recent_window_fraction)
    recent_window_start = window_size - recent_window_size

    if debug:
        print(f'len(windowed_data): {len(windowed_data)}')
        print(f'recent_window_size: {recent_window_size}')
        print(f'recent_window_start: {recent_window_start}')
        print(f'upper_band: {upper_band[-5:]}')
        print(f'lower_band: {lower_band[-5:]}')

    last_upper_crossover, last_lower_crossover = calculate_bollinger_crossovers(windowed_data, upper_band, lower_band,
                                                                                recent_window_fraction)


    if last_upper_crossover is not None and last_upper_crossover >= window_size - recent_window_size:
        if debug:
            print(f'TRUE:last_upper_crossover:')
            print(f'DEBUG:strategy.py:end')
        return "sell"
    elif last_lower_crossover is not None and last_lower_crossover >= window_size - recent_window_size:
        if debug:
            print(f'TRUE:last_lower_crossover:')
            print(f'DEBUG:strategy.py:end')
        return "buy"
    else:
        if debug:
            print(f'TRUE:else:')
            print(f'last_upper_crossover:{last_upper_crossover}')
            print(f'last_lower_crossover:{last_lower_crossover}')
            print(f'DEBUG:strategy.py:end')
        return "none"


def find_engulfing(trade_items):
    engulfing_indices = []

    for i in range(1, len(trade_items)):
        prev_item = trade_items[i - 1]
        curr_item = trade_items[i]

        if (prev_item['c'] < prev_item['o']) and (curr_item['c'] > curr_item['o']) and \
                (curr_item['o'] < prev_item['c']) and (curr_item['c'] > prev_item['o']):
            engulfing_indices.append(i)
        elif (prev_item['c'] > prev_item['o']) and (curr_item['c'] < curr_item['o']) and \
                (curr_item['o'] > prev_item['c']) and (curr_item['c'] < prev_item['o']):
            engulfing_indices.append(i)

    return engulfing_indices


def engulfing(data):
    engulfing_signals = np.zeros(len(data), dtype=int)
    for i in range(1, len(data)):
        current, previous = data[i], data[i - 1]
        if (current['c'] > current['o'] and previous['c'] < previous['o'] and
                current['c'] >= previous['o'] and current['o'] <= previous['c']):
            engulfing_signals[i] = 100
        elif (current['c'] < current['o'] and previous['c'] > previous['o'] and
              current['o'] >= previous['c'] and current['c'] <= previous['o']):
            engulfing_signals[i] = -100
    return engulfing_signals


def doji(data, threshold=0.03):
    doji_signals = np.zeros(len(data), dtype=int)
    for i in range(len(data)):
        price_range = data[i]['h'] - data[i]['l']
        if abs(data[i]['c'] - data[i]['o']) <= price_range * threshold:
            doji_signals[i] = 1
    return doji_signals


def hammer(data, threshold=0.02):
    hammer_signals = np.zeros(len(data), dtype=int)
    for i in range(len(data)):
        body = abs(data[i]['c'] - data[i]['o'])
        total_length = data[i]['h'] - data[i]['l']
        lower_shadow = min(data[i]['c'], data[i]['o']) - data[i]['l']

        if lower_shadow >= body * 2 and (total_length - body) * threshold >= body:
            if data[i]['c'] > data[i]['o']:
                hammer_signals[i] = 100
            else:
                hammer_signals[i] = -100
    return hammer_signals


def analyze_data(data):
    eng_signals = engulfing(data)
    doji_signals = doji(data)
    hammer_signals = hammer(data)
    upper_band, lower_band = D_calculate_bollinger_bands(data)
    upper_crossovers, lower_crossovers = calculate_bollinger_crossovers(data, upper_band, lower_band)

    return eng_signals, doji_signals, hammer_signals, upper_crossovers, lower_crossovers


def band_offset(band_in, offset):
    """
    Apply an offset to a band array.
    :param band_in: Input band array.
    :param offset: Number of steps to offset the band's position.
    :return: Offset band array.
    """
    return np.roll(band_in, offset)