# Mitigator
The Beginnings of a Reinforcement Trade Bot For Forex Majors/Minors Aim to be working for 2025. xMx
I am working out git convention lol
Im new to python, I like to code in Psudo fasion it will likely be messy sorry.

# code of interest trading signals/experimentals
https://colab.research.google.com/drive/1a7bhdGPq-Z9uLX1P7b4lpzWD5ZDqzU8R?usp=sharing


# ToDo:
- Implement the new AI risk management, be interesting to see how the compounded effect of conviction[High, Med, Low] has on Profit .
- Implement Mitigation stack and Control for Deep Learn.
- Implement Live Demo test using Oandas Live Demo.
-  
- New - Thread issue - bug >if crash with errors video not initiated,

- most likely bank empty or ran to end of data>setting game.is_over == True
  
   The main.py  Loop
    [while not game.is_over():]
  
  IF conditions met >.is_over =True
  It will crash-out, with message >graphics/video not initiated
  
## [Sim]

Incorperate the Data I finally aquired (8 years history of all majors) @ 1 min

# Switch From Day to 1M est [Sept]

# Enable Mitigator   est [OCT]
## [Live]
Add config to allow any Live account and update rate, not sure python be any good at time below 1M
Bank/open/close all straight calls 



### Activate the Mitigation AI system:
#### Choose sensors 
- [Parallel All Pairs]
- [Serial Single]
- [Dist to Mean]
- [ Max&Min[4] [12] [132] [17292]]-17440

- 
Design Modes [Learn] [Active] [Active & Learn] [Dissable]

### Make use of configs.
On startup, make use of user config files to determin modes/rules.

## Document All the parts in detail.
main.py

-

## Document all the parts and command line options.
[]
[]
[]
[]

-


## Document Live Link To API of choice.
[]
[]
[]
[]

# Mitigator Project

Mitigator is a comprehensive trading bot designed to execute and analyze trades based on a predefined strategy, With the Ability to Mitigate!. This project includes features for backtesting, live trading, and detailed analysis of trading performance.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Last Run](#last-run)

## Features

- **Automated Trading**: Execute trades automatically based on predefined strategies.
- **Backtesting**: Test trading strategies on historical data.
- **Performance Analysis**: Generate detailed reports and visualizations of trading performance.
- **Trade History Management**: Store and manage trade history in JSON format.
- **Mitigation**: Deep learn Mitigation of incorrect opening of posistion.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/MindsMend-org/mitigator.git
   cd mitigator


## Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
## Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage
Can be Run Debug mode Using Main.py

Backtesting:

To perform backtesting, run the following command:
```bash
python backtest.py --config config/backtest_config.json
```

Live Trading:

For live trading, use the following command:
```bash
python live_trading.py --config config/live_trading_config.json
```

Analyzing Trade History/Summaries:

To analyze trade history and generate visualizations, use:
```bash
python analyze_trade_history.py --file trade_history.json
```

To analyze trade summaries and generate visualizations, use:
```bash
python analyze_trade_summaries.py --file trade_summaries.json
```
### For speed removed html_analysis.py from running in SIM/Live.
To convert trade summaries into html graphs, use:
```bash
python summaries_to_html.py  trade_summaries.json
```


##Configuration
The project uses JSON configuration files to manage different settings for backtesting and live trading. Sample configuration files are provided in the config directory.

Example Configuration
```json
{
  "strategy": "mean_reversion",
  "initial_capital": 100000,
  "risk_management": {
    "stop_loss": 0.02,
    "take_profit": 0.05
  },
  "data_source": "historical_data.csv"
}
```

##WIP When A Complete Working Version is Available, Feel Free Send Me Some Of Our Rewards X

ETH:
0x581b91d5751eb77142694E9770f5984f857e2B84


DODGE:
0x581b91d5751eb77142694E9770f5984f857e2B84



TRX:
TT9aMi9JdYQQUj6unE3ddT7pxPyjcWqcw1



BTC:
bc1qnmycts7xdlzgesf0vwmm940psdvuejrc9grru2


## Last Run
Analysis
The analysis of trade history includes visualizations of the cumulative profit over time, profit/loss distribution, and trade performance metrics.

Cumulative Profit Over Time [if used simulation mode then 5 mins = about 3 months ]
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/MindsMend-org/Mitigator/blob/main/analysis/cumulative_profit_over_time.png?raw=true">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/MindsMend-org/Mitigator/blob/main/analysis/cumulative_profit_over_time.png?raw=true">
  <img alt="Cumulative Profit Over Time" src="https://github.com/MindsMend-org/Mitigator/blob/main/analysis/cumulative_profit_over_time.png?raw=true">
</picture>
Profit/Loss Distribution
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/MindsMend-org/Mitigator/blob/main/analysis/profit_loss_distribution.png?raw=true">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/MindsMend-org/Mitigator/blob/main/analysis/profit_loss_distribution.png?raw=true">
  <img alt="Profit/Loss Distribution" src="https://github.com/MindsMend-org/Mitigator/blob/main/analysis/profit_loss_distribution.png?raw=true">
</picture>
Trade Duration Distribution
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/MindsMend-org/Mitigator/blob/main/analysis/trade_duration_distribution.png?raw=true">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/MindsMend-org/Mitigator/blob/main/analysis/trade_duration_distribution.png?raw=true">
  <img alt="Profit/Loss Distribution" src="https://github.com/MindsMend-org/Mitigator/blob/main/analysis/trade_duration_distribution.pngg?raw=true">
</picture>
Trade Performance Metrics
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/MindsMend-org/Mitigator/blob/main/analysis/Trade_performance_metrics.png?raw=true">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/MindsMend-org/Mitigator/blob/main/analysis/Trade_performance_metrics.png?raw=true">
  <img alt="Trade Performance Metrics" src="https://github.com/MindsMend-org/Mitigator/blob/main/analysis/Trade_performance_metrics.png?raw=true">
</picture>

# Open Modes [M_bands/Mean Reversion]
- % of Bank 
- AI position wager [AI risk management] (Involves AI determining how much of one's bankroll or investment capital to risk on a particular trade)

# -- add
- Random Open
- Hammer / Engulf

[Read the detailed trade analysis report](./trade_analysis_report.html)



> Part Of Folding-Circles
