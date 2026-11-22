import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit as st

st.set_page_config(
    page_title="Kelantan Autism GIS — Multi-Page Platform",
    page_icon="🗺️",
    layout="wide",
)

DISTRICT_INFO = {
    "KOTA BHARU": {
        "lat": 6.1254,
        "lon": 102.2381,
        "centres": 4,
        "zone": "Green Zone",
        "color": "green",
        "place_summary": "Kota Bharu Central & Kubang Kerian Hub (4 centres, 15 students).",
        "recommended_centre": "NASOM Malaysia - Kota Bharu",
        "therapists": "Speech-Language Pathologists (SLP), Occupational Therapists (OT), ABA Therapists, Special Educators",
        "why_suitable": "Strongest concentration of therapy specialists and structured programs in the registry.",
    },
    "BACHOK": {
        "lat": 6.0610,
        "lon": 102.3976,
        "centres": 2,
        "zone": "Yellow Zone",
        "color": "orange",
        "place_summary": "Bachok Coastal & Tembila/Melawi Zone (2 centres, 15 students).",
        "recommended_centre": "Bachok Autism Outreach Clinic",
        "therapists": "Early Intervention Specialists, Speech Therapy Support, Behavioral Coaches",
        "why_suitable": "Keeps travel short within Bachok to reduce travel fatigue and support daily routine consistency.",
    },
    "PASIR MAS": {
        "lat": 6.1042,
        "lon": 102.1412,
        "centres": 2,
        "zone": "Yellow Zone",
        "color": "orange",
        "place_summary": "Pasir Mas Town & Western Corridor (2 centres, 15 students).",
        "recommended_centre": "Pasir Mas Early Intervention Centre",
        "therapists": "Early Childhood Special Educators, Speech & Language Therapists, Sensory-Motor Therapists",
        "why_suitable": "Offers local early intervention and structured skill development close to home.",
    },
    "PASIR PUTEH": {
        "lat": 5.8361,
        "lon": 102.4042,
        "centres": 1,
        "zone": "Red Zone",
        "color": "red",
        "place_summary": "Pasir Puteh Southern Zone (High deficit: 15 students to 1 centre).",
        "recommended_centre": "Pasir Puteh Special Needs Center",
        "therapists": "Developmental Therapists, Motor & Play Specialists, Caregiver Counselors",
        "why_suitable": "Closest local option in Pasir Puteh for foundational therapy and parent guidance.",
    },
    "WAKAF BHARU": {
        "lat": 6.1400,
        "lon": 102.2100,
        "centres": 1,
        "zone": "Red Zone",
        "color": "red",
        "place_summary": "Wakaf Bharu Border Zone (High deficit: 15 students to 1 centre).",
        "recommended_centre": "Wakaf Bharu Care & Intervention Hub",
        "therapists": "Occupational Therapy Practitioners, Daily Living Skills Coaches, Sensory Facilitators",
        "why_suitable": "Supports daily living routines, sensory regulation, and practical skill carryover.",
    },
    "TUMPAT": {
        "lat": 6.1990,
        "lon": 102.1700,
        "centres": 1,
        "zone": "Red Zone",
        "color": "red",
        "place_summary": "Tumpat Northern Delta Zone (High deficit: 15 students to 1 centre).",
        "recommended_centre": "Tumpat Pediatric Therapy Unit",
        "therapists": "Pediatric Speech Therapists, Play-Based Interventionists, Social Communication Coaches",
        "why_suitable": "Provides child-friendly speech and play-based communication support in Tumpat.",
    },
    "RANTAU PANJANG": {
        "lat": 6.0200,
        "lon": 101.9800,
        "centres": 1,
        "zone": "Yellow Zone",
        "color": "orange",
        "place_summary": "Rantau Panjang Border Zone (14 students to 1 support hub).",
        "recommended_centre": "Rantau Panjang Autism Support Hub",
        "therapists": "Outreach Special Educators, Speech & Communication Coaches, Parent Training Advisors",
        "why_suitable": "Reduces long travel distances for border families and supports home-based routines.",
    },
}

MODULES_4 = [
    {
        "code": "Module AG",
        "title": "Toilet Training & Hygiene",
        "domain": "Self-Care & Daily Routine",
        "steps": "1. Use visual bathroom step cards.\n2. Keep handwashing steps consistent.\n3. Praise or reward independent attempts right away.",
    },
    {
        "code": "Module AH",
        "title": "Arrival Routine & Classroom Transition",
        "domain": "Home & Learning Transitions",
        "steps": "1. Give a 5-minute warning before transitions.\n2. Use a visual 'First / Then' card.\n3. Keep arrival routines calm and predictable.",
    },
    {
        "code": "Module AI",
        "title": "Morning Walk & Sensory Regulation",
        "domain": "Physical, Motor & Sensory",
        "steps": "1. Start the morning with a calm walk or movement activity.\n2. Watch for noise or sensory overload.\n3. Use quiet breaks before focused tasks.",
    },
    {
        "code": "Module SK",
        "title": "Speech & Picture Exchange (PECS)",
        "domain": "Communication Support",
        "steps": "1. Pair picture cards or gestures with simple spoken words.\n2. Practice asking for everyday needs (water, food, break, help).\n3. Encourage every communication attempt.",
    },
]


@st.cache_data
def load_initial_csv(path: str = "Kelantan_Student_Registry_104.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["District"] = df["District"].astype(str).str.strip().str.upper()
    return df


if "student_df" not in st.session_state:
    st.session_state["student_df"] = load_initial_csv().copy()

if "selected_map_district" not in st.session_state:
    st.session_state["selected_map_district"] = "PASIR PUTEH"

df_students = st.session_state["student_df"].copy()

# Sidebar Multi-Page Menu
st.sidebar.title("KELANTAN GIS")
st.sidebar.caption("Multi-Page Autism Registry & Matcher")

page = st.sidebar.radio(
    "Pages",
    [
        "1. Admin: Zone Map & Analytics",
        "2. Admin: Student Registry (Edit & Insert)",
        "3. Admin: Service & Age Graphs",
        "4. Parents: Child & Centre Matcher",
        "5. Parents: 4 Training Modules",
    ],
)

counts_by_dist = df_students["District"].value_counts().to_dict()

# ==============================================================================
# PAGE 1: ADMIN — ZONE MAP (RED / GREEN / YELLOW) + POP-UP + DISTRICT GRAPHS
# ==============================================================================
if page == "1. Admin: Zone Map & Analytics":
    st.title("Admin — Kelantan Deficit Zone Map & Analytics")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Students", len(df_students))
    k2.metric("Verified Active", int((df_students["Status"] == "Verified Active").sum()))
    k3.metric("Pending Verification", int((df_students["Status"] == "Pending Verification").sum()))
    k4.metric("Red Zone Districts", sum(1 for info in DISTRICT_INFO.values() if info["zone"] == "Red Zone"))

    st.divider()
    map_col, popup_col = st.columns([7, 5], gap="large")

    with map_col:
        st.subheader("Kelantan Zone Map (Red / Green / Yellow)")
        m = folium.Map(location=[6.02, 102.22], zoom_start=10, tiles="OpenStreetMap")

        for dist_name, info in DISTRICT_INFO.items():
            stu_count = int(counts_by_dist.get(dist_name, 0))
            popup_html = (
                f"<b>{dist_name}</b><br>"
                f"<b>Zone:</b> {info['zone']}<br>"
                f"<b>Students:</b> {stu_count} | <b>Centres:</b> {info['centres']}<br>"
                f"<b>Centre:</b> {info['recommended_centre']}"
            )
            folium.CircleMarker(
                location=[info["lat"], info["lon"]],
                radius=14,
                color=info["color"],
                fill=True,
                fill_color=info["color"],
                fill_opacity=0.75,
                tooltip=dist_name,
                popup=folium.Popup(popup_html, max_width=250),
            ).add_to(m)

        map_data = st_folium(m, width=None, height=390, returned_objects=["last_object_clicked_tooltip"])
        clicked_tooltip = map_data.get("last_object_clicked_tooltip") if map_data else None
        if clicked_tooltip in DISTRICT_INFO:
            st.session_state["selected_map_district"] = clicked_tooltip

    with popup_col:
        st.subheader("Pop-Up Place Details")
        chosen_dist = st.selectbox(
            "Selected Zone / District",
            options=list(DISTRICT_INFO.keys()),
            index=list(DISTRICT_INFO.keys()).index(st.session_state["selected_map_district"]),
        )
        st.session_state["selected_map_district"] = chosen_dist

        d_info = DISTRICT_INFO[chosen_dist]
        d_sub = df_students[df_students["District"] == chosen_dist]

        with st.container(border=True):
            st.markdown(f"### 📍 {chosen_dist} — {d_info['zone']}")
            st.write(d_info["place_summary"])
            st.markdown(f"- **Registered Students:** `{len(d_sub)}`")
            st.markdown(f"- **Centres:** `{d_info['centres']}`")
            st.markdown(
                f"- **Diagnosis Split:** Mild `{int((d_sub['Diagnosis'] == 'Mild Autism').sum())}` • "
                f"High-Function `{int((d_sub['Diagnosis'] == 'High-Function Autism').sum())}` • "
                f"Severe `{int((d_sub['Diagnosis'] == 'Severe Autism').sum())}`"
            )
            st.markdown(f"- **Key Centre:** {d_info['recommended_centre']}")
            st.markdown(f"- **Therapists:** {d_info['therapists']}")

    st.divider()
    st.subheader("District Student & Diagnosis Graphs")
    g1, g2 = st.columns(2, gap="large")

    with g1:
        st.markdown("**Students per District**")
        dist_chart_df = df_students.groupby("District").size().rename("Student Count")
        st.bar_chart(dist_chart_df, height=280)

    with g2:
        st.markdown("**Autism Diagnosis Breakdown by District**")
        diag_pivot = pd.crosstab(df_students["District"], df_students["Diagnosis"])
        st.bar_chart(diag_pivot, height=280)

# ==============================================================================
# PAGE 2: ADMIN — STUDENT REGISTRY (EDIT & INSERT 104 RECORDS)
# ==============================================================================
elif page == "2. Admin: Student Registry (Edit & Insert)":
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
        label="⬇️ Download CSV",
        data=st.session_state["student_df"].to_csv(index=False).encode("utf-8"),
        file_name="kelantan_student_registry_updated.csv",
        mime="text/csv",
    )

# ==============================================================================
# PAGE 3: ADMIN — SERVICE & AGE GRAPHS
# ==============================================================================
elif page == "3. Admin: Service & Age Graphs":
    st.title("Admin — Required Services & Age Distribution Graphs")

    s1, s2 = st.columns(2, gap="large")
    with s1:
        st.subheader("Required Service by District")
        serv_pivot = pd.crosstab(df_students["District"], df_students["Required Service"])
        st.bar_chart(serv_pivot, height=340)

    with s2:
        st.subheader("Student Count by Age")
        age_counts = df_students.groupby("Age").size().rename("Students")
        st.bar_chart(age_counts, height=340)

    st.divider()
    st.subheader("Summary Cross-Tabulation (Diagnosis vs. Required Service)")
    st.dataframe(pd.crosstab(df_students["Diagnosis"], df_students["Required Service"]), use_container_width=True)

# ==============================================================================
# PAGE 4: PARENTS — CHILD RECORD, AUTISM TYPE, SUITABLE CENTRE & THERAPISTS
# ==============================================================================
elif page == "4. Parents: Child & Centre Matcher":
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

# ==============================================================================
# PAGE 5: PARENTS — 4 TRAINING & INTERVENTION MODULES
# ==============================================================================
else:
    st.title("Parents Portal — 4 Intervention & Training Modules")
    st.caption("Practical home routines and guides across four core areas.")

    cols = st.columns(2, gap="large")
    for idx, mod in enumerate(MODULES_4):
        with cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"### {mod['code']}: {mod['title']}")
                st.caption(f"Focus Area: {mod['domain']}")
                st.text(mod["steps"])
                guide_bytes = f"{mod['code']} - {mod['title']}\nFocus: {mod['domain']}\n\n{mod['steps']}\n".encode("utf-8")
                st.download_button(
                    label=f"Download {mod['code']} Guide",
                    data=guide_bytes,
                    file_name=f"{mod['code'].replace(' ', '_')}.txt",
                    mime="text/plain",
                    key=f"mod_dl_{idx}",
                )
