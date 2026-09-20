from datetime import datetime, timedelta, time
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
    date: Optional[str] = None,
    transactions: pd.DataFrame = pd.read_csv(os.path.join(DATA_DIR, "operations.csv")),
) -> pd.DataFrame:
    """Return expenses for the specified category for the last three months."""

    transactions["Дата операции"] = transactions["Дата операции"].apply(
        lambda row: datetime.strptime(row, "%d.%m.%Y %H:%M:%S")
    )
    transactions["Сумма операции"] = transactions["Сумма операции"].astype(str).str.replace(",", ".").astype(float)
    spendings = transactions[(transactions["Категория"] == category) & (transactions["Сумма операции"] < 0)]

    if date is not None:
        date = datetime.strptime(date, "%Y.%m.%d")
        date = datetime.combine(date, time.max)
    else:
        date = datetime.today()
    end_date = date
    start_date = date - timedelta(days=90)

    spendings_filtered = spendings[
        (spendings["Дата операции"] >= start_date) & (spendings["Дата операции"] <= end_date)
    ]
    spendigs_dict = spendings_filtered.to_dict(orient="records")
    return spendigs_dict


def reports_main():
    print("Do you want to get the expenses for the last three months? (yes/no)")
    whether_expenses = input("Enter yes or no: ").capitalize()
    if whether_expenses == "Yes":
        print("To get expenses by category, enter the desired category and optionally specify a date.")
        category = input("Enter the category to get expenses for: ")
        print("Do you want to specify a date? (yes/no)")
        whether_date = input("Enter yes or no: ").capitalize()

        if whether_date == "Yes":
            date = input("Enter the date in the format YYYY.MM.DD: ")
            spendings_by_category = find_spending_by_category(category, date)
        else:
            spendings_by_category = find_spending_by_category(category)

        print("Displaying expenses for the specified category.")
        return spendings_by_category
    else:
        return ""
