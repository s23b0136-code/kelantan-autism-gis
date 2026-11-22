import streamlit as st
from shared_data import init_state

st.set_page_config(
    page_title="Kelantan Autism GIS Platform",
    page_icon="🗺️",
    layout="wide",
)

init_state()

pg = st.navigation(
    {
        "Admin Portal": [
            st.Page("app_pages/1_admin_zone_map.py", title="Zone Map & Analytics", icon="🗺️"),
            st.Page("app_pages/2_admin_student_registry.py", title="Student Registry (Edit & Insert)", icon="📋"),
            st.Page("app_pages/3_admin_service_graphs.py", title="Service & Age Graphs", icon="📊"),
        ],
        "Parents Portal": [
            st.Page("app_pages/4_parents_child_matcher.py", title="Child & Centre Matcher", icon="🏥"),
            st.Page("app_pages/5_parents_training_modules.py", title="4 Training Modules", icon="📚"),
        ],
    }
)

pg.run()
