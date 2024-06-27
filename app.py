import os
import re
import plot
import threading
import mysql.connector
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
host = 'localhost'
user = 'anda'
password = 'password'
database = 'test'

mysql_db = mysql.connector.connect(host = host,
                                user = user,
                                password = password,
                                database = database)

# Make sure API
# if not os.environ.get("API_KEY"):
    # raise RuntimeError("API_KEY not set")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    db = mysql_db.cursor()
    # Get user's current cash
    db.execute("SELECT cash FROM users WHERE id = %s", (session["user_id"],))
    user_cash = db.fetchone()
    user_cash = { "cash" : user_cash[0] }
    # Get the stocks' data user is holding
    db.execute("SELECT symbol, SUM(holdings) as holdings FROM stocks WHERE user_id = %s GROUP BY symbol HAVING (SUM(holdings) > 0)", (session["user_id"],))
    stocks = db.fetchall()
    key_tuple = ("symbol", "holdings")
    for stock in stocks:
        stock = dict(zip(key_tuple, stock))
    # total value of stocks held by user
    total_stock_value = 0
    # update stocks
    for stock in stocks:
        quote = lookup(stock["symbol"])
        stock["name"] = quote["name"]
        stock["price"] = quote["price"]
        stock["total"] = stock["holdings"] * stock["price"]
        total_stock_value += stock["total"]
    # total value of user including cash
    total_cash = total_stock_value + user_cash["cash"] # user_cash + total_s_v is 'int' + 'list' not valid operand
    # user_cash = list, user_cash[0]=dict, user_cash[0]["cash"]=float or int
    return render_template("index.html", stocks=stocks, user_cash=user_cash["cash"], total_cash=total_cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    db = mysql_db.cursor()
    # user arrives via post
    if request.method == "POST":
        symbol = request.form.get("symbol") # which company
        data = lookup(symbol) # lookup through api
        shares = request.form.get("shares") # shares user wants to buy
        db.execute("SELECT cash FROM users WHERE id = %s", (session["user_id"],)) #??? id
        user_cash = db.fetchone()
        user_cash = { "cash" : user_cash[0] }

        if not request.form.get("symbol"):
            return apology("must provide a symbol", 400)

        elif data is None:
            return apology("invalid symbol", 400)

        #try and exception in python
        try:
            shares = int(shares)
            if shares < 1 :
                return apology("enter positive number of shares", 400)
        except ValueError: # valueerror = anything except numbers
            return apology("enter positive number of shares", 400)

        share_price = shares * data["price"]

        date = datetime.now() #??? real time date?

        if user_cash["cash"] < share_price:
            return apology("cash insufficient", 400)
        else:
            # updating the users table to new cash values
            db.execute("UPDATE users SET cash = cash - %s WHERE id = %s", (share_price, session["user_id"])) #???
            # add the transaction to stocks table
            db.execute("INSERT INTO stocks (user_id, symbol, name, holdings, price, tran_date, operation) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                       (session["user_id"],
                        data["symbol"],
                        data["name"],
                        shares,
                        data["price"],
                        date.strftime("%Y-%m-%d %H:%M:%S"), # strftime is function under datetime imported
                        "buy",
                        ))
            mysql_db.commit()
            #flash message to user
            flash("Bought Successfully!")
            return redirect("/")
    # user arrives via get request
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    db = mysql_db.cursor()
    # get the data from transaction table
    db.execute("SELECT * FROM stocks WHERE user_id = ?", (session["user_id"],))
    stocks = db.fetchall()
    key_tuple = ('user_id', 'symbol', 'name', 'holdings', 'price', 'tran_date', 'operation')
    for stock in stocks:
        stock = dict(zip(key_tuple, stock))
    return render_template("history.html", stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    db = mysql_db.cursor()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        db.execute("SELECT * FROM users WHERE username = %s", (request.form.get("username"),))
        rows = db.fetchone()
        rows = {'id': rows[0], 'user': rows[1], 'hash': rows[2], 'cash' : rows[3]}

        # Ensure username exists and password is correct
        if rows and not (rows["hash"] == request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # USer reached via POST route
    if request.method == "POST":

        # Ensure that symbol is provided
        if not request.form.get("symbol"):
            return apology("missing symbol", 400)

        #lookup the current statstics and store in a dict
        quote = lookup(request.form.get("symbol"))

        # Check if the quote exists
        if quote is None:
            return apology("invalid symbol", 400)
        # IF exists print the values of the symbol
        else:
            return render_template("quoted.html", name=quote["name"], symbol=quote["symbol"], price=quote["price"])

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    db = mysql_db.cursor()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        db.execute("SELECT * FROM users WHERE username = %s", (username,))
        row = db.fetchone()
        # row = {'id': row[0], 'user': row[1], 'hash': row[2], 'cash' : row[3]}
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Check if user already registered
        elif row:
            return apology("already registed",403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 403)

        # Ensure confirmation = password
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("re-enter the password", 403)

        # Password Restriction using regex
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$"
        conf = re.search(re.compile(reg), request.form.get("password"))

        if not conf:
            return apology("invalid password", 403)

        # Add the user if no problems
        db.execute("INSERT INTO users (username,hash) VALUES (%s,%s)", (request.form.get("username"), request.form.get("password")))
        mysql_db.commit()

        # Redirect user to homepage
        return redirect("/")

    # if user comes via get request allow the user to register
    else:
        flash("Password must contain atleast One Uppercase, One Lowercase and One Number between 0 and 9")
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    db = mysql_db.cursor()
    # user arrives via post
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        data = lookup(symbol)

        if not symbol:
            return apology("must provide a symbol", 400)

        try:
            shares = int(shares)
            if shares < 1:
                return apology("enter positive number of shares", 400)
        except ValueError: # valueerror = anything except numbers
            return apology("enter positive number of shares", 400)

        db.execute("SELECT SUM(holdings) as holdings FROM stocks WHERE user_id = %s AND symbol = %s",
                    (session["user_id"],
                     data["symbol"])
                    )
        stocks = db.fetchall()
        stocks = { 'holdings': stocks[0] }
        date = datetime.now()

        if shares > stocks["holdings"]: # Typeerror ??
            return apology("no of shares are more than owned", 400)
        else:
            # updating the users table to new cash values
            db.execute("UPDATE users SET cash = cash + %s WHERE id = %s", ((data["price"] * shares), session["user_id"]))
            # add the transaction to stocks table
            db.execute("INSERT INTO stocks (user_id, symbol, name, holdings, price, tran_date, operation) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (session["user_id"],
                        data["symbol"],
                        data["name"],
                        -shares,
                        data["price"],
                        date.strftime("%Y-%m-%d %H:%M:%S"), # strftime is function under datetime imported but why not working??
                        "sell",
                        ))

            #flash message to user
            flash("Sold Successfully!")
            return redirect("/")
    # user arrives via get request
    else:
         db.execute("SELECT symbol FROM stocks WHERE user_id = ? GROUP BY symbol",(session["user_id"],))
         stocks = db.fetchall()
         for stock in stocks:
            stock = dict(zip(('symbol',), stock))
         return render_template("sell.html", stocks=stocks)

@app.route("/graph", methods=["GET", "POST"])
@login_required
def plot_graph():
    graph = False
    if request.method == "POST":
        symbol = request.form.get("symbol")
        y_hat30 = []
        start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
        end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")
        interval = request.form.get("interval")
        stock_data = plot.get_historical_data(symbol, start_date, end_date, interval)
        pred_data = plot.feature_engi(stock_data)
        th1 = threading.Thread(target=plot.prediction, args=(pred_data['engi_data'], pred_data['30daytest'], y_hat30))
        th2 = threading.Thread(target=plot.plot_candlesticks, args=(stock_data, symbol, graph,))
        th1.start()
        th2.start()
        url = f"static/graphs/{symbol}.png"
        day30pred = y_hat30[-1]
        day7pred = y_hat30[-23]
        return render_template("graph.html", graph=graph, url=url, symbol=symbol, day30pred=day30pred, day7pred=day7pred)
    else:
        return render_template("graph.html", graph=graph)