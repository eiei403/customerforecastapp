from config import fetch_forecast_from_mssql
import pandas as pd

def load():
    df = fetch_forecast_from_mssql()
    df = df.dropna(subset=['ItemKey','SalesRepKey'])
    df['ItemKey'] = df['ItemKey'].astype('Int64').astype(str)
    df = df[df['CurrencyCode'].isin(['USD', 'EUR', 'INR'])]
    eur_to_usd = 1.1
    inr_tousd = 0.012
    df.loc[df['CurrencyCode'] == 'EUR', 'InvoiceAmount'] *= eur_to_usd
    df.loc[df['CurrencyCode'] == 'INR', 'InvoiceAmount'] *= inr_tousd
    df['CurrencyCode'] = 'USD'
    df['YearMonth'] = pd.to_datetime(df['InvoiceDate'], format = '%Y%M')
    
    # Drop rows where 'ItemKey' is missing
    # df = df.dropna(subset=['ItemKey'])

    # Group by (CustomerKey, ItemKey, YearMonth) to create time series
    monthly_sales = df.groupby(['CustomerKey', 'ItemKey', 'YearMonth']).agg({
        'InvoiceAmount': 'sum',
        'Quantity': 'sum'
    }).reset_index()

    return monthly_sales