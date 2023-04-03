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
        payment_base = self.context_payments.equal_payments(loan_date)
        
        arr_capital = []
        arr_dates = []
        arr_payments = []
        arr_interest = []
        arr_instalments = []
        arr_extra_payments = []
        arr_cumulative_inflation = []
        cumulative_inflation = 0
        while capital >= 0:
            arr_dates.append(loan_date)
            cumulative_inflation = self.context_inflation.get_monthly(arr_dates[-1])

            arr_cumulative_inflation.append(cumulative_inflation)
            arr_capital.append(capital * (1 + arr_cumulative_inflation[-1]))

            arr_payments.append(
                self.context_payments.calculate_equal_payments(
                    arr_capital[-1],
                    max(self.context_payments.loan_context.n_payments - (len(arr_capital) - 1), 1),
                    self.context_payments.rate_context.get_monthly_rate(arr_dates[-1])
                )
            )

            arr_interest.append(arr_capital[-1] * rate)
            arr_instalments.append(payment_base - arr_interest[-1])
            arr_extra_payments.append(0)
            
            loan_date = DateHandler.increment_by_month(loan_date)
            capital -= arr_instalments[-1]

        self.df = pd.DataFrame(
            dict(
                date=arr_dates,
                cumulative_inflation=arr_cumulative_inflation,
                capital_base=arr_capital,
                payments_base=arr_payments,
                payments_extra=arr_extra_payments,
                interests_base=arr_interest,
                instalments_base=arr_instalments
            )
        )
        
        return self.df

    def recalculate(self):
        # Re-adjust capital based on extra payments made 
        self.df['payments_base'] = self.df.apply(lambda row: self.context_payments.calculate_equal_payments(
            row['capital_base'],
            self.context_payments.loan_context.n_payments - row.name,
            self.context_payments.rate_context.get_monthly_rate(row['date'])
        ), axis=1)

    def calculate(self):
        self.df['inflation_csum'] = self.df['monthly_inflation'].cumsum()
        self.df['capital'] = self.df['capital_base'] * (1 + self.df['inflation_csum'])
        self.df['payment'] = self.df['payments_base'] * (1 + self.df['inflation_csum'])
        self.df['interest'] = self.df['interests_base'] * (1 + self.df['inflation_csum'])
        self.df['instalments'] = self.df['instalments_base'] * (1 + self.df['inflation_csum'])