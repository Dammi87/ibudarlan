from .downpayments import DownPayments
from calculator.utils import DateHandler
from calculator.rates import InflationContext
import pandas as pd

class IndexBasedLoan:
    def __init__(self, context_payments: DownPayments, context_inflation: InflationContext):
        self.context_payments = context_payments
        self.context_inflation = context_inflation
        self.df: pd.DataFrame = None
        self.initialize()

    def initialize(self):
        capital = self.context_payments.loan_context.capital
        loan_date = self.context_payments.loan_context.date_of_loan
        rate = self.context_payments.rate_context.get_monthly_rate(loan_date)
        payment_base = self.context_payments.equal_capital_payment(loan_date)
        inflation_base = self.context_inflation.get_monthly(loan_date)
        
        arr_capital = []
        arr_dates = []
        arr_payments = []
        arr_interest = []
        arr_instalments = []
        
        while capital >= 0:
            arr_capital.append(capital)
            arr_dates.append(loan_date)
            arr_payments.append(payment_base)
            arr_interest.append(arr_capital[-1] * rate)
            arr_instalments.append(payment_base - arr_interest[-1])
            
            loan_date = DateHandler.increment_by_month(loan_date)
            capital -= arr_instalments[-1]

        self.df = pd.DataFrame(
            dict(
                date=arr_dates,
                capital_base=arr_capital,
                payments_base=arr_payments,
                interests_base=arr_interest,
                instalments_base=arr_instalments
            )
        )
        
        return self.df

    def calculate(self):
        self.df['inflation_csum'] = self.df['date'].apply(
            lambda x: self.context_inflation.get_monthly(x)
        ).cumsum()
        self.df['capital'] = self.df['capital_base'] * (1 + self.df['inflation_csum'])
        self.df['payment'] = self.df['payments_base'] * (1 + self.df['inflation_csum'])
        self.df['interest'] = self.df['interests_base'] * (1 + self.df['inflation_csum'])
        self.df['instalments'] = self.df['instalments_base'] * (1 + self.df['inflation_csum'])
    