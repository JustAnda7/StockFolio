import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
# import pandas_datareader.data as web
import yfinance as yf
from matplotlib import style
import mplfinance as mpf
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpdates

style.use('ggplot')

def get_historical_data(symbol, start_date, end_date, interval):
  start_t = str(int(start_date.timestamp()))
  end_t = datetime.datetime.now() if datetime.datetime.now() < end_date else end_date
  end_t = str(int(end_date.timestamp()))
  # interval = interval
  # events = 'history'
  # includeAdjClose = 'true'
  # url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start_t}&period2={end_t}&interval={interval}&events={events}&includeAdjustedClose={includeAdjClose}"
  stock = yf.Ticker(symbol)
  hist_data = stock.history(start=start_t, end=end_t, period=interval)
  # df = pd.read_csv(url)
  hist_data = hist_stock_mani(hist_data)
  return hist_data

def hist_stock_mani(hist_data):
  hist_data['Price20ma'] = hist_data['Close'].rolling(window=20, min_periods=0).mean()
  hist_data['Vol20ma'] = hist_data['Volume'].rolling(window=20, min_periods=0).mean()
  hist_data['Price50ma'] = hist_data['Close'].rolling(window=50, min_periods=0).mean()
  return hist_data

def plot_line_graph(hist_data, symbol):
  plt.figure(figsize=(70, 30))
  ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1)
  ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)
  ax1.plot(hist_data.index, hist_data['Close'], color='r')
  ax1.plot(hist_data.index, hist_data['Price20ma'], color='g')
  ax1.plot(hist_data.index, hist_data['Price50ma'], color='b')
  ax2.bar(hist_data.index, hist_data['Volume'], color='b')
  ax2.plot(hist_data.index, hist_data['Vol20ma'], color='r')
  plt.savefig(os.path.join('static', 'graphs', f"{symbol}.png"))
  return True

def plot_candlesticks(hist_data, symbol):
  his = hist_data.drop(['Dividends', 'Stock Splits', 'Price100ma', 'Vol20ma', 'Price50ma'], axis='columns')
  his.reset_index(inplace=True)
  his['Date'] = pd.to_datetime(his['Date']).map(mpdates.date2num)
  plt.figure(figsize = (70,30))
  ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1)
  ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)
  candlestick_ohlc(ax1, his.values, width=0.6, colorup='green', colordown='red', alpha=0.8)
  ax1.plot(hist_data.index, hist_data['Price20ma'], color='g')
  ax1.plot(hist_data.index, hist_data['Price50ma'], color='b')
  ax2.bar(hist_data.index, hist_data['Volume'], color='b')
  ax2.plot(hist_data.index, hist_data['Vol20ma'], color='r')
  plt.savefig(os.path.join('static', 'graphs', f"{symbol}.png"))
  return True  