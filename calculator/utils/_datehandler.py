import datetime
from dateutil.relativedelta import relativedelta

class DateHandler:
    @classmethod
    def increment_by_month(cls, date: datetime.datetime):
        return date + relativedelta(months=1)