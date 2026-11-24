import json
import os
import sqlite3
from urllib.parse import quote

import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Kelantan Autism GIS Analytics Dashboard",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("AUTISM_GIS_DB_PATH", os.path.join(BASE_DIR, "kelantan_autism_gis.db"))
GEOJSON_PATH = os.path.join(BASE_DIR, "data", "kelantan_districts.geojson")

GRAPH_PALETTE = [
    "#17365D",  # Navy Blue
    "#0F8B8D",  # Teal
    "#6D28D9",  # Purple
    "#1E3A5F",  # Dark Blue
    "#0284C7",  # Sky Blue
    "#0D9488",  # Deep Teal
    "#7C3AED",  # Violet
    "#475569",  # Slate
]

ACCESSIBILITY_COLORS = {
    "Good": "#16A34A",
    "Moderate": "#EAB308",
    "Poor": "#DC2626",
}


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS districts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            accessibility_status TEXT NOT NULL CHECK(accessibility_status IN ('Good', 'Moderate', 'Poor')),
            lat REAL NOT NULL,
            lng REAL NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS centres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            district_name TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            therapies_offered TEXT NOT NULL,
            FOREIGN KEY (district_name) REFERENCES districts(name)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_code TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            district_name TEXT NOT NULL,
            diagnosis TEXT NOT NULL,
            therapy_required TEXT NOT NULL,
            is_verified INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (district_name) REFERENCES districts(name)
        )
        """
    )

    cur.execute("SELECT COUNT(*) AS cnt FROM districts")
    if cur.fetchone()["cnt"] == 0:
        kelantan_districts = [
            ("Kota Bharu", "Good", 6.1254, 102.2381),
            ("Pasir Mas", "Moderate", 6.0406, 102.1422),
            ("Tumpat", "Moderate", 6.1978, 102.1708),
            ("Bachok", "Moderate", 6.0636, 102.3989),
            ("Tanah Merah", "Moderate", 5.8069, 102.1475),
            ("Pasir Puteh", "Moderate", 5.8356, 102.4036),
            ("Machang", "Poor", 5.7647, 102.2189),
            ("Kuala Krai", "Poor", 5.5314, 102.2006),
            ("Gua Musang", "Poor", 4.8844, 101.9686),
            ("Jeli", "Poor", 5.6947, 101.8414),
        ]
        cur.executemany(
            "INSERT INTO districts (name, accessibility_status, lat, lng) VALUES (?, ?, ?, ?)",
            kelantan_districts,
        )

    cur.execute("SELECT COUNT(*) AS cnt FROM centres")
    if cur.fetchone()["cnt"] == 0:
        sample_centres = [
            ("Pusat Intervensi Autisme Kota Bharu", "Kota Bharu", 6.1185, 102.2442, "Speech Therapy, Occupational Therapy, ABA Therapy"),
            ("Pusat Pemulihan & Terapi Kubang Kerian", "Kota Bharu", 6.0942, 102.2836, "Occupational Therapy, Sensory Integration"),
            ("Unit Sokongan Pembelajaran Pasir Mas", "Pasir Mas", 6.0361, 102.1389, "Speech Therapy, Behavioral Support"),
            ("Pusat Terapi Kanak-Kanak Tumpat", "Tumpat", 6.1920, 102.1640, "Occupational Therapy, Speech Therapy"),
            ("Pusat Sokongan Autisme Tanah Merah", "Tanah Merah", 5.8042, 102.1451, "Speech Therapy, Occupational Therapy"),
            ("Pusat Intervensi Kuala Krai", "Kuala Krai", 5.5345, 102.2030, "Speech Therapy"),
        ]
        cur.executemany(
            "INSERT INTO centres (name, district_name, lat, lng, therapies_offered) VALUES (?, ?, ?, ?, ?)",
            sample_centres,
        )

    cur.execute("SELECT COUNT(*) AS cnt FROM students")
    if cur.fetchone()["cnt"] == 0:
        sample_students = [
            ("KLT-001", "Student A", "Kota Bharu", "ASD Level 1", "Speech Therapy", 1),
            ("KLT-002", "Student B", "Kota Bharu", "ASD Level 2", "Occupational Therapy", 1),
            ("KLT-003", "Student C", "Kota Bharu", "ASD Level 1", "ABA Therapy", 1),
            ("KLT-004", "Student D", "Kota Bharu", "Speech & Language Delay (ASD)", "Speech Therapy", 0),
            ("KLT-005", "Student E", "Pasir Mas", "ASD Level 2", "Speech Therapy", 1),
            ("KLT-006", "Student F", "Pasir Mas", "ASD Level 1", "Behavioral Support", 1),
            ("KLT-007", "Student G", "Tumpat", "ASD Level 2", "Occupational Therapy", 1),
            ("KLT-008", "Student H", "Bachok", "ASD Level 1", "Speech Therapy", 1),
            ("KLT-009", "Student I", "Tanah Merah", "ASD Level 2", "Occupational Therapy", 1),
            ("KLT-010", "Student J", "Pasir Puteh", "ASD Level 3", "Sensory Integration", 1),
            ("KLT-011", "Student K", "Machang", "ASD Level 2", "Speech Therapy", 1),
            ("KLT-012", "Student L", "Kuala Krai", "ASD Level 2", "Speech Therapy", 1),
            ("KLT-013", "Student M", "Kuala Krai", "ASD Level 3", "Occupational Therapy", 0),
            ("KLT-014", "Student N", "Gua Musang", "ASD Level 2", "Speech Therapy", 1),
            ("KLT-015", "Student O", "Jeli", "ASD Level 1", "Behavioral Support", 1),
        ]
        cur.executemany(
            """
            INSERT INTO students (student_code, full_name, district_name, diagnosis, therapy_required, is_verified)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            sample_students,
        )

    conn.commit()
    conn.close()


def load_dashboard_data():
    conn = get_conn()
    districts_df = pd.read_sql_query(
        "SELECT id, name, accessibility_status, lat, lng FROM districts ORDER BY name ASC", conn
    )
    centres_df = pd.read_sql_query(
        "SELECT id, name, district_name, lat, lng, therapies_offered FROM centres ORDER BY name ASC", conn
    )
    students_df = pd.read_sql_query(
        "SELECT id, student_code, full_name, district_name, diagnosis, therapy_required, is_verified FROM students ORDER BY id DESC",
        conn,
    )
    conn.close()

    student_counts = (
        students_df.groupby("district_name").size().to_dict() if not students_df.empty else {}
    )
    centre_counts = (
        centres_df.groupby("district_name").size().to_dict() if not centres_df.empty else {}
    )

    district_rows = []
    for _, row in districts_df.iterrows():
        d_name = row["name"]
        d_centres = centres_df[centres_df["district_name"] == d_name] if not centres_df.empty else pd.DataFrame()
        d_students = students_df[students_df["district_name"] == d_name] if not students_df.empty else pd.DataFrame()

        therapies_set = set()
        if not d_centres.empty:
            for raw in d_centres["therapies_offered"].fillna(""):
                for part in str(raw).split(","):
                    clean = part.strip()
                    if clean:
                        therapies_set.add(clean)

        therapy_demand = []
        if not d_students.empty:
            vc = d_students["therapy_required"].value_counts()
            for svc, cnt in vc.items():
                therapy_demand.append({"service": svc, "students": int(cnt)})

        district_rows.append(
            {
                "District": d_name,
                "Registered Students": int(student_counts.get(d_name, 0)),
                "Autism Centres": int(centre_counts.get(d_name, 0)),
                "Accessibility Status": row["accessibility_status"],
                "Available Therapies": ", ".join(sorted(therapies_set)) if therapies_set else "No data available",
                "Therapy Demand": therapy_demand,
            }
        )

    summary_df = pd.DataFrame(district_rows)
    return {
        "districts_df": districts_df,
        "centres_df": centres_df,
        "students_df": students_df,
        "summary_df": summary_df,
        "total_students": int(len(students_df)),
        "verified_students": int(students_df["is_verified"].sum()) if not students_df.empty else 0,
        "total_centres": int(len(centres_df)),
        "total_districts": int(len(districts_df)),
    }


def add_student_record(student_code, full_name, district_name, diagnosis, therapy_required, is_verified):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO students (student_code, full_name, district_name, diagnosis, therapy_required, is_verified)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            student_code.strip(),
            full_name.strip(),
            district_name.strip(),
            diagnosis.strip(),
            therapy_required.strip(),
            1 if is_verified else 0,
        ),
    )
    conn.commit()
    conn.close()


def add_centre_record(name, district_name, lat, lng, therapies_offered):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO centres (name, district_name, lat, lng, therapies_offered)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name.strip(),
            district_name.strip(),
            float(lat),
            float(lng),
            therapies_offered.strip(),
        ),
    )
    conn.commit()
    conn.close()


def apply_custom_theme():
    font_svg = quote(
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#172033" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>'
    )
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

            html, body, [class*="css"], .stApp {{
                font-family: 'Inter', 'Roboto', Arial, sans-serif;
                color: #000000;
                background-color: #F4F7FB;
            }}

            .stApp {{
                background-color: #F4F7FB;
            }}

            [data-testid="stSidebar"] {{
                background-color: #FFFFFF;
                border-right: 1px solid #CBD5E1;
            }}

            [data-testid="stSidebar"] * {{
                color: #000000 !important;
            }}

            h1, h2, h3, h4, h5, h6 {{
                color: #000000 !important;
                font-weight: 700 !important;
            }}

            p, span, label, div, li {{
                color: #000000;
            }}

            [data-testid="stMarkdownContainer"] *,
            [data-testid="stWidgetLabel"] *,
            [data-testid="stCaptionContainer"] *,
            .caption-muted, small {{
                color: #000000 !important;
            }}

            [data-testid="stMetric"] {{
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-top: 4px solid #17365D;
                border-radius: 10px;
                padding: 0.85rem 1rem;
            }}

            [data-testid="stMetricLabel"] *,
            [data-testid="stMetricValue"] * {{
                color: #000000 !important;
                font-weight: 700 !important;
            }}

            .section-card {{
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
                padding: 1.1rem 1.25rem;
                margin-bottom: 1rem;
            }}

            .detail-box {{
                background-color: #FFFFFF;
                border: 1px solid #0F8B8D;
                border-left: 5px solid #17365D;
                border-radius: 10px;
                padding: 1.1rem 1.3rem;
                margin-top: 0.75rem;
                margin-bottom: 1.25rem;
            }}

            .stButton > button {{
                background-color: #17365D;
                color: #FFFFFF !important;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }}

            .stButton > button * {{
                color: #FFFFFF !important;
            }}

            .stButton > button:hover {{
                background-color: #1E3A5F;
            }}

            input, textarea, select, [data-baseweb="select"] > div {{
                background-color: #FFFFFF !important;
                color: #000000 !important;
                border-color: #94A3B8 !important;
            }}

            [data-baseweb="select"] span, [data-baseweb="popover"] li {{
                color: #000000 !important;
                background-color: #FFFFFF !important;
            }}

            .map-legend {{
                display: flex;
                flex-wrap: wrap;
                gap: 1.1rem;
                margin-top: 0.65rem;
                font-size: 0.9rem;
                font-weight: 500;
                color: #000000;
            }}

            .swatch {{
                display: inline-block;
                width: 14px;
                height: 14px;
                border-radius: 3px;
                margin-right: 6px;
                vertical-align: middle;
                border: 1px solid rgba(17, 24, 39, 0.25);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_plotly_fig(fig, x_title="", y_title="", is_pie=False):
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, Roboto, Arial, sans-serif", color="#1F2937", size=12),
        title=dict(font=dict(color="#111827", size=16)),
        legend=dict(font=dict(color="#111827", size=12)),
        margin=dict(t=45, b=45, l=45, r=25),
    )
    if not is_pie:
        fig.update_xaxes(
            title_text=x_title,
            title_font=dict(color="#111827", size=12),
            tickfont=dict(color="#1F2937", size=11),
            showgrid=True,
            gridcolor="#E2E8F0",
            linecolor="#CBD5E1",
        )
        fig.update_yaxes(
            title_text=y_title,
            title_font=dict(color="#111827", size=12),
            tickfont=dict(color="#1F2937", size=11),
            showgrid=True,
            gridcolor="#E2E8F0",
            linecolor="#CBD5E1",
        )
    return fig


def render_kelantan_map(summary_df, centres_df):
    try:
        if not os.path.exists(GEOJSON_PATH):
            st.info("Map temporarily unavailable")
            return

        with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
            geo_data = json.load(f)

        stats_lookup = {}
        if not summary_df.empty:
            for _, r in summary_df.iterrows():
                stats_lookup[r["District"]] = r.to_dict()

        fmap = folium.Map(location=[5.65, 102.15], zoom_start=9, tiles="OpenStreetMap")

        def style_fn(feature):
            d_name = feature.get("properties", {}).get("district", "")
            status = stats_lookup.get(d_name, {}).get("Accessibility Status", "")
            fill_col = ACCESSIBILITY_COLORS.get(status, "#64748B")
            return {
                "fillColor": fill_col,
                "color": "#17365D",
                "weight": 1.8,
                "fillOpacity": 0.58,
            }

        for feat in geo_data.get("features", []):
            d_name = feat.get("properties", {}).get("district", "District")
            info = stats_lookup.get(
                d_name,
                {
                    "Registered Students": 0,
                    "Autism Centres": 0,
                    "Accessibility Status": "No data available",
                },
            )
            tooltip_html = (
                f"<b>{d_name}</b><br/>"
                f"Students: {info['Registered Students']}<br/>"
                f"Autism Centres: {info['Autism Centres']}<br/>"
                f"Accessibility: {info['Accessibility Status']}"
            )
            folium.GeoJson(
                {"type": "FeatureCollection", "features": [feat]},
                style_function=style_fn,
                tooltip=folium.Tooltip(tooltip_html),
            ).add_to(fmap)

        if not centres_df.empty:
            for _, c in centres_df.iterrows():
                popup_html = (
                    f"<b>{c['name']}</b><br/>"
                    f"District: {c['district_name']}<br/>"
                    f"Therapies: {c['therapies_offered']}"
                )
                folium.CircleMarker(
                    location=[float(c["lat"]), float(c["lng"])],
                    radius=7,
                    color="#FFFFFF",
                    weight=2,
                    fill=True,
                    fill_color="#17365D",
                    fill_opacity=0.95,
                    popup=folium.Popup(popup_html, max_width=260),
                ).add_to(fmap)

        components.html(fmap._repr_html_(), height=430, scrolling=False)
        st.markdown(
            """
            <div class="map-legend">
                <span><span class="swatch" style="background:#16A34A;"></span>Good Accessibility</span>
                <span><span class="swatch" style="background:#EAB308;"></span>Moderate Accessibility</span>
                <span><span class="swatch" style="background:#DC2626;"></span>Poor Accessibility</span>
                <span><span class="swatch" style="background:#17365D;border-radius:50%;"></span>Autism Centre</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        st.info("Map temporarily unavailable")


def render_expanded_detail_panel():
    detail = st.session_state.get("expanded_detail")
    if not detail:
        return

    st.markdown('<div class="detail-box">', unsafe_allow_html=True)
    hdr_col, btn_col = st.columns([6, 1])
    with hdr_col:
        st.subheader(detail["title"])
        if detail.get("subtitle"):
            st.caption(detail["subtitle"])
    with btn_col:
        if st.button("Close View", key="close_expanded_detail_btn"):
            st.session_state.pop("expanded_detail", None)
            st.rerun()

    chart_col, info_col = st.columns([3, 2])
    with chart_col:
        st.plotly_chart(detail["fig"], use_container_width=True, key="expanded_modal_plotly")
    with info_col:
        for item in detail.get("metrics", []):
            st.markdown(f"**{item['label']}:** {item['value']}")
    st.markdown("</div>", unsafe_allow_html=True)


def main():
    init_db()
    apply_custom_theme()

    st.sidebar.markdown("### Kelantan Healthcare GIS")
    st.sidebar.markdown("**Autism Analytics Portal**")
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard Overview", "District GIS Map", "Student & Centre Records"],
        label_visibility="collapsed",
    )

    data = load_dashboard_data()
    summary_df = data["summary_df"]
    centres_df = data["centres_df"]
    students_df = data["students_df"]

    st.title("Kelantan Autism GIS Analytics Dashboard")
    st.caption("District-level service accessibility, diagnosis profiles, and therapy demand")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Registered Students", data["total_students"])
    k2.metric("Verified Student Records", data["verified_students"])
    k3.metric("Autism Centres", data["total_centres"])
    k4.metric("Kelantan Districts Mapped", data["total_districts"])

    render_expanded_detail_panel()

    if page == "Dashboard Overview":
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Students by District")
            if summary_df.empty or summary_df["Registered Students"].sum() == 0:
                st.info("No data available")
            else:
                fig_dist = px.bar(
                    summary_df,
                    x="District",
                    y="Registered Students",
                    color="District",
                    color_discrete_sequence=GRAPH_PALETTE,
                    text="Registered Students",
                )
                fig_dist.update_traces(textposition="outside", textfont_color="#111827")
                style_plotly_fig(fig_dist, x_title="Kelantan District", y_title="Registered Students")
                st.plotly_chart(fig_dist, use_container_width=True, key="chart_students_district")

                selected_dist = st.selectbox(
                    "Inspect District Expanded View",
                    options=summary_df["District"].tolist(),
                    key="select_district_expand",
                )
                if st.button("Expand District Analytics", key="btn_expand_district"):
                    row = summary_df[summary_df["District"] == selected_dist].iloc[0].to_dict()
                    t_lines = [
                        {"label": f"{t['service']} Demand", "value": f"{t['students']} students"}
                        for t in row.get("Therapy Demand", [])
                    ] or [{"label": "Therapy Demand", "value": "No data available"}]
                    exp_fig = go.Figure(
                        data=[
                            go.Bar(
                                name=selected_dist,
                                x=["Registered Students", "Autism Centres"],
                                y=[row["Registered Students"], row["Autism Centres"]],
                                marker_color=["#17365D", "#0F8B8D"],
                                text=[row["Registered Students"], row["Autism Centres"]],
                                textposition="outside",
                            )
                        ]
                    )
                    style_plotly_fig(exp_fig, x_title="Indicator", y_title="Count")
                    st.session_state["expanded_detail"] = {
                        "title": f"{selected_dist} – Expanded District View",
                        "subtitle": f"Accessibility Status: {row['Accessibility Status']}",
                        "fig": exp_fig,
                        "metrics": [
                            {"label": "Total Registered Students", "value": row["Registered Students"]},
                            {"label": "Number of Autism Centres", "value": row["Autism Centres"]},
                            {"label": "Available Therapy Services", "value": row["Available Therapies"]},
                            {"label": "Accessibility Status", "value": row["Accessibility Status"]},
                            *t_lines,
                        ],
                    }
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Diagnosis Distribution")
            if students_df.empty:
                st.info("No data available")
            else:
                diag_df = (
                    students_df.groupby("diagnosis")
                    .size()
                    .reset_index(name="Students")
                    .sort_values("Students", ascending=False)
                )
                total_diag = diag_df["Students"].sum()
                diag_df["Percentage"] = diag_df["Students"].apply(
                    lambda v: f"{(v / total_diag * 100):.1f}%" if total_diag > 0 else "0.0%"
                )

                fig_diag = px.pie(
                    diag_df,
                    names="diagnosis",
                    values="Students",
                    hole=0.48,
                    color_discrete_sequence=GRAPH_PALETTE,
                )
                fig_diag.update_traces(
                    textinfo="label+value+percent",
                    textfont_color="#111827",
                )
                style_plotly_fig(fig_diag, is_pie=True)
                st.plotly_chart(fig_diag, use_container_width=True, key="chart_diagnosis_doughnut")

                selected_diag = st.selectbox(
                    "Inspect Diagnosis Category",
                    options=diag_df["diagnosis"].tolist(),
                    key="select_diagnosis_expand",
                )
                if st.button("Expand Diagnosis View", key="btn_expand_diagnosis"):
                    d_row = diag_df[diag_df["diagnosis"] == selected_diag].iloc[0]
                    exp_diag_fig = px.pie(
                        diag_df,
                        names="diagnosis",
                        values="Students",
                        hole=0.48,
                        color_discrete_sequence=GRAPH_PALETTE,
                    )
                    exp_diag_fig.update_traces(textinfo="label+value+percent", textfont_color="#111827")
                    style_plotly_fig(exp_diag_fig, is_pie=True)
                    st.session_state["expanded_detail"] = {
                        "title": f"Diagnosis Category: {selected_diag}",
                        "subtitle": f"Exact student count and percentage across {total_diag} records",
                        "fig": exp_diag_fig,
                        "metrics": [
                            {"label": "Diagnosis Category", "value": selected_diag},
                            {"label": "Number of Students", "value": int(d_row["Students"])},
                            {"label": "Percentage of Total", "value": d_row["Percentage"]},
                        ],
                    }
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        t_col, c_col = st.columns(2)

        with t_col:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Therapy Service Demand")
            if students_df.empty:
                st.info("No data available")
            else:
                therapy_df = (
                    students_df.groupby("therapy_required")
                    .size()
                    .reset_index(name="Students Requiring Service")
                    .sort_values("Students Requiring Service", ascending=True)
                )
                total_th = therapy_df["Students Requiring Service"].sum()

                fig_th = px.bar(
                    therapy_df,
                    x="Students Requiring Service",
                    y="therapy_required",
                    orientation="h",
                    color="therapy_required",
                    color_discrete_sequence=GRAPH_PALETTE,
                    text="Students Requiring Service",
                )
                fig_th.update_traces(textposition="outside", textfont_color="#111827")
                style_plotly_fig(fig_th, x_title="Students Requiring Service", y_title="Therapy Service")
                st.plotly_chart(fig_th, use_container_width=True, key="chart_therapy_hbar")

                selected_th = st.selectbox(
                    "Inspect Therapy Service",
                    options=therapy_df["therapy_required"].tolist(),
                    key="select_therapy_expand",
                )
                if st.button("Expand Therapy View", key="btn_expand_therapy"):
                    th_row = therapy_df[therapy_df["therapy_required"] == selected_th].iloc[0]
                    cnt_val = int(th_row["Students Requiring Service"])
                    pct_val = f"{(cnt_val / total_th * 100):.1f}%" if total_th > 0 else "0.0%"
                    exp_th_fig = go.Figure(
                        data=[
                            go.Bar(
                                x=[cnt_val],
                                y=[selected_th],
                                orientation="h",
                                marker_color="#0F8B8D",
                                text=[cnt_val],
                                textposition="outside",
                            )
                        ]
                    )
                    style_plotly_fig(exp_th_fig, x_title="Students Requiring Service", y_title="Therapy Service")
                    st.session_state["expanded_detail"] = {
                        "title": f"Therapy Service: {selected_th}",
                        "subtitle": "Demand breakdown from database records",
                        "fig": exp_th_fig,
                        "metrics": [
                            {"label": "Therapy Service", "value": selected_th},
                            {"label": "Students Requiring Service", "value": cnt_val},
                            {"label": "Share of Therapy Requests", "value": pct_val},
                        ],
                    }
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with c_col:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Autism Centre Distribution")
            if summary_df.empty or summary_df["Autism Centres"].sum() == 0:
                st.info("No data available")
            else:
                fig_cnt = px.bar(
                    summary_df,
                    x="District",
                    y="Autism Centres",
                    color="District",
                    color_discrete_sequence=GRAPH_PALETTE,
                    text="Autism Centres",
                )
                fig_cnt.update_traces(textposition="outside", textfont_color="#111827")
                style_plotly_fig(fig_cnt, x_title="District", y_title="Number of Autism Centres")
                st.plotly_chart(fig_cnt, use_container_width=True, key="chart_centres_dist")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Kelantan District Accessibility Choropleth Map")
        render_kelantan_map(summary_df, centres_df)
        st.markdown("</div>", unsafe_allow_html=True)

    elif page == "District GIS Map":
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Kelantan District Accessibility Map")
        render_kelantan_map(summary_df, centres_df)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("District Accessibility Summary")
        if summary_df.empty:
            st.info("No data available")
        else:
            st.dataframe(
                summary_df[["District", "Registered Students", "Autism Centres", "Accessibility Status", "Available Therapies"]],
                use_container_width=True,
                hide_index=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    elif page == "Student & Centre Records":
        f1, f2 = st.columns(2)
        district_names = summary_df["District"].tolist() if not summary_df.empty else ["Kota Bharu"]

        with f1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Add Student Record")
            with st.form("add_student_form", clear_on_submit=True):
                s_code = st.text_input("Student ID", placeholder="e.g. KLT-020")
                s_name = st.text_input("Student Name", placeholder="Enter student name")
                s_dist = st.selectbox("District", options=district_names)
                s_diag = st.text_input("Diagnosis Category", placeholder="e.g. ASD Level 1")
                s_th = st.text_input("Therapy Required", placeholder="e.g. Speech Therapy")
                s_ver = st.checkbox("Verified Record", value=True)
                submitted_s = st.form_submit_button("Save Student Record")

            if submitted_s:
                if not all([s_code.strip(), s_name.strip(), s_diag.strip(), s_th.strip()]):
                    st.error("Please fill in all required student fields.")
                else:
                    try:
                        add_student_record(s_code, s_name, s_dist, s_diag, s_th, s_ver)
                        st.success("Student record saved and analytics updated.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Student ID already exists.")
            st.markdown("</div>", unsafe_allow_html=True)

        with f2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Add Autism Centre")
            with st.form("add_centre_form", clear_on_submit=True):
                c_name = st.text_input("Centre Name", placeholder="Enter autism centre name")
                c_dist = st.selectbox("District", options=district_names, key="centre_dist_select")
                c_lat = st.number_input("Latitude", value=6.1254, format="%.6f")
                c_lng = st.number_input("Longitude", value=102.2381, format="%.6f")
                c_th = st.text_input("Therapies Offered", placeholder="e.g. Speech Therapy, OT")
                submitted_c = st.form_submit_button("Save Autism Centre")

            if submitted_c:
                if not all([c_name.strip(), c_th.strip()]):
                    st.error("Please fill in centre name and therapies offered.")
                else:
                    add_centre_record(c_name, c_dist, c_lat, c_lng, c_th)
                    st.success("Autism centre saved and map/analytics updated.")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Registered Student Records")
        if students_df.empty:
            st.info("No data available")
        else:
            st.dataframe(students_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
