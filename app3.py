import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Configuration de la page
st.set_page_config(page_title="Analyse de Série Temporelle", layout="wide")

st.title("Application d'Analyse et Prédiction de Séries Temporelles")
st.markdown("""
Cette interface interactive permet de charger des données, d'analyser la stationnarité et de réaliser des prévisions 
professionnelles à l'aide des modèles **ARIMA** et **SARIMA**.
""")

# --- 1. CHARGEMENT DES DONNÉES ---
st.sidebar.header("1. Chargement des données")
uploaded_file = st.sidebar.file_uploader("Charger un fichier CSV ou Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Lecture du fichier selon le format
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Vérification et configuration de la colonne Date
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            st.sidebar.success("Index temporel configuré.")
        else:
            st.sidebar.error("Erreur : La colonne 'Date' est manquante.")
        
        # Choix de la variable à prédire (ex: CO(GT), T, ou RH)
        target_col = st.selectbox("Sélectionnez la variable à analyser", df.columns)
        
        # Nettoyage : On remplace les 0.0 (souvent des erreurs capteurs) par la valeur précédente
        df[target_col] = df[target_col].replace(0, pd.NA).ffill()

        # --- 2. VISUALISATION (Exigence PDF) ---
        st.header("2. Visualisation des Données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Série Originale")
            fig1, ax1 = plt.subplots(figsize=(10, 5))
            ax1.plot(df.index, df[target_col], color='#1f77b4', label="Valeurs Observées")
            ax1.set_title(f"Évolution temporelle de {target_col}")
            ax1.set_ylabel("Valeur")
            ax1.legend()
            st.pyplot(fig1)

        with col2:
            st.subheader("Décomposition STL")
            # period=7 car les données de qualité de l'air suivent souvent un cycle de 7 jours (semaine)
            res = STL(df[target_col], period=7).fit()
            fig2, (ax_t, ax_s, ax_r) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
            res.trend.plot(ax=ax_t, title="Tendance (Trend)")
            res.seasonal.plot(ax=ax_s, title="Saisonnalité (Seasonality)")
            res.resid.plot(ax=ax_r, title="Résidus (Bruit)")
            plt.tight_layout()
            st.pyplot(fig2)

        # --- 3. STATIONNARITÉ (Exigence PDF : Test ADF + Message) ---
        st.write("---")
        st.header("3. Analyse de Stationnarité")
        
        result = adfuller(df[target_col].dropna())
        p_value = result[1]
        
        st.metric(label="Valeur p (Test ADF)", value=f"{p_value:.4f}")

        if p_value <= 0.05:
            st.success(" La série est **stationnaire** (p-value ≤ 0.05).")
            st.info("Message explicatif : Les propriétés statistiques ne changent pas dans le temps. Vous pouvez utiliser d=0.")
        else:
            st.warning("⚠️ La série n'est **pas stationnaire** (p-value > 0.05).")
            st.info("Message explicatif : Une tendance est présente. Il est conseillé d'utiliser d=1 (différenciation) dans le modèle.")



        # --- 4 & 5. PARAMÉTRAGE ET MODÈLE ---
        st.write("---")
        st.header("4. Paramétrage du Modèle")
        
        model_choice = st.radio("Type de modèle :", ("ARIMA", "SARIMA"))

        st.subheader("Paramètres de base (p, d, q)")
        cp, cd, cq = st.columns(3)
        with cp: p = st.number_input("p (AR)", min_value=0, value=1)
        with cd: d = st.number_input("d (Diff)", min_value=0, value=1)
        with cq: q = st.number_input("q (MA)", min_value=0, value=1)

        seasonal_order = (0, 0, 0, 0)
        if model_choice == "SARIMA":
            st.subheader("Paramètres Saisonniers (P, D, Q, s)")
            sp, sd, sq, ss = st.columns(4)
            with sp: P = st.number_input("P (Saisonnier AR)", min_value=0, value=0)
            with sd: D = st.number_input("D (Diff Saisonnière)", min_value=0, value=0)
            with sq: Q = st.number_input("Q (Saisonnier MA)", min_value=0, value=0)
            with ss: s = st.number_input("s (Période, ex: 7)", min_value=1, value=7)
            seasonal_order = (P, D, Q, s)

        # Choix de l'horizon de prédiction
        horizon = st.slider("Horizon de prédiction (pas de temps futurs)", 1, 60, 30)

        if st.button(f"Entraîner et Prédire"):
            try:
                with st.spinner('Calculs en cours...'):
                    # SARIMAX gère les deux types de modèles
                    model = SARIMAX(df[target_col], order=(p, d, q), seasonal_order=seasonal_order)
                    results = model.fit(disp=False)
                    st.session_state['results'] = results
                    st.success("Modèle entraîné !")

            except Exception as e:
                st.error(f"Erreur d'entraînement : {e}")

        # --- 6. RÉSULTATS ET COMPARAISON (Exigence PDF) ---
        if 'results' in st.session_state:
            st.write("---")
            st.header("5. Résultats de la Prédiction")
            
            res_fit = st.session_state['results']
            forecast = res_fit.get_forecast(steps=horizon)
            forecast_df = forecast.summary_frame()

            st.subheader("Graphique Global")
            fig_res, ax_res = plt.subplots(figsize=(12, 6))
            ax_res.plot(df.index, df[target_col], label="Historique")
            ax_res.plot(forecast_df.index, forecast_df['mean'], label="Prédiction", color='red', linestyle='--')
            ax_res.fill_between(forecast_df.index, forecast_df['mean_ci_lower'], forecast_df['mean_ci_upper'], color='pink', alpha=0.3, label="Confiance 95%")
            ax_res.legend()
            st.pyplot(fig_res)

            st.subheader("Comparaison : Zoom sur la période récente")
            fig_z, ax_z = plt.subplots(figsize=(12, 5))
            # On affiche les 20 derniers jours + le futur
            ax_z.plot(df[target_col].tail(20), label="Observé (Recent)", marker='o')
            ax_z.plot(forecast_df['mean'], label="Prédiction", color='red', marker='x', linestyle='--')
            ax_z.legend()
            st.pyplot(fig_z)

    except Exception as e:
        st.error(f"Erreur : {e}")