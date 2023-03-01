import datetime


class InterestContext:
    
    def __init__(self, base_rate: float):
        self.base_rate = base_rate / 100

    def get_rate(self, date: datetime.datetime) -> float:
        return self.base_rate # Steady rate

    def get_monthly_rate(self, date: datetime.datetime) -> float:
        return self.get_rate(date) / 12