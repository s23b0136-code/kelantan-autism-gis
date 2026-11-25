import pandas as pd
import streamlit as st
from shared_data import DISTRICT_INFO, init_state

st.markdown(
    """
    <style>
        :root, .stApp {
            --text-color: #000000 !important;
            color: #000000 !important;
        }

        h1, h2, h3, h4, h5, h6,
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] *,
        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] *,
        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] summary *,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] label {
            color: #000000 !important;
            opacity: 1 !important;
        }

        [data-testid="stMarkdownContainer"] [style*="color: #fff"],
        [data-testid="stMarkdownContainer"] [style*="color: #ffffff"],
        [data-testid="stMarkdownContainer"] [style*="color: white"],
        [data-testid="stMarkdownContainer"] [style*="color:#fff"],
        [data-testid="stMarkdownContainer"] [style*="color:#ffffff"],
        [data-testid="stMarkdownContainer"] [style*="color:white"],
        [data-testid="stMarkdownContainer"] [style*="color: rgba(255"],
        [data-testid="stMarkdownContainer"] [style*="color:rgba(255"] {
            color: #000000 !important;
        }

        .stButton > button,
        .stButton > button *,
        .stFormSubmitButton > button,
        .stFormSubmitButton > button *,
        [data-testid="stDownloadButton"] > button,
        [data-testid="stDownloadButton"] > button * {
            background-color: #17365D !important;
            color: #FFFFFF !important;
            border-color: #0F2440 !important;
            opacity: 1 !important;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-baseweb="select"] > div,
        [data-baseweb="select"] > div * {
            color: #FFFFFF !important;
            opacity: 1 !important;
        }

        [data-baseweb="popover"] li,
        [data-baseweb="popover"] li * {
            color: #000000 !important;
            background-color: #FFFFFF !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

df_students = init_state()

st.title("Admin — Student Registry (Edit & Insert Records)")

with st.expander("➕ Insert New Student Record", expanded=False):
    with st.form("insert_student_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        new_id = c1.text_input("Record ID", value=f"KOD-{1000 + len(df_students)}")
        new_ident = c2.text_input("Identifier", value=f"Child Record #{len(df_students) + 1} (Anonymized)")
        new_age = c3.number_input("Age", min_value=1, max_value=21, value=6)
        new_dist = c4.selectbox("District", list(DISTRICT_INFO.keys()))

        c5, c6, c7, c8 = st.columns(4)
        new_diag = c5.selectbox("Diagnosis", ["Mild Autism", "High-Function Autism", "Severe Autism"])
        new_serv = c6.selectbox("Required Service", ["Speech Therapy", "ABA Therapy", "Occupational Sensory", "Early Intervention"])
        new_date = c7.text_input("Date (YYYY-MM-DD)", value="2026-11-22")
        new_status = c8.selectbox("Status", ["Verified Active", "Pending Verification"])

        if st.form_submit_button("Insert Record"):
            new_row = pd.DataFrame([{
                "Record ID": new_id.strip(),
                "Identifier": new_ident.strip(),
                "Age": int(new_age),
                "District": new_dist,
                "Diagnosis": new_diag,
                "Required Service": new_serv,
                "Date": new_date.strip(),
                "Status": new_status,
            }])
            st.session_state["student_df"] = pd.concat([st.session_state["student_df"], new_row], ignore_index=True)
            st.success(f"Inserted record {new_id}!")
            st.rerun()

st.caption("Edit any cell directly in the table, then click **Save Edits**.")
edited_df = st.data_editor(
    st.session_state["student_df"],
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "District": st.column_config.SelectboxColumn("District", options=list(DISTRICT_INFO.keys()), required=True),
        "Diagnosis": st.column_config.SelectboxColumn("Diagnosis", options=["Mild Autism", "High-Function Autism", "Severe Autism"], required=True),
        "Required Service": st.column_config.SelectboxColumn("Required Service", options=["Speech Therapy", "ABA Therapy", "Occupational Sensory", "Early Intervention"], required=True),
        "Status": st.column_config.SelectboxColumn("Status", options=["Verified Active", "Pending Verification"], required=True),
    },
)

b1, b2 = st.columns([2, 3])
if b1.button("💾 Save Edits", type="primary"):
    st.session_state["student_df"] = edited_df.copy()
    st.success("Saved registry updates!")

b2.download_button(
    label="⬇️ Download Updated CSV",
    data=st.session_state["student_df"].to_csv(index=False).encode("utf-8"),
    file_name="kelantan_student_registry_updated.csv",
    mime="text/csv",
)
