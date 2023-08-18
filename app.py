import warnings
import streamlit as st
import yfinance as yf
import pandas as pd
from pandas_datareader import data as pdr
import pytrendline as ptl
from datetime import date, timedelta
from plot import plot_graph_bokeh
import mplfinance as mpf
import quantstats as qs

yf.pdr_override()

warnings.filterwarnings("ignore")


def ticker_to_df(symbol, period):
    today = date.today()
    start_date = today - timedelta(days=int(period))
    ticker_df = pdr.get_data_yahoo(symbol, start=start_date, end=today, threads=False)

    ticker_df["Symbol"] = symbol
    ticker_df["Date"] = ticker_df.index

    return pd.concat([pd.DataFrame(), ticker_df], ignore_index=True)


def detect_trendlines(full_df):
    first_must_be_pivot = st.sidebar.checkbox('First point must be pivot', value=True)
    last_must_be_pivot = st.sidebar.checkbox('Last point must be pivot', value=True)
    all_must_be_pivots = st.sidebar.checkbox('All points must be pivots', value=True)
    include_global_maxmin_pt = st.sidebar.checkbox('Include global max/min point', value=False)

    candlestick_data = ptl.CandlestickData(
        df=full_df,
        time_interval="1d",  # choose between 1m,3m,5m,10m,15m,30m,1h,1d
        open_col="Open",  # name of the column containing candle "Open" price
        high_col="High",  # name of the column containing candle "High" price
        low_col="Low",  # name of the column containing candle "Low" price
        close_col="Close",  # name of the column containing candle "Close" price
        datetime_col="Date"  # name of the column containing candle datetime price (use none if datetime is in index)
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
        config={}
    )


def plot_trendlines(results, symbol, period):
    return plot_graph_bokeh(results, symbol, period)


def plot_graph(symbol, period):
    chart_df = ticker_to_df(symbol, period)
    chart_df.index = pd.DatetimeIndex(chart_df['Date'])

    sma_period_1 = st.sidebar.slider('SMA 1 period', min_value=5, max_value=500, value=50, step=1)
    sma_period_2 = st.sidebar.slider('SMA 2 period', min_value=5, max_value=500, value=200, step=1)

    fig, ax = mpf.plot(
        chart_df,
        title=f'{symbol}',
        type='ohlc_bars',
        show_nontrading=False,
        mav=(int(sma_period_1), int(sma_period_2)),
        volume=True,
        figsize=(15, 10),

        # Need this setting for Streamlit, see source code (line 778) here:
        # https://github.com/matplotlib/mplfinance/blob/master/src/mplfinance/plotting.py
        returnfig=True
    )

    st.pyplot(fig)


def compute_stock_statistics(symbol, df):
    df.index = pd.DatetimeIndex(df['Date'])
    stock = qs.utils.download_returns(symbol, period=df.index)
    bench = qs.utils.download_returns('SPY', period=df.index)

    return qs.reports.metrics(stock, mode='full', benchmark=bench, display=False)


def st_ui():
    st.set_page_config(layout="wide")
    symbol = st.sidebar.text_input("Enter a symbol", "QQQ").upper()

    if symbol == "":
        st.warning("Please enter a symbol")
        st.stop()

    period = st.sidebar.slider("Time period for stock price", 10, 900, 365)

    st.title(f"{symbol} trendline detection")
    st.sidebar.subheader('Options')

    full_df = ticker_to_df(symbol, period)

    if full_df.empty:
        st.warning("No data found for the symbol")
        st.stop()

    results = detect_trendlines(full_df)
    p = plot_trendlines(results, symbol, period)
    st.bokeh_chart(p, use_container_width=True)

    # st.subheader("Stock price data")
    # plot_graph(symbol, period, data)

    if st.sidebar.checkbox('View statistics'):
        st.subheader('Statistics with respect to SPY')
        stats = compute_stock_statistics(symbol, full_df)
        st.table(stats)


if __name__ == "__main__":
    st_ui()
