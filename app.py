from pathlib import Path

import altair as alt
import joblib
import pandas as pd
import streamlit as st


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="RetainIQ | Customer Churn & Retention Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# 2. COLOUR PALETTES
# ==================================================
# Add or edit palettes here. Each one controls the page background,
# cards, header banner, buttons and chart colours.

PALETTES = {
    "Ocean Mist": {
        "dark": False,
        "bg1": "#E4F1F6", "bg2": "#F8FBFC",
        "surface": "rgba(255,255,255,0.78)", "border": "rgba(20,48,74,0.14)",
        "sidebar": "#DCEBF2", "text": "#14304A",
        "primary": "#14304A", "on_primary": "#FFFFFF",
        "hero1": "#14304A", "hero2": "#1F6F8B",
        "stay": "#0F9D8A", "churn": "#E4572E", "warn": "#E9A23B",
    },
    "Forest Sage": {
        "dark": False,
        "bg1": "#E6EFE0", "bg2": "#FAFBF6",
        "surface": "rgba(255,255,255,0.80)", "border": "rgba(38,68,47,0.15)",
        "sidebar": "#DCE8D5", "text": "#1F3A29",
        "primary": "#26442F", "on_primary": "#FFFFFF",
        "hero1": "#26442F", "hero2": "#4F8A63",
        "stay": "#3C8D5A", "churn": "#C8553D", "warn": "#D9A441",
    },
    "Sunset Coral": {
        "dark": False,
        "bg1": "#FFE9DF", "bg2": "#FFF9F5",
        "surface": "rgba(255,255,255,0.82)", "border": "rgba(122,46,59,0.15)",
        "sidebar": "#FBDDD0", "text": "#4A1F29",
        "primary": "#7A2E3B", "on_primary": "#FFFFFF",
        "hero1": "#7A2E3B", "hero2": "#D1495B",
        "stay": "#2A9D8F", "churn": "#E63946", "warn": "#F4A261",
    },
    "Royal Violet": {
        "dark": False,
        "bg1": "#ECE6FA", "bg2": "#FAF8FE",
        "surface": "rgba(255,255,255,0.80)", "border": "rgba(59,42,107,0.15)",
        "sidebar": "#E3DBF6", "text": "#2E2150",
        "primary": "#3B2A6B", "on_primary": "#FFFFFF",
        "hero1": "#3B2A6B", "hero2": "#7457E0",
        "stay": "#1FA67A", "churn": "#E5484D", "warn": "#F0A020",
    },
    "Slate & Gold": {
        "dark": False,
        "bg1": "#ECEEF1", "bg2": "#FBFBFC",
        "surface": "rgba(255,255,255,0.85)", "border": "rgba(35,42,52,0.14)",
        "sidebar": "#E2E5EA", "text": "#232A34",
        "primary": "#232A34", "on_primary": "#FFFFFF",
        "hero1": "#232A34", "hero2": "#5B6577",
        "stay": "#2E8B6E", "churn": "#D4572B", "warn": "#C99A2E",
    },
    "Midnight Blue (dark)": {
        "dark": True,
        "bg1": "#0A1020", "bg2": "#16223D",
        "surface": "rgba(255,255,255,0.06)", "border": "rgba(255,255,255,0.14)",
        "sidebar": "#0D1528", "text": "#E6EDF7",
        "primary": "#3B82F6", "on_primary": "#FFFFFF",
        "hero1": "#1E3A8A", "hero2": "#2563EB",
        "stay": "#34D399", "churn": "#FB7185", "warn": "#FBBF24",
    },
    "Charcoal Amber (dark)": {
        "dark": True,
        "bg1": "#14120E", "bg2": "#2A241B",
        "surface": "rgba(255,255,255,0.06)", "border": "rgba(255,255,255,0.14)",
        "sidebar": "#191611", "text": "#F3EDE2",
        "primary": "#F59E0B", "on_primary": "#1A1203",
        "hero1": "#78350F", "hero2": "#B45309",
        "stay": "#4ADE80", "churn": "#F87171", "warn": "#FACC15",
    },
}

with st.sidebar:
    st.markdown("### Colour theme")
    palette_name = st.selectbox(
        "Choose a palette",
        list(PALETTES),
        key="palette",
        label_visibility="collapsed",
    )
    P = PALETTES[palette_name]

    swatches = "".join(
        f'<span style="display:inline-block;width:26px;height:26px;border-radius:50%;'
        f'margin-right:6px;background:{P[key]};border:1px solid {P["border"]}"></span>'
        for key in ("hero1", "hero2", "stay", "churn", "warn")
    )
    st.markdown(swatches, unsafe_allow_html=True)

STAY_COLOR = P["stay"]
CHURN_COLOR = P["churn"]
WARN_COLOR = P["warn"]
TEXT = P["text"]


def style_chart(chart):
    """Make Altair charts follow the selected palette."""
    return (
        chart.configure(background="transparent")
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=TEXT, titleColor=TEXT,
            gridColor=P["border"], domainColor=P["border"], tickColor=P["border"],
        )
        .configure_legend(labelColor=TEXT, titleColor=TEXT)
    )


# ==================================================
# 3. STYLING
# ==================================================

dark_overrides = ""
if P["dark"]:
    dark_overrides = f"""
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] {{
        background: rgba(255,255,255,0.07) !important;
        border-color: {P["border"]} !important;
    }}
    .stApp input, .stApp div[data-baseweb="select"] * {{
        color: {TEXT} !important;
        -webkit-text-fill-color: {TEXT} !important;
    }}
    div[data-testid="stAlert"] {{
        background: rgba(255,255,255,0.08) !important;
    }}
    div[data-testid="stExpander"] {{
        border-color: {P["border"]} !important;
    }}
    """

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"], .stMarkdown, .stButton button {{
        font-family: 'Inter', sans-serif;
    }}
    h1, h2, h3, .hero-title {{
        font-family: 'Sora', sans-serif !important;
        letter-spacing: -0.01em;
    }}

    /* Page background: soft gradient with two colour glows */
    .stApp {{
        background:
            radial-gradient(circle at 8% 6%, {P["hero2"]}33 0, transparent 38%),
            radial-gradient(circle at 94% 92%, {P["stay"]}26 0, transparent 40%),
            linear-gradient(160deg, {P["bg1"]} 0%, {P["bg2"]} 100%);
        background-attachment: fixed;
        color: {TEXT};
    }}
    header[data-testid="stHeader"] {{
        background: transparent;
    }}
    section[data-testid="stSidebar"] {{
        background: {P["sidebar"]};
        border-right: 1px solid {P["border"]};
    }}

    /* Text colours that follow the palette */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stCaptionContainer"],
    .stApp [data-testid="stWidgetLabel"] p,
    .stApp [data-testid="stMetricLabel"] p,
    .stApp [data-testid="stMetricValue"],
    .stApp button[data-baseweb="tab"] p {{
        color: {TEXT};
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }}

    /* Hero */
    .hero {{
        background: linear-gradient(120deg, {P["hero1"]} 0%, {P["hero2"]} 100%);
        border-radius: 18px;
        padding: 2rem 2.25rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px {P["hero1"]}44;
    }}
    .stApp .hero .hero-title {{
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.35rem 0;
        color: #FFFFFF;
    }}
    .stApp .hero .hero-sub {{
        font-size: 1rem;
        margin: 0;
        max-width: 640px;
        color: rgba(255, 255, 255, 0.85);
        line-height: 1.55;
    }}

    /* Metric cards */
    div[data-testid="stMetric"] {{
        background: {P["surface"]};
        border: 1px solid {P["border"]};
        border-left: 5px solid {P["primary"]};
        border-radius: 12px;
        padding: 1rem 1.25rem;
    }}
    div[data-testid="stMetricLabel"] p {{
        font-size: 0.85rem;
        opacity: 0.8;
    }}
    div[data-testid="stMetricValue"] {{
        font-family: 'Sora', sans-serif;
        font-weight: 700;
    }}

    /* Forms and expanders as panels */
    div[data-testid="stForm"] {{
        background: {P["surface"]};
        border: 1px solid {P["border"]};
        border-radius: 14px;
        padding: 1.25rem;
    }}
    div[data-testid="stExpander"] {{
        background: {P["surface"]};
        border-radius: 12px;
    }}

    /* Result panel for a single prediction */
    .result {{
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 0.75rem;
        border: 1px solid {P["border"]};
    }}
    .result.churn {{ background: {CHURN_COLOR}20; border-left: 6px solid {CHURN_COLOR}; }}
    .result.stay  {{ background: {STAY_COLOR}20; border-left: 6px solid {STAY_COLOR}; }}
    .stApp .result h3 {{ margin: 0 0 0.25rem 0; color: {TEXT}; }}
    .stApp .result p  {{ margin: 0; opacity: 0.85; color: {TEXT}; }}

    /* Risk bar */
    .riskbar {{
        height: 12px;
        border-radius: 999px;
        background: {P["border"]};
        overflow: hidden;
        margin: 0.5rem 0 0.25rem 0;
    }}
    .riskbar > div {{ height: 100%; border-radius: 999px; }}

    /* Tabs */
    button[data-baseweb="tab"] {{
        font-weight: 600;
        padding: 0.6rem 1.1rem;
    }}
    div[data-baseweb="tab-highlight"] {{
        background-color: {P["primary"]} !important;
    }}

    /* Buttons */
    .stButton button[kind="primary"],
    .stFormSubmitButton button[kind="primary"] {{
        background: {P["primary"]};
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1rem;
    }}
    .stApp .stButton button[kind="primary"] p,
    .stApp .stFormSubmitButton button[kind="primary"] p {{
        color: {P["on_primary"]};
    }}
    .stButton button[kind="primary"]:hover,
    .stFormSubmitButton button[kind="primary"]:hover {{
        background: {P["hero2"]};
    }}
    .stDownloadButton button {{
        border-radius: 10px;
        font-weight: 600;
        background: {P["surface"]};
        border: 1px solid {P["border"]};
    }}
    .stApp .stDownloadButton button p {{
        color: {TEXT};
    }}

    {dark_overrides}

    /* Hide default Streamlit chrome */
    #MainMenu, footer {{ visibility: hidden; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# 3. MODEL CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "retainIQ_model.pkl"

FEATURES = [
    "Age",
    "Total_Purchase",
    "Account_Manager",
    "Years",
    "Num_Sites",
]

ACCOUNT_MAPPING = {
    "yes": 1,
    "no": 0,
    "true": 1,
    "false": 0,
    "1": 1,
    "0": 0,
    "1.0": 1,
    "0.0": 0,
}


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


def churn_probability(model, data):
    """Return P(churn) for each row, or None if the model has no predict_proba."""
    if not hasattr(model, "predict_proba"):
        return None
    try:
        proba = model.predict_proba(data)
        classes = list(getattr(model, "classes_", [0, 1]))
        if 1 not in classes:
            return None
        return proba[:, classes.index(1)]
    except Exception:
        return None


def risk_level(p):
    if p >= 0.70:
        return "High"
    if p >= 0.40:
        return "Medium"
    return "Low"


def risk_color(p):
    if p >= 0.70:
        return CHURN_COLOR
    if p >= 0.40:
        return WARN_COLOR
    return STAY_COLOR


def prepare_bulk_input(customers):
    """Clean the uploaded CSV and return model-ready data."""
    model_input = customers[FEATURES].copy()

    model_input["Account_Manager"] = (
        model_input["Account_Manager"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(ACCOUNT_MAPPING)
    )

    for column in FEATURES:
        model_input[column] = pd.to_numeric(model_input[column], errors="coerce")

    return model_input


# ==================================================
# 4. HEADER
# ==================================================

st.markdown(
    """
    <div class="hero">
        <p class="hero-title">RetainIQ: Customer Churn & Retention Engine</p>
        <p class="hero-sub">
            See which customers are likely to leave and act before they do.
            Check one customer, or upload a CSV to score your whole customer base.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# 5. LOAD MODEL
# ==================================================

if not MODEL_PATH.exists():
    st.error(
        "Model file not found. Place 'retainIQ_model.pkl' in the same folder as app.py."
    )
    st.stop()

try:
    model = load_model()
except Exception as error:
    st.error("The trained model could not be loaded.")
    st.exception(error)
    st.stop()


# ==================================================
# 6. SIDEBAR
# ==================================================

with st.sidebar:
    st.markdown("### About this tool")
    st.write(
        "Uses a trained machine learning model to classify each customer "
        "as likely to **stay** or **churn**."
    )

    st.markdown("### How to read results")
    st.markdown(
        f"""
        - <span style="color:{STAY_COLOR};font-weight:600">0 = Stay</span>
        - <span style="color:{CHURN_COLOR};font-weight:600">1 = Churn</span>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Check that these labels match your model's training data.")

    st.markdown("### Model inputs")
    for feature in FEATURES:
        st.markdown(f"- `{feature}`")

    st.divider()
    st.caption("Risk levels: Low below 40%, Medium 40-70%, High above 70% churn probability.")


# ==================================================
# 7. TABS
# ==================================================

single_tab, bulk_tab = st.tabs(["👤 Single customer", "📂 Bulk CSV prediction"])


# ==================================================
# 8. SINGLE CUSTOMER
# ==================================================

with single_tab:

    left, right = st.columns([1.1, 1], gap="large")

    with left:
        st.subheader("Customer details")

        with st.form("single_customer_form"):
            col1, col2 = st.columns(2)

            with col1:
                age = st.number_input("Customer age", min_value=18, max_value=100, value=35)
                total_purchase = st.number_input(
                    "Total purchase", min_value=0.0, value=8000.0, step=500.0
                )
                account_manager = st.selectbox("Has an account manager?", ["Yes", "No"])

            with col2:
                years = st.number_input(
                    "Years as a customer", min_value=0.0, value=4.0, step=0.5
                )
                num_sites = st.number_input("Number of sites", min_value=0, value=5)

            predict_button = st.form_submit_button(
                "Predict churn", type="primary", use_container_width=True
            )

    with right:
        st.subheader("Prediction")

        if not predict_button:
            st.info("Enter the customer details and select **Predict churn** to see the result.")
        else:
            customer_data = pd.DataFrame(
                [
                    {
                        "Age": age,
                        "Total_Purchase": total_purchase,
                        "Account_Manager": 1 if account_manager == "Yes" else 0,
                        "Years": years,
                        "Num_Sites": num_sites,
                    }
                ]
            )

            try:
                prediction = model.predict(customer_data)[0]
                proba = churn_probability(model, customer_data)

                if prediction == 1:
                    st.markdown(
                        """
                        <div class="result churn">
                            <h3>⚠️ Likely to churn</h3>
                            <p>This customer shows a pattern similar to customers who left.</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                elif prediction == 0:
                    st.markdown(
                        """
                        <div class="result stay">
                            <h3>✅ Likely to stay</h3>
                            <p>This customer shows a pattern similar to customers who stayed.</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.warning(f"Unexpected prediction label: {prediction}")

                if proba is not None:
                    p = float(proba[0])
                    st.metric("Churn probability", f"{p:.0%}", help="Model's estimated chance this customer leaves.")
                    st.markdown(
                        f'<div class="riskbar"><div style="width:{p * 100:.0f}%;background:{risk_color(p)}"></div></div>',
                        unsafe_allow_html=True,
                    )
                    st.caption(f"Risk level: **{risk_level(p)}**")

                    if p >= 0.40:
                        st.markdown("**Suggested next step**")
                        st.write(
                            "Reach out with a personal check-in. Assigning an account "
                            "manager or reviewing the customer's site usage can help."
                        )

            except Exception as error:
                st.error("Prediction failed. The model may expect different features.")
                st.exception(error)


# ==================================================
# 9. BULK CSV
# ==================================================

with bulk_tab:

    st.subheader("Score many customers at once")

    step1, step2 = st.columns([1.2, 1], gap="large")

    with step1:
        st.markdown("**1. Prepare your file**")
        st.write("Your CSV needs these columns, spelled exactly like this:")
        st.code(", ".join(FEATURES), language=None)
        st.caption("Account_Manager can be Yes/No or 1/0.")

    with step2:
        st.markdown("**2. Start from a template**")
        template = pd.DataFrame(
            [
                {"Age": 35, "Total_Purchase": 8000, "Account_Manager": 1, "Years": 4, "Num_Sites": 5},
                {"Age": 42, "Total_Purchase": 12000, "Account_Manager": 0, "Years": 6, "Num_Sites": 8},
                {"Age": 28, "Total_Purchase": 4000, "Account_Manager": 1, "Years": 2, "Num_Sites": 3},
            ]
        )
        st.download_button(
            label="⬇️ Download sample CSV",
            data=template.to_csv(index=False).encode("utf-8"),
            file_name="customer_template.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.divider()
    st.markdown("**3. Upload your customers**")

    uploaded_file = st.file_uploader(
        "Upload customer CSV",
        type=["csv"],
        key="bulk_customer_upload",
        label_visibility="collapsed",
    )

    if uploaded_file is None:
        st.info("Upload a CSV file to get started.")
    else:
        try:
            customers = pd.read_csv(uploaded_file)
        except Exception as error:
            st.error("Could not read the file. Check that it is a valid CSV.")
            st.exception(error)
            st.stop()

        if customers.empty:
            st.error("The uploaded CSV has no customer rows.")
            st.stop()

        missing_columns = [c for c in FEATURES if c not in customers.columns]

        if missing_columns:
            st.error("Missing required columns: " + ", ".join(missing_columns))
            st.write("Use the sample template and make sure the column names match exactly.")
            st.stop()

        st.success(f"Loaded {len(customers):,} customers.")

        with st.expander("Preview uploaded data", expanded=False):
            st.dataframe(customers.head(10), use_container_width=True)

        model_input = prepare_bulk_input(customers)

        if model_input.isnull().any().any():
            invalid_columns = model_input.columns[model_input.isnull().any()].tolist()
            st.error("Missing or invalid values found in: " + ", ".join(invalid_columns))
            st.write("Fix those cells in your CSV and upload it again.")
            st.stop()

        if st.button("🚀 Predict all customers", type="primary", use_container_width=True):
            st.session_state["bulk_results"] = None
            try:
                predictions = model.predict(model_input)
                proba = churn_probability(model, model_input)

                results = customers.copy()
                results["Churn_Prediction"] = predictions
                results["Churn_Status"] = (
                    results["Churn_Prediction"].map({0: "Stay", 1: "Churn"}).fillna("Unknown")
                )

                if proba is not None:
                    results["Churn_Probability"] = proba.round(3)
                    results["Risk_Level"] = [risk_level(p) for p in proba]

                st.session_state["bulk_results"] = results

            except Exception as error:
                st.error(
                    "Bulk prediction failed. The model may expect different "
                    "features or preprocessing."
                )
                st.exception(error)

        results = st.session_state.get("bulk_results")

        if results is not None:
            st.divider()
            st.subheader("Results")

            total = len(results)
            churn_count = int((results["Churn_Prediction"] == 1).sum())
            stay_count = int((results["Churn_Prediction"] == 0).sum())
            other_count = total - churn_count - stay_count
            churn_rate = churn_count / total if total else 0

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total customers", f"{total:,}")
            m2.metric("Predicted to churn", f"{churn_count:,}")
            m3.metric("Predicted to stay", f"{stay_count:,}")
            m4.metric("Churn rate", f"{churn_rate:.1%}")

            if other_count > 0:
                st.warning(f"{other_count} rows returned unexpected prediction labels.")

            # ---------- Charts ----------
            chart_left, chart_right = st.columns(2, gap="large")

            with chart_left:
                st.markdown("**Churn vs stay**")
                split = pd.DataFrame(
                    {"Status": ["Stay", "Churn"], "Customers": [stay_count, churn_count]}
                )
                split_chart = (
                    alt.Chart(split)
                    .mark_arc(innerRadius=60)
                    .encode(
                        theta="Customers:Q",
                        color=alt.Color(
                            "Status:N",
                            scale=alt.Scale(domain=["Stay", "Churn"], range=[STAY_COLOR, CHURN_COLOR]),
                            legend=alt.Legend(title=None, orient="bottom"),
                        ),
                        tooltip=["Status", "Customers"],
                    )
                    .properties(height=260)
                )
                st.altair_chart(style_chart(split_chart), use_container_width=True, theme=None)

            with chart_right:
                if "Risk_Level" in results.columns:
                    st.markdown("**Customers by risk level**")
                    order = ["Low", "Medium", "High"]
                    risk_counts = (
                        results["Risk_Level"]
                        .value_counts()
                        .reindex(order, fill_value=0)
                        .reset_index()
                    )
                    risk_counts.columns = ["Risk", "Customers"]
                    risk_chart = (
                        alt.Chart(risk_counts)
                        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
                        .encode(
                            x=alt.X("Risk:N", sort=order, title=None),
                            y=alt.Y("Customers:Q", title=None),
                            color=alt.Color(
                                "Risk:N",
                                scale=alt.Scale(domain=order, range=[STAY_COLOR, WARN_COLOR, CHURN_COLOR]),
                                legend=None,
                            ),
                            tooltip=["Risk", "Customers"],
                        )
                        .properties(height=260)
                    )
                    st.altair_chart(style_chart(risk_chart), use_container_width=True, theme=None)
                else:
                    st.markdown("**Customers by status**")
                    st.caption("Risk levels are unavailable because this model does not provide probabilities.")

            # ---------- Filters ----------
            st.markdown("**Customer list**")

            f1, f2 = st.columns([1, 1])
            with f1:
                selected_group = st.selectbox(
                    "Show", ["All customers", "Churn (1)", "Stay (0)"]
                )
            with f2:
                if "Risk_Level" in results.columns:
                    selected_risk = st.multiselect(
                        "Risk level", ["High", "Medium", "Low"], default=["High", "Medium", "Low"]
                    )
                else:
                    selected_risk = None

            displayed = results
            if selected_group == "Churn (1)":
                displayed = displayed[displayed["Churn_Prediction"] == 1]
            elif selected_group == "Stay (0)":
                displayed = displayed[displayed["Churn_Prediction"] == 0]

            if selected_risk is not None:
                displayed = displayed[displayed["Risk_Level"].isin(selected_risk)]

            if "Churn_Probability" in displayed.columns:
                displayed = displayed.sort_values("Churn_Probability", ascending=False)

            st.caption(f"Showing {len(displayed):,} of {total:,} customers.")

            column_config = {}
            if "Churn_Probability" in displayed.columns:
                column_config["Churn_Probability"] = st.column_config.ProgressColumn(
                    "Churn probability", min_value=0.0, max_value=1.0, format="%.0f%%"
                )

            st.dataframe(
                displayed,
                use_container_width=True,
                hide_index=True,
                column_config=column_config,
            )

            # ---------- Downloads ----------
            d1, d2 = st.columns(2)
            with d1:
                st.download_button(
                    label="⬇️ Download all results",
                    data=results.to_csv(index=False).encode("utf-8-sig"),
                    file_name="churn_predictions.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with d2:
                st.download_button(
                    label="⬇️ Download at-risk customers only",
                    data=results[results["Churn_Prediction"] == 1]
                    .to_csv(index=False)
                    .encode("utf-8-sig"),
                    file_name="at_risk_customers.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
