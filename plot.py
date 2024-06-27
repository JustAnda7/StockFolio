import os
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import model
# import pandas_datareader.data as web
import yfinance as yf
from sklearn.model_selection import train_test_split
from matplotlib import style
import mplfinance as mpf
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpdates
from statsmodels.tsa.deterministic import CalendarFourier, DeterministicProcess

style.use('ggplot')

def get_historical_data(symbol, start_date, end_date, interval):
  start_t = (start_date)
  end_t = datetime.datetime.now() if datetime.datetime.now() < end_date else end_date
  end_t = (end_date)
  stock = yf.Ticker(symbol)
  hist_data = stock.history(start=start_t, end=end_t, period=interval)
  hist_data = hist_stock_mani(hist_data)
  return hist_data

def hist_stock_mani(hist_data):
  hist_data['Price20ma'] = hist_data['Close'].rolling(window=20, min_periods=0).mean()
  hist_data['Vol20ma'] = hist_data['Volume'].rolling(window=20, min_periods=0).mean()
  hist_data['Price50ma'] = hist_data['Close'].rolling(window=50, min_periods=0).mean()
  hist_data['pct_change'] = ((hist_data['Close'] - hist_data['Open'])/hist_data['Open'])*100
  return hist_data

def feature_engi(hist_data):
  df = hist_data.iloc[:, ['Close']]
  df.index = df.index.to_period("D")
  ma = df['Close'].rolling(window=21, center=False).mean()
  fourier = CalendarFourier(freq="Y", order=10)
  dp = DeterministicProcess(
          index=df.index,
          period=12,
          constant=True,
          order=1,
          seasonal=True,
          additional_terms=[fourier],
          drop=True
        )
  X = dp.in_sample()
  X['trend'] = ma
  X['close'] = df['Close']
  for i in range(1, 7):
    X[f"lag{i}"] = X['close'].shift(i)
  X_test7 = X.iloc[-7:]
  X_test30 = X.iloc[-30:]
  X['pred7'] = X['close'].shift(-7)
  X['pred30'] = X['close'].shift(-30)
  engi_data = X.dropna()
  return {'engi_data':engi_data,'7daytest': X_test7, '30daytest': X_test30}

def prediction(engi_data, X_test7, X_test30, y_hat30):
  lwr = model.LocallyWeightedRegression()
  # y1 = np.array([engi_data['pred7']])
  # y1 = y1.T
  y1 = np.array([engi_data['pred30']])
  y1 = y1.T
  X = np.array(engi_data.drop(['pred7', 'pred30'], axis=1))
  X_test30 = np.array(X_test30)
  y_hat30 = lwr.fit_and_predict(X, y1, X_test30)
  return y_hat30

def plot_line_graph(hist_data, symbol, graph):
  try:
    plt.figure(figsize=(70, 30))
    ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1)
    ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)
    ax1.plot(hist_data.index, hist_data['Close'], color='r')
    ax1.plot(hist_data.index, hist_data['Price20ma'], color='g')
    ax1.plot(hist_data.index, hist_data['Price50ma'], color='b')
    ax2.bar(hist_data.index, hist_data['Volume'], color='b')
    ax2.plot(hist_data.index, hist_data['Vol20ma'], color='r')
    plt.savefig(f"static/graphs/{symbol}.png")
  except:
    graph = False
  
  graph = True

def plot_candlesticks(hist_data, symbol, graph):
  try:
    his = hist_data.drop(['Dividends', 'Stock Splits', 'Price20ma', 'Vol20ma', 'Price50ma'], axis='columns')
    his.reset_index(inplace=True)
    start_date = his['Date'][1]
    end_date = his['Date'][len(his['Date'])-1]
    his['Date'] = pd.to_datetime(his['Date']).map(mpdates.date2num)
    xtik = pd.date_range(start=start_date, end=end_date, freq="W").strftime("%d-%m-%Y")
    plt.figure(figsize=(20,10))
    plt.title("CandleStick Chart")
    ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1)
    ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)
    ax2.set_title("Volume")
    candlestick_ohlc(ax1, his.values, width=0.6, colorup='green', colordown='red', alpha=0.8)
    ax1.plot(hist_data.index, hist_data['Price20ma'], color='g', label="20 Day Moving Average")
    ax1.plot(hist_data.index, hist_data['Price50ma'], color='b', label="50 Day Moving Average")
    ax1.legend()
    ax2.bar(hist_data.index, hist_data['Volume'], color='b', label="Volume (in hundred millions)")
    ax2.plot(hist_data.index, hist_data['Vol20ma'], color='r', label="20 Day moving Average")
    ax2.legend()
    ax1.set_xticks(xtik, xtik, rotation=45)
    ax1.set_ylabel("Price (in local currency)")
    ax2.set_xticks(xtik, xtik, rotation='vertical')
    ax2.set_ylabel("Vol")
    plt.savefig(f"static/graphs/{symbol}.png")
  except:
    graph = False
  
  graph = True  