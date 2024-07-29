import sys
import json
from html_analysis import html_analysis  # Assuming the above code is in html_analysis.py


__version__ = "0.0.0001"
print(f'summaries_to_html.py {__version__}')


def main():
    if len(sys.argv) > 1:
        json_file_path = sys.argv[1]  # Path to the trade_summaries.json
    else:
        print("Usage: python summaries_to_html.py <path_to_trade_summaries.json>")
        sys.exit(1)

    # Load trade data from the specified JSON file
    try:
        with open(json_file_path, 'r') as file:
            trade_data = json.load(file)
    except Exception as e:
        print(f"Failed to read or parse the JSON file: {e}")
        sys.exit(1)

    # Process each trade in the JSON data
    for trade in trade_data:
        html_analysis(trade)

if __name__ == "__main__":
    main()
