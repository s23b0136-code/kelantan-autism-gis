import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit as st

st.set_page_config(
    page_title="Kelantan Autism GIS — Zone Map & Analytics",
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
        "recommended_centre": "NASOM Malaysia - Kota Bharu",
        "therapists": "Speech Therapists (SLP), Occupational Therapists (OT), ABA Therapists, Special Educators",
    },
    "BACHOK": {
        "lat": 6.0610,
        "lon": 102.3976,
        "centres": 2,
        "zone": "Yellow Zone",
        "color": "orange",
        "recommended_centre": "Bachok Autism Outreach Clinic",
        "therapists": "Early Intervention Specialists, Speech Support, Behavioral Coaches",
    },
    "PASIR MAS": {
        "lat": 6.1042,
        "lon": 102.1412,
        "centres": 2,
        "zone": "Yellow Zone",
        "color": "orange",
        "recommended_centre": "Pasir Mas Early Intervention Centre",
        "therapists": "Early Childhood Special Educators, Speech Therapists, Sensory-Motor Therapists",
    },
    "PASIR PUTEH": {
        "lat": 5.8361,
        "lon": 102.4042,
        "centres": 1,
        "zone": "Red Zone",
        "color": "red",
        "recommended_centre": "Pasir Puteh Special Needs Center",
        "therapists": "Developmental Therapists, Motor & Play Specialists, Caregiver Counselors",
    },
    "WAKAF BHARU": {
        "lat": 6.1400,
        "lon": 102.2100,
        "centres": 1,
        "zone": "Red Zone",
        "color": "red",
        "recommended_centre": "Wakaf Bharu Care & Intervention Hub",
        "therapists": "Occupational Therapy Practitioners, Daily Living Skills Coaches, Sensory Facilitators",
    },
    "TUMPAT": {
        "lat": 6.1990,
        "lon": 102.1700,
        "centres": 1,
        "zone": "Red Zone",
        "color": "red",
        "recommended_centre": "Tumpat Pediatric Therapy Unit",
        "therapists": "Pediatric Speech Therapists, Play-Based Interventionists, Social Communication Coaches",
    },
    "RANTAU PANJANG": {
        "lat": 6.0200,
        "lon": 101.9800,
        "centres": 1,
        "zone": "Yellow Zone",
        "color": "orange",
        "recommended_centre": "Rantau Panjang Autism Support Hub",
        "therapists": "Outreach Special Educators, Speech & Communication Coaches, Parent Training Advisors",
    },
}


@st.cache_data
def load_students(path: str = "Kelantan_Student_Registry_104.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["District"] = df["District"].astype(str).str.strip().str.upper()
    return df


if "selected_zone_district" not in st.session_state:
    st.session_state["selected_zone_district"] = "PASIR PUTEH"

df_students = load_students()
counts_by_dist = df_students["District"].value_counts().to_dict()

st.title("Zone Map & Analytics — Kelantan Autism Registry")

# 1. Top KPI Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Registered Students", len(df_students))
m2.metric("Verified Active", int((df_students["Status"] == "Verified Active").sum()))
m3.metric("Pending Verification", int((df_students["Status"] == "Pending Verification").sum()))
m4.metric("Red Zone Districts", sum(1 for v in DISTRICT_INFO.values() if v["zone"] == "Red Zone"))

st.divider()

# 2. Zone Map + Pop-Up Place Inspector
map_col, info_col = st.columns([7, 5], gap="large")

with map_col:
    st.subheader("Kelantan Red / Green / Yellow Zone Map")
    fmap = folium.Map(location=[6.02, 102.22], zoom_start=10, tiles="OpenStreetMap")

    for dist_name, info in DISTRICT_INFO.items():
        stu_cnt = int(counts_by_dist.get(dist_name, 0))
        popup_html = (
            f"<b>{dist_name}</b><br>"
            f"Zone: <b>{info['zone']}</b><br>"
            f"Students: <b>{stu_cnt}</b> | Centres: <b>{info['centres']}</b><br>"
            f"Centre: {info['recommended_centre']}"
        )
        folium.CircleMarker(
            location=[info["lat"], info["lon"]],
            radius=15,
            color=info["color"],
            fill=True,
            fill_color=info["color"],
            fill_opacity=0.8,
            tooltip=dist_name,
            popup=folium.Popup(popup_html, max_width=260),
        ).add_to(fmap)

    map_out = st_folium(
        fmap,
        use_container_width=True,
        height=400,
        returned_objects=["last_object_clicked_tooltip"],
    )

    clicked = map_out.get("last_object_clicked_tooltip") if isinstance(map_out, dict) else None
    if clicked in DISTRICT_INFO:
        st.session_state["selected_zone_district"] = clicked

with info_col:
    st.subheader("Place Pop-Up Details")
    selected_dist = st.selectbox(
        "Click a marker on the map or pick a district:",
        options=list(DISTRICT_INFO.keys()),
        index=list(DISTRICT_INFO.keys()).index(st.session_state["selected_zone_district"]),
    )
    st.session_state["selected_zone_district"] = selected_dist

    d_info = DISTRICT_INFO[selected_dist]
    d_rows = df_students[df_students["District"] == selected_dist]

    with st.container(border=True):
        st.markdown(f"### 📍 {selected_dist} — `{d_info['zone']}`")
        st.markdown(f"- **Students in District:** `{len(d_rows)}`")
        st.markdown(f"- **Therapy Centres:** `{d_info['centres']}`")
        st.markdown(
            f"- **Autism Types:** Mild `{int((d_rows['Diagnosis'] == 'Mild Autism').sum())}` • "
            f"High-Function `{int((d_rows['Diagnosis'] == 'High-Function Autism').sum())}` • "
            f"Severe `{int((d_rows['Diagnosis'] == 'Severe Autism').sum())}`"
        )
        st.markdown(f"- **Recommended Centre:** {d_info['recommended_centre']}")
        st.markdown(f"- **Therapists Provided:** {d_info['therapists']}")

st.divider()

# 3. Analytics Charts
st.subheader("Analytics Graphs")
c1, c2 = st.columns(2, gap="large")

with c1:
    st.markdown("**Students per District**")
    st.bar_chart(df_students.groupby("District").size().rename("Students"), height=280)

with c2:
    st.markdown("**Diagnosis Breakdown by District**")
    st.bar_chart(pd.crosstab(df_students["District"], df_students["Diagnosis"]), height=280)
