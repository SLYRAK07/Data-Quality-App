import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from streamlit_option_menu import option_menu
import os


st.set_page_config(page_title="DataTrack", layout="wide")
API_URL = os.getenv("API_URL", "http://backend:8000")

# ----- AUTHENTIFICATION -----
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

def login_page():
    st.markdown("""
    <style>
        .st-key-login_container {
            max-width: 420px;
            margin: 60px auto;
            background-color: #F4FBF7;
            border: 1px solid #0B6E4F22;
            border-radius: 16px;
            padding: 40px;
        }
        .st-key-login_container label p {
            color: #333333 !important;
        }
        .st-key-login_container .stButton button {
            background-color: #0B6E4F !important;
            color: #FFFFFF !important;
        }
        .st-key-login_container div[role="radiogroup"] {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 20px;
        }
        .st-key-login_container div[role="radiogroup"] label {
            background-color: transparent !important;
        }
        .st-key-login_container div[role="radiogroup"] label p {
            color: #888888 !important;
            font-size: 16px !important;
            font-weight: 600 !important;
        }
        .login-title {
            color: #0B6E4F;
            text-align: center;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .login-subtitle {
            color: #555555;
            text-align: center;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 1.4, 1])
    with col_center:
        with st.container(key="login_container"):
            st.markdown('<div class="login-title">DataTrack</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-subtitle"> Suivi de la Qualité des Données</div>', unsafe_allow_html=True)

            mode = st.radio(
                "Mode",
                options=["Connexion", "Créer un compte"],
                horizontal=True,
                label_visibility="collapsed",
                key="auth_mode",
            )

            st.write("")

            if mode == "Connexion":
                username = st.text_input("Nom d'utilisateur", key="login_username")
                password = st.text_input("Mot de passe", type="password", key="login_password")
                if st.button("Se connecter", use_container_width=True):
                    if username and password:
                        response = requests.post(f"{API_URL}/login", data={"username": username, "password": password})
                        result = response.json()
                        if result["status"] == "ok":
                            st.session_state["authenticated"] = True
                            st.session_state["current_user"] = username
                            st.session_state["current_full_name"] = result.get("full_name", username)
                            st.rerun()
                        else:
                            st.error(result["message"])
                    else:
                        st.warning("Veuillez remplir tous les champs.")

            else:
                new_full_name = st.text_input("Nom complet", key="register_full_name")
                new_email = st.text_input("Email", key="register_email")
                new_username = st.text_input("Nom d'utilisateur", key="register_username")
                new_password = st.text_input("Mot de passe", type="password", key="register_password")
                confirm_password = st.text_input("Confirmer le mot de passe", type="password", key="confirm_password")
                if st.button("Creer le compte", use_container_width=True):
                    if not new_full_name or not new_email or not new_username or not new_password:
                        st.warning("Veuillez remplir tous les champs.")
                    elif "@" not in new_email or "." not in new_email:
                        st.error("Veuillez saisir un email valide.")
                    elif new_password != confirm_password:
                        st.error("Les mots de passe ne correspondent pas.")
                    elif len(new_password) < 6:
                        st.error("Le mot de passe doit contenir au moins 6 caracteres.")
                    else:
                        response = requests.post(f"{API_URL}/register", data={
                            "username": new_username,
                            "full_name": new_full_name,
                            "email": new_email,
                            "password": new_password,
                        })
                        result = response.json()
                        if result["status"] == "ok":
                            st.success("Compte cree ! Vous pouvez maintenant vous connecter.")
                        else:
                            st.error(result["message"])

        st.markdown('</div>', unsafe_allow_html=True)


if "show_login" not in st.session_state:
    st.session_state["show_login"] = False


def landing_page():
    st.markdown("""
    <style>
        .landing-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding:10px 8px;
            border-bottom: 1px solid #EEEEEE;
            margin-bottom: 20px;
        }
        .landing-nav-logo {
            color: #0B6E4F;
            font-size: 22px;
            font-weight: 800;
        }
        .landing-hero {
            background: linear-gradient(135deg, #073D2C 0%, #0B6E4F 45%, #14A76C 100%);
            padding: 32px 50px 28px 50px;
            border-radius: 20px;
            color: white;
            position: relative;
            overflow: hidden;
        }
        .landing-hero::before {
            content: "";
            position: absolute;
            top: -60px;
            right: -60px;
            width: 260px;
            height: 260px;
            border-radius: 50%;
            background: rgba(255,255,255,0.08);
        }
        .landing-badge {
            display: inline-block;
            background: rgba(255,255,255,0.15);
            color: white;
            font-size: 13px;
            font-weight: 600;
            padding: 6px 14px;
            border-radius: 20px;
            margin-bottom: 18px;
        }
        .landing-hero h1 {
            color: white;
            font-size: 38px;
            font-weight: 800;
            margin-bottom: 12px;
            line-height: 1.15;
        }
        .landing-hero p {
            font-size: 17px;
            max-width: 560px;
            line-height: 1.6;
            opacity: 0.92;
            margin-bottom: 0;
        }
        .landing-stats {
            display: flex;
            gap: 40px;
            margin-top: 40px;
            padding-top: 28px;
            border-top: 1px solid rgba(255,255,255,0.2);
            position: relative;
            z-index: 2;
        }
        .landing-stat-value {
            font-size: 30px;
            font-weight: 800;
            color: white;
        }
        .landing-stat-label {
            font-size: 13px;
            color: rgba(255,255,255,0.75);
            margin-top: 2px;
        }
        .landing-footer {
            text-align: center;
            color: #999999;
            font-size: 13px;
            margin-top: 40px;
            padding-top: 24px;
            border-top: 1px solid #EEEEEE;
        }
        .st-key-btn_get_started button {
            background-color: white !important;
            color: #0B6E4F !important;
            font-weight: 700 !important;
            border: none !important;
            padding: 14px 36px !important;
            font-size: 16px !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 14px rgba(0,0,0,0.15) !important;
        }
        .st-key-btn_get_started button:hover {
            background-color: #F0F0F0 !important;
            box-shadow: 0 6px 18px rgba(0,0,0,0.2) !important;
        }

        .block-container {
            padding-top: 1.5rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="landing-nav">
        <div class="landing-nav-logo"> DataTrack</div>
        <div style="color:#888; font-size:14px;"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="landing-hero">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1; position: relative; z-index: 2;">
                <div class="landing-badge">Qualité des données</div>
                <h1>Maitrisez la qualité<br/>de vos données</h1>
                <p>Detectez automatiquement les valeurs manquantes, les anomalies et les doublons
                dans n'importe quel fichier CSV. Un score de qualité clair,
                des rapports prets a partager.</p>
            </div>
            <div style="flex-shrink: 0; margin-left: 30px; position: relative; z-index: 2;">
                <svg width="220" height="180" viewBox="0 0 220 180" xmlns="http://www.w3.org/2000/svg">
                    <rect x="10" y="20" width="200" height="140" rx="12" fill="rgba(255,255,255,0.1)" stroke="rgba(255,255,255,0.25)" stroke-width="1.5"/>
                    <circle cx="35" cy="40" r="4" fill="#FF6B6B"/>
                    <circle cx="50" cy="40" r="4" fill="#FFD166"/>
                    <circle cx="65" cy="40" r="4" fill="#90BE6D"/>
                    <rect x="30" y="60" width="30" height="70" rx="3" fill="rgba(255,255,255,0.35)"/>
                    <rect x="70" y="80" width="30" height="50" rx="3" fill="rgba(255,255,255,0.55)"/>
                    <rect x="110" y="50" width="30" height="80" rx="3" fill="rgba(255,255,255,0.75)"/>
                    <rect x="150" y="95" width="30" height="35" rx="3" fill="rgba(255,255,255,0.45)"/>
                    <polyline points="35,120 65,100 100,110 125,65 165,105" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="125" cy="65" r="4.5" fill="white"/>
                    <path d="M180 45 L188 45 M184 41 L184 49" stroke="white" stroke-width="2" stroke-linecap="round"/>
                    <circle cx="184" cy="45" r="10" fill="none" stroke="white" stroke-width="1.5" opacity="0.6"/>
                </svg>
            </div>
        </div>
        <div class="landing-stats">
            <div>
                <div class="landing-stat-value">3</div>
                <div class="landing-stat-label">Controles automatiques</div>
            </div>
            <div>
                <div class="landing-stat-value">100%</div>
                <div class="landing-stat-label">Colonnes personnalisables</div>
            </div>
            <div>
                <div class="landing-stat-value">PDF / CSV</div>
                <div class="landing-stat-label">Rapports exportables</div>
            </div>
            <div>
                <div class="landing-stat-value">Temps reel</div>
                <div class="landing-stat-label">Suivi du score qualité</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    with st.container(key="btn_get_started"):
        if st.button("Se connecter", use_container_width=False):
            st.session_state["show_login"] = True
            st.rerun()

    st.markdown('<div class="landing-footer">DataTrack &copy; 2026 </div>', unsafe_allow_html=True)


if not st.session_state["authenticated"]:
    if not st.session_state["show_login"]:
        landing_page()
    else:
        login_page()
    st.stop()
# ----- STYLE OCP (vert // blanc) -----
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
    st.caption(f"Connecte : {st.session_state.get('current_full_name', st.session_state['current_user'])}")
    if st.button("Se deconnecter"):
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
        st.session_state["current_full_name"] = None
        st.rerun()
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
    <style>
        .st-key-card_analyse,  .st-key-card_historique ,.st-key-card_dashboard {
            background-color: #F4FBF7;
            border: 1px solid #0B6E4F22;
            border-radius: 12px;
            padding: 20px;
        }
        .st-key-card_analyse h3,  .st-key-card_historique h3 , .st-key-card_dashboard h3 {
            color: #0B6E4F;
            margin-top: 0;
        }
        .st-key-card_analyse p, .st-key-card_historique p , .st-key-card_dashboard p{
            color: #333333;
            font-size: 15px;
            line-height: 1.5;
        }
        .st-key-card_analyse .stButton button, .st-key-card_historique .stButton button , .st-key-card_dashboard .stButton button {
            background-color: transparent !important;
            color: #0B6E4F !important;
            border: 1px solid #0B6E4F !important;
            font-weight: 600 !important;
        }
        .st-key-card_analyse .stButton button:hover , .st-key-card_historique .stButton button:hover , .st-key-card_dashboard .stButton button:hover {
            background-color: #0B6E4F !important;
            color: #FFFFFF !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
        .accueil-hero {
            background: linear-gradient(135deg, #073D2C 0%, #0B6E4F 45%, #14A76C 100%);
            padding: 32px 50px;
            border-radius: 20px;
            color: white;
            margin-bottom: 30px;
        }
        .accueil-hero h1 { color: white; margin-bottom: 6px; }
        .accueil-hero p { color: rgba(255,255,255,0.9); margin: 0; font-size: 16px; }
    </style>
    <div class="accueil-hero">
        <h1>Bienvenue sur DataTrack</h1>
        <p>Choisissez une action ci-dessous pour commencer.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(key="card_analyse"):
            st.markdown('<h3>Analyse</h3><p>Importez un CSV et parametrez vos controles de qualite sur plusieurs colonnes.</p>', unsafe_allow_html=True)
            if st.button("Analyser", key="btn_analyse", use_container_width=True):
                st.session_state["menu_redirect"] = "Analyse"
                st.rerun()


    with col2:
        with st.container(key="card_historique"):
            st.markdown('<h3>Historique</h3><p>Consultez toutes les analyses precedentes.</p>', unsafe_allow_html=True)
            if st.button("Consulter l'historique", key="btn_historique", use_container_width=True):
                st.session_state["menu_redirect"] = "Historique"
                st.rerun()

    with col3:
        with st.container(key="card_dashboard"):
            st.markdown('<h3>Tableau de bord</h3><p>Visualisez le score de qualite et son evolution.</p>', unsafe_allow_html=True)
            if st.button("Voir le tableau de bord", key="btn_dashboard", use_container_width=True):
                st.session_state["menu_redirect"] = "Tableau de bord"
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
        c1.metric("Score de qualité", f"{result['quality_score']} %")
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
            col_score.metric("Score de qualité", f"{dernier['quality_score']} %")
            col_total.metric("Lignes analysees", int(dernier["total_rows"]))
            col_nb.metric("Analyses effectuees", len(history_df))

            col_gauge, col_pie = st.columns(2)
            with col_gauge:
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=dernier["quality_score"],
                    title={"text": "Score de qualité (%)"},
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
                    title="Evolution du score de qualité dans le temps", markers=True,
                )
                fig_line.update_traces(line_color="#0B6E4F")
                fig_line.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig_line, use_container_width=True)