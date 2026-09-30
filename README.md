# Banking Application for Transaction Analysis

An application for analyzing bank transactions from a CSV file. It allows users to filter transactions by date, separate
them into expenses and income, generate category-based analytics, retrieve currency exchange rates and stock prices
through external APIs, and search for transactions containing phone numbers.

## Features

The application provides the following features:

* analyze bank transactions from a CSV file;
* filter transactions by a selected date range;
* separate transactions into income and expenses;
* analyze transactions by category;
* generate summary information about income and expenses in JSON format;
* retrieve currency exchange rates through an external API;
* retrieve stock prices through an external API;
* find transactions containing phone numbers;
* generate reports;
* log application activity.

## Architecture and Key Features

* **Pandas** is used to load, process, and filter bank transactions from a CSV file.
* **Requests** is used to retrieve currency exchange rates and stock prices through external APIs.
* **Defaultdict** is used to group income and expenses by category and calculate totals.
* **Data normalization** is used to convert `NaN` and `pandas.Timestamp` values into Python and JSON-compatible values.
* **Logging** is used to track the main stages of application execution and write information to a log file.

## Tech Stack

* Python
* pandas
* requests
* python-dotenv
* Poetry
* logging
* JSON
* Regular expressions (`re`)
* CSV

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/stepanbaidakov/course_work_1.git
cd course_work_1
```

### 2. Install dependencies

If you are using Poetry:

```bash
poetry install
```

To install the dependencies without installing the project itself:

```bash
poetry install --no-root
```

Alternatively, dependencies can be installed using `pip`:

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the root directory of the project.

Add your API keys:

```env
API_KEY_CURRENCIES=your_currency_api_key
API_KEY_STOCKS=your_stocks_api_key
```

The `.env` file should not be committed to the repository. Add it to `.gitignore` to prevent it from being tracked by
Git.

It is recommended to create a `.env.example` file:

```env
API_KEY_CURRENCIES=
API_KEY_STOCKS=
```

## Running the Application

Run the application using Poetry:

```bash
poetry run python main.py
```

If the Poetry virtual environment is activated:

```bash
python main.py
```

The application can also be launched directly from PyCharm by running the `main()` function in `main.py`.

## Output

The application generates structured data in JSON format, which can be used to display information on web pages or for
further processing.

It also provides separate reports on income, expenses, currency exchange rates, stock prices, transactions containing
phone numbers or filtered by a category.

## Testing

The project includes tests written with `pytest`. The tests cover the main application functionality, including transaction processing, reports, currency exchange rates, stock prices, and other application services.

To run all tests, use:

```bash
pytest
```

To run tests with more detailed output:

```bash
pytest -v
```

To run a specific test file:

```bash
pytest tests/test_reports.py
```

To run a specific test:

```bash
pytest tests/test_reports.py::test_spending_by_category_report -v
```

The project also uses `unittest.mock` to mock external API requests, allowing the tests to run without making real HTTP requests.
