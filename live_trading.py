import json
import argparse


def load_config(config_path):
    with open(config_path, 'r') as file:
        return json.load(file)


def live_trading(config):
    strategy = config['strategy']
    initial_capital = config['initial_capital']
    risk_management = config['risk_management']
    data_source = config['data_source']

    # Your live trading logic here


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run live trading using a trading strategy.')
    parser.add_argument('--config', type=str, required=True, help='Path to the configuration file.')

    args = parser.parse_args()
    config = load_config(args.config)

    live_trading(config)
