# Introduction

StockFolio is a user-friendly stock portfolio management application where the user can view buy and sell stocks of interest. It is a Flask Web Application displayed using HTML, CSS and Javascript which utilises MySQL to store
information regarding the user, the portfolio and the transactions. The application also provides weekly and monthly prediction about the price of a stock in the portfolio using machine learning algorithms.

## Local Installation

You can fork this repository or clone it on your local machine with `git clone https://github.com/JustAnda7/StockFolio.git`

## Running the application

Note - Requires a stable version of Python3 installed and MySQL database configured on the local machine. Running MySQL in a container is also an option.

- `cd StockFolio`
- `python -m venv .venv`
- `source ./.venv/bin/activate`
- `pip install -r requirements.txt`
- `FLASK_ENV=development flask run`

## Future Development Prospects

- Containerizing the application using Docker and Kubernetes.
- Incorporating different ML models and techniques to make better forecasts.

### Misc

Feel free to test the application and report any bugs or issues with the application. Also always open for suggestions and improvements about the application.
The Frontend of the application is still under development, so sorry for the look of the website.
