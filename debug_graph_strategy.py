import numpy as np
import matplotlib.pyplot as plt

__version__ = "0.0.001"
print(f'debug_graph_strategy.py {__version__}')


def D_calculate_bollinger_bands(data, smoothing_window=20, num_std=2):
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


def plot_bollinger_bands(data, window_size=20, num_std=2, recent_window_fraction=1/2, future_estimates=5):
    """
    Plot the Bollinger Bands, closing prices, and detected crossovers.
    :param data: Forex Pair Data.
    :param window_size: Number of periods for the moving average.
    :param num_std: Number of standard deviations for the bands.
    :param recent_window_fraction: Fraction of the window to consider for recent crossovers.
    :param future_estimates: Number of future estimates to include.
    """
    current_step = len(data)

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

    upper_band, lower_band = D_calculate_bollinger_bands(windowed_data, smoothing_window=window_size, num_std=num_std)
    last_upper_crossover, last_lower_crossover = calculate_bollinger_crossovers(windowed_data, upper_band, lower_band, recent_window_fraction)

    # Plotting
    plt.figure(figsize=(14, 7))
    plt.plot(windowed_data['c'], label='Closing Prices', color='blue')
    plt.plot(upper_band, label='Upper Bollinger Band', color='red')
    plt.plot(lower_band, label='Lower Bollinger Band', color='green')

    # Mark crossovers
    if last_upper_crossover is not None:
        plt.axvline(x=last_upper_crossover, color='orange', linestyle='--', label='Last Upper Crossover')
    if last_lower_crossover is not None:
        plt.axvline(x=last_lower_crossover, color='purple', linestyle='--', label='Last Lower Crossover')

    plt.legend(loc='best')
    plt.title('Bollinger Bands and Closing Prices')
    plt.xlabel('Time Steps')
    plt.ylabel('Price')
    plt.grid(True)
    plt.show()


def band_offset(band_in, offset):
    """
    Apply an offset to a band array.
    :param band_in: Input band array.
    :param offset: Number of steps to offset the band's position.
    :return: Offset band array.
    """
    return np.roll(band_in, offset)

def window_plot_bollinger_bands(windowed_data, upper_band, lower_band, window_size=20, num_std=2, recent_window_fraction=1/2, future_estimates=5, offset=-10):
    """
    Plot the Bollinger Bands, closing prices, and detected crossovers.
    :param windowed_data: Structured array containing 'o', 'h', 'l', 'c' (open, high, low, close prices).
    :param upper_band: Calculated upper Bollinger Band.
    :param lower_band: Calculated lower Bollinger Band.
    :param window_size: Number of periods for the moving average.
    :param num_std: Number of standard deviations for the bands.
    :param recent_window_fraction: Fraction of the window to consider for recent crossovers.
    :param future_estimates: Number of future estimates to include.
    """
    current_step = len(windowed_data)

    # Adjust the bands' position using the offset
    upper_band = band_offset(upper_band, offset)
    lower_band = band_offset(lower_band, offset)

    # Plotting
    plt.figure(figsize=(14, 7))
    plt.plot(windowed_data['c'], label='Closing Prices', color='blue')
    plt.plot(upper_band, label='Upper Bollinger Band', color='red')
    plt.plot(lower_band, label='Lower Bollinger Band', color='green')

    last_upper_crossover, last_lower_crossover = calculate_bollinger_crossovers(windowed_data, upper_band, lower_band, recent_window_fraction)

    # Mark crossovers
    if last_upper_crossover is not None:
        plt.axvline(x=last_upper_crossover, color='orange', linestyle='--', label='Last Upper Crossover')
    if last_lower_crossover is not None:
        plt.axvline(x=last_lower_crossover, color='purple', linestyle='--', label='Last Lower Crossover')

    plt.legend(loc='best')
    plt.title('Bollinger Bands and Closing Prices')
    plt.xlabel('Time Steps')
    plt.ylabel('Price')
    plt.grid(True)
    plt.show()





# Example usage
if __name__ == "__main__":
    # Example data (replace this with real data)
    example_data = [
        {'open': 1.0, 'high': 1.2, 'low': 0.8, 'close': 1.1},
        {'open': 1.1, 'high': 1.3, 'low': 0.9, 'close': 1.2},
        {'open': 1.2, 'high': 1.4, 'low': 1.0, 'close': 1.3},
        {'open': 1.3, 'high': 1.5, 'low': 1.1, 'close': 1.4},
        {'open': 1.4, 'high': 1.6, 'low': 1.2, 'close': 1.5},
        {'open': 1.5, 'high': 1.7, 'low': 1.3, 'close': 1.6},
        {'open': 1.6, 'high': 1.8, 'low': 1.4, 'close': 1.7},
        {'open': 1.7, 'high': 1.9, 'low': 1.5, 'close': 1.8},
        {'open': 1.8, 'high': 2.0, 'low': 1.6, 'close': 1.9},
        {'open': 1.9, 'high': 2.1, 'low': 1.7, 'close': 2.0},
        {'open': 2.0, 'high': 2.2, 'low': 1.8, 'close': 2.1},
        {'open': 2.1, 'high': 2.3, 'low': 1.9, 'close': 2.2},
        {'open': 2.2, 'high': 2.4, 'low': 2.0, 'close': 2.3},
        {'open': 2.3, 'high': 2.5, 'low': 2.1, 'close': 2.4},
        {'open': 2.4, 'high': 2.6, 'low': 2.2, 'close': 2.5},
        {'open': 2.5, 'high': 2.7, 'low': 2.3, 'close': 2.6},
        {'open': 2.6, 'high': 2.8, 'low': 2.4, 'close': 2.7},
        {'open': 2.7, 'high': 2.9, 'low': 2.5, 'close': 2.8},
        {'open': 2.8, 'high': 3.0, 'low': 2.6, 'close': 2.9},
        {'open': 2.9, 'high': 3.1, 'low': 2.7, 'close': 3.0},
        {'open': 3.0, 'high': 3.2, 'low': 2.8, 'close': 3.1},
        {'open': 3.1, 'high': 3.3, 'low': 2.9, 'close': 3.2},
        {'open': 3.2, 'high': 3.4, 'low': 3.0, 'close': 3.3},
        {'open': 3.3, 'high': 3.5, 'low': 3.1, 'close': 3.4},
        {'open': 3.4, 'high': 3.6, 'low': 3.2, 'close': 3.5},
    ]

    plot_bollinger_bands(example_data)
