from utils.constants import CONSTANT
import streamlit as st
from models.healthpost import HealthPost, HealthPostAggregator, HealthCareWorker

st.header('RHOS Healthpost Profitability')

df_healthposts = st.session_state.healthposts

healthpost_list = []
for k, v in df_healthposts.iterrows():
    nurses = [HealthCareWorker(name=f"{k}_{i}") for i in range(int(v.nurses))]
    hp = HealthPost(
        name=k,
        patients=int(v['patients']) + 1,
        rev_per_visit=v['rev_per_visit'],
        nurses=nurses)

    healthpost_list.append(hp)

hp_agg = HealthPostAggregator(name="RHOS", healthposts=healthpost_list)
hp     = hp_agg.hp

st.header("Income Statement")
income_statement = st.empty()
charts = st.empty()

with income_statement:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(f"1st Year Revenue: RWF", value=f"{hp.revenue:,.0f}")
    col2.metric(f"1st Year Cost: RWF", f"{hp.total_cost:,.0f}")
    col3.metric(f"1st Year Net Income: RWF", f"{hp.net_income:,.0f}")
    col4.metric(f"NPV @ {CONSTANT['discount_rate'] * 100:,.1f}%", f"{hp.npv:,.0f}")

with charts:
    cost_breakdown, cashflow_chart, cashflows = st.tabs(['Cost Breakdown', 'Cashflow Chart', 'Cashflows'])
    cost_breakdown.pyplot(hp.chart_cost_breakdown())
    cfs = hp.generate_cashflows()
    cashflows.dataframe(cfs.df)
    cashflow_chart.bar_chart(cfs.aggregate_frequency('QE'), y='total')



