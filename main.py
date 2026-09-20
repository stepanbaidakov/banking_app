from src.reports import reports_main
from src.services import services_main
from src.views import views_main
from src.utils import *


def main():
    """Run the project."""
    transactions = views_main()
    yield transactions

    spendings_by_category = reports_main()
    yield spendings_by_category

    found_by_number = services_main()
    yield found_by_number

for step in main():
    print(step)
