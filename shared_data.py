import pandas as pd
import streamlit as st

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


def init_state() -> pd.DataFrame:
    if "student_df" not in st.session_state:
        st.session_state["student_df"] = load_initial_csv().copy()
    if "selected_map_district" not in st.session_state:
        st.session_state["selected_map_district"] = "PASIR PUTEH"
    return st.session_state["student_df"]
