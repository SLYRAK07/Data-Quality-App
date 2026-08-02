import streamlit as st
import requests
import pandas as pd

st.title("Suivi de la qualite des donnees")

uploaded_file = st.file_uploader("Importer un fichier CSV", type="csv")

if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
    response = requests.post("http://127.0.0.1:8000/analyze", files=files)

    if response.status_code == 200:
        result = response.json()

        st.subheader("Indicateurs")
        col1, col2, col3 = st.columns(3)
        col1.metric("Valeurs manquantes", len(result["missing"]))
        col2.metric("Valeurs hors seuil", len(result["outliers"]))
        col3.metric("Doublons", len(result["duplicates"]))

        st.subheader("Detail des anomalies")

        st.write("Valeurs manquantes")
        st.dataframe(pd.DataFrame(result["missing"]))

        st.write("Valeurs hors seuil")
        st.dataframe(pd.DataFrame(result["outliers"]))

        st.write("Doublons")
        st.dataframe(pd.DataFrame(result["duplicates"]))
    else:
        st.error("Erreur lors de l'analyse du fichier.")

st.subheader("Historique des analyses")
history_response = requests.get("http://127.0.0.1:8000/history")
if history_response.status_code == 200:
    history = history_response.json()
    st.dataframe(pd.DataFrame(history))