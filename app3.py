import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(layout="wide", page_title="Dashboard NovaRetail")

# Chargement des données (basé sur l'analyse précédente)
# On simule ici df_final et df_campaigns pour le fonctionnement du code
data_leads = {
    'channel': ['Emailing', 'Google Ads', 'LinkedIn Ads', 'Emailing', 'Google Ads', 'LinkedIn Ads', 'Emailing', 'Google Ads', 'LinkedIn Ads', 'Emailing'],
    'status': ['MQL', 'SQL', 'Client', 'MQL', 'SQL', 'Client', 'MQL', 'SQL', 'Client', 'MQL'],
    'sector': ['SaaS', 'Industry', 'Finance', 'HealthTech', 'Retail', 'SaaS', 'Education', 'Industry', 'Finance', 'SaaS'],
    'cost': [1500, 4200, 3800, 1500, 4200, 3800, 1500, 4200, 3800, 1500]
}
df_final = pd.DataFrame(data_leads)

campaigns = [
    {"channel": "Emailing", "cost": 1500, "clicks": 1800, "conversions": 150},
    {"channel": "Google Ads", "cost": 4200, "clicks": 3200, "conversions": 260},
    {"channel": "LinkedIn Ads", "cost": 3800, "clicks": 1100, "conversions": 95}
]
df_campaigns = pd.DataFrame(campaigns)

# Calcul des KPI globaux
total_cost = df_campaigns['cost'].sum()
total_leads = df_campaigns['conversions'].sum()
avg_cpl = total_cost / total_leads
total_clients = len(df_final[df_final['status'] == 'Client'])
conversion_rate = (total_leads / df_campaigns['clicks'].sum()) * 100

# --- INTERFACE STREAMLIT ---

st.title("Tableau de Bord Décisionnel - NovaRetail (Octobre 2025)")

# 1. Section KPI (5 indicateurs)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Budget Total", f"{total_cost} €")
col2.metric("Total Leads", total_leads)
col3.metric("CPL Moyen", f"{avg_cpl:.2f} €")
col4.metric("Total Clients", total_clients)
col5.metric("Taux Conv. Global", f"{conversion_rate:.2f} %")

st.markdown("---")

# 2. Section Graphiques
left_column, right_column = st.columns(2)

with left_column:
    st.subheader("Rentabilité : CPL par Canal")
    df_campaigns['CPL'] = df_campaigns['cost'] / df_campaigns['conversions']
    fig_cpl = px.bar(df_campaigns, x='channel', y='CPL', 
                     labels={'CPL': 'Coût par Lead (€)', 'channel': 'Canal'},
                     color='channel')
    st.plotly_chart(fig_cpl, use_container_width=True)

with right_column:
    st.subheader("Qualité : Statut CRM par Canal")
    status_counts = df_final.groupby(['channel', 'status']).size().reset_index(name='count')
    fig_status = px.bar(status_counts, x='channel', y='count', color='status', 
                        barmode='stack', labels={'count': 'Nombre de Leads'})
    st.plotly_chart(fig_status, use_container_width=True)

# 3. Section Basse
st.subheader("Segmentation des Leads par Secteur d'Activité")
sector_counts = df_final['sector'].value_counts().reset_index()
sector_counts.columns = ['Secteur', 'Nombre']
fig_sector = px.pie(sector_counts, values='Nombre', names='Secteur', hole=0.4)
st.plotly_chart(fig_sector, use_container_width=True)
