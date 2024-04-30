import streamlit as st

st.title('Assumptions for Health Post Profitability')

st.header('Revenue assumptions')
col1, col2, col3 = st.columns(3)
num_healthposts = int(col1.number_input('Number of Healthposts to simulate', value=350, key='num_healthposts'))
ave_patients    = col2.number_input('Number of Patients per day', value=100, key='ave_patients')
rev_patient     = col3.number_input('Average Revenue per patients per day', value=10, key='rev_patient')

st.header('Expense assumptions')




