# ai_risk_management_III.py 
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from collections import deque


class AI_RISK_RollingWindow:
    """
    We attempt to manage Buy/Sell Wager Confidence.
    We can possible benefit from wager confidence using 2 AI models combined to generate confidence levels.
    LR :{Buy/Hold/Sell}
    RF :{Buy/Hold/Sell}
    If mitigator wants to open
    [Sell position:]
    LR:Sell & RF:Sell = tier [1]

    LR:Sell & RF:Hold = tier [2]
    LR:Hold & RF:Sell = tier [2]

    LR:Hold & RF:Hold = tier [3]

    LR:Buy & RF:Sell = tier [4]
    LR:Sell & RF:Buy = tier [4]

    LR:Buy & RF:Buy = tier [5]

    [Buy position:]
    LR:Buy & RF:Buy = tier [1]

    LR:Buy & RF:Hold = tier [2]
    LR:Hold & RF:Buy = tier [2]

    LR:Hold & RF:Hold = tier [3]

    LR:Buy & RF:Sell = tier [4]
    LR:Sell & RF:Buy = tier [4]

    LR:Sell & RF:Sell = tier [5]
    """

    def __init__(self, window_size=30):
        self.window_size = window_size
        self.data_windows = {}

    def add_pair(self, pair):
        if pair not in self.data_windows:
            self.data_windows[pair] = deque(maxlen=self.window_size)

    def update_pair(self, pair, date, open_price, close_price, high_price, low_price):
        if pair in self.data_windows:
            self.data_windows[pair].append({
                'Date': date,
                'Open': open_price,
                'Close': close_price,
                'High': high_price,
                'Low': low_price
            })
        else:
            raise ValueError(f"Pair '{pair}' not found in the data windows.")

    def _get_window_data(self, pair):
        if pair in self.data_windows and len(self.data_windows[pair]) == self.window_size:
            window_df = pd.DataFrame(list(self.data_windows[pair]))
            feature_df = self.create_time_windows(window_df, self.window_size)
            return feature_df
        else:
            return pd.DataFrame()  # Return an empty DataFrame if the window is not yet full

    def get_window_data(self, pair):
        if pair in self.data_windows:
            return pd.DataFrame(list(self.data_windows[pair]))
        else:
            raise ValueError(f"Pair '{pair}' not found in the data windows.")

    def create_time_windows(self, data, window_size):
        rolling_windows = data[['Open', 'Close', 'High', 'Low']].rolling(window=window_size)
        features = rolling_windows.mean().shift(1)  # Example feature, can add more
        data = data.join(features, rsuffix='_feature')
        data.bfill(inplace=True)  # Fill NaNs with the next valid observation
        data.dropna(inplace=True)  # Ensure no NaNs remain
        return data


def preprocess_data(data, feature_names=None):
    if 'Date' in data.columns:
        dates = data['Date']
        data = data.drop(columns='Date')
    else:
        dates = None

    if feature_names is not None:
        data = data[feature_names]  # Reorder and filter columns to match the feature names

    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)
    data_scaled = pd.DataFrame(data_scaled, columns=data.columns)  # Convert back to DataFrame with feature names

    return data_scaled, dates


def make_prediction(model, data, feature_names):
    if data.empty:
        return [0]  # Return a default value or handle empty case as needed

    data_scaled, _ = preprocess_data(data, feature_names)
    return model.predict(data_scaled)


def make_prediction_with_dates(model, data, feature_names):
    if data.empty:
        raise ValueError("No data available for prediction")

    data_scaled, dates = preprocess_data(data, feature_names)
    predictions = model.predict(data_scaled)
    if dates is not None:
        return list(zip(dates, predictions))
    else:
        return predictions


def keep_predict_RandomForestClassifier(data):
    if 'Date' in data.columns:
        dates = data['Date']
        data = data.drop(columns='Date')
    if 'Close_feature' in data.columns:
        data = data.drop(columns='Close')
    if 'High_feature' in data.columns:
        data = data.drop(columns='High')
    if 'Low_feature' in data.columns:
        data = data.drop(columns='Low')
    if 'Open_feature' in data.columns:
        data = data.drop(columns='Open')

    if 'Close_feature' in data.columns:
        data = data.rename(columns={
            'Open_feature': 'Open',
            'Close_feature': 'Close',
            'High_feature': 'High',
            'Low_feature': 'Low'
        })

    X = data.drop('Label', axis=1)
    print(X.info())
    print(X.head())
    print(X.columns)
    y = data['Label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print(classification_report(y_test, predictions))
    return model, X.columns


def predict_RandomForestClassifier(data, feature_names, debug=False):
    if 'Date' in data.columns:
        dates = data['Date']
        data = data.drop(columns='Date')
    if 'Close_feature' in data.columns:
        data = data.rename(columns={
            'Open_feature': 'Open',
            'Close_feature': 'Close',
            'High_feature': 'High',
            'Low_feature': 'Low'
        })

    X = data[feature_names]
    y = data['Label']

    if debug:
        print(X.info())
        print(X.head())
        print(X.columns)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print(classification_report(y_test, predictions))
    return model, data.columns


def load_and_process_data(file_name, invert_data=False, scale_data=True):
    data = pd.read_csv(file_name)

    if 'Date' in data.columns:
        dates = data['Date']  # Preserve the dates
        data = data.drop(columns='Date')  # Drop the date column before scaling

    if invert_data:
        data = data.iloc[::-1].reset_index(drop=True)

    if scale_data:
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(data)
        data = pd.DataFrame(data_scaled, columns=data.columns)  # Convert back to DataFrame

    if 'Date' in data.columns:
        data['Date'] = dates.reset_index(drop=True)

    return data


def calculate_labels(data, window_size, label_length, min_change_pct):
    future_price = data['Close'].shift(-(window_size + label_length))
    pct_change = (future_price - data['Close']) / data['Close'] * 100
    data['Label'] = 0  # Default to no significant change
    data.loc[pct_change >= min_change_pct, 'Label'] = 1  # Positive significant change
    data.loc[pct_change <= -min_change_pct, 'Label'] = -1  # Negative significant change
    data.dropna(inplace=True)
    return data


def create_time_windows(data, window_size):
    rolling_windows = data.rolling(window=window_size)
    features = rolling_windows.mean().shift(1)  # Example feature, can add more
    return features


def create_datasets(file_name, window_size=35, label_length=5, min_change_pct=1.0, debug=False):
    data = load_and_process_data(file_name)
    data = calculate_labels(data, window_size, label_length, min_change_pct)
    features = create_time_windows(data[['Open', 'Close', 'High', 'Low']], window_size)
    data = data.join(features, rsuffix='_feature')
    data.dropna(inplace=True)  # Drop rows with NaN values
    if debug:
        print('ALL DATA SETS')
        print(data.head())
    return data


def train_model(model, data, test_size=0.2, feature_name_explicit=True, feature_rename=True, debug=False):
    if feature_rename:
        if 'Close_feature' in data.columns:
            data = data.rename(columns={
                'Close_feature': 'Close',
                'Open_feature': 'Open',
                'High_feature': 'High',
                'Low_feature': 'Low'
            })

    X = data[[col for col in data.columns if col != 'Label']]
    y = data['Label']

    if debug: print(X.head())
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model.fit(X_train_scaled, y_train)

    if feature_name_explicit:
        model.feature_names_in_ = X.columns  # Explicitly set the feature names

    y_pred = model.predict(X_test_scaled)

    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("Accuracy Score:", accuracy_score(y_test, y_pred))
    print("Classification Report:\n", classification_report(y_test, y_pred))

    return X.columns  # Return feature names used for training


def predict_model(data):
    X = data[[col for col in data.columns if '_feature' in col]]
    y = data['Label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print(classification_report(y_test, predictions))


def textify_yp(yps, debug=False):
    ret_str = []
    last_yp = ''

    for yp in yps:
        if yp == 1:
            ret_str.append('Buy')
        elif yp == -1:
            ret_str.append('Sell')
        else:
            ret_str.append('Hold')
    if debug: print(ret_str)
    last_yp = ret_str[-1]
    return last_yp

def main():
    # Idea Demo
    print(f'LogisticRegression')
    lr_model = LogisticRegression()

    # Train models and store feature names
    data = create_datasets('AUDJPY_data_corrected.csv', min_change_pct=6.0)
    lr_features = train_model(lr_model, data)

    data = create_datasets('AUDUSD_data_corrected.csv', min_change_pct=6.0)
    lr_features = train_model(lr_model, data)

    data = create_datasets('EURUSD_data_corrected.csv', min_change_pct=6.0)
    lr_features = train_model(lr_model, data)

    data = create_datasets('GBPUSD_data_corrected.csv', min_change_pct=6.0)
    lr_features = train_model(lr_model, data)

    data = create_datasets('AUDJPY_data_corrected.csv', min_change_pct=5.0)
    lr_features = train_model(lr_model, data)

    data = create_datasets('AUDUSD_data_corrected.csv', min_change_pct=5.0)
    lr_features = train_model(lr_model, data)

    data = create_datasets('EURUSD_data_corrected.csv', min_change_pct=5.0)
    lr_features = train_model(lr_model, data)

    data = create_datasets('GBPUSD_data_corrected.csv', min_change_pct=5.0)
    lr_features = train_model(lr_model, data)

    print(f'Random Forest')
    print('Old')
    data = create_datasets('NZDUSD_data_corrected.csv', min_change_pct=5.0)
    rf_model, rf_features = keep_predict_RandomForestClassifier(data)

    print('New')
    data = create_datasets('AUDJPY_data_corrected.csv', min_change_pct=5.0)
    predict_RandomForestClassifier(data, rf_features)

    print(f'LogisticRegression')
    # RollingWindows
    pairs = ['EURUSD', 'USDJPY', 'GBPUSD', 'AUDUSD', 'NZDUSD']  # Currency pairs
    rolling_window = AI_RISK_RollingWindow(window_size=35)

    # Add pairs to the rolling window
    for pair in pairs:
        rolling_window.add_pair(pair)

    # Initialize with enough initial data points to fill the window
    initial_data = {
        'Date': '2024-04-01',
        'Open': np.random.random(),
        'Close': np.random.random(),
        'High': np.random.random(),
        'Low': np.random.random()
    }

    for _ in range(rolling_window.window_size):
        for pair in pairs:
            rolling_window.update_pair(pair, initial_data['Date'], initial_data['Open'], initial_data['Close'],
                                       initial_data['High'], initial_data['Low'])

    # Simulate incoming data updates
    for _ in range(5000):
        SIM_DEMO_ALL = True
        print('-')
        for pair in pairs:
            new_data = {
                'Date': '2024-04-01',
                'Open': np.random.random(),
                'Close': np.random.random(),
                'High': np.random.random(),
                'Low': np.random.random()
            }
            rolling_window.update_pair(pair, new_data['Date'], new_data['Open'], new_data['Close'], new_data['High'],
                                       new_data['Low'])
            # Data is same for both LR & RF
            lr_window_data = rolling_window.get_window_data(pair)
            rf_window_data = rolling_window.get_window_data(pair)

            if not rf_window_data.empty:
                print('LR')
                prediction = make_prediction(lr_model, lr_window_data, lr_features)
                print('RF')
                rf_prediction = make_prediction(rf_model, rf_window_data, rf_features)
                if SIM_DEMO_ALL:
                    print(f"Prediction at step {_} for {pair}: LR:{textify_yp(prediction)}  RF:{textify_yp(rf_prediction)}")
                else:
                    if pair == 'GBPUSD':
                        print(
                            f"Prediction at step {_} for {pair}: LR:{textify_yp(prediction)}   RF:{textify_yp(rf_prediction)}")
            else:
                print(f"No data available for prediction at step {_} for {pair}")

if __name__ == "__main__":
    main()