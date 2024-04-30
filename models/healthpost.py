from pydantic import BaseModel

class Equipment(BaseModel):
    equipment_type: str
    capital_investment: float
    monthly_maintenance: float
    num_units: float

class Service(BaseModel):
    service_type: str
    cost_per_service: float
    service_prop: float
    cases: float = 0

class HealthPost(BaseModel):
    name: str
    patients: int
    rev_per_visit: float
    nurses: int
    salary: float
    equipment: list[Equipment]
    service: list[Service]

    @property
    def revenue(self) -> float:
        return self.patients * self.rev_per_visit * 220

    @property
    def salaries_cost(self) -> float:
        return self.nurses * self.salary
    
    @property
    def cost_of_care(self) -> float:
        return sum([s.cases * s.cost_per_service for s in self.service])

    @property
    def equipment_capital(self) -> float:
        return sum([e.num_units * e.capital_investment for e in self.equipment])
    
    @property
    def equipment_maintenance(self) -> float:
        return sum([e.num_units * e.monthly_maintenance * 12 for e in self.equipment])
    
    @property
    def total_cost(self) -> float:
        return self.salaries_cost + self.cost_of_care + self.equipment_capital + self.equipment_maintenance
    
    @property
    def net_income(self) -> float:
        return self.revenue - self.total_cost

# Define the HealthPost model
health_post_model = HealthPost