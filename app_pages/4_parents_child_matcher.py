import streamlit as st
from shared_data import DISTRICT_INFO, init_state

df_students = init_state()

st.title("Parents Portal — Child Record, Suitable Centre & Therapists")

f1, f2 = st.columns([2, 4])
dist_filter = f1.selectbox("Filter District", ["ALL"] + list(DISTRICT_INFO.keys()))
pool_df = df_students if dist_filter == "ALL" else df_students[df_students["District"] == dist_filter]

selected_rec_id = f2.selectbox(
    "Click / Choose Child Record",
    options=pool_df["Record ID"].tolist(),
    format_func=lambda rid: f"{rid} — {pool_df.loc[pool_df['Record ID'] == rid, 'Identifier'].values[0]} ({pool_df.loc[pool_df['Record ID'] == rid, 'District'].values[0]})",
)

child_row = df_students[df_students["Record ID"] == selected_rec_id].iloc[0]
c_dist = str(child_row["District"]).upper()
c_diag = str(child_row["Diagnosis"])
c_info = DISTRICT_INFO.get(c_dist, DISTRICT_INFO["KOTA BHARU"])

left, right = st.columns([5, 7], gap="large")

with left:
    st.subheader("👶 Child Information")
    with st.container(border=True):
        st.markdown(f"**Record ID:** `{child_row['Record ID']}`")
        st.markdown(f"**Identifier:** {child_row['Identifier']}")
        st.markdown(f"**Age:** `{child_row['Age']}` years old")
        st.markdown(f"**District:** `{c_dist}` (`{c_info['zone']}`)")
        st.markdown(f"**Autism Type:** `{c_diag}`")
        st.markdown(f"**Required Service:** `{child_row['Required Service']}`")
        st.markdown(f"**Registration Date:** `{child_row['Date']}`")
        st.markdown(f"**Status:** `{child_row['Status']}`")

with right:
    st.subheader("🏥 Suitable Centre & Therapists")
    with st.container(border=True):
        st.markdown(f"### ⭐ {c_info['recommended_centre']}")
        st.caption(f"District: **{c_dist}** | Zone: **{c_info['zone']}** | Lat: `{c_info['lat']}`, Lng: `{c_info['lon']}`")
        st.markdown(f"**Why Suitable:** {c_info['why_suitable']}")
        st.markdown(f"**Therapists Provided:** {c_info['therapists']}")
        st.markdown(f"**Matches Required Service:** `{child_row['Required Service']}`")

    st.markdown("**Service Demand in This District**")
    dist_serv = df_students[df_students["District"] == c_dist].groupby("Required Service").size().rename("Students")
    st.bar_chart(dist_serv, height=220)
