import streamlit as st
import requests
import plotly.graph_objects as go
import time
import threading

# Replace 'YOUR_API_KEY' with your actual Alpha Vantage API key
API_KEY = 'LTA22U77EPT4MX4T'

def fetch_stock_data(symbol):
    try:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "Time Series (5min)" not in data:
            st.error("Error fetching stock data. Please try again.")
            return None
        
        time_series = data["Time Series (5min)"]
        chart_data = [
            {"time": time, "price": float(values["4. close"])}
            for time, values in time_series.items()
        ]
        chart_data.reverse()  # To ensure the data is in chronological order
        return chart_data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching stock data: {e}")
        return None

def update_chart():
    symbol = st.session_state.symbol
    if symbol.strip():
        stock_data = fetch_stock_data(symbol)
        if stock_data:
            st.session_state.stock_data = stock_data
            st.session_state.show_chart = True
        else:
            st.session_state.show_chart = False
    else:
        st.session_state.show_chart = False

def check_alert(symbol, threshold, email):
    while True:
        stock_data = fetch_stock_data(symbol)
        if stock_data:
            current_price = stock_data[-1]['price']
            if current_price >= threshold:
                # In a real application, you would send an email here
                print(f"Alert: {symbol} has reached {current_price}, which is above the threshold of {threshold}. Notifying {email}")
                break
        time.sleep(300)  # Check every 5 minutes

def main():
    st.title("Stock Price Viewer & Alert System")

    # Initialize session state
    if 'show_chart' not in st.session_state:
        st.session_state.show_chart = False
    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = None
    if 'alerts' not in st.session_state:
        st.session_state.alerts = []

    # Chart placeholder
    chart_placeholder = st.empty()

    # Input for stock symbol
    symbol = st.text_input("Enter stock symbol:", key="symbol", on_change=update_chart)

    # Display chart if data is available
    if st.session_state.show_chart and st.session_state.stock_data:
        with chart_placeholder.container():
            stock_data = st.session_state.stock_data
            st.write(f"**Symbol:** {symbol.strip().upper()}")
            st.write(f"**Price:** ${stock_data[-1]['price']:.2f}")  # Latest price
            st.write(f"**Last Updated:** {stock_data[-1]['time']}")

            # Generate the chart
            fig = go.Figure(
                data=go.Scatter(
                    x=[item['time'] for item in stock_data],
                    y=[item['price'] for item in stock_data],
                    mode='lines',
                    name='Stock Price'
                )
            )
            fig.update_layout(
                title='Stock Price Chart',
                xaxis_title='Time',
                yaxis_title='Price'
            )
            st.plotly_chart(fig)

    # Alert system
    threshold = st.number_input("Set price threshold:", min_value=0.0)
    email = st.text_input("Enter your email for alerts:")

    if st.button("Set Alert"):
        if not symbol.strip() or not email.strip():
            st.error("Please enter a valid stock symbol and email")
        else:
            alert_thread = threading.Thread(target=check_alert, args=(symbol.strip(), threshold, email.strip()))
            alert_thread.start()
            st.session_state.alerts.append({
                "symbol": symbol.strip(),
                "threshold": threshold,
                "email": email.strip()
            })
            st.success("Alert set successfully")

    # Display active alerts
    if st.session_state.alerts:
        st.subheader("Active Alerts")
        for alert in st.session_state.alerts:
            st.write(f"Symbol: {alert['symbol']}, Threshold: {alert['threshold']}, Email: {alert['email']}")

    # Trading parameters form
    st.header("Set Trading Parameters")
    with st.form(key='trading_form'):
        selling_point = st.number_input('Selling Point', min_value=0.0, format="%.2f")
        fixed_loss = st.number_input('Fixed Loss', min_value=0.0, format="%.2f")
        submit_params = st.form_submit_button('Set Parameters')
        if submit_params:
            st.write(f'Selling point set to: {selling_point}')
            st.write(f'Fixed loss set to: {fixed_loss}')

if __name__ == "__main__":
    main()
