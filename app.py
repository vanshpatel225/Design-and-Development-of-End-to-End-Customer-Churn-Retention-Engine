
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Design and Development of End-to-End Customer Churn & Retention Engine",
    page_icon="📊",
    layout="wide"
)


# ==================================================
# 2. MODEL CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "retainIQ_model.pkl"

FEATURES = [
    "Age",
    "Total_Purchase",
    "Account_Manager",
    "Years",
    "Num_Sites"
]


# ==================================================
# 3. LOAD TRAINED MODEL
# ==================================================

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


st.title("📊 Customer Churn Prediction System")

st.write(
    """
    Predict whether customers are likely to leave or stay.

    Upload a CSV file to classify multiple customers
    automatically using the trained Machine Learning model.
    """
)

st.info(
    "Prediction labels: 0 = Stay, 1 = Churn. "
    "Verify that these labels match your model's training data."
)


# ==================================================
# 4. CHECK AND LOAD MODEL
# ==================================================

if not MODEL_PATH.exists():
    st.error(
        "Model file not found! Place "
        "'retainIQ_model.pkl' in the same folder as app.py."
    )
    st.stop()

try:
    model = load_model()

except Exception as error:
    st.error("The trained model could not be loaded.")
    st.exception(error)
    st.stop()


# ==================================================
# 5. CREATE APPLICATION TABS
# ==================================================

single_tab, bulk_tab = st.tabs(
    [
        "👤 Single Customer",
        "📂 Bulk CSV Prediction"
    ]
)


# ==================================================
# 6. SINGLE CUSTOMER PREDICTION
# ==================================================

with single_tab:

    st.header("Predict One Customer")

    with st.form("single_customer_form"):

        col1, col2 = st.columns(2)

        with col1:

            age = st.number_input(
                "Customer Age",
                min_value=18,
                max_value=100,
                value=35
            )

            total_purchase = st.number_input(
                "Total Purchase",
                min_value=0.0,
                value=8000.0
            )

            account_manager = st.selectbox(
                "Has an Account Manager?",
                ["Yes", "No"]
            )

        with col2:

            years = st.number_input(
                "Years as a Customer",
                min_value=0.0,
                value=4.0
            )

            num_sites = st.number_input(
                "Number of Sites",
                min_value=0,
                value=5
            )

        predict_button = st.form_submit_button(
            "Predict Churn",
            type="primary"
        )

    if predict_button:

        customer_data = pd.DataFrame(
            [
                {
                    "Age": age,
                    "Total_Purchase": total_purchase,
                    "Account_Manager": (
                        1 if account_manager == "Yes" else 0
                    ),
                    "Years": years,
                    "Num_Sites": num_sites
                }
            ]
        )

        try:

            prediction = model.predict(customer_data)[0]

            if prediction == 1:

                st.error(
                    "⚠️ Prediction: CHURN (1)"
                )

            elif prediction == 0:

                st.success(
                    "✅ Prediction: STAY (0)"
                )

            else:

                st.warning(
                    f"Unexpected prediction: {prediction}"
                )

        except Exception as error:

            st.error("Prediction failed.")
            st.exception(error)


# ==================================================
# 7. BULK CSV PREDICTION
# ==================================================

with bulk_tab:

    st.header("Bulk Customer Classification")

    st.write(
        "Upload a CSV containing multiple customers. "
        "The model will predict each customer's churn status."
    )

    st.subheader("Required CSV Columns")

    st.code(
        "Age, Total_Purchase, Account_Manager, Years, Num_Sites"
    )

    st.caption(
        "Account_Manager can contain Yes/No or 1/0, "
        "provided this matches the model's training format."
    )

    # --------------------------------------------------
    # CSV TEMPLATE DOWNLOAD
    # --------------------------------------------------

    template = pd.DataFrame(
        [
            {
                "Age": 35,
                "Total_Purchase": 8000,
                "Account_Manager": 1,
                "Years": 4,
                "Num_Sites": 5
            },
            {
                "Age": 42,
                "Total_Purchase": 12000,
                "Account_Manager": 0,
                "Years": 6,
                "Num_Sites": 8
            },
            {
                "Age": 28,
                "Total_Purchase": 4000,
                "Account_Manager": 1,
                "Years": 2,
                "Num_Sites": 3
            }
        ]
    )

    st.download_button(
        label="⬇️ Download Sample CSV Template",
        data=template.to_csv(index=False).encode("utf-8"),
        file_name="customer_template.csv",
        mime="text/csv"
    )

    st.divider()

    # --------------------------------------------------
    # UPLOAD CSV
    # --------------------------------------------------

    uploaded_file = st.file_uploader(
        "Upload Customer CSV File",
        type=["csv"],
        key="bulk_customer_upload"
    )

    if uploaded_file is not None:

        try:

            customers = pd.read_csv(uploaded_file)

            if customers.empty:

                st.error("The uploaded CSV has no customer rows.")

            else:

                st.success(
                    f"Successfully loaded {len(customers)} customer rows."
                )

                st.subheader("Uploaded Customer Data")

                st.dataframe(
                    customers.head(10),
                    use_container_width=True
                )

                missing_columns = [
                    column
                    for column in FEATURES
                    if column not in customers.columns
                ]

                if missing_columns:

                    st.error(
                        "Missing required columns: "
                        + ", ".join(missing_columns)
                    )

                    st.write(
                        "Use the sample CSV template and make sure "
                        "the column names match exactly."
                    )

                else:

                    # ------------------------------------------
                    # VALIDATE AND PREPARE INPUT DATA
                    # ------------------------------------------

                    model_input = customers[FEATURES].copy()

                    # Convert Yes/No to 1/0 for Account_Manager.
                    account_values = (
                        model_input["Account_Manager"]
                        .astype(str)
                        .str.strip()
                        .str.lower()
                    )

                    account_mapping = {
                        "yes": 1,
                        "no": 0,
                        "true": 1,
                        "false": 0,
                        "1": 1,
                        "0": 0
                    }

                    model_input["Account_Manager"] = (
                        account_values.map(account_mapping)
                    )

                    # Convert all model features to numbers.
                    for column in FEATURES:

                        model_input[column] = pd.to_numeric(
                            model_input[column],
                            errors="coerce"
                        )

                    # Check missing and invalid values.
                    if model_input.isnull().any().any():

                        invalid_columns = model_input.columns[
                            model_input.isnull().any()
                        ].tolist()

                        st.error(
                            "Missing or invalid values found in: "
                            + ", ".join(invalid_columns)
                        )

                        st.write(
                            "Fix the invalid cells in your CSV "
                            "and upload it again."
                        )

                    else:

                        # --------------------------------------
                        # PREDICT ALL CUSTOMERS
                        # --------------------------------------

                        if st.button(
                            "🚀 Predict All Customers",
                            type="primary",
                            use_container_width=True
                        ):

                            try:

                                predictions = model.predict(model_input)

                                results = customers.copy()

                                results["Churn_Prediction"] = (
                                    predictions
                                )

                                # Add readable status labels.
                                results["Churn_Status"] = (
                                    results["Churn_Prediction"]
                                    .map({
                                        0: "Stay",
                                        1: "Churn"
                                    })
                                    .fillna("Unknown")
                                )

                                # ----------------------------------
                                # SUMMARY METRICS
                                # ----------------------------------

                                total_customers = len(results)

                                churn_count = int(
                                    (predictions == 1).sum()
                                )

                                stay_count = int(
                                    (predictions == 0).sum()
                                )

                                other_count = (
                                    total_customers
                                    - churn_count
                                    - stay_count
                                )

                                col1, col2, col3 = st.columns(3)

                                col1.metric(
                                    "Total Customers",
                                    total_customers
                                )

                                col2.metric(
                                    "Predicted Churn",
                                    churn_count
                                )

                                col3.metric(
                                    "Predicted Stay",
                                    stay_count
                                )

                                if other_count > 0:

                                    st.warning(
                                        f"{other_count} rows returned "
                                        "unexpected prediction labels."
                                    )

                                st.divider()

                                # ----------------------------------
                                # FILTER RESULTS BY GROUP
                                # ----------------------------------

                                st.subheader(
                                    "Customer Classification Results"
                                )

                                selected_group = st.selectbox(
                                    "Filter Customers",
                                    [
                                        "All Customers",
                                        "Churn (1)",
                                        "Stay (0)"
                                    ]
                                )

                                if selected_group == "Churn (1)":

                                    displayed_results = results[
                                        results["Churn_Prediction"] == 1
                                    ]

                                elif selected_group == "Stay (0)":

                                    displayed_results = results[
                                        results["Churn_Prediction"] == 0
                                    ]

                                else:

                                    displayed_results = results

                                st.write(
                                    f"Showing {len(displayed_results)} "
                                    "customers."
                                )

                                st.dataframe(
                                    displayed_results,
                                    use_container_width=True
                                )

                                # ----------------------------------
                                # DOWNLOAD COMPLETE RESULTS
                                # ----------------------------------

                                csv_output = results.to_csv(
                                    index=False
                                ).encode("utf-8-sig")

                                st.download_button(
                                    label="⬇️ Download All Prediction Results",
                                    data=csv_output,
                                    file_name="churn_predictions.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )

                            except Exception as error:

                                st.error(
                                    "Bulk prediction failed. "
                                    "The model may expect different "
                                    "features or preprocessing."
                                )

                                st.exception(error)

        except Exception as error:

            st.error(
                "Could not read the CSV. Please check that "
                "the uploaded file is a valid CSV."
            )

            st.exception(error)
