import datetime
from calculator.rates import InterestContext
from calculator import LoanContext


class DownPayments:
    
    def __init__(self, loan_context: LoanContext, rate_context: InterestContext):
        self.loan_context = loan_context
        self.rate_context = rate_context

    def equal_instalments(self, date: datetime.datetime) -> float:
        return self.loan_context.capital / self.loan_context.n_payments

    def equal_payments(self, date: datetime.datetime) -> float:
        r = self.rate_context.get_monthly_rate(date)
        a = 1 + r
        b = (1 + r)**self.loan_context.n_payments
        return self.loan_context.capital*b*r/(b - 1)

    def calculate_equal_instalments(self, capital: float, n_payments: int, rate: float):
        return capital / n_payments

    def calculate_equal_payments(self, capital: float, n_payments: int, rate: float):
        b = (1 + rate)**n_payments
        return capital*b*rate/(b - 1)
