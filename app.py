import numpy as np
import pandas as pd
import streamlit as st
import datetime
import os
import requests
import json
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool

# Function to download data from alpha vantage api
@st.cache()
def aquire(symbol):
	if len(symbol):
		preurl = "https://www.alphavantage.co/query?function={:s}"
		posturl = "&{:s}={:s}&apikey={:s}&outputsize=full&datatype=csv"
		apikey = os.environ.get("apikey")
		daily_fun = "TIME_SERIES_DAILY"
		search_fun = "SYMBOL_SEARCH"
		url = preurl.format(daily_fun) + posturl.format("symbol", symbol, apikey)
		try:
			df = pd.read_csv(url, parse_dates = ["timestamp"],
					index_col = "timestamp")
			df = df.sort_values("timestamp")
			return df
		except ValueError:
			url = preurl.format(search_fun) + posturl.format("keywords",
					symbol, apikey)
			df = pd.read_csv(url)
			return df
	else:
		return None

# GUI and plotting
symbol = st.sidebar.text_input("Ticker:")
df = aquire(symbol)
if df is not None and "close" in df.columns:
	years = np.arange(df.index.min().year, df.index.max().year + 1)
else:
	years = np.arange(2000, 2020)
# Input
month = np.arange(1, 13)
year = st.sidebar.selectbox("Year:", years)
month = st.sidebar.selectbox("Month:", month)
# Output
st.title("TDI 12-day Milestone project.")
st.caption("Download and display daily close data using Streamlit and Bokeh.")
# Print matched tickers when not found
if df is not None and "symbol" in df.columns:
	st.write("Invalid ticker")
	if len(df):
		items = []
		for i in df.index:
			items.append(df.loc[i, "symbol"] + ' -- ' +
					df.loc[i, "name"])
		output = '\n'.join(items)
		st.write("Best maches:")
		st.text(output)
# Plot the graph
elif df is not None and "close" in df.columns:
	begin = datetime.date(year = year, month = month, day = 1)
	if month < 12:
		end = datetime.date(year = year, month = month + 1, day = 1)
	else:
		end = datetime.date(year = year + 1, month = 1, day = 1)
	end -= datetime.timedelta(days = 1)
	source = ColumnDataSource(df[begin:end].reset_index())
	p = figure(title = "Stock daily close data in a month",
			x_axis_label = "Date",
			y_axis_label = "Close",
			x_axis_type = "datetime",
			height = 300)
	p.line(x = "timestamp", y = "close", source = source)
	p.circle(x = "timestamp", y = "close", color = "red",
			source = source, size = 10)
	hover = HoverTool(tooltips = [
		("Close", "@close{%.2f}"),
		("Date", "@timestamp{%F}")],
		formatters = {"@close": "printf", "@timestamp": "datetime"})
	p.add_tools(hover)
	st.bokeh_chart(p, use_container_width = True)
