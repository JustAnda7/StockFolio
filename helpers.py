import requests
# from bs4 import BeautifulSoup
import yfinance as yf

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    return render_template("apology.html", top=code, bottom=message), code


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    # Contact API
    # try:
    #     # api_key = os.environ.get("API_KEY")
    #     url = f"https://finance.yahoo.com/quote/{symbol}"
    #     # url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
    #     response = requests.get(url)
    #     response.raise_for_status()
    # except requests.RequestException:
    #     return None

    # # Parse response
    # try:
    #     soup = BeautifulSoup(response.text, 'html.parser')
    #     stock_info = {}
    #     stock = soup.find('h1', { 'class':'svelte-3a2v0c' })
    #     stock_info['name'], stock_info['symbol'] = stock.text.split('(')[0], stock.text.split('(')[1] 
    #     priceinfo = soup.find('div', { 'class': 'container svelte-mgkamr'}).find_all('fin-streamer')
    #     stock_info['price'], stock_info['change'], stock_info['pct_change'] = float(priceinfo[0].text), float(priceinfo[1].text), float(priceinfo[2].text[1:-2])

    #     return stock_info
    # except (KeyError, TypeError, ValueError):
    #     return None
    stock = yf.Ticker(symbol.strip())
    data = {
        "name": stock.info["longName"],
        "symbol": stock.info["symbol"],
        "price": stock.info["currentPrice"]
    }
    return data


def usd(value):
    """Format value as USD."""
    return f"${value:.2f}"
