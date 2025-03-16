# import pymysql

# pymysql.install_as_MySQLdb()

# connection = pymysql.connect(
#   host='localhost',
#   user='anda',
#   password='password',
#   database='test'
# )

# cursor = connection.cursor()

# cursor.execute('SELECT VERSION()')
# version = cursor.fetchone()
# print(version)
import yfinance as yf
import time
def lookup():
  stock = yf.Ticker("AAPL")
  try:
    time.sleep(1)
    print(stock.info)
  except Exception as e:
    print(e)
  # print(stock.info)

lookup()