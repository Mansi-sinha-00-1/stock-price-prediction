import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import plotly.graph_objects as go
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')   # ✅ use non-GUI backend
import matplotlib.pyplot as plt
import logging

# Set up logger
logger = logging.getLogger(__name__)

# ------------------------------
# Fetch stock data using yfinance
# ------------------------------ 
def fetch_stock_data(ticker, period='1y'):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            return None, "No data found for this ticker."
        return df, None
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}")
        return None, f"Error fetching data: {str(e)}"

# ------------------------------
# Prepare data for prediction (safe)
# ------------------------------
def prepare_data(df, forecast_days=30):
    df = df[['Close']].copy()
    df['Prediction'] = df['Close'].shift(-forecast_days)

    # ✅ Check: enough rows?
    if len(df) <= forecast_days:
        return None, None, None, forecast_days, "Not enough data for the given forecast days."

    X = np.array(df.drop(['Prediction'], axis=1))[:-forecast_days]
    y = np.array(df['Prediction'])[:-forecast_days]

    return X, y, df, forecast_days, None

# ------------------------------
# Train Linear Regression model
# ------------------------------
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model, X_test, y_test

# ------------------------------
# Make future predictions
# ------------------------------
def make_predictions(model, df, forecast_days):
    x_forecast = np.array(df.drop(['Prediction'], axis=1))[-forecast_days:]
    y_pred = model.predict(x_forecast)

    # Create future date index
    last_date = df.index[-1]
    future_dates = pd.date_range(last_date, periods=forecast_days + 1)[1:]

    predictions = pd.DataFrame({
        'Date': future_dates,
        'Predicted_Close': y_pred
    }).set_index('Date')

    return predictions

# ------------------------------
# Generate Plotly chart
# ------------------------------
def generate_plotly_chart(actual_df, predicted_df, ticker):
    fig = go.Figure()

    # Actual data
    fig.add_trace(go.Scatter(
        x=actual_df.index,
        y=actual_df['Close'],
        mode='lines',
        name='Actual Price',
        line=dict(color='blue')
    ))

    # Predicted data
    fig.add_trace(go.Scatter(
        x=predicted_df.index,
        y=predicted_df['Predicted_Close'],
        mode='lines',
        name='Predicted Price',
        line=dict(color='red', dash='dash')
    ))

    fig.update_layout(
        title=f'{ticker} Stock Price Prediction',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_white',
        hovermode='x unified'
    )

    return fig.to_html(full_html=False)

# ------------------------------
# Generate Matplotlib chart
# ------------------------------
def generate_matplotlib_chart(actual_df, predicted_df, ticker):
    plt.figure(figsize=(12, 6))
    plt.plot(actual_df.index, actual_df['Close'], label='Actual Price', color='blue')
    plt.plot(predicted_df.index, predicted_df['Predicted_Close'],
             label='Predicted Price', color='red', linestyle='--')

    plt.title(f'{ticker} Stock Price Prediction')
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.legend()
    plt.grid(True)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    return base64.b64encode(buffer.read()).decode('utf-8')

# ------------------------------
# Main processing pipeline (safe)
# Always returns: df, fig, chart, error
# ------------------------------
def process_stock_data(ticker, period='1y', forecast_days=30, chart_type='plotly'):
    # 1. Fetch data
    df, error = fetch_stock_data(ticker, period)
    if error:
        return None, None, None, error

    # 2. Prepare data safely
    X, y, df, forecast_days, prep_error = prepare_data(df, forecast_days)
    if prep_error:
        return None, None, None, prep_error

    # 3. Final safe check
    if X is None or y is None or len(X) == 0 or len(y) == 0:
        return None, None, None, "Not enough data after preparation to train the model."

    # 4. Train model
    model, X_test, y_test = train_model(X, y)

    # 5. Predict
    predictions = make_predictions(model, df, forecast_days)

    # 6. Generate chart
    if chart_type == 'plotly':
        chart = generate_plotly_chart(df, predictions, ticker)
    else:
        chart = generate_matplotlib_chart(df, predictions, ticker)

    # 7. Combine for CSV
    combined_df = pd.concat([
        df[['Close']].rename(columns={'Close': 'Actual_Close'}),
        predictions.rename(columns={'Predicted_Close': 'Predicted_Close'})
    ], axis=1)

    return combined_df, None, chart, None
