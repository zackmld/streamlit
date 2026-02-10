import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- PREPARATION DES DONNEES (votre code) ---

leads_raw = """lead_id,date,channel,device
201,2025-10-02,Emailing,Desktop
202,2025-10-03,Google Ads,Mobile
203,2025-10-04,LinkedIn Ads,Desktop
204,2025-10-05,Emailing,Mobile
205,2025-10-06,Google Ads,Tablet
206,2025-10-07,LinkedIn Ads,Desktop
207,2025-10-08,Emailing,Mobile
208,2025-10-09,Google Ads,Desktop
209,2025-10-10,LinkedIn Ads,Mobile
210,2025-10-11,Emailing,Desktop"""

df_leads = pd.read_csv(io.StringIO(leads_raw))
df_leads['date'] = pd.to_datetime(df_leads['date'])

campaigns_data = [
    {"campaign_id": "NR01", "channel": "Emailing", "cost": 1500, "impressions": 60000, "clicks": 1800, "conversions": 150},
    {"campaign_id": "NR02", "channel": "Google Ads", "cost": 4200, "impressions": 120000, "clicks": 3200, "conversions": 260},
    {"campaign_id": "NR03", "channel": "LinkedIn Ads", "cost": 3800, "impressions": 50000, "clicks": 1100, "conversions": 95}
]
df_campaigns = pd.DataFrame(campaigns_data)

crm_data = {
    'lead_id': [201, 202, 203, 204, 205, 206, 207, 208, 209, 210],
    'company_size': ['1-10', '10-50', '50-100', '1-10', '100-500', '50-100', '10-50', '100-500', '50-100', '1-10'],
    'sector': ['SaaS', 'Industry', 'Finance', 'HealthTech', 'Retail', 'SaaS', 'Education', 'Industry', 'Finance', 'SaaS'],
    'region': ['Île-de-France', 'Hauts-de-France', 'PACA', 'Occitanie', 'Auvergne-Rhône-Alpes', 'Île-de-France', 'Nouvelle-Aquitaine', 'Grand Est', 'Île-de-France', 'Bretagne'],
    'status': ['MQL', 'SQL', 'Client', 'MQL', 'SQL', 'Client', 'MQL', 'SQL', 'Client', 'MQL']
}
df_crm = pd.DataFrame(crm_data)

df_leads = df_leads[(df_leads['date'] >= '2025-10-01') & (df_leads['date'] <= '2025-10-31')]
df_leads = df_leads.drop_duplicates(subset='lead_id')
df_merged = pd.merge(df_leads, df_crm, on='lead_id', how='inner')
df_final = pd.merge(df_merged, df_campaigns, on='channel', how='left')

# --- CONFIGURATION DU DASHBOARD ---

st.set_page_config(layout="wide", page_title="Dashboard NovaRetail")

st.title("Tableau de Bord Décisionnel - NovaRetail (Octobre 2025)")
st.markdown("Analyse de la performance des campagnes marketing et de la qualité CRM.")

# 1. SECTION KPI (5 KPI sélectionnés)
st.subheader("Indicateurs Clés de Performance")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

# Calculs
total_budget = df_campaigns['cost'].sum()
total_conversions = df_campaigns['conversions'].sum()
avg_cpl = total_budget / total_conversions
total_clients = len(df_final[df_final['status'] == 'Client'])
avg_ctr = (df_campaigns['clicks'].sum() / df_campaigns['impressions'].sum()) * 100

kpi1.metric("Budget Investi", f"{total_budget:,} €")
kpi2.metric("Total Leads", f"{total_conversions}")
kpi3.metric("CPL Moyen", f"{avg_cpl:.2f} €")
kpi4.metric("Clients Signés", f"{total_clients}")
kpi5.metric("CTR Global", f"{avg_ctr:.2f} %")

st.divider()

# 2. SECTION ANALYSE PERFORMANCE ET QUALITÉ
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Performance : CPL par Canal")
    df_campaigns['CPL'] = df_campaigns['cost'] / df_campaigns['conversions']
    fig_cpl = px.bar(
        df_campaigns, 
        x='channel', 
        y='CPL', 
        color='channel',
        labels={'CPL': 'Coût par Lead (€)', 'channel': 'Canal'},
        text_auto='.2f'
    )
    st.plotly_chart(fig_cpl, use_container_width=True)

with col_right:
    st.subheader("Qualité : Répartition des Statuts par Canal")
    status_order = ['MQL', 'SQL', 'Client']
    fig_status = px.histogram(
        df_final, 
        x='channel', 
        color='status', 
        barmode='group',
        category_orders={"status": status_order},
        labels={'channel': 'Canal', 'status': 'Statut CRM', 'count': 'Nombre de Leads'}
    )
    st.plotly_chart(fig_status, use_container_width=True)

st.divider()

# 3. SECTION SEGMENTATION MÉTIER
col_low_left, col_low_right = st.columns(2)

with col_low_left:
    st.subheader("Répartition des Leads par Secteur")
    fig_sector = px.pie(
        df_final, 
        names='sector', 
        hole=0.4
    )
    st.plotly_chart(fig_sector, use_container_width=True)

with col_low_right:
    st.subheader("Analyse par Taille d'Entreprise")
    fig_size = px.bar(
        df_final['company_size'].value_counts().reset_index(),
        x='company_size',
        y='count',
        labels={'company_size': 'Taille entreprise', 'count': 'Nombre de Leads'},
        color_discrete_sequence=['#636EFA']
    )
    st.plotly_chart(fig_size, use_container_width=True)

# 4. TABLEAU DE DONNÉES FILTRÉES (Optionnel pour lisibilité)
if st.checkbox("Afficher les données brutes consolidées"):
    st.dataframe(df_final)
