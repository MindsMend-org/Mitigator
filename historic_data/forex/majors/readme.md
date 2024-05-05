We have from 2019-01-open to 2023-12-close for the following:[historic forex data 7 Majors @ 1M]

EUR/USD (Euro/US Dollar)
USD/JPY (US Dollar/Japanese Yen)
GBP/USD (British Pound/US Dollar)
USD/CHF (US Dollar/Swiss Franc)
AUD/USD (Australian Dollar/US Dollar)
USD/CAD (US Dollar/Canadian Dollar)
NZD/USD (New Zealand Dollar/US Dollar)

You can access historical forex data from several sources:
Broker platforms: Some brokers offer historical forex data directly.
Financial data services: Sites like OANDA, Investing.com, and MetaTrader often have downloadable data.
APIs and Market Data Providers: Platforms like Alpha Vantage, FXCM, and Quandl provide APIs that let you query and download historic data.

# Alphavantage
https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=EUR&to_symbol=USD&interval=1min&apikey=YOUR_API_KEY

# OANDA via requests/V20/& legacy oandav20
using requests api
access_token = "ccIIIcIIIIIcIIIcIcccIcIIcIcIcIIc-IIIcIcIIccIccIIIcIcIIIIcIIIcIcII"
    headers = {'Authorization': f'Bearer {access_token}'}
    account_id = "III-III-IIIIIIII-III"
    currency_pairs = ['EUR_USD', 'USD_JPY', 'GBP_USD', 'AUD_USD', 'USD_CAD', 'USD_CHF', 'NZD_USD']
    instruments = ','.join(currency_pairs)
    url = f"https://api-fxpractice.oanda.com/v3/accounts/{account_id}/pricing?instruments={instruments}"
    if response.status_code == 200:
                data = response.?

# yfinance Assuming you are fetching data that can be serialized to JSON
import yfinance as yf
data = yf.download(tickers='EURUSD=X', period='1d', interval='5m')
