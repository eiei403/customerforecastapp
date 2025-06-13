import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
from loadandcleandata import load
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

def evaluate_model(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    variance = np.var(y_true)

    print(f"MSE: {mse:.2f}")
    print(f"MAE: {mae:.2f}")
    print(f"R2 Score: {r2:.2f}")
    print(f"Variance (y_true): {variance:.2f}")
    
    return {
        'mse': mse,
        'mae': mae,
        'r2': r2,
        'variance': variance
    }

def plot_forecast():
    df = load()
    
    df = df.groupby('YearMonth', as_index=False)['InvoiceAmount'].sum()
    df['ds'] = pd.to_datetime(df['YearMonth'], format='%Y%m')
    df = df[['ds', 'InvoiceAmount']].rename(columns={'InvoiceAmount': 'y'})
    df.dropna(inplace=True)

    df['dayofweek'] = df['ds'].dt.dayofweek
    df['day'] = df['ds'].dt.day
    df['month'] = df['ds'].dt.month
    df['year'] = df['ds'].dt.year

    train = df[(df['ds'] >= '2015-01-01') & (df['ds'] <= '2016-10-31')]
    test = df[(df['ds'] >= '2016-11-01') & (df['ds'] <= '2016-12-31')]

    features = ['dayofweek', 'day', 'month', 'year']
    X_train = train[features]
    y_train = train['y']
    X_test = test[features]
    y_test = test['y']

    model = xgb.XGBRegressor(n_estimators=100)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_pred = np.maximum(0, y_pred)

    y_pred_df = pd.DataFrame({
        'ds': test['ds'].values,
        'y': y_pred
    })

    future_dates = pd.date_range(start='2017-01-01', end='2017-06-30')
    future_df = pd.DataFrame({'ds': future_dates})
    future_df['dayofweek'] = future_df['ds'].dt.dayofweek
    future_df['day'] = future_df['ds'].dt.day
    future_df['month'] = future_df['ds'].dt.month
    future_df['year'] = future_df['ds'].dt.year

    X_future = future_df[features]
    y_future = model.predict(X_future)
    y_future = np.maximum(0, y_future)

    future_pred_df = pd.DataFrame({
        'ds': future_df['ds'],
        'y': y_future
    })

    # ✅ Correct way to plot and return figure
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(test['ds'], y_test, label='Actual', color='black', alpha=0.5)
    ax.plot(y_pred_df['ds'], y_pred_df['y'], label='XGBoost Prediction (Test)', color='blue', marker='o')
    ax.plot(future_pred_df['ds'], future_pred_df['y'], label='Forecast 2017', color='red', linestyle='--')

    ax.set_title('Actual vs Predicted vs Forecast (XGBoost)')
    ax.set_xlabel('Date')
    ax.set_ylabel('y')
    ax.legend()
    ax.grid(True)
    fig.tight_layout()

    return fig
