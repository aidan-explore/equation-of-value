import pandas as pd
import streamlit as st

st.title('Assumptions for Health Post Profitability')

st.header('Revenue assumptions')
col1, col2, col3 = st.columns(3)

col1.number_input('Number of Healthposts to simulate', value=50, key='num_healthposts')
col2.number_input('Number of Patients Per Day', value=20, key='ave_patients')
col3.number_input('Average Revenue Per Visit RWF', value=1500, key='rev_patient')

st.header('Expense assumptions')
healthposts, nurses, services, equipment = st.tabs(['Healthposts', 'Nurses', 'Services', 'Equipment'])

if 'healthposts' not in st.session_state:
    df = pd.read_csv('data/healthposts.csv')
    df.set_index('id', inplace=True)
    st.session_state['healthposts'] = df

if 'nurses' not in st.session_state:
    df = pd.read_csv('data/healthcareworkers.csv')
    df.set_index('id', inplace=True)
    st.session_state['nurses'] = df

if 'services' not in st.session_state:
    df = pd.read_csv('data/services.csv')
    df.set_index('service_type', inplace=True)
    df = df.astype(float)
    df = df[['cost_per_service', 'service_prop']]
    st.session_state['services'] = df

if 'equipment' not in st.session_state:
    df = pd.read_csv('data/equipment.csv')
    df.set_index('equipment_type', inplace=True)
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





