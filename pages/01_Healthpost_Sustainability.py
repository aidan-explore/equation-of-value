import streamlit as st
import pandas as pd

from models.healthpost import HealthPost, Equipment, Service
from charts.breakdown import chart_cost_breakdown


def calculate_income_statement_model() -> HealthPost:

    hp = HealthPost(
        name = "",
        patients = st.session_state.patients, 
        rev_per_visit = st.session_state.rev_per_visit,
        nurses = st.session_state.nurses,
        salary = st.session_state.salary,
        equipment = [Equipment(equipment_type=k,**v) for k, v in st.session_state.equipment.iterrows()],
        service = [Service(service_type=k, **v) for k, v in st.session_state.service.iterrows()]
    )

    return hp

# Define the input parameters
st.title("Rural Health Post Sustainability")

st.header("Income Statement")
income_statement = st.empty()
charts = st.empty()

st.header("Revenue Drivers")
col1, col2 = st.columns(2)

number_of_patients = int(col1.number_input("Number of Patients per day: ", value= 100, min_value=1, step=1, key='patients'))
average_revenue_per_patient = float(col2.number_input("Average Revenue per Patient Visit: $", value=10, key="rev_per_visit"))

st.header("Cost Drivers")
st.subheader("Salaries")

col1, col2 = st.columns(2)
number_of_nurses = int(col1.number_input("Number of Nurses: ", min_value=1, step=1, value=10, key='nurses'))
average_salary = float(col2.number_input("Average Salary per Nurse: $", value=10_000, key='salary'))

st.subheader("Cost of Care")
service_data = [
    ['Pregnancy', 1000, 0.5],
    ['Malaria', 100, 0.5]
]
service_df = pd.DataFrame(data=service_data,
                            columns=['service_type', 'cost_per_service', 'service_prop'])
service_df.set_index('service_type', inplace=True)
service_df = service_df.astype(float)
service_df['cases'] = service_df['service_prop'] * st.session_state.patients

# TODO update case column on service proportion change
def update_cases():
    df = st.session_state['service']
    df['cases'] = df['service_prop'] * st.session_state.patients
    st.session_state['service'] = df

st.session_state['service'] = st.data_editor(service_df, 
               num_rows = "dynamic",
               key='service_change', use_container_width = True, on_change=update_cases)

st.subheader("Equipment Costs")
equipment_data = [
    ['Starlink', 10_000, 10, 1],
    ['eFiche', 100, 50, 1]
]
equipment_df = pd.DataFrame(data=equipment_data,
                            columns=['equipment_type', 'capital_investment', 'monthly_maintenance', 'num_units'])
equipment_df.set_index('equipment_type', inplace=True)
equipment_df = equipment_df.astype(float)
st.session_state['equipment'] = st.data_editor(equipment_df, 
               num_rows = "dynamic",
               key='equipment_change', use_container_width=True)

#calculate the Income Statement
hp = calculate_income_statement_model()

with income_statement:
    col1, col2, col3 = st.columns(3)

    col1.write(f"Revenue: ${hp.revenue:,.0f}")
    col2.write(f"Total Cost: ${hp.total_cost:,.0f}")
    col3.write(f"Net Income: ${hp.net_income:,.0f}")

with charts:
    with st.expander("Click down to see charts"):
        st.pyplot(chart_cost_breakdown(hp))

st.markdown("### Note:")
st.markdown("The above calculations are based on the assumptions made and may not reflect actual financial performance of a rural health post.")