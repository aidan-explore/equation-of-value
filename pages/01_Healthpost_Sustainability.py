import streamlit as st
import pandas as pd

from utils.constants import CONSTANT
from models.healthpost import HealthPost, Equipment, Service, HealthCareWorker
from charts.breakdown import chart_cost_breakdown

def calculate_income_statement_model() -> HealthPost:
    for k, v in st.session_state.service.iterrows():
        print (k, v)
        break

    hp = HealthPost(
        name = "",
        patients = st.session_state.patients, 
        rev_per_visit = st.session_state.rev_per_visit,
        nurses = [HealthCareWorker(salary=st.session_state.salary) for _ in range(st.session_state.num_nurses)],
        equipment = [Equipment(equipment_type=k,**v) for k, v in st.session_state.equipment.iterrows()],
        service = [Service(service_type=k, **v) for k, v in st.session_state.service.iterrows()]
    )

    return hp

# Define the input parameters
st.title("Health Post Sustainability")

st.header("Income Statement")
income_statement = st.empty()
charts = st.empty()

st.header("Revenue Drivers")
col1, col2 = st.columns(2)

number_of_patients = int(col1.number_input("Number of Patients per day: ", value=20, min_value=1, step=1, key='patients'))
average_revenue_per_patient = float(col2.number_input("Average Revenue per Patient Visit: $", value=1_500, key="rev_per_visit"))

col1, col2 = st.columns(2)
col1.header("Cost Drivers")
cost_per_patient = col2.empty()

st.subheader("Salaries")
col1, col2, col3 = st.columns(3)
number_of_nurses = int(col1.number_input("Number of Nurses: ", min_value=1, step=1, value=2, key='num_nurses'))
average_salary = float(col2.number_input("Average Annual Salary per Nurse: RWF", value=6_000_000, key='salary', ))
patients_per_nurse = col3.empty()

st.subheader("Cost of Care")
df = st.session_state['services']
df['cases'] = df['service_prop'] * st.session_state.patients

# TODO update case column on service proportion change
def update_cases():
    df = st.session_state['service']
    df['cases'] = df['service_prop'] * st.session_state.patients
    st.session_state['service'] = df

st.session_state['service'] = st.data_editor(df, 
               num_rows = "dynamic",
               key='service_change', use_container_width = True, on_change=update_cases)

st.subheader("Equipment Costs")
equipment_df = st.session_state.equipment
equipment_df['num_units'] = 1
st.session_state['equipment'] = st.data_editor(equipment_df, 
               num_rows = "dynamic",
               key='equipment_change', use_container_width=True)

#calculate the Income Statement
hp = calculate_income_statement_model()

with income_statement:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(f"1st Year Revenue: RWF", value=f"{hp.revenue:,.0f}")
    col2.metric(f"1st Year Cost: RWF", f"{hp.total_cost:,.0f}")
    col3.metric(f"1st Year Net Income: RWF", f"{hp.net_income:,.0f}")
    col4.metric(f"NPV @ {CONSTANT['discount_rate'] * 100:,.1f}%", f"{hp.npv:,.0f}")

with charts:
    with st.expander("Click down to see detailed breakdown"):
        cost_breakdown, cashflow_chart, cashflows = st.tabs(['Cost Breakdown', 'Cashflow Chart', 'Cashflows'])
        cost_breakdown.pyplot(hp.chart_cost_breakdown())
        cfs = hp.generate_cashflows()
        cashflows.dataframe(cfs.df)
        cashflow_chart.bar_chart(cfs.aggregate_frequency('QE'), y='total')

cost_per_patient.metric(label="Cost per patient", 
              value=f"RWF {hp.cost_per_patient:,.1f}")

patients_per_nurse.metric(label="Patients per nurse per day",
                          value=f"{hp.patients_per_nurse:,.1f}")

st.markdown("### Note:")
st.markdown("The above calculations are based on the assumptions made and may not reflect actual financial performance of a rural health post.")