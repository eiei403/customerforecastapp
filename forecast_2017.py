import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from tqdm import tqdm
from loadandcleandata import load
from sklearn.metrics import mean_absolute_error

def forecast_2017(progress_callback=None):
    df = load()
    
    df['Month'] = df['YearMonth'].astype(str).str[-2:].astype(int)
    df['year'] = df['YearMonth'].astype(str).str[:4].astype(int)
    df['Lag1'] = df.groupby(['CustomerKey', 'ItemKey'])['InvoiceAmount'].shift(1)
    df['Lag3'] = df.groupby(['CustomerKey', 'ItemKey'])['InvoiceAmount'].shift(3)
    df['Lag6'] = df.groupby(['CustomerKey', 'ItemKey'])['InvoiceAmount'].shift(6)
    df['Lag9'] = df.groupby(['CustomerKey', 'ItemKey'])['InvoiceAmount'].shift(9)
    df['lag_qty_1'] = df.groupby(['CustomerKey', 'ItemKey'])['Quantity'].shift(1)
    df['lag_qty_3'] = df.groupby(['CustomerKey', 'ItemKey'])['Quantity'].shift(3)
    df.dropna(inplace=True)

    df['YearMonth1'] = pd.to_datetime(df['YearMonth'], format='%Y%m').dt.to_period('M')
    df = df.sort_values(['CustomerKey', 'ItemKey', 'YearMonth1'])

    results = []
    test_actual = []
    test_predicted = []

    grouped = df.groupby(['CustomerKey', 'ItemKey'])
    total = len(grouped)

    for i, ((cust_key, item_key), group) in enumerate(grouped):
        if progress_callback:
            progress_callback(i + 1, total, cust_key, item_key)

        if len(group) < 10:
            continue

        train = group[(group['YearMonth1'] >= '2015-01') & (group['YearMonth1'] <= '2016-10')]
        test = group[(group['YearMonth1'] >= '2016-11') & (group['YearMonth1'] <= '2016-12')]

        if len(train) < 6 or test.empty:
            continue

        features = ['Month','year', 'Lag1','Lag3','Lag6','Lag9','lag_qty_1','lag_qty_3']
        X_train = train[features]
        y_train = np.log1p(train['InvoiceAmount'])

        model = XGBRegressor()
        model.fit(X_train, y_train)

        X_test = test[features]
        y_test = test['InvoiceAmount']
        y_pred = np.expm1(model.predict(X_test))

        test_actual.extend(y_test.values)
        test_predicted.extend(y_pred)

        last_rows = group[group['YearMonth1'] <= '2016-12'].copy()
        if last_rows.empty:
            continue
        last_row = last_rows.iloc[-1]

        for month in range(1, 13):
            year = 2017
            yearmonth = f"{year}{month:02d}"
            yearmonth_dt = pd.to_datetime(yearmonth, format="%Y%m")

            def safe_get(arr, idx, fallback):
                return arr.iloc[idx] if len(arr) > abs(idx) else fallback

            X_input = pd.DataFrame([{
                'Month': month,
                'year': year,
                'Lag1': last_row['InvoiceAmount'],
                'Lag3': safe_get(last_rows, -3, last_row)['InvoiceAmount'],
                'Lag6': safe_get(last_rows, -6, last_row)['InvoiceAmount'],
                'Lag9': safe_get(last_rows, -9, last_row)['InvoiceAmount'],
                'lag_qty_1': last_row['Quantity'],
                'lag_qty_3': safe_get(last_rows, -3, last_row)['Quantity']
            }])

            pred_log = model.predict(X_input)[0]
            pred_invoice = np.expm1(pred_log)

            results.append({
                'CustomerKey': cust_key,
                'ItemKey': item_key,
                'YearMonth': yearmonth,
                'ForecastInvoice': pred_invoice
            })

            new_row = {
                'InvoiceAmount': pred_invoice,
                'Quantity': last_row['Quantity'],
                'YearMonth1': yearmonth_dt.to_period('M')
            }
            last_rows = pd.concat([last_rows, pd.DataFrame([new_row])], ignore_index=True)
            last_row = new_row

    forecast_df = pd.DataFrame(results)

    # Accuracy calc
    test_actual = np.array(test_actual)
    test_predicted = np.array(test_predicted)
    mae = mean_absolute_error(test_actual, test_predicted)
    mean_actual = np.mean(test_actual)
    accuracy = max(0, 1 - mae / mean_actual)
    accuracy_percentage = round(accuracy * 100, 2)

    return forecast_df, accuracy_percentage