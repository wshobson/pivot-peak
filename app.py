import streamlit as st
from bokeh.plotting import figure
import yfinance as yf
import bokeh
import pandas as pd
from datetime import date
from datetime import timedelta


def plot_price(symbol, period, ticker_data):
    title = f"{symbol} stock price evolution for the last {period} days"
    p = figure(title=title, x_axis_label="Date", y_axis_label="Opening Price (USD)",
               x_axis_type='datetime', sizing_mode='stretch_both', background_fill_alpha=0)

    today = date.today()
    ticker_df = ticker_data.history(period='1d', start=today - timedelta(days=int(period)), end=today)

    ticker_df["Symbol"] = symbol
    ticker_df["Date"] = ticker_df.index

    p.line(ticker_df["Date"].tolist(), ticker_df["Open"].tolist(), legend_label=symbol, line_width=2, line_color='orange')

    full_df = pd.concat([pd.DataFrame(), ticker_df], ignore_index=True)

    return p, full_df


def st_ui():
    st.set_page_config(layout="wide")
    symbol = st.sidebar.text_input("Enter a symbol", "SPY")
    period = st.sidebar.slider("Time period for stock price plot", 10, 900, 365)

    data = yf.Ticker(symbol)

    st.title(f"Stock price for {symbol} over the last {period} days")

    p, full_df = plot_price(symbol, period, data)
    st.bokeh_chart(p, use_container_width=True)

    st.dataframe(full_df)


if __name__ == "__main__":
    st_ui()
