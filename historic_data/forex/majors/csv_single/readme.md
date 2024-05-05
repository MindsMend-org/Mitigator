# Forex Data for Mitigation Training

## Overview

This repository contains a file named `forex_data.csv`, which is used for training Mitigation on historical forex data. The dataset includes data from the seven major currency pairs:

- EUR/USD (Euro/US Dollar)
- USD/JPY (US Dollar/Japanese Yen)
- GBP/USD (British Pound/US Dollar)
- USD/CHF (US Dollar/Swiss Franc)
- AUD/USD (Australian Dollar/US Dollar)
- USD/CAD (US Dollar/Canadian Dollar)
- NZD/USD (New Zealand Dollar/US Dollar)

The data spans from **2019-01-01T22:00:00** to **2023-12-29T21:57** and loops back to **2019-01-01T22:00:00** at the end.

## Purpose

The `forex_data.csv` file is used exclusively for training Mitigation strategies, adhering to a "one file" policy for consistent training. This dataset enables Mitigation to be trained not only during live or simulated runs but also on historical datasets, potentially sourced from external providers such as Kaggle or private data services.

## File Usage

- **Training:** This file is solely for training purposes, helping to improve the performance of Mitigation algorithms.
- **Live and Simulation Data:** Separate files will be needed for live trading and simulation to represent any tradable item on any market, allowing Mitigation to adapt to various scenarios effectively.

## Data Structure

The `forex_data.csv` file contains the following columns:

1. **Timestamp:** The date and time of the data point.
2. **Pair:** Currency pair (e.g., EUR/USD).
3. **Open:** The opening price at the timestamp.
4. **High:** The highest price during the timestamp period.
5. **Low:** The lowest price during the timestamp period.
6. **Close:** The closing price at the end of the timestamp period.
7. **Volume:** The trading volume.

## Next Steps

1. **Download and Prepare the Data:** Make sure you have the correct `forex_data.csv` file ready for training Mitigation.
2. **Train Mitigation:** Follow the instructions to train Mitigation using the dataset.

## Notes on Data Synchronization

Due to the method used to gather data, some timestamps might drift slightly in seconds. All pairs will temporarily be adjusted to become sequential.

## Contact

For inquiries or support, please reach out via [mince@foldingcircles.co.uk] or open an issue in this repository.
