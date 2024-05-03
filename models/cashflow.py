import numpy_financial as npf
from typing import Literal
import datetime as dt
import pandas as pd
from pydantic import BaseModel

from utils.constants import CONSTANT

class CashFlow(BaseModel):
    name: str = ""
    amount: float
    start_date: dt.date = CONSTANT['start_date']
    end_date: dt.date = CONSTANT['end_date']
    frequency: Literal['D', 'WD', 'ME', 'QE', 'Y'] = 'ME'
    cashflow_type: Literal['repeat', 'smooth', 'once-off'] = "repeat" 

    @property
    def cashflow(self):
        # Create a time series with the specified frequency
        # TODO create a business day
        ts = pd.date_range(start=self.start_date, end=self.end_date, freq=f"{self.frequency}")
        num_periods = len(ts)

        if self.cashflow_type == 'repeat':
            cf = [self.amount] * num_periods
        elif self.cashflow_type == 'smooth':
            cf = [self.amount / num_periods] * num_periods
        elif self.cashflow_type == 'once-off':
            cf = [self.amount] + [0] * (num_periods - 1)

        # Generate cash flows as a pandas Series
        cashflows = pd.Series(cf, index=ts, name=self.name)

        return cashflows
    
class CashFlowAggregator():
    def __init__(self, cashflows=list[CashFlow]):
        self.cashflows = cashflows
        self.df = pd.DataFrame()
        self.aggregate_cashflows()

    def aggregate_cashflows(self, fillna: int = 0) -> pd.DataFrame:
        for i, cf in enumerate(self.cashflows):
            if not self.df.empty:
                self.df = self.df.join(cf.cashflow, how='outer', rsuffix=f'_{i}')
            else:
                self.df[cf.name] = cf.cashflow
        self.df.fillna(fillna, inplace=True)

    def aggregate_frequency(self, frequency: str) -> pd.DataFrame:
        df = self.df.resample(frequency).sum()
        df['total'] = df.sum(axis=1)
        return df
    
    @property
    def npv(self) -> float:
        values = self.aggregate_frequency('QE')['total'].values
        rate = CONSTANT['discount_rate'] / 4
        return npf.npv(rate, values)

if __name__ == "__main__":
    # Example usage:
    start_date = dt.date(2022, 1, 1)
    end_date = dt.date(2023, 12, 31)
    frequency = "QE"  # or "D", "W", "Y", "Q"
    amount = 1000

    cashflow1 = CashFlow(name="repeat", start_date=start_date, end_date=end_date, frequency=frequency, amount=1000)  
    cashflow2 = CashFlow(name="once-off", start_date=dt.date(2023, 1, 1), end_date=end_date, frequency=frequency, amount=1000, cashflow_type="once-off")
    cashflow3 = CashFlow(name="smooth", start_date=start_date, end_date=end_date, frequency="M", amount=10000, cashflow_type="smooth")

    cf_agg = CashFlowAggregator([cashflow1, cashflow2, cashflow3])
    print(cf_agg.df)

    print(cf_agg.aggregate_frequency('QE'))


    
