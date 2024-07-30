import streamlit as st

from models.healthpost import HealthPost, HealthCareWorker, Service

def calculate_npv() -> HealthPost:

    health_post = HealthPost(
        patients=st.session_state['be_patients'],
        rev_per_visit=st.session_state['be_revenue'],
        nurses=[HealthCareWorker(salary=st.session_state['be_salary'])] * int(st.session_state['be_nurses']),
        equipment=[],
        services=services
    )
    st.session_state['be_healthpost'] = health_post

def update_nurses(num_nurses, salary: None) -> list[HealthCareWorker]:
    if salary is None:
        salary = st.session_state['be_salary']
    return [HealthCareWorker(salary)] * num_nurses


def find_breakeven(hp: HealthPost, metric, start, end, step, target = 0) -> float:
    value = start
    while True:
        setattr(hp, metric, value)
        if (hp.npv < target) and (value < end):
            value += step
        else:
            break
    
    return value

def find_breakeven_nurses(hp: HealthPost, change_nurses: bool, change_salary: bool, start, end, step, target = 0) -> float:
    if change_nurses and change_salary:
        raise Exception('please dont change two things at the same time in a breakeven')
    
    if change_salary:
        nurses = st.session_state['be_nurses']

    if change_nurses:
        salary = st.session_state['be_salary']

    value = start
    while True:
        if change_salary: 
            salary = value
        if change_nurses:
            nurses = value

        hp.nurses = [HealthCareWorker(salary=salary)] * nurses

        if (hp.npv < target) and (value > end):
            value += step

        else:
            break
    
    return value

# Streamlit UI
st.title("HealthPost Breakeven Point Analysis")

col1, col2 = st.columns([3, 1])
npv = col1.empty()
calculate = col2.empty()

col1, col2 = st.columns([3, 1])
patients = col1.slider("Number of Daily Patients", min_value=0, max_value=500, value=70, step= 10, key='be_patients', on_change=calculate_npv)
patients_breakeven = col2.empty()

col1, col2 = st.columns([3, 1])
revenue_per_patient = col1.slider("Average Revenue per Patient", min_value=0.0, max_value=5000.0, value=1000.0, key='be_revenue', on_change=calculate_npv)
revenue_breakeven = col2.empty()

col1, col2 = st.columns([3, 1])
nurses = col1.slider("Number of Nurses", min_value=0, max_value=10, value=1, key='be_nurses', on_change=calculate_npv)
nurses_breakeven = col2.empty()

col1, col2 = st.columns([3, 1])
salary = col1.slider("Average Salary of Nurses", min_value=0, max_value=10_000_000, value=6_000_000, step=100_000, key='be_salary', on_change=calculate_npv)
salary_breakeven = col2.empty()

services = [Service(service_type=k, **v) for k, v in st.session_state.services.iterrows()]

if 'be_healthpost' not in st.session_state:
    calculate_npv()

hp = st.session_state['be_healthpost']
npv.metric('NPV with current assumptions', hp.npv)

if calculate.button('Calculate Breakeven', key='calculate'):

    breakeven_patients = find_breakeven(hp, 'patients', start=0, end=500, step=10)
    patients_breakeven.metric("Breakeven Number of Patients", breakeven_patients)

    # breakeven_revenue = find_breakeven(hp, 'average', 0, 500, 10)
    # revenue_breakeven.metric("Breakeven Revenue per Patient", breakeven_revenue)

    breakeven_nurses = find_breakeven_nurses(hp, change_nurses=True, change_salary=False, start=10, end=0, step=-1, target=0)
    nurses_breakeven.metric(f"Breakeven Number of Nurses", breakeven_nurses)

    breakeven_salary = find_breakeven_nurses(hp, change_nurses=False, change_salary=True, start=10_000_000, end=0, step=-100_000, target=0)
    salary_breakeven.metric(f"Breakeven Number of Nurses", breakeven_salary)
