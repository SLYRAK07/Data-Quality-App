import streamlit as st
import requests
import pandas as pd

st.title("Suivi de la qualite des donnees")

uploaded_file = st.file_uploader("Importer un fichier CSV", type="csv")

if uploaded_file is not None:
    # On lit un aperçu du CSV pour connaitre ses colonnes
    preview_df = pd.read_csv(uploaded_file)
    uploaded_file.seek(0)  # remet le curseur au debut du fichier pour l'envoi

    st.subheader("Apercu du fichier")
    st.dataframe(preview_df.head())

    columns = list(preview_df.columns)
    numeric_columns = list(preview_df.select_dtypes(include="number").columns)

    st.subheader("Parametrage des controles")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        range_column = st.selectbox(
            "Colonne a controler (valeurs hors seuil)",
            options=["Aucune"] + numeric_columns,
        )
    with col_b:
        min_val = st.number_input("Valeur minimum acceptee", value=0.0)
    with col_c:
        max_val = st.number_input("Valeur maximum acceptee", value=100.0)

    ignore_columns = st.multiselect(
        "Colonnes a ignorer pour la detection de doublons (ex: id)",
        options=columns,
        default=[columns[0]] if columns else [],
    )

    if st.button("Lancer l'analyse"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
        params = {
            "ignore_columns": ",".join(ignore_columns) if ignore_columns else None,
        }
        if range_column != "Aucune":
            params["range_column"] = range_column
            params["min_val"] = min_val
            params["max_val"] = max_val

        response = requests.post("http://backend:8000/analyze", files=files, params=params)
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
            st.text(response.text)

st.subheader("Historique des analyses")
history_response = requests.get("http://backend:8000/history")
if history_response.status_code == 200:
    history = history_response.json()
    st.dataframe(pd.DataFrame(history))