import numpy as np

def D_calculate_bollinger_bands(windowed_data, smoothing_window=20, num_std=2):
    close_prices = windowed_data['c']
    rolling_mean = np.convolve(close_prices, np.ones(smoothing_window) / smoothing_window, mode='valid')
    rolling_std = np.zeros_like(rolling_mean)

    for i in range(len(rolling_mean)):
        start_idx = max(0, i - smoothing_window + 1)
        end_idx = i + 1
        rolling_std[i] = np.std(close_prices[start_idx:end_idx])

    upper_band = np.concatenate((rolling_mean[:1], rolling_mean + num_std * rolling_std))
    lower_band = np.concatenate((rolling_mean[:1], rolling_mean - num_std * rolling_std))

    return upper_band, lower_band

def calculate_bollinger_crossovers(data, upper_band, lower_band):
    upper_band_crossovers = []
    lower_band_crossovers = []

    for i in range(1, min(len(data), len(upper_band), len(lower_band))):
        if data['c'][i] > upper_band[i] and data['c'][i - 1] <= upper_band[i - 1]:
            upper_band_crossovers.append(i)
        elif data['c'][i] < lower_band[i] and data['c'][i - 1] >= lower_band[i - 1]:
            lower_band_crossovers.append(i)

    return upper_band_crossovers, lower_band_crossovers

def get_trade_signal(data, window_size=20, num_std=2):
    if len(data) < window_size:
        return "none"

    # Extract fields and create a structured array
    dtype = [('o', 'f8'), ('h', 'f8'), ('l', 'f8'), ('c', 'f8')]
    windowed_data = np.array(
        [(item['open'], item['high'], item['low'], item['close']) for item in data[-window_size:]],
        dtype=dtype
    )

    upper_band, lower_band = D_calculate_bollinger_bands(windowed_data, smoothing_window=window_size, num_std=num_std)
    upper_crossovers, lower_crossovers = calculate_bollinger_crossovers(windowed_data, upper_band, lower_band)

    if upper_crossovers:
        return "sell"
    elif lower_crossovers:
        return "buy"
    else:
        return "none"

def _calculate_bollinger_crossovers(data, upper_band, lower_band):
    upper_band_crossovers = []
    lower_band_crossovers = []

    for i in range(1, min(len(data), len(upper_band), len(lower_band))):
        if data['c'][i] > upper_band[i] and data['c'][i - 1] <= upper_band[i - 1]:
            upper_band_crossovers.append(i)
        elif data['c'][i] < lower_band[i] and data['c'][i - 1] >= lower_band[i - 1]:
            lower_band_crossovers.append(i)

    return upper_band_crossovers, lower_band_crossovers

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
