import os

import pandas as pd
import pytest

from config import DATA_DIR
from src.reports import find_spending_by_category


@pytest.fixture
def sample_transactions():
    return pd.DataFrame(
        [
            {
                "Дата операции": pd.Timestamp("20.03.2020 23:59:59"),
                "Категория": "Магнит",
                "Сумма операции": -1000,
                "Описание": "Магнит",
            },
            {
                "Дата операции": pd.Timestamp("15.02.2020 12:00:00"),
                "Категория": "Магнит",
                "Сумма операции": -500,
                "Описание": "Магнит",
            },
            {
                "Дата операции": pd.Timestamp("19.12.2019 12:00:00"),
                "Категория": "Магнит",
                "Сумма операции": -300,
                "Описание": "Магнит",
            },
            {
                "Дата операции": pd.Timestamp("20.03.2020 12:00:00"),
                "Категория": "Продукты",
                "Сумма операции": -700,
                "Описание": "Пятёрочка",
            },
            {
                "Дата операции": pd.Timestamp("20.03.2020 12:00:00"),
                "Категория": "Магнит",
                "Сумма операции": 1000,
                "Описание": "Магнит",
            },
        ]
    )



def test_spending_by_category_report(sample_transactions):
    result = find_spending_by_category("Магнит", sample_transactions, "20.03.2020",)

    assert isinstance(result, list)
    assert len(result) == 2

    assert result[0]["Описание"] == "Магнит"
    assert result[0]["Сумма операции"] == -1000

    assert result[1]["Описание"] == "Магнит"
    assert result[1]["Сумма операции"] == -500


def test_only_negative_operations_are_returned(sample_transactions):
    result = find_spending_by_category(
    "Магнит",
    sample_transactions,
    "20.03.2020",
    )

    assert all(item["Сумма операции"] < 0 for item in result)


def test_only_requested_category_is_returned(sample_transactions):
    result = find_spending_by_category(
    "Магнит",
    sample_transactions,
    "20.03.2020",
    )

    assert all(item["Категория"] == "Магнит" for item in result)


def test_three_month_period(sample_transactions):
    result = find_spending_by_category(
    "Магнит",
    sample_transactions,
    "20.03.2020",
    )

    dates = [item["Дата операции"] for item in result]

    assert "20.03.2020" in dates
    assert "15.02.2020" in dates
    assert "20.12.2019" not in dates


def test_without_date(sample_transactions):
    result = find_spending_by_category(
    "Магнит",
    sample_transactions,
    )

    assert isinstance(result, list)


def test_invalid_date(sample_transactions):
    with pytest.raises(ValueError):
        find_spending_by_category(
        "Магнит",
        sample_transactions,
        "2020.03.20",
        )


def test_report_file_exists(sample_transactions):
    find_spending_by_category(
    "Магнит",
    sample_transactions,
    "20.03.2020",
    )

    report_path = os.path.join(DATA_DIR, "reports.txt")

    assert os.path.exists(report_path)

    with open(report_path, "r", encoding="utf-8") as file:
        content = file.read()

    assert "Магнит" in content
