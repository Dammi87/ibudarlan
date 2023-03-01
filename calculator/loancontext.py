import datetime
from dateutil.relativedelta import relativedelta

class LoanContext:
    
    def __init__(self, capital: int, date_of_loan: datetime.datetime, n_years: int):
        self.capital = capital
        self.date_of_loan = date_of_loan
        self.n_years = n_years

    @property
    def n_payments(self):
        return int(self.n_years * 12)

    @property
    def idx_payment(self):
        diff = relativedelta(datetime.datetime.today(), self.date_of_loan)
        return int(diff.years * 12 + diff.months)

