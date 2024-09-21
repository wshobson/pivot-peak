import warnings
from datetime import date, timedelta

import pandas as pd
import pytrendline as ptl
import quantstats as qs
import streamlit as st
import pandas_datareader as pdr

from PIL import Image

from plot import plot_graph_bokeh

warnings.filterwarnings("ignore")

TIINGO_TOKEN = st.secrets["TIINGO_API_KEY"]


def ticker_to_df(symbol, period):
    try:
        today = date.today()
        start = today - timedelta(days=int(period))
        start_date = start.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        ticker_df = pdr.get_data_tiingo(symbol, start=start_date, end=end_date, api_key=TIINGO_TOKEN)
        ticker_df.reset_index(inplace=True)

        ticker_df["Open"] = ticker_df["open"]
        ticker_df["High"] = ticker_df["high"]
        ticker_df["Low"] = ticker_df["low"]
        ticker_df["Close"] = ticker_df["close"]
        ticker_df["Symbol"] = symbol
        ticker_df["Date"] = ticker_df["date"]

        return pd.concat([pd.DataFrame(), ticker_df], ignore_index=True)
    except Exception as e:
        print(f"Error searching {symbol} occured: {e}")
        return pd.DataFrame()


def detect_trendlines(full_df):
    first_must_be_pivot = st.sidebar.checkbox("First point must be a pivot", value=True)
    last_must_be_pivot = st.sidebar.checkbox("Last point must be a pivot", value=True)
    all_must_be_pivots = st.sidebar.checkbox("All points must be pivots", value=True)
    include_global_maxmin_pt = st.sidebar.checkbox("Include global max/min point", value=False)

    candlestick_data = ptl.CandlestickData(
        df=full_df,
        time_interval="1d",  # choose between 1m,3m,5m,10m,15m,30m,1h,1d
        open_col="Open",  # name of the column containing candle "Open" price
        high_col="High",  # name of the column containing candle "High" price
        low_col="Low",  # name of the column containing candle "Low" price
        close_col="Close",  # name of the column containing candle "Close" price
        datetime_col="Date",  # name of the column containing candle datetime price (use none if datetime is in index)
    )

    return ptl.detect(
        candlestick_data=candlestick_data,
        # Choose between BOTH, SUPPORT or RESISTANCE
        trend_type=ptl.TrendlineTypes.BOTH,
        # Specify if you require the first point of a trendline to be a pivot
        first_pt_must_be_pivot=first_must_be_pivot,
        # Specify if you require the last point of the trendline to be a pivot
        last_pt_must_be_pivot=last_must_be_pivot,
        # Specify if you require all trendline points to be pivots
        all_pts_must_be_pivots=all_must_be_pivots,
        # Specify if you require one of the trendline points to be global max or min price
        trendline_must_include_global_maxmin_pt=include_global_maxmin_pt,
        # Specify minimum amount of points required for trendline detection (NOTE: must be at least two)
        min_points_required=3,
        # Specify if you want to ignore prices before some date
        scan_from_date=None,
        # Specify if you want to ignore 'breakout' lines. That is, lines that intersect a candle
        ignore_breakouts=True,
        # Specify and override to default config (See docs on how)
        config={},
    )


def plot_trendlines(results, symbol, period):
    return plot_graph_bokeh(results, symbol, period)


def compute_stock_statistics(symbol, df):
    df.index = pd.DatetimeIndex(df["Date"])
    stock = qs.utils.download_returns(symbol, period=df.index)
    bench = qs.utils.download_returns("SPY", period=df.index)

    return qs.reports.metrics(stock, mode="full", benchmark=bench, display=False)


def st_ui():
    st.set_page_config(page_title="PivotPeak.AI", page_icon="📈", layout="wide")

    logo = Image.open("logo.png")
    st.sidebar.image(logo, width=90, caption="PivotPeak.AI")

    params = st.query_params.get_all("symbol")

    default_symbol = "MSFT"
    if len(params) > 0:
        default_symbol = params[0].upper()

    symbol = st.sidebar.text_input("Enter a stock symbol", default_symbol).upper()

    st.title(f"{symbol} stock trendline detection")

    if symbol == "":
        st.warning("Please enter a stock symbol")
        st.stop()

    period = st.sidebar.slider("Time period for stock price", 10, 730, 252)

    st.sidebar.subheader("Options")

    full_df = ticker_to_df(symbol, period)

    if full_df.empty:
        st.warning("No data found for the symbol")
        st.stop()

    results = detect_trendlines(full_df)
    p = plot_trendlines(results, symbol, period)

    st.bokeh_chart(p, use_container_width=True)

    if st.sidebar.checkbox("View statistics"):
        st.divider()
        st.subheader("Statistics with respect to SPY")

        stats = compute_stock_statistics(symbol, full_df)
        st.table(stats)


if __name__ == "__main__":
    st_ui()
