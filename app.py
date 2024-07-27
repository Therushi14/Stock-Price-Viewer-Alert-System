import streamlit as st
import requests

def main():
    st.title("Stock Price Viewer & Alert System")

    # Input for stock symbol and alert threshold
    symbol = st.text_input("Enter stock symbol:")
    threshold = st.number_input("Set price threshold:", min_value=0.0)
    email = st.text_input("Enter your email for alerts:")

    # Button to set an alert
    if st.button("Set Alert"):
        if not symbol.strip() or not email.strip():
            st.error("Please enter a valid stock symbol and email")
            return
        
        alert_data = {
            "symbol": symbol.strip(),
            "threshold": threshold,
            "email": email.strip()
        }

        try:
            response = requests.post('http://localhost:3000/set-alert', json=alert_data)
            response.raise_for_status()
            st.success("Alert set successfully")
        except requests.exceptions.RequestException as e:
            st.error(f"Error setting alert: {e}")

    # Button to fetch stock data
    if st.button("Fetch Stock Data"):
        if not symbol.strip():
            st.error("Please enter a valid stock symbol")
            return

        try:
            response = requests.get(f'http://localhost:3000/stock/{symbol.strip()}')
            response.raise_for_status()
            data = response.json()

            st.write(f"**Symbol:** {data.get('symbol', 'N/A')}")
            st.write(f"**Price:** ${data.get('price', 'N/A'):.2f}")
            st.write(f"**Last Updated:** {data.get('lastUpdated', 'N/A')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching stock data: {e}")

if __name__ == "__main__":
    main()
