from typing import List
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from scipy.stats import truncnorm


class HealthPost():
    def __init__(self, name:str, patients:int, ave_rev: float) -> None:
        self.name = name
        self.patients = patients
        self.ave_rev = ave_rev
        self.simulated_revenue = []
        self.simulated_expenses = []

        self.data = pd.DataFrame(columns = ["patients", "ave_revenue", "hcw", "ave_salary"])

    def revenue(self) -> float:
        if self.simulated_revenue == []:
            self.simulate_revenue()
        return sum(self.simulated_revenue)
    
    def expenses(self) -> float:
        if self.simulated_expenses == []:
            self.simulate_expenses()
        return sum(self.simulated_expenses)

    def simulate_revenue(self, days: int = 365) -> None:
        revenue = []
        for _ in range(days):
            # Simulate number of patients per day using a truncated normal distribution
            low, high, floc, scale = (50, 200, self.patients, 100)
            patients_per_day = truncnorm.rvs(a=low / scale, b=high / scale, loc=floc).astype(int)

            # Simulate average revenue per patient using a truncated normal distribution
            low, high, floc, scale = (20, 50, self.ave_rev, 10)
            average_revenue_per_patient = truncnorm.rvs(a=low / scale, b=high / scale, loc=floc).astype(float)

            # Calculate total revenue for this day
            revenue.append(patients_per_day * average_revenue_per_patient)

        self.simulated_revenue = revenue

    def simulate_expenses(self, days: int = 365) -> None:
        revenue = []
        for _ in range(days):
            # Simulate number of patients per day using a truncated normal distribution
            low, high, floc, scale = (50, 200, self.patients, 100)
            patients_per_day = truncnorm.rvs(a=low / scale, b=high / scale, loc=floc).astype(int)

            # Simulate average revenue per patient using a truncated normal distribution
            low, high, floc, scale = (20, 50, self.ave_rev, 10)
            average_revenue_per_patient = truncnorm.rvs(a=low / scale, b=high / scale, loc=floc).astype(float)

            # Calculate total revenue for this day
            revenue.append(patients_per_day * average_revenue_per_patient)

        self.simulated_revenue = revenue

def plot_health_post_revenue(healthposts: List[HealthPost]) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=[healthpost.revenue() for healthpost in healthposts], 
                 bins=50, stat="density", kde=True, 
                 palette='viridis')
    ax.set_title("Histogram of Revenue")
    ax.legend()

    return fig, ax

st.title('Simulating Health Post Profitability')
num_healthposts = st.session_state['num_healthposts'] 
ave_patients    = st.session_state['ave_patients'] 
rev_patient     = st.session_state['rev_patient']

healthposts = [HealthPost(f"Healthpost {i}", ave_patients, rev_patient) for i in range(num_healthposts)]

# Plot the revenue histogram
fig, ax = plot_health_post_revenue(healthposts)

st.pyplot(fig)




