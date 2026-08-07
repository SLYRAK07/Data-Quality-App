import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from streamlit_option_menu import option_menu

st.set_page_config(page_title="DataTrack", layout="wide")
API_URL = "http://backend:8000"

# ----- STYLE OCP (vert / blanc) -----
st.markdown("""
<style>
    .main { background-color: #FFFFFF; }
    h1, h2, h3 { color: #0B6E4F; font-weight: 700; }
    div[data-testid="stMetric"] {
        background-color: #F4FBF7 !important;
        border: 1px solid #0B6E4F33;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    div[data-testid="stMetric"] * { color: #4a4a4a !important; }
    div[data-testid="stMetricValue"] { color: #0B6E4F !important; font-size: 2rem !important; }
    div[data-testid="stMetricLabel"] p { color: #4a4a4a !important; font-weight: 500 !important; }
    .stButton>button {
        background-color: #0B6E4F;
        color: #FFFFFF;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
    }
    .stButton>button:hover { background-color: #095A40; }
    .hero {
        background: linear-gradient(135deg, #0B6E4F 0%, #14A76C 100%);
        padding: 24px 40px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
    }
    .hero h1 { margin-bottom: 4px; color: white; }
    .hero p { margin: 0; }

    /* ----- CARTES CLIQUABLES DE LA PAGE ACCUEIL ----- */
    .st-key-card_analyse, .st-key-card_dashboard, .st-key-card_historique {
        background-color: #F4FBF7;
        border: 1px solid #0B6E4F22;
        border-radius: 12px;
        padding: 20px;
        cursor: pointer;
        transition: box-shadow 0.2s, transform 0.2s;
    }
    .st-key-card_analyse:hover, .st-key-card_dashboard:hover, .st-key-card_historique:hover {
        box-shadow: 0 4px 14px rgba(11,110,79,0.25);
        transform: translateY(-2px);
    }
    .st-key-card_analyse h3, .st-key-card_dashboard h3, .st-key-card_historique h3 {
        color: #0B6E4F;
        margin-top: 0;
    }
    .st-key-card_analyse p, .st-key-card_dashboard p, .st-key-card_historique p {
        color: #333333;
        font-size: 15px;
        line-height: 1.5;
    }
    /* Le bouton reel reste dans le DOM (necessaire pour declencher le rerun)
       mais invisible : c'est le JS plus bas qui le declenche au clic sur la carte. */
    .st-key-card_analyse button, .st-key-card_dashboard button, .st-key-card_historique button {
        display: none !important;
    }

    div[data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #0B6E4F22;
        overflow: hidden;
    }
    div[data-testid="stDataFrame"] * { color: #1a1a1a !important; }
    div[data-testid="stDataFrame"] [role="columnheader"] {
        background-color: #0B6E4F !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    .range-row {
        background-color: #F4FBF7;
        border: 1px solid #0B6E4F22;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ----- MEMOIRE DE SESSION -----
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "uploaded_filename" not in st.session_state:
    st.session_state["uploaded_filename"] = None
if "range_rows" not in st.session_state:
    st.session_state["range_rows"] = [{"column": None, "min": 0.0, "max": 100.0}]

# ----- MENU LATERAL -----
menu_options = ["Accueil", "Analyse", "Historique", "Tableau de bord"]

if "page" not in st.session_state:
    st.session_state["page"] = "Accueil"

came_from_card = False
manual_select = None
if "menu_redirect" in st.session_state:
    st.session_state["page"] = st.session_state.pop("menu_redirect")
    came_from_card = True
    manual_select = menu_options.index(st.session_state["page"])

with st.sidebar:
    st.markdown("### DataTrack")
    menu_selection = option_menu(
        menu_title=None,
        options=menu_options,
        icons=["house", "upload", "clock-history", "bar-chart-line"],
        default_index=0,
        key="main_menu",
        manual_select=manual_select,
        styles={
            "container": {"padding": "0", "background-color": "#FFFFFF"},
            "icon": {"color": "#0B6E4F", "font-size": "18px"},
            "nav-link": {
                "font-size": "15px", "text-align": "left", "margin": "4px 0",
                "border-radius": "8px", "color": "#333333",
            },
            "nav-link-selected": {"background-color": "#0B6E4F", "color": "white"},
        },
    )

if not came_from_card:
    st.session_state["page"] = menu_selection

selected = st.session_state["page"]

# ----- PAGE ACCUEIL -----
if selected == "Accueil":
    st.markdown("""
    <div class="hero">
        <h1>Suivi de la Qualité des Données</h1>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(key="card_analyse"):
            st.markdown("### Analyse")
            st.write("Analyser un fichier CSV")
            if st.button("Analyse", key="btn_analyse"):
                st.session_state["menu_redirect"] = "Analyse"
                st.rerun()

    with col2:
        with st.container(key="card_dashboard"):
            st.markdown("### Tableau de bord")
            st.write("Visualiser les indicateurs.")
            if st.button("Tableau de bord", key="btn_dashboard"):
                st.session_state["menu_redirect"] = "Tableau de bord"
                st.rerun()

    with col3:
        with st.container(key="card_historique"):
            st.markdown("### Historique")
            st.write("Consulter les analyses précédentes.")
            if st.button("Historique", key="btn_historique"):
                st.session_state["menu_redirect"] = "Historique"
                st.rerun()

    # ----- JS : transmet le clic sur toute la carte vers le bouton cache -----
    st.components.v1.html("""
    <script>
    function attachCardClicks() {
        const doc = window.parent.document;
        const map = {
            "card_analyse": "Analyse",
            "card_dashboard": "Tableau de bord",
            "card_historique": "Historique"
        };
        Object.keys(map).forEach(function(cls) {
            const card = doc.querySelector('.st-key-' + cls);
            if (card && !card.dataset.bound) {
                card.dataset.bound = "true";
                card.addEventListener('click', function() {
                    const btn = card.querySelector('button');
                    if (btn) btn.click();
                });
            }
        });
    }
    setTimeout(attachCardClicks, 300);
    </script>
    """, height=0)

# ----- PAGE ANALYSE -----
elif selected == "Analyse":
    st.title("Analyse d'un fichier CSV")

    uploaded_file = st.file_uploader("Importer un fichier CSV", type="csv")

    if uploaded_file is not None:
        preview_df = pd.read_csv(uploaded_file)
        uploaded_file.seek(0)

        st.subheader("Apercu du fichier")
        st.dataframe(preview_df.head())

        columns = list(preview_df.columns)
        numeric_columns = list(preview_df.select_dtypes(include="number").columns)

        # ----- CONFIGURATIONS SAUVEGARDEES -----
         #st.subheader("Configuration des controles")

         #configs_response = requests.get(f"{API_URL}/configs")
         #saved_configs = configs_response.json() if configs_response.status_code == 200 else []
         #config_names = ["Nouvelle configuration"] + [c["name"] for c in saved_configs]

         #col_load, col_save = st.columns([2, 1])
         #with col_load:
             #chosen_config = st.selectbox("Charger une configuration existante", options=config_names)

         #if chosen_config != "Nouvelle configuration":
             #matching = next(c for c in saved_configs if c["name"] == chosen_config)
             #if st.button("Appliquer cette configuration"):
                 #st.session_state["range_rows"] = matching["range_configs"] if matching["range_configs"] else [{"column": None, "min": 0.0, "max": 100.0}]
                 #st.session_state["loaded_ignore_columns"] = matching["ignore_columns"]
                 #st.rerun()

        # ----- CONTROLES MULTI-COLONNES -----
        st.write("**Colonnes a controler (valeurs hors seuil)**")

        rows_to_remove = None
        for i, row in enumerate(st.session_state["range_rows"]):
            st.markdown('<div class="range-row">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            with c1:
                default_index = numeric_columns.index(row["column"]) + 1 if row.get("column") in numeric_columns else 0
                col_choice = st.selectbox(
                    "Colonne", options=["Aucune"] + numeric_columns,
                    index=default_index, key=f"col_{i}",
                )
                st.session_state["range_rows"][i]["column"] = None if col_choice == "Aucune" else col_choice
            with c2:
                st.session_state["range_rows"][i]["min"] = st.number_input(
                    "Min", value=float(row.get("min", 0.0)), key=f"min_{i}",
                )
            with c3:
                st.session_state["range_rows"][i]["max"] = st.number_input(
                    "Max", value=float(row.get("max", 100.0)), key=f"max_{i}",
                )
            with c4:
                st.write("")
                st.write("")
                if st.button("Retirer", key=f"remove_{i}") and len(st.session_state["range_rows"]) > 1:
                    rows_to_remove = i
            st.markdown('</div>', unsafe_allow_html=True)

        if rows_to_remove is not None:
            st.session_state["range_rows"].pop(rows_to_remove)
            st.rerun()

        if st.button("Ajouter une colonne a controler"):
            st.session_state["range_rows"].append({"column": None, "min": 0.0, "max": 100.0})
            st.rerun()

        default_ignore = [columns[0]] if columns else []
        ignore_columns = st.multiselect(
            "Colonnes a ignorer pour la detection de doublons",
            options=columns,
            default=[c for c in default_ignore if c in columns],
        )

         #with col_save:
             #st.write("")
             #config_name = st.text_input("Nom de la configuration a sauvegarder")
             #if st.button("Sauvegarder cette config") and config_name:
                 #active_configs = [r for r in st.session_state["range_rows"] if r["column"]]
                 #requests.post(f"{API_URL}/configs", data={
                     #"name": config_name,
                     #"range_configs": json.dumps(active_configs),
                     #"ignore_columns": ",".join(ignore_columns) if ignore_columns else "",
                 #})
                 #st.success(f"Configuration '{config_name}' sauvegardee.")

        # ----- LANCER L'ANALYSE -----
        if st.button("Lancer l'analyse"):
            active_configs = [r for r in st.session_state["range_rows"] if r["column"]]

            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            data = {
                "range_configs": json.dumps(active_configs),
                "ignore_columns": ",".join(ignore_columns) if ignore_columns else "",
            }

            response = requests.post(f"{API_URL}/analyze", files=files, data=data)

            if response.status_code == 200:
                st.session_state["analysis_result"] = response.json()
                st.session_state["uploaded_filename"] = uploaded_file.name
                st.session_state["pdf_data"] = data
                st.session_state["pdf_file_bytes"] = uploaded_file.getvalue()
            else:
                st.session_state["analysis_result"] = None
                st.error("Erreur lors de l'analyse du fichier.")
                st.text(response.text)

    # ----- AFFICHAGE DES RESULTATS -----
    if st.session_state["analysis_result"] is not None:
        result = st.session_state["analysis_result"]

        st.subheader(f"Resultats ({st.session_state['uploaded_filename']})")

        pdf_files = {"file": (st.session_state["uploaded_filename"], st.session_state["pdf_file_bytes"], "text/csv")}
        pdf_response = requests.post(f"{API_URL}/generate-report", files=pdf_files, data=st.session_state["pdf_data"])
        if pdf_response.status_code == 200:
            st.download_button(
                label="Telecharger le rapport PDF",
                data=pdf_response.content,
                file_name=f"rapport_{st.session_state['uploaded_filename']}.pdf",
                mime="application/pdf",
                key="download_pdf",
            )

        csv_files = {"file": (st.session_state["uploaded_filename"], st.session_state["pdf_file_bytes"], "text/csv")}
        csv_response = requests.post(f"{API_URL}/export-csv", files=csv_files, data=st.session_state["pdf_data"])
        if csv_response.status_code == 200:
            st.download_button(
                label="Télécharger le rapport CSV",
                data=csv_response.content,
                file_name=f"anomalies_{st.session_state['uploaded_filename']}.csv",
                mime="text/csv",
                key="download_csv",
            )

        total_outliers = sum(len(v) for v in result["outliers_by_column"].values())

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Score de qualite", f"{result['quality_score']} %")
        c2.metric("Valeurs manquantes", len(result["missing"]))
        c3.metric("Valeurs hors seuil", total_outliers)
        c4.metric("Doublons", len(result["duplicates"]))
        c5.metric("Colonnes figées", len(result["frozen_columns"]))

        st.subheader("Detail des anomalies")
        st.write("Valeurs manquantes")
        st.dataframe(pd.DataFrame(result["missing"]))

        if result["outliers_by_column"]:
            for column, rows in result["outliers_by_column"].items():
                st.write(f"Valeurs hors seuil - colonne '{column}'")
                st.dataframe(pd.DataFrame(rows))
        else:
            st.write("Valeurs hors seuil")
            st.info("Aucune colonne controlee.")

        st.write("Doublons")
        st.dataframe(pd.DataFrame(result["duplicates"]))

        st.write("Colonnes à valeur figée")
        if result["frozen_columns"]:
            st.dataframe(pd.DataFrame(result["frozen_columns"]))
        else:
            st.info("Aucune colonne à valeur figée détectée.")

# ----- PAGE HISTORIQUE -----
elif selected == "Historique":
    st.title("Historique des analyses")
    history_response = requests.get(f"{API_URL}/history")
    if history_response.status_code == 200:
        history = history_response.json()
        if history:
            st.dataframe(pd.DataFrame(history), use_container_width=True)
        else:
            st.info("Aucune analyse effectuee pour le moment.")

# ----- PAGE TABLEAU DE BORD -----
elif selected == "Tableau de bord":
    st.title("Tableau de bord")
    history_response = requests.get(f"{API_URL}/history")
    if history_response.status_code == 200:
        history = history_response.json()
        history_df = pd.DataFrame(history)

        if history_df.empty:
            st.info("Aucune analyse effectuee pour le moment. Rendez-vous sur la page Analyse.")
        else:
            dernier = history_df.iloc[-1]

            col_score, col_total, col_nb = st.columns(3)
            col_score.metric("Score de qualite", f"{dernier['quality_score']} %")
            col_total.metric("Lignes analysees", int(dernier["total_rows"]))
            col_nb.metric("Analyses effectuees", len(history_df))

            col_gauge, col_pie = st.columns(2)
            with col_gauge:
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=dernier["quality_score"],
                    title={"text": "Score de qualite (%)"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#0B6E4F"},
                        "steps": [
                            {"range": [0, 50], "color": "#F4A261"},
                            {"range": [50, 80], "color": "#F9C74F"},
                            {"range": [80, 100], "color": "#90BE6D"},
                        ],
                    },
                ))
                fig_gauge.update_layout(height=280, margin=dict(t=40, b=10))
                st.plotly_chart(fig_gauge, use_container_width=True)

            with col_pie:
                repartition = pd.DataFrame({
                    "Type": ["Manquantes", "Hors seuil", "Doublons"],
                    "Nombre": [dernier["missing"], dernier["outliers"], dernier["duplicates"]],
                })
                fig_pie = px.pie(
                    repartition, names="Type", values="Nombre",
                    title="Repartition des anomalies", hole=0.4,
                    color_discrete_sequence=["#0B6E4F", "#14A76C", "#90BE6D"],
                )
                fig_pie.update_layout(height=280, margin=dict(t=40, b=10))
                st.plotly_chart(fig_pie, use_container_width=True)

            if len(history_df) > 1:
                fig_line = px.line(
                    history_df, x="timestamp", y="quality_score",
                    title="Evolution du score de qualite dans le temps", markers=True,
                )
                fig_line.update_traces(line_color="#0B6E4F")
                fig_line.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig_line, use_container_width=True)