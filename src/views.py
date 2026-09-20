import json
import os

from config import DATA_DIR
from src.utils import (
    calculate_expenses,
    calculate_incomes,
    get_currency_rates,
    get_date_range,
    get_stocks_prices,
    get_transactions,
    split_transactions,
    transform_date,
)


def views_main():
    """Return a complete list of all transactions and exchange rates."""
    print("Hello! Welcome to the banking transactions management program.")
    print("Enter the date in the format YYYY-MM-DD from which transactions will be searched.")
    while True:
        date = input("Enter the date: ")
        try:
            transformed_date = transform_date(date)
            break
        except ValueError:
            print("Wrong Date Format")

    print("Enter the date range to search transactions, W, M, Y or ALL:")
    while True:
        range_type = input("Enter the range: ").upper()
        try:
            date_range = get_date_range(transformed_date, range_type)
            break
        except ValueError:
            print("Wrong Range Type")


    got_transactions = get_transactions(
        date_range[0],
        date_range[1],
        os.path.join(DATA_DIR, "operations.csv"),
    )

    plus, minus = split_transactions(got_transactions)
    expenses_calc = calculate_expenses(minus)
    incomes_calc = calculate_incomes(plus)


    print("Do you want to get the current currency rates? (yes/no)")
    while True:
        whether_currencies = input("Enter yes or no: ").capitalize()
        if whether_currencies == "Yes":
            print("Enter the currencies for which you want to get exchange rates:")
            while True:
                user_input_currencies = input("Enter currencies: ").upper()
                try:
                    if "," in user_input_currencies:
                        user_currencies_splitted = user_input_currencies.split(", ")
                    else:
                        user_currencies_splitted = [user_input_currencies]
                    got_currencies_rates = get_currency_rates(user_currencies_splitted)
                    break
                except AttributeError:
                    print("Please enter an existing currency.")
            break
        elif whether_currencies == "No":
            got_currencies_rates = []
            break
        else:
            print("Please enter yes or no.")

    print("Do you want to get the current stock prices? (yes/no)")
    while True:
        whether_stocks = input("Enter yes or no: ").capitalize()
        if whether_stocks == "Yes":
            print("Enter the stocks for which you want to get prices:")
            while True:
                user_input_stocks = input("Enter stocks: ").upper()
                try:
                    if "," in user_input_stocks:
                        user_stocks_splitted = user_input_stocks.split(", ")
                    else:
                        user_stocks_splitted = [user_input_stocks]
                    got_stocks_prices = get_stocks_prices(user_stocks_splitted)
                    break
                except ValueError:
                    print("Please enter an existing stock.")
            break
        elif whether_stocks == "No":
            got_stocks_prices = []
            break
        else:
            print("Please enter yes or no.")

    response = {}
    response["expenses"] = expenses_calc
    response["incomes"] = incomes_calc
    response["currency_rates"] = got_currencies_rates
    response["stock_prices"] = got_stocks_prices
    print("Displaying desired data")
    return response
