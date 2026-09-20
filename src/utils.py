import json
import logging
import re

import math
import os
from collections import defaultdict
from datetime import datetime, date, time, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

from config import DATA_DIR, LOGS_DIR

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    filename=os.path.join(LOGS_DIR, "views.log"),
    filemode="w",
    encoding="utf-8",
)

transform_date_logger = logging.getLogger("app.views.transform_date")
get_range_logger = logging.getLogger("app.views.get_range")
get_transactions_logger = logging.getLogger("app.views.get_transactions")
split_transactions_logger = logging.getLogger("app.views.split_transactions")
calculate_expenses_logger = logging.getLogger("app.views.calculate_expenses")
calculate_incomes_logger = logging.getLogger("app.views.calculate_incomes")
get_currency_rates_logger = logging.getLogger("app.views.get_currency_rates")
get_stock_prices_logger = logging.getLogger("app.views.get_stock_rates")

pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def transform_date(date_str: str) -> datetime:
    """Transform string date to datetime format"""
    if pattern.match(date_str):
        date = datetime.strptime(date_str, "%Y-%m-%d")
        date_object = datetime.combine(date, time.max)
        transform_date_logger.info("Transform date to datetime format")
        return date_object

    transform_date_logger.error("Wrong date format")
    raise ValueError("Wrong date format")


def get_date_range(date: datetime, range_type: str = "M") -> list[datetime]:
    """Define the boundaries of the time range depending on range_type"""
    if range_type == "W":
        start_date = date - timedelta(days=date.weekday())
        end_date = date
        get_range_logger.info("Range W")

    elif range_type == "M":
        start_date = date.replace(day=1)
        end_date = date
        get_range_logger.info("Range M")

    elif range_type == "Y":
        start_date = date.replace(month=1, day=1)
        end_date = date
        get_range_logger.info("Range Y")

    elif range_type == "ALL":
        end_date = datetime(2018, 1, 1)
        end_date = datetime.combine(date, time.max)
        get_range_logger.info("Whole payment history up to the selected date")
    else:
        get_range_logger.error("Wrong Range Type")
        raise ValueError()
    return [start_date, end_date]


def normalize_value(value):
    """Transform unfitting values to python format"""
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    return value


def get_transactions(start_date: datetime, end_date: datetime, path: str) -> list[dict]:
    """Output transactions for specified dates"""
    operations = pd.read_csv(path)
    operations["Дата операции"] = operations["Дата операции"].apply(
        lambda row: datetime.strptime(row, "%d.%m.%Y %H:%M:%S")
    )
    operations_filtered = operations[
        (operations["Дата операции"] >= start_date) & (operations["Дата операции"] <= end_date)
    ]

    if not operations_filtered.empty:
        get_transactions_logger.info("Outputting transactions for specified dates")
        transactions = operations_filtered.to_dict(orient="records")
        normalized = []
        for operation in transactions:
            norm_row = {key: normalize_value(value) for key, value in operation.items()}
            normalized.append(norm_row)
        return normalized
    else:
        get_transactions_logger.error("No transactions for specified dates found")
        return []


def split_transactions(transactions: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split transactions to expenses and incomes"""
    plus_transactions = []
    minus_transactions = []

    for operation in transactions:
        operation["Сумма операции"] = float(operation["Сумма операции"].replace(",", "."))
        if float(operation.get("Сумма операции", "")) > 0:
            split_transactions_logger.info("Income")
            plus_transactions.append(operation)
        elif float(operation.get("Сумма операции", "")) < 0:
            split_transactions_logger.info("Expense")
            minus_transactions.append(operation)

    return plus_transactions, minus_transactions


def calculate_expenses(expenses: list[dict]):
    """Return expenses grouped by category, including cash withdrawals."""
    expenses_totals = []
    category_sums = defaultdict(float)

    for expense in expenses:
        amount = abs(expense.get("Сумма операции", 0))
        expenses_totals.append(amount)
        category = expense.get("Категория", "")
        category_sums[category] += amount
    all_categories = [{"category": cat, "amount": round(amt, 2)} for cat, amt in category_sums.items()]
    calculate_expenses_logger.info("Creating a list of expenses for each category")

    sorted_category_expenses = sorted(all_categories, key=lambda x: x["amount"], reverse=True)
    calculate_expenses_logger.info("Sorting expenses by category in descending order")

    cash_categories_list = []
    cash_amount = 0
    cash_categories = ["Наличные", "Переводы"]
    main_categories = [
        category for category in sorted_category_expenses if category.get("category", "") not in cash_categories
    ][:6]
    rest_categories = sorted_category_expenses[7:]
    rest_totals = sum(cat["amount"] for cat in rest_categories)
    calculate_expenses_logger.info("Splitting expenses into main and remaining categories")

    categories_count = 0
    for cat in rest_categories:
        categories_count += 1

    for category in sorted_category_expenses:
        if category["category"] in cash_categories:
            cash_amount += category["amount"]
            cash_categories_list.append({"category": category["category"], "amount": cash_amount})
    calculate_expenses_logger.info("Recording cash and transfer expenses separately")

    if categories_count > 0:
        main_categories.append({"category": "Остальное", "amount": rest_totals})
        result = {
            "total_amount": round(sum(expenses_totals), 2),
            "main": main_categories,
            "transfers_and_cash": cash_categories_list,
        }
        calculate_expenses_logger.info(
            'Returning a JSON response with expenses grouped by category and cash, including the "Остальное" section'
        )
    else:
        result = {
            "total_amount": round(sum(expenses_totals), 2),
            "main": main_categories,
            "transfers_and_cash": cash_categories_list,
        }
        calculate_expenses_logger.info(
            'Returning a JSON response with expenses grouped by category and cash, without the "Остальное" section'
        )
    return result


def calculate_incomes(incomes: list[dict]):
    """Return incomes grouped by category as a JSON-compatible dictionary."""
    incomes_totals = []
    category_sums = defaultdict(float)

    for income in incomes:
        amount = income.get("Сумма операции", 0)
        incomes_totals.append(amount)
        category = income.get("Категория", "")
        category_sums[category] += amount
    all_categories = [{"category": cat, "amount": amt} for cat, amt in category_sums.items()]
    calculate_incomes_logger.info("Creating a list of incomes for each category")

    sorted_category_incomes = sorted(all_categories, key=lambda x: x["amount"], reverse=True)
    calculate_incomes_logger.info("Sorting incomes by category")

    main_categories = sorted_category_incomes[:6]
    rest_categories = sorted_category_incomes[7:]
    rest_totals = sum(item["amount"] for item in rest_categories)
    calculate_incomes_logger.info("Splitting incomes into main and remaining categories")

    categories_count = 0
    for cat in rest_categories:
        categories_count += 1

    if categories_count > 0:
        sorted_category_incomes.append({"category": "Остальное", "amount": rest_totals})
        result = {"total_amount": sum(incomes_totals), "main": main_categories}
        calculate_incomes_logger.info(
            'Returning a JSON response with incomes grouped by category, including the "Остальное" section'
        )
    else:
        result = {"total_amount": sum(incomes_totals), "main": main_categories}
        calculate_incomes_logger.info(
            'Returning a JSON response with incomes grouped by category, without the "Остальное" section'
        )
    return result


def get_currency_rates(currencies: list):
    """Return a list of exchange rates for the selected currencies."""
    rates = []
    load_dotenv()
    headers = {"apikey": os.getenv("API_KEY_CURRENCIES")}

    bases = currencies
    get_currency_rates_logger.info("Loading data for the selected currencies from the configuration file")

    for base in bases:
        response = requests.get(
            f"https://api.apilayer.com/exchangerates_data/latest?base={base}&symbols=RUB",
            headers,
        )
        content = response.json()
        get_currency_rates_logger.info("Exchange rates received as a JSON response")

        rate = round(content.get("rates", "").get("RUB", ""), 2)
        rates.append({"currency": base, "rate": rate})

        get_currency_rates_logger.info("Exchange rate data added to the response")

    return rates


def get_stocks_prices(stocks: list):
    """Return a list of prices for the selected stocks."""

    tickers = stocks
    load_dotenv()
    prices = []

    get_stock_prices_logger.info("Loading data for the selected stocks from the configuration file")

    for ticker in tickers:
        response = requests.get(
            f"https://api.twelvedata.com/price?symbol={ticker}&apikey={os.getenv('API_KEY_STOCKS')}"
        )
        data = response.json()

        get_currency_rates_logger.info("Stock prices received as a JSON response")

        price = round(float(data.get("price", "")), 3)
        prices.append({"stock": ticker, "price": price})

    return prices
