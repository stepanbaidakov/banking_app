import logging
import os
import re
import pandas as pd
from config import DATA_DIR, LOGS_DIR


log_path = os.path.join(LOGS_DIR, "services.log")
services_logger = logging.Logger(__name__)
file_handler = logging.FileHandler(log_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
services_logger.addHandler(file_handler)
services_logger.setLevel(logging.DEBUG)


def normalize_value(value):
    """Convert incompatible values to Python-compatible values."""
    if pd.isna(value):
        return None
    if isinstance(value, str) and value == "null":
        return None
    return value


def find_by_number():
    """Return a JSON response with all transactions containing phone numbers in their description."""
    print("Displaying transactions containing phone numbers.")
    operations = pd.read_csv(os.path.join(DATA_DIR, "operations.csv"))
    services_logger.info("Loading the transactions file")

    pattern = re.compile(r"\+\d+\s\d+\s\d+\W\d+\W\d+")
    find_filter = operations["Описание"].astype(str).apply(lambda x: bool(pattern.search(x)))

    services_logger.info("Searching for transactions containing a phone number")

    number_operations = operations[find_filter]
    result = number_operations.to_dict(orient="records")

    normalized = []
    for operation in result:
        norm_operation = {key: normalize_value(value) for key, value in operation.items()}
        normalized.append(norm_operation)

    services_logger.info("Returning the matching transactions as a JSON response")
    return normalized


def services_main():
    """Run the services."""
    print("Do you want to display the transactions containing phone numbers in their description? (yes/no)")
    whether_find = input("Enter yes or no: ")
    if whether_find == "yes":
        return find_by_number()
    else:
        return ""
