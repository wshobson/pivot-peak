import warnings
from datetime import date, timedelta

import mplfinance as mpf
import pandas as pd
import pytrendline as ptl
import quantstats as qs
import streamlit as st
import yfinance as yf
from PIL import Image
from pandas_datareader import data as pdr
from streamlit.components.v1 import html

from plot import plot_graph_bokeh

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
    first_must_be_pivot = st.sidebar.checkbox('First point must be a pivot', value=True)
    last_must_be_pivot = st.sidebar.checkbox('Last point must be a pivot', value=True)
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
    params = st.experimental_get_query_params()

    logo = Image.open('logo.png')
    st.set_page_config(page_title="PivotPeak.AI", page_icon="📈", layout="wide")

    st.sidebar.image(logo, width=90, caption="PivotPeak.AI")

    if "symbol" in params:
        symbol = params["symbol"][0].upper()
    else:
        symbol = st.sidebar.text_input("Enter a stock symbol", "MSFT").upper()

    st.title(f"{symbol} stock trendline detection")

    if symbol == "":
        st.warning("Please enter a stock symbol")
        st.stop()

    period = st.sidebar.slider("Time period for stock price", 10, 730, 252)

    st.sidebar.subheader('Options')

    full_df = ticker_to_df(symbol, period)

    if full_df.empty:
        st.warning("No data found for the symbol")
        st.stop()

    results = detect_trendlines(full_df)
    p = plot_trendlines(results, symbol, period)

    st.bokeh_chart(p, use_container_width=True)

    if st.sidebar.checkbox('View statistics'):
        st.divider()
        st.subheader('Statistics with respect to SPY')

        stats = compute_stock_statistics(symbol, full_df)
        st.table(stats)

    with st.sidebar:
        button = """
        <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="fc4mDv55wG" data-color="#FFDD00" data-emoji="" data-font="Bree" data-text="Buy me a coffee" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>
        """

        html(button, height=70, width=260)

        st.markdown(
            """
            <style>
                iframe[width="260"] {
                    position: fixed;
                    bottom: 0;
                    margin-bottom: 40px;
                    -ms-zoom: 0.60;
                    -moz-transform: scale(0.60);
                    -moz-transform-origin: 0 0;
                    -o-transform: scale(0.60);
                    -o-transform-origin: 0 0;
                    -webkit-transform: scale(0.60); 
                    -webkit-transform-origin: 0 0;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    st_ui()
