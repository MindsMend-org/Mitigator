# M@FC 2024
# dataframe_validator.py

import pandas as pd

def validate_and_correct_data(file_path):
    """
    Validate chronology and high < low
    :param file_path:
    :return:df, corrected_file_path
    """
    # Load the data from CSV
    df = pd.read_csv(file_path)

    # Check and reverse the DataFrame if dates are in descending order
    if pd.to_datetime(df['Date']).iloc[0] > pd.to_datetime(df['Date']).iloc[-1]:
        df = df.iloc[::-1].reset_index(drop=True)
        print(f"Data in {file_path} reversed to chronological order.")

    # Validate and correct the data
    invalid_rows = df[df['High'] < df['Low']]
    if not invalid_rows.empty:
        print(f"Found invalid rows in {file_path}:")
        print(invalid_rows)

        # Correcting data: assuming a simple correction by swapping High and Low
        df.loc[df['High'] < df['Low'], ['High', 'Low']] = df.loc[df['High'] < df['Low'], ['Low', 'High']].values

    # Save the corrected data back to CSV
    corrected_file_path = file_path.replace('.csv', '_corrected.csv')
    df.to_csv(corrected_file_path, index=False)
    print(f"Corrected data saved to {corrected_file_path}")

    return df, corrected_file_path