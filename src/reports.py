from datetime import datetime, time
from dateutil.relativedelta import relativedelta
import logging
import os.path
from typing import Optional
import pandas as pd
from config import DATA_DIR, LOGS_DIR

log_path = os.path.join(LOGS_DIR, "services.log")
services_logger = logging.Logger(__name__)
file_handler = logging.FileHandler(log_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
services_logger.addHandler(file_handler)


def report(func):
    """Accept a function and save its result to a report file."""
    def wrapper(*args, **kwargs):
        """Save the report data to a file."""
        result = func(*args, **kwargs)
        result_str = str(result)
        with open(os.path.join(DATA_DIR, "reports.txt"), "w", encoding="utf-8") as file:
            file.write(result_str)
        return result

    return wrapper


@report
def find_spending_by_category(
    category: str,
    transactions: pd.DataFrame,
    date: Optional[str] = None,
) -> dict:
    """Return expenses for the specified category for the last three months."""
    spendings = transactions[(transactions["Категория"] == category) & (transactions["Сумма операции"] < 0)]

    if date is not None:
        end_date = datetime.strptime(date, "%d.%m.%Y")
        end_date = datetime.combine(end_date, time.max)
    else:
        end_date = datetime.now()

    start_date = end_date - relativedelta(months=3)
    start_date = datetime.combine(start_date, time.min)

    spendings_filtered = spendings[
        (spendings["Дата операции"] >= start_date) & (spendings["Дата операции"] <= end_date)
    ].copy()
    spendings_filtered["Дата операции"] = spendings_filtered["Дата операции"].dt.strftime("%d.%m.%Y")
    spendings_dict = spendings_filtered.to_dict(orient="records")
    return {"spendings": spendings_dict}


def reports_main():
    """Run reports"""
    transactions = pd.read_csv(os.path.join(DATA_DIR, "operations.csv"))
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    transactions["Сумма операции"] = transactions["Сумма операции"].astype(str).str.replace(",", ".").astype(float)

    print("Do you want to get the expenses for the last three months? (yes/no)")
    whether_expenses = input("Enter yes or no: ").capitalize()

    if whether_expenses == "Yes":
        print("To get expenses by category, enter the desired category and optionally specify a date.")
        category = input("Enter the category to get expenses for: ").capitalize()
        print("Do you want to specify a date? (yes/no)")
        whether_date = input("Enter yes or no: ").capitalize()

        if whether_date == "Yes":
            while True:
                date = input("Enter the date in the format DD.MM.YYYY: ")
                try:
                    spendings_by_category = find_spending_by_category(category, transactions, date)
                    break
                except ValueError:
                    print("Please enter a valid date.")
        else:
            spendings_by_category = find_spending_by_category(category, transactions)

        print("Displaying expenses for the specified category.")
        return spendings_by_category
    else:
        return {}
