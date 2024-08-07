import datetime as dt
import pandas as pd
import streamlit as st

from utils.constants import CONSTANT

st. set_page_config(layout="wide") 

st.title('Assumptions for Health Post Sustainability')
col1, col2 = st.columns(2)
col1.markdown(body="""
### What is included:
* Top Down Revenue = Patients per day * Ave Revenue Per Patient
* Bottom Up Revenue = Patients per day * Proportion of each service * revenue per service
* Salary Cost = Number of nurses * salary
* Cost of Service = Cost per Service * Proportion of Service * Patients
* Equipment Capital = Type * Number * Cost to Install
* Equipment Maintenance = Type * Number * Monthly Fee
""")
col2.markdown(body="""
### Still to do:
* Get the equipment list per facility
* Get the nurse/health care worker list
* update the npv calc to be based off services (not top down revenue)
* add different types of healthcare workers (not just nurses)
* Lots of calibration
* :tick: 20% margin on cost to serve
* modelling payment delays
* How many nurses per patient do we need?
""")

st.header('Overall Assumptions')
col1, col2, col3, col4 = st.columns(4)
col1.date_input("Start date for projections", value=CONSTANT['start_date'], key='start_date')
col2.date_input("End date for projections", value=CONSTANT['end_date'], key='end_date')
col3.selectbox('Reporting currency?', options=['RWF', 'USD'], key='currency', disabled=True)
col4.number_input('USD / RWF exchange rate', value=CONSTANT['USDxRWF'], key='USDxRWF', disabled=True)

st.header('Revenue assumptions')
col1, col2, col3 = st.columns(3)

col1.number_input('Number of Healthposts to simulate', value=50, key='num_healthposts')
col2.number_input('Number of Patients Per Day', value=20, key='ave_patients')
col3.number_input('Average Revenue Per Visit RWF', value=1500, key='rev_patient')

st.header('Expense assumptions')
healthposts, nurses, services, equipment, constants = st.tabs(['Healthposts', 'Nurses', 'Services', 'Equipment', 'Constants'])

if 'healthposts' not in st.session_state:
    df = pd.read_csv('data/healthposts.csv')
    df.set_index('name', inplace=True)
    df = df.astype(float)
    st.session_state['healthposts'] = df

if 'nurses' not in st.session_state:
    df = pd.read_csv('data/healthcareworkers.csv')
    df.set_index('id', inplace=True)
    st.session_state['nurses'] = df

if 'services' not in st.session_state:
    df = pd.read_csv('data/services.csv')
    df.set_index('service_type', inplace=True)
    df = df.astype(float)
    df = df[['revenue_per_service', 'cost_per_service', 'service_prop']]
    df.sort_values('service_prop', ascending=False, inplace=True)
    st.session_state['services'] = df

if 'equipment' not in st.session_state:
    df = pd.read_csv('data/equipment.csv')
    df.set_index('equipment_type', inplace=True)
    df.fillna(0.0, inplace=True)
    st.session_state['equipment'] = df

with healthposts:
    df = st.session_state['healthposts']

    col1, col2 = st.columns(2)
    col1.metric('Average Patients Per Day', value=f"{df['patients'].mean():,.0f}")
    col2.metric('Average Revenue Per Visit', value=f"{((df['rev_per_visit'] * df['patients']).sum()/df['patients'].sum()):,.0f}")
    st.dataframe(df, use_container_width=True)

services.dataframe(st.session_state['services'], use_container_width=True)
equipment.dataframe(st.session_state['equipment'], use_container_width=True)
nurses.dataframe(st.session_state['nurses'], use_container_width=True)

constants.write(CONSTANT)





