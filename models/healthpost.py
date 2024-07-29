from __future__ import annotations
from uuid import UUID
from models.cashflow import CashFlow, CashFlowAggregator
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns

from utils.constants import CONSTANT
from pydantic import BaseModel

# TODO put this is in a better place
SALARY = 10_000 * CONSTANT['USDxRWF']

class HealthCareWorker(BaseModel):
    id: UUID | None = None
    name: str = None
    salary: float = SALARY
    start_date: dt.date = CONSTANT['start_date']
    end_date: dt.date = CONSTANT['end_date']

class Equipment(BaseModel):
    equipment_type: str
    capital_investment: float
    monthly_maintenance: float
    num_units: float

    def __add__(self, other: Equipment) -> Equipment:
        if self.equipment_type == other.equipment_type:
            equipment_type = self.equipment_type
            num_units = self.num_units + other.num_units
            capital_investment = (self.num_units * self.capital_investment + other.num_units * other.capital_investment) / num_units
            monthly_maintenance =(self.num_units * self.monthly_maintenance + other.num_units * other.monthly_maintenance) / num_units

            return Equipment(equipment_type, capital_investment, monthly_maintenance, num_units) 

class Service(BaseModel):
    service_type: str 
    cost_per_service: float
    service_prop: float
    cases: float = 0.0

class HealthPost(BaseModel):
    id: UUID | None = None
    name: str = ""

    # revenue drivers
    patients: int = 0
    rev_per_visit: float = 0

    # cost drivers
    nurses: list[HealthCareWorker] = []
    equipment: list[Equipment] = []
    service: list[Service] = []

    @property
    def revenue(self) -> float:
        return self.patients * self.rev_per_visit * CONSTANT['WORKING_DAYS']
    
    @property
    def num_nurses(self) -> float:
        return len(self.nurses)

    @property
    def salaries_cost(self) -> float:
        return sum([nurse.salary for nurse in self.nurses])
    
    @property
    def cost_of_care(self) -> float:
        return sum([s.cases * s.cost_per_service for s in self.service]) * CONSTANT['WORKING_DAYS']

    @property
    def equipment_capital(self) -> float:
        return sum([e.num_units * e.capital_investment for e in self.equipment])
    
    @property
    def equipment_maintenance(self) -> float:
        return sum([e.num_units * e.monthly_maintenance * 12 for e in self.equipment]) * CONSTANT['USDxRWF']
    
    @property
    def total_cost(self) -> float:
        return self.salaries_cost + self.cost_of_care + self.equipment_capital + self.equipment_maintenance
    
    @property
    def cost_per_patient(self) -> float:
        return (self.total_cost / 220) / self.patients
    
    @property
    def patients_per_nurse(self) -> float:
        return self.patients / self.num_nurses

    @property
    def net_income(self) -> float:
        return self.revenue - self.total_cost
    
    @property
    def npv(self) -> float:
        return self.generate_cashflows().npv
    
    def generate_cashflows(self) -> CashFlowAggregator:
        
        rev_cf = CashFlow(  name='patient_rev', 
                            amount=self.patients * self.rev_per_visit,
                            frequency='D'
                            )

        cfs = [rev_cf]
        for nurse in self.nurses:
            nurse_cf = CashFlow( 
                name=nurse.name if nurse.name is not None else f"nurse_id_{nurse.id}", 
                amount=-nurse.salary / 12,
                frequency='ME'
                )
            cfs.append(nurse_cf)

        for equipment in self.equipment:
            capital = CashFlow(name=f"{equipment.equipment_type}_capital", 
                             amount = -equipment.capital_investment * equipment.num_units * CONSTANT['USDxRWF'],
                             cashflow_type='once-off')
            maintain = CashFlow(name=f"{equipment.equipment_type}_maintain",
                                amount = -equipment.monthly_maintenance * equipment.num_units * CONSTANT['USDxRWF'],
                                )
            cfs.extend([capital, maintain])

        return CashFlowAggregator(cfs)
    
    def chart_cost_breakdown(self: HealthPost) -> plt:

        # Create a bar chart to show each of the individual costs in the total cost
        plt.figure(figsize=(10, 6))
        sns.barplot(x=["Salaries", "Cost of Care", "Equipment Capital", "Equipment Maintenance"], 
                    y=[self.salaries_cost, self.cost_of_care, self.equipment_capital, self.equipment_maintenance], palette="husl")

        # Set title and labels
        plt.title("Individual Costs in Total Cost")
        plt.xlabel("Cost Category")
        plt.ylabel("Cost (RWF)")

        return plt
    
    def __add__(self, other: HealthPost) -> HealthPost:
        patients = self.patients + other.patients
        rev_per_patient = (self.revenue + other.revenue) / patients

        nurses = self.nurses + other.nurses
        salary = (self.salaries_cost + other.salaries_cost) / nurses

        equipment = self.equipment + other.equipment
        service = self.service + other.service

        return HealthPost(patients=patients, rev_per_patient=rev_per_patient, nurses=nurses, salary=salary, equipment=equipment, service=service)

    def __sub__(self, other: HealthPost) -> float:
        return self.net_income - other.net_income
    
    def __str__(self):
        return f"Total Net Income: Total = {self.net_income:.2f}"

class HealthPostAggregator():
    def __init__(self, name:str, healthposts: list[HealthPost]):
        if not all(isinstance(healthpost, HealthPost) for healthpost in healthposts):
            raise ValueError("All elements in the list must be of type HealthPost")
        self.name = name
        self.healthposts = healthposts    
        self._aggregate()
        
    def _aggregate(self):
        patients = sum([hp.patients for hp in self.healthposts])
        print(patients)
        rev_per_visit = sum([hp.revenue for hp in self.healthposts]) / patients

        nurses = [nurse for hp in self.healthposts for nurse in hp.nurses]
        equipment = [equipment for hp in self.healthposts for equipment in hp.equipment]
        services = [service for hp in self.healthposts for service in hp.service]

        self.hp = HealthPost(
            name=self.name,
            patients=patients,
            rev_per_visit=rev_per_visit,
            nurses=nurses,
            equipment=equipment,
            service=services)
        
    def add(self, other: HealthPost):
        if not isinstance(other, HealthPost):
            raise ValueError("Unsupported type for aggregation")
        self.healthposts.append(other)
        self._aggregate()

# Define the HealthPost model
health_post_model = HealthPost