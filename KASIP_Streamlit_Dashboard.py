import html
import json
import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit as st

st.set_page_config(
    page_title="KASIP | Autism Service Intelligence Platform",
    page_icon="🧩",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b1220;
        color: #f4f7fc;
    }
    section[data-testid="stSidebar"] {
        background-color: #101a2c;
        border-right: 1px solid #2b3b56;
    }
    .kasip-header {
        background: linear-gradient(120deg, #121e32 0%, #1c2c4a 60%, #123d39 100%);
        border: 1px solid #2b3b56;
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .kasip-eyebrow {
        color: #93a7c7;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.2px;
    }
    .kasip-title {
        margin: 4px 0 0 0;
        font-size: 24px;
        font-weight: 800;
        color: #f4f7fc;
    }
    .kasip-pill {
        background: #123d39;
        color: #70e2c6;
        border: 1px solid #1b6b60;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
    }
    .kasip-panel {
        background: #121e32;
        border: 1px solid #2b3b56;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
    }
    .kasip-dist-card {
        background: #1b2b44;
        border: 1px solid #2c405e;
        border-radius: 10px;
        padding: 11px 13px;
        margin-bottom: 8px;
    }
    .kasip-bar-track {
        height: 9px;
        border-radius: 10px;
        background: #2b3c57;
        overflow: hidden;
        margin-top: 5px;
        margin-bottom: 12px;
    }
    .kasip-bar-fill {
        height: 100%;
        border-radius: 10px;
    }
    .kasip-badge {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        color: #ffffff;
    }
    .flip-preview-box {
        background: #1b2b44;
        border: 1px solid #2c405e;
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0 12px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DISTRICT_META = {
    "KOTA BHARU": {
        "lat": 6.1254,
        "lon": 102.2381,
        "centres": 4,
        "access": "Good access",
        "zone": "Green Zone",
        "color": "green",
        "hex": "#22a879",
        "recommended_centre": "NASOM Malaysia - Kota Bharu",
        "therapists": "Speech-Language Pathologists (SLP), Occupational Therapists (OT), ABA Therapists, Special Educators",
        "why_suitable": "Highest concentration of therapy specialists and structured autism programs in the registry.",
    },
    "BACHOK": {
        "lat": 6.0610,
        "lon": 102.3976,
        "centres": 2,
        "access": "Moderate access",
        "zone": "Yellow Zone",
        "color": "orange",
        "hex": "#e4ae42",
        "recommended_centre": "Bachok Autism Outreach Clinic",
        "therapists": "Early Intervention Specialists, Speech Therapy Support, Behavioral Coaches",
        "why_suitable": "Keeps travel short within Bachok to reduce travel fatigue and support daily routine consistency.",
    },
    "PASIR MAS": {
        "lat": 6.1042,
        "lon": 102.1412,
        "centres": 2,
        "access": "Good access",
        "zone": "Yellow Zone",
        "color": "orange",
        "hex": "#e4ae42",
        "recommended_centre": "Pasir Mas Early Intervention Centre",
        "therapists": "Early Childhood Special Educators, Speech & Language Therapists, Sensory-Motor Therapists",
        "why_suitable": "Offers local early intervention and structured skill development close to home.",
    },
    "PASIR PUTEH": {
        "lat": 5.8361,
        "lon": 102.4042,
        "centres": 1,
        "access": "Critical shortage",
        "zone": "Red Zone",
        "color": "red",
        "hex": "#e05d65",
        "recommended_centre": "Pasir Puteh Special Needs Center",
        "therapists": "Developmental Therapists, Motor & Play Specialists, Caregiver Counselors",
        "why_suitable": "Closest local option in Pasir Puteh for foundational therapy and parent guidance.",
    },
    "WAKAF BHARU": {
        "lat": 6.1400,
        "lon": 102.2100,
        "centres": 1,
        "access": "Critical shortage",
        "zone": "Red Zone",
        "color": "red",
        "hex": "#e05d65",
        "recommended_centre": "Wakaf Bharu Care & Intervention Hub",
        "therapists": "Occupational Therapy Practitioners, Daily Living Skills Coaches, Sensory Facilitators",
        "why_suitable": "Supports daily living routines, sensory regulation, and practical skill carryover.",
    },
    "TUMPAT": {
        "lat": 6.1990,
        "lon": 102.1700,
        "centres": 1,
        "access": "Critical shortage",
        "zone": "Red Zone",
        "color": "red",
        "hex": "#e05d65",
        "recommended_centre": "Tumpat Pediatric Therapy Unit",
        "therapists": "Pediatric Speech Therapists, Play-Based Interventionists, Social Communication Coaches",
        "why_suitable": "Provides child-friendly speech and play-based communication support in Tumpat.",
    },
    "RANTAU PANJANG": {
        "lat": 6.0200,
        "lon": 101.9800,
        "centres": 1,
        "access": "Moderate access",
        "zone": "Yellow Zone",
        "color": "orange",
        "hex": "#e4ae42",
        "recommended_centre": "Rantau Panjang Autism Support Hub",
        "therapists": "Outreach Special Educators, Speech & Communication Coaches, Parent Training Advisors",
        "why_suitable": "Reduces long travel distances for border families and supports home-based routines.",
    },
}

MODULES_4 = [
    {
        "key": "AG",
        "code": "Module AG",
        "title": "Toilet Training & Hygiene",
        "domain": "Self-Care & Daily Routine",
        "color": "#3987e8",
        "soft_bg": "#152b47",
        "pages": [
            ("Page 1 • Welcome & Goal", "Build calm, predictable toilet and handwashing habits at home and at the centre.", "• Use clear visual cues for each step.\n• Keep bathroom visits calm and unhurried.\n• Praise effort right after each step."),
            ("Page 2 • Visual Cue Card", "Show the toilet visual card before walking into the bathroom.", "• Hold or point to the card at eye level.\n• Say a short phrase: 'Time for toilet.'\n• Keep instructions brief during transitions."),
            ("Page 3 • Hygiene & Handwashing", "Follow a steady sequence: sit, wipe/flush, soap, rinse & dry.", "• Count gently to 10 while washing with soap.\n• Keep soap and towel within easy reach."),
            ("Page 4 • Encouragement & Tracking", "Celebrate progress and stay patient if an accident happens.", "• Praise independent steps right away.\n• Stay calm and reset neutrally if accidents occur."),
        ],
    },
    {
        "key": "AH",
        "code": "Module AH",
        "title": "Arrival Routine & Classroom Transition",
        "domain": "Home & Learning Transitions",
        "color": "#7667ed",
        "soft_bg": "#231e4a",
        "pages": [
            ("Page 1 • Welcome & Goal", "Help your child move smoothly from home to car, centre, or classroom.", "• Give advance countdowns before changes.\n• Use a 'First / Then' visual board.\n• Keep morning greetings calm and welcoming."),
            ("Page 2 • Countdown Cue", "Let your child know a transition is coming 3 to 5 minutes ahead.", "• Use a visual timer or count down slowly.\n• Repeat the cue once when time is almost up."),
            ("Page 3 • 'First / Then' Board", "Pair a routine task ('First: Bag & shoes') with a motivating step ('Then: Play').", "• Point to 'First' while doing the task.\n• Move to 'Then' right after completion."),
            ("Page 4 • Calm Arrival Check-In", "Give a few quiet moments to settle in when arriving at a new space.", "• Allow your child to hold a comfort item or visual card.\n• Avoid rushing questions right at the door."),
        ],
    },
    {
        "key": "AI",
        "code": "Module AI",
        "title": "Morning Walk & Sensory Regulation",
        "domain": "Physical, Motor & Sensory",
        "color": "#16b8a6",
        "soft_bg": "#11373a",
        "pages": [
            ("Page 1 • Welcome & Goal", "Use gentle morning movement and sensory awareness to support calm focus.", "• Walk at your child's comfortable pace.\n• Notice early signs of sensory overload.\n• Include a calm reset before learning tasks."),
            ("Page 2 • Morning Walk Routine", "Take a short, predictable walk along a quiet path or yard.", "• Focus on steady footsteps and fresh air.\n• Keep talking light and encouraging."),
            ("Page 3 • Sensory Environment Check", "Adjust sound, brightness, or crowding before discomfort builds.", "• Offer ear defenders/headphones or a quiet corner early.\n• Watch for signs of noise or crowd overload."),
            ("Page 4 • Calm Reset Before Tasks", "Take 1–2 minutes for slow breathing, stretching, or water sip.", "• A regulated body makes listening and learning easier."),
        ],
    },
    {
        "key": "SK",
        "code": "Module SK",
        "title": "Speech & Picture Exchange (PECS)",
        "domain": "Communication Support",
        "color": "#f2a64a",
        "soft_bg": "#3b2c19",
        "pages": [
            ("Page 1 • Welcome & Goal", "Support everyday communication using picture cards, gestures, and clear speech.", "• Honor picture/card requests immediately.\n• Pair spoken words with visual cues.\n• Keep communication fun and stress-free."),
            ("Page 2 • Exchanging Picture Cards", "Teach your child to hand over or tap a card for a desired item.", "• Start with 2–3 high-interest items (water, snack, toy, break).\n• Give the item right away so the connection is clear."),
            ("Page 3 • Pairing Clear Spoken Words", "Say the target word clearly right as the card is shared.", "• Use short, clear models like 'Water' or 'More'.\n• Avoid forcing long sentences if your child feels stuck."),
            ("Page 4 • Daily Home Practice", "Keep key communication cards handy during meals, play, and therapy.", "• Add new cards gradually as your child's needs and interests grow."),
        ],
    },
]

EMBEDDED_RECORDS = json.loads("""[{"Record ID": "KOD-1000", "Identifier": "Child Record #1 (Anonymized)", "Age": 4, "District": "KOTA BHARU", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1001", "Identifier": "Child Record #2 (Anonymized)", "Age": 5, "District": "BACHOK", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1002", "Identifier": "Child Record #3 (Anonymized)", "Age": 6, "District": "PASIR MAS", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1003", "Identifier": "Child Record #4 (Anonymized)", "Age": 7, "District": "PASIR PUTEH", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1004", "Identifier": "Child Record #5 (Anonymized)", "Age": 8, "District": "WAKAF BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1005", "Identifier": "Child Record #6 (Anonymized)", "Age": 9, "District": "TUMPAT", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1006", "Identifier": "Child Record #7 (Anonymized)", "Age": 10, "District": "RANTAU PANJANG", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1007", "Identifier": "Child Record #8 (Anonymized)", "Age": 11, "District": "KOTA BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1008", "Identifier": "Child Record #9 (Anonymized)", "Age": 12, "District": "BACHOK", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1009", "Identifier": "Child Record #10 (Anonymized)", "Age": 13, "District": "PASIR MAS", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1010", "Identifier": "Child Record #11 (Anonymized)", "Age": 14, "District": "PASIR PUTEH", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1011", "Identifier": "Child Record #12 (Anonymized)", "Age": 15, "District": "WAKAF BHARU", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1012", "Identifier": "Child Record #13 (Anonymized)", "Age": 4, "District": "TUMPAT", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1013", "Identifier": "Child Record #14 (Anonymized)", "Age": 5, "District": "RANTAU PANJANG", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1014", "Identifier": "Child Record #15 (Anonymized)", "Age": 6, "District": "KOTA BHARU", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1015", "Identifier": "Child Record #16 (Anonymized)", "Age": 7, "District": "BACHOK", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1016", "Identifier": "Child Record #17 (Anonymized)", "Age": 8, "District": "PASIR MAS", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1017", "Identifier": "Child Record #18 (Anonymized)", "Age": 9, "District": "PASIR PUTEH", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1018", "Identifier": "Child Record #19 (Anonymized)", "Age": 10, "District": "WAKAF BHARU", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1019", "Identifier": "Child Record #20 (Anonymized)", "Age": 11, "District": "TUMPAT", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1020", "Identifier": "Child Record #21 (Anonymized)", "Age": 12, "District": "RANTAU PANJANG", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1021", "Identifier": "Child Record #22 (Anonymized)", "Age": 13, "District": "KOTA BHARU", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1022", "Identifier": "Child Record #23 (Anonymized)", "Age": 14, "District": "BACHOK", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1023", "Identifier": "Child Record #24 (Anonymized)", "Age": 15, "District": "PASIR MAS", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1024", "Identifier": "Child Record #25 (Anonymized)", "Age": 4, "District": "PASIR PUTEH", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1025", "Identifier": "Child Record #26 (Anonymized)", "Age": 5, "District": "WAKAF BHARU", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1026", "Identifier": "Child Record #27 (Anonymized)", "Age": 6, "District": "TUMPAT", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1027", "Identifier": "Child Record #28 (Anonymized)", "Age": 7, "District": "RANTAU PANJANG", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1028", "Identifier": "Child Record #29 (Anonymized)", "Age": 8, "District": "KOTA BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1029", "Identifier": "Child Record #30 (Anonymized)", "Age": 9, "District": "BACHOK", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1030", "Identifier": "Child Record #31 (Anonymized)", "Age": 10, "District": "PASIR MAS", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1031", "Identifier": "Child Record #32 (Anonymized)", "Age": 11, "District": "PASIR PUTEH", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1032", "Identifier": "Child Record #33 (Anonymized)", "Age": 12, "District": "WAKAF BHARU", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1033", "Identifier": "Child Record #34 (Anonymized)", "Age": 13, "District": "TUMPAT", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1034", "Identifier": "Child Record #35 (Anonymized)", "Age": 14, "District": "RANTAU PANJANG", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1035", "Identifier": "Child Record #36 (Anonymized)", "Age": 15, "District": "KOTA BHARU", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1036", "Identifier": "Child Record #37 (Anonymized)", "Age": 4, "District": "BACHOK", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1037", "Identifier": "Child Record #38 (Anonymized)", "Age": 5, "District": "PASIR MAS", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1038", "Identifier": "Child Record #39 (Anonymized)", "Age": 6, "District": "PASIR PUTEH", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1039", "Identifier": "Child Record #40 (Anonymized)", "Age": 7, "District": "WAKAF BHARU", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1040", "Identifier": "Child Record #41 (Anonymized)", "Age": 8, "District": "TUMPAT", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1041", "Identifier": "Child Record #42 (Anonymized)", "Age": 9, "District": "RANTAU PANJANG", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1042", "Identifier": "Child Record #43 (Anonymized)", "Age": 10, "District": "KOTA BHARU", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1043", "Identifier": "Child Record #44 (Anonymized)", "Age": 11, "District": "BACHOK", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1044", "Identifier": "Child Record #45 (Anonymized)", "Age": 12, "District": "PASIR MAS", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1045", "Identifier": "Child Record #46 (Anonymized)", "Age": 13, "District": "PASIR PUTEH", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1046", "Identifier": "Child Record #47 (Anonymized)", "Age": 14, "District": "WAKAF BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1047", "Identifier": "Child Record #48 (Anonymized)", "Age": 15, "District": "TUMPAT", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1048", "Identifier": "Child Record #49 (Anonymized)", "Age": 4, "District": "RANTAU PANJANG", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1049", "Identifier": "Child Record #50 (Anonymized)", "Age": 5, "District": "KOTA BHARU", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1050", "Identifier": "Child Record #51 (Anonymized)", "Age": 6, "District": "BACHOK", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1051", "Identifier": "Child Record #52 (Anonymized)", "Age": 7, "District": "PASIR MAS", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1052", "Identifier": "Child Record #53 (Anonymized)", "Age": 8, "District": "PASIR PUTEH", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1053", "Identifier": "Child Record #54 (Anonymized)", "Age": 9, "District": "WAKAF BHARU", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1054", "Identifier": "Child Record #55 (Anonymized)", "Age": 10, "District": "TUMPAT", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1055", "Identifier": "Child Record #56 (Anonymized)", "Age": 11, "District": "RANTAU PANJANG", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1056", "Identifier": "Child Record #57 (Anonymized)", "Age": 12, "District": "KOTA BHARU", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1057", "Identifier": "Child Record #58 (Anonymized)", "Age": 13, "District": "BACHOK", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1058", "Identifier": "Child Record #59 (Anonymized)", "Age": 14, "District": "PASIR MAS", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1059", "Identifier": "Child Record #60 (Anonymized)", "Age": 15, "District": "PASIR PUTEH", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1060", "Identifier": "Child Record #61 (Anonymized)", "Age": 4, "District": "WAKAF BHARU", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1061", "Identifier": "Child Record #62 (Anonymized)", "Age": 5, "District": "TUMPAT", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1062", "Identifier": "Child Record #63 (Anonymized)", "Age": 6, "District": "RANTAU PANJANG", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1063", "Identifier": "Child Record #64 (Anonymized)", "Age": 7, "District": "KOTA BHARU", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1064", "Identifier": "Child Record #65 (Anonymized)", "Age": 8, "District": "BACHOK", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1065", "Identifier": "Child Record #66 (Anonymized)", "Age": 9, "District": "PASIR MAS", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1066", "Identifier": "Child Record #67 (Anonymized)", "Age": 10, "District": "PASIR PUTEH", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1067", "Identifier": "Child Record #68 (Anonymized)", "Age": 11, "District": "WAKAF BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1068", "Identifier": "Child Record #69 (Anonymized)", "Age": 12, "District": "TUMPAT", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1069", "Identifier": "Child Record #70 (Anonymized)", "Age": 13, "District": "RANTAU PANJANG", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1070", "Identifier": "Child Record #71 (Anonymized)", "Age": 14, "District": "KOTA BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1071", "Identifier": "Child Record #72 (Anonymized)", "Age": 15, "District": "BACHOK", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1072", "Identifier": "Child Record #73 (Anonymized)", "Age": 4, "District": "PASIR MAS", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1073", "Identifier": "Child Record #74 (Anonymized)", "Age": 5, "District": "PASIR PUTEH", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1074", "Identifier": "Child Record #75 (Anonymized)", "Age": 6, "District": "WAKAF BHARU", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1075", "Identifier": "Child Record #76 (Anonymized)", "Age": 7, "District": "TUMPAT", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1076", "Identifier": "Child Record #77 (Anonymized)", "Age": 8, "District": "RANTAU PANJANG", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1077", "Identifier": "Child Record #78 (Anonymized)", "Age": 9, "District": "KOTA BHARU", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1078", "Identifier": "Child Record #79 (Anonymized)", "Age": 10, "District": "BACHOK", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1079", "Identifier": "Child Record #80 (Anonymized)", "Age": 11, "District": "PASIR MAS", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1080", "Identifier": "Child Record #81 (Anonymized)", "Age": 12, "District": "PASIR PUTEH", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1081", "Identifier": "Child Record #82 (Anonymized)", "Age": 13, "District": "WAKAF BHARU", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1082", "Identifier": "Child Record #83 (Anonymized)", "Age": 14, "District": "TUMPAT", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1083", "Identifier": "Child Record #84 (Anonymized)", "Age": 15, "District": "RANTAU PANJANG", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1084", "Identifier": "Child Record #85 (Anonymized)", "Age": 4, "District": "KOTA BHARU", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1085", "Identifier": "Child Record #86 (Anonymized)", "Age": 5, "District": "BACHOK", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1086", "Identifier": "Child Record #87 (Anonymized)", "Age": 6, "District": "PASIR MAS", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1087", "Identifier": "Child Record #88 (Anonymized)", "Age": 7, "District": "PASIR PUTEH", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1088", "Identifier": "Child Record #89 (Anonymized)", "Age": 8, "District": "WAKAF BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1089", "Identifier": "Child Record #90 (Anonymized)", "Age": 9, "District": "TUMPAT", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1090", "Identifier": "Child Record #91 (Anonymized)", "Age": 10, "District": "RANTAU PANJANG", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1091", "Identifier": "Child Record #92 (Anonymized)", "Age": 11, "District": "KOTA BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1092", "Identifier": "Child Record #93 (Anonymized)", "Age": 12, "District": "BACHOK", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1093", "Identifier": "Child Record #94 (Anonymized)", "Age": 13, "District": "PASIR MAS", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1094", "Identifier": "Child Record #95 (Anonymized)", "Age": 14, "District": "PASIR PUTEH", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1095", "Identifier": "Child Record #96 (Anonymized)", "Age": 15, "District": "WAKAF BHARU", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1096", "Identifier": "Child Record #97 (Anonymized)", "Age": 4, "District": "TUMPAT", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1097", "Identifier": "Child Record #98 (Anonymized)", "Age": 5, "District": "RANTAU PANJANG", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1098", "Identifier": "Child Record #99 (Anonymized)", "Age": 6, "District": "KOTA BHARU", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1099", "Identifier": "Child Record #100 (Anonymized)", "Age": 7, "District": "BACHOK", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1100", "Identifier": "Child Record #101 (Anonymized)", "Age": 8, "District": "PASIR MAS", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1101", "Identifier": "Child Record #102 (Anonymized)", "Age": 9, "District": "PASIR PUTEH", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1102", "Identifier": "Child Record #103 (Anonymized)", "Age": 10, "District": "WAKAF BHARU", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1103", "Identifier": "Child Record #104 (Anonymized)", "Age": 11, "District": "TUMPAT", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}]""")


def module_svg(mod_key: str, accent: str, soft_bg: str) -> str:
    if mod_key == "AG":
        art = """
        <rect x="34" y="32" width="76" height="92" rx="14" fill="#121e32" stroke="#3987e8" stroke-width="3"/>
        <circle cx="72" cy="62" r="14" fill="#254c7a"/>
        <path d="M54 100 Q72 82 90 100 Z" fill="#3987e8"/>
        <path d="M148 54 Q168 36 188 54 Q188 82 168 94 Q148 82 148 54 Z" fill="#38bdf8"/>
        <circle cx="226" cy="72" r="24" fill="#121e32" stroke="#22a879" stroke-width="3"/>
        <path d="M216 72 L223 79 L237 65" fill="none" stroke="#22a879" stroke-width="4" stroke-linecap="round"/>
        """
    elif mod_key == "AH":
        art = """
        <rect x="32" y="36" width="96" height="84" rx="12" fill="#121e32" stroke="#7667ed" stroke-width="3"/>
        <text x="80" y="62" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#a599ff">FIRST</text>
        <rect x="52" y="72" width="56" height="32" rx="6" fill="#2b255c"/>
        <polygon points="144,70 162,78 144,86" fill="#7667ed"/>
        <rect x="174" y="36" width="96" height="84" rx="12" fill="#121e32" stroke="#22a879" stroke-width="3"/>
        <text x="222" y="62" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#70e2c6">THEN</text>
        <circle cx="222" cy="88" r="16" fill="#164e44"/>
        """
    elif mod_key == "AI":
        art = """
        <circle cx="64" cy="52" r="18" fill="#f2a64a"/>
        <path d="M28 122 Q85 94 145 110 T276 94 L276 140 L28 140 Z" fill="#144943"/>
        <circle cx="152" cy="64" r="11" fill="#70e2c6"/>
        <path d="M152 75 L145 100 L134 116 M152 75 L160 100 L172 113 M152 82 L136 92 M152 82 L168 90" stroke="#70e2c6" stroke-width="4" stroke-linecap="round" fill="none"/>
        <circle cx="235" cy="62" r="20" fill="#121e32" stroke="#16b8a6" stroke-width="3"/>
        <path d="M225 62 Q235 50 245 62 Q235 74 225 62" fill="#16b8a6"/>
        """
    else:
        art = """
        <rect x="34" y="36" width="84" height="84" rx="12" fill="#121e32" stroke="#f2a64a" stroke-width="3"/>
        <circle cx="76" cy="68" r="16" fill="#5e431e"/>
        <rect x="52" y="92" width="48" height="10" rx="5" fill="#f2a64a"/>
        <path d="M132 78 L156 78" stroke="#f2a64a" stroke-width="4" stroke-linecap="round"/>
        <polygon points="154,70 168,78 154,86" fill="#f2a64a"/>
        <rect x="178" y="36" width="94" height="84" rx="12" fill="#121e32" stroke="#3987e8" stroke-width="3"/>
        <circle cx="212" cy="68" r="10" fill="#3987e8"/>
        <circle cx="242" cy="68" r="10" fill="#22a879"/>
        <rect x="196" y="90" width="58" height="12" rx="6" fill="#1d3557"/>
        """
    return f"""
    <svg viewBox="0 0 304 152" width="100%" height="152" xmlns="http://www.w3.org/2000/svg" style="border-radius:12px;background:{soft_bg};display:block;">
        {art}
    </svg>
    """


def build_flipbook_html(mod: dict) -> str:
    title_esc = html.escape(f"{mod['code']}: {mod['title']}")
    domain_esc = html.escape(mod["domain"])
    accent = mod["color"]
    soft_bg = mod["soft_bg"]
    svg_art = module_svg(mod["key"], accent, soft_bg)

    pages_js = []
    for p_title, p_summary, p_steps in mod["pages"]:
        pages_js.append(
            "{"
            f'"heading": "{html.escape(p_title)}", '
            f'"summary": "{html.escape(p_summary)}", '
            f'"steps": "{html.escape(p_steps).replace(chr(10), "<br>")}"'
            "}"
        )
    pages_arr = "[" + ", ".join(pages_js) + "]"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title_esc} — KASIP Flipbook</title>
<style>
  body {{
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #0b1220;
    margin: 0;
    padding: 28px;
    color: #f4f7fc;
    display: flex;
    justify-content: center;
  }}
  .book {{
    max-width: 720px;
    width: 100%;
    background: #121e32;
    border: 1px solid #2b3b56;
    border-top: 7px solid {accent};
    border-radius: 16px;
    padding: 24px;
  }}
  .badge {{
    display: inline-block;
    background: {accent};
    color: #ffffff;
    font-weight: 700;
    font-size: 12px;
    padding: 4px 12px;
    border-radius: 999px;
  }}
  h1 {{ margin: 10px 0 4px 0; font-size: 23px; }}
  .sub {{ color: #a9b8d0; font-size: 13px; margin-bottom: 14px; }}
  .page-card {{
    background: {soft_bg};
    border: 1px solid #2c405e;
    border-radius: 12px;
    padding: 18px;
    margin-top: 14px;
  }}
  .p-title {{ font-size: 17px; font-weight: 700; margin-bottom: 8px; }}
  .p-sum {{ color: #e3eaf5; margin-bottom: 12px; line-height: 1.5; }}
  .p-steps {{ background: #121e32; padding: 14px; border-radius: 10px; line-height: 1.65; font-size: 14px; }}
  .controls {{ display: flex; justify-content: space-between; align-items: center; margin-top: 18px; }}
  button {{
    background: {accent}; color: #ffffff; border: 0; padding: 10px 16px;
    border-radius: 9px; font-weight: 700; cursor: pointer;
  }}
  button:disabled {{ background: #2b3c57; color: #8fa1bd; cursor: not-allowed; }}
</style>
</head>
<body>
  <div class="book">
    <span class="badge">INTERACTIVE FLIPBOOK</span>
    <h1>{title_esc}</h1>
    <div class="sub">Domain: {domain_esc} • Use buttons or Left/Right arrow keys</div>
    {svg_art}
    <div class="page-card">
      <div class="p-title" id="h"></div>
      <div class="p-sum" id="s"></div>
      <div class="p-steps" id="t"></div>
    </div>
    <div class="controls">
      <button id="prevBtn" onclick="go(-1)">← Previous</button>
      <span id="ind" style="font-weight:700;color:#a9b8d0;"></span>
      <button id="nextBtn" onclick="go(1)">Next →</button>
    </div>
  </div>
<script>
  const pages = {pages_arr};
  let i = 0;
  function render() {{
    const p = pages[i];
    document.getElementById("h").innerHTML = p.heading;
    document.getElementById("s").innerHTML = p.summary;
    document.getElementById("t").innerHTML = p.steps;
    document.getElementById("ind").innerText = `Page ${{i + 1}} of ${{pages.length}}`;
    document.getElementById("prevBtn").disabled = i === 0;
    document.getElementById("nextBtn").disabled = i === pages.length - 1;
  }}
  function go(d) {{
    if (i + d >= 0 && i + d < pages.length) {{ i += d; render(); }}
  }}
  document.addEventListener("keydown", e => {{
    if (e.key === "ArrowRight") go(1);
    if (e.key === "ArrowLeft") go(-1);
  }});
  render();
</script>
</body>
</html>
"""


@st.cache_data
def load_csv_fallback(path: str = "Kelantan_Student_Registry_104.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except Exception:
        df = pd.DataFrame(EMBEDDED_RECORDS)
    df["District"] = df["District"].astype(str).str.strip().str.upper()
    return df


if "student_df" not in st.session_state:
    st.session_state["student_df"] = load_csv_fallback().copy()

if "selected_zone_district" not in st.session_state:
    st.session_state["selected_zone_district"] = "PASIR PUTEH"

for mod in MODULES_4:
    k = f"flip_idx_{mod['key']}"
    if k not in st.session_state:
        st.session_state[k] = 0

df_students = st.session_state["student_df"].copy()

st.sidebar.markdown("### 🧩 KASIP")
st.sidebar.caption("Autism Service Intelligence Platform")
st.sidebar.markdown("**ADMIN PORTAL**")
admin_pages = [
    "Zone Map & Analytics",
    "Student Registry",
    "Service & Age Graphs",
]
st.sidebar.markdown("**PARENTS PORTAL**")
parent_pages = [
    "Child & Centre Matcher",
    "4 Training Modules",
]
all_pages = admin_pages + parent_pages
page = st.sidebar.radio("Navigate", all_pages, label_visibility="collapsed")

portal_label = "ADMIN PORTAL" if page in admin_pages else "PARENTS PORTAL"
st.markdown(
    f"""
    <div class="kasip-header">
        <div>
            <div class="kasip-eyebrow">KELANTAN • {portal_label}</div>
            <div class="kasip-title">{html.escape(page)}</div>
        </div>
        <span class="kasip-pill">● INTERACTIVE LIVE</span>
    </div>
    """,
    unsafe_allow_html=True,
)

counts_by_dist = df_students["District"].value_counts().to_dict()

if page == "Zone Map & Analytics":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registered Children", len(df_students), "Kelantan Registry")
    c2.metric("Verified Active", int((df_students["Status"] == "Verified Active").sum()), "Active status")
    c3.metric("Pending Verification", int((df_students["Status"] == "Pending Verification").sum()), "Needs review")
    c4.metric("Red Zone Districts", sum(1 for v in DISTRICT_META.values() if v["zone"] == "Red Zone"), "High deficit")

    map_col, right_col = st.columns([1.25, 0.85], gap="large")

    with map_col:
        st.markdown('<div class="kasip-panel">', unsafe_allow_html=True)
        st.markdown("### Kelantan Zone Map & District Distribution")
        st.caption("Click any coloured district marker on the map or choose below to open place details.")

        fmap = folium.Map(location=[6.02, 102.22], zoom_start=10, tiles="OpenStreetMap")
        for d_name, meta in DISTRICT_META.items():
            stu_n = int(counts_by_dist.get(d_name, 0))
            pop_txt = (
                f"<b>{d_name}</b><br>"
                f"Zone: <b>{meta['zone']}</b> ({meta['access']})<br>"
                f"Students: <b>{stu_n}</b> | Centres: <b>{meta['centres']}</b><br>"
                f"Centre: {meta['recommended_centre']}"
            )
            folium.CircleMarker(
                location=[meta["lat"], meta["lon"]],
                radius=15,
                color=meta["color"],
                fill=True,
                fill_color=meta["color"],
                fill_opacity=0.82,
                tooltip=d_name,
                popup=folium.Popup(pop_txt, max_width=260),
            ).add_to(fmap)

        out = st_folium(fmap, use_container_width=True, height=350, returned_objects=["last_object_clicked_tooltip"])
        clicked = out.get("last_object_clicked_tooltip") if isinstance(out, dict) else None
        if clicked in DISTRICT_META:
            st.session_state["selected_zone_district"] = clicked

        chosen_dist = st.selectbox(
            "Pop-Up Place Details (Synced with Map)",
            options=list(DISTRICT_META.keys()),
            index=list(DISTRICT_META.keys()).index(st.session_state["selected_zone_district"]),
        )
        st.session_state["selected_zone_district"] = chosen_dist
        m_info = DISTRICT_META[chosen_dist]
        d_sub = df_students[df_students["District"] == chosen_dist]

        st.markdown(
            f"""
            <div class="kasip-dist-card" style="border-left:4px solid {m_info['hex']};margin-top:8px;">
                <span class="kasip-badge" style="background:{m_info['hex']};">{m_info['zone']} • {m_info['access']}</span>
                <div style="font-weight:700;font-size:15px;margin-top:6px;">📍 {chosen_dist}</div>
                <div style="color:#a9b8d0;font-size:12px;margin-top:4px;">
                    Students: <b>{len(d_sub)}</b> | Centres: <b>{m_info['centres']}</b> | Recommended: <b>{html.escape(m_info['recommended_centre'])}</b>
                </div>
                <div style="color:#cbd6e8;font-size:12px;margin-top:4px;">
                    Therapists: {html.escape(m_info['therapists'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="kasip-panel">', unsafe_allow_html=True)
        st.markdown("### Service Categories & District Share")
        st.caption("Share of students by required service and district")
        total_n = max(1, len(df_students))
        service_colors = {
            "Speech Therapy": "#3987e8",
            "Occupational Sensory": "#16b8a6",
            "Early Intervention": "#7667ed",
            "ABA Therapy": "#f2a64a",
        }
        for s_name, s_cnt in df_students["Required Service"].value_counts().items():
            pct = round((int(s_cnt) / total_n) * 100)
            col_hex = service_colors.get(s_name, "#7667ed")
            st.markdown(
                f"""
                <div style="display:flex;justify-content:space-between;font-size:13px;">
                    <span>{html.escape(str(s_name))}</span><b>{pct}% ({int(s_cnt)})</b>
                </div>
                <div class="kasip-bar-track">
                    <div class="kasip-bar-fill" style="width:{pct}%;background:{col_hex};"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.bar_chart(df_students.groupby("District").size().rename("Students"), height=190)
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Student Registry":
    st.markdown('<div class="kasip-panel">', unsafe_allow_html=True)
    st.markdown("### Insert New Student Record")
    with st.form("add_student_form", clear_on_submit=True):
        f1, f2, f3, f4 = st.columns(4)
        new_id = f1.text_input("Student / Record ID", value=f"KOD-{1000 + len(df_students)}")
        new_ident = f2.text_input("Child Identifier / Name", value=f"Child Record #{len(df_students) + 1} (Anonymized)")
        new_age = f3.number_input("Age", min_value=1, max_value=21, value=6)
        new_dist = f4.selectbox("District", list(DISTRICT_META.keys()))

        f5, f6, f7, f8 = st.columns(4)
        new_diag = f5.selectbox("Diagnosis", ["Mild Autism", "High-Function Autism", "Severe Autism"])
        new_serv = f6.selectbox("Required Service", ["Speech Therapy", "ABA Therapy", "Occupational Sensory", "Early Intervention"])
        new_date = f7.text_input("Date (YYYY-MM-DD)", value="2026-11-23")
        new_status = f8.selectbox("Status", ["Verified Active", "Pending Verification"])

        if st.form_submit_button("＋ Add Student"):
            row = pd.DataFrame([{
                "Record ID": new_id.strip(),
                "Identifier": new_ident.strip(),
                "Age": int(new_age),
                "District": new_dist,
                "Diagnosis": new_diag,
                "Required Service": new_serv,
                "Date": new_date.strip(),
                "Status": new_status,
            }])
            st.session_state["student_df"] = pd.concat([st.session_state["student_df"], row], ignore_index=True)
            st.success(f"Added {new_id}!")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="kasip-panel">', unsafe_allow_html=True)
    st.markdown("### Registered Children (Editable Table)")
    st.caption("Edit any cell directly below, then click Save Table Edits.")
    edited = st.data_editor(
        st.session_state["student_df"],
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "District": st.column_config.SelectboxColumn("District", options=list(DISTRICT_META.keys()), required=True),
            "Diagnosis": st.column_config.SelectboxColumn("Diagnosis", options=["Mild Autism", "High-Function Autism", "Severe Autism"], required=True),
            "Required Service": st.column_config.SelectboxColumn("Required Service", options=["Speech Therapy", "ABA Therapy", "Occupational Sensory", "Early Intervention"], required=True),
            "Status": st.column_config.SelectboxColumn("Status", options=["Verified Active", "Pending Verification"], required=True),
        },
    )
    b1, b2 = st.columns([1.5, 2.5])
    if b1.button("💾 Save Table Edits", type="primary"):
        st.session_state["student_df"] = edited.copy()
        st.success("Registry updated!")
    b2.download_button(
        "⬇️ Download Updated CSV",
        data=st.session_state["student_df"].to_csv(index=False).encode("utf-8"),
        file_name="Kelantan_Student_Registry_104_updated.csv",
        mime="text/csv",
    )
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Service & Age Graphs":
    g1, g2 = st.columns(2, gap="large")
    with g1:
        st.markdown('<div class="kasip-panel">', unsafe_allow_html=True)
        st.markdown("### Age Distribution")
        st.bar_chart(df_students.groupby("Age").size().rename("Students"), height=300)
        st.markdown("</div>", unsafe_allow_html=True)
    with g2:
        st.markdown('<div class="kasip-panel">', unsafe_allow_html=True)
        st.markdown("### Required Service by District")
        st.bar_chart(pd.crosstab(df_students["District"], df_students["Required Service"]), height=300)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="kasip-panel">', unsafe_allow_html=True)
    st.markdown("### Diagnosis vs. Required Service")
    st.bar_chart(pd.crosstab(df_students["Diagnosis"], df_students["Required Service"]), height=260)
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Child & Centre Matcher":
    st.markdown('<div class="kasip-panel">', unsafe_allow_html=True)
    f1, f2 = st.columns([2, 4])
    d_filt = f1.selectbox("Filter by District", ["ALL"] + list(DISTRICT_META.keys()))
    sub_pool = df_students if d_filt == "ALL" else df_students[df_students["District"] == d_filt]

    chosen_rec = f2.selectbox(
        "Select Child Record",
        options=sub_pool["Record ID"].tolist(),
        format_func=lambda rid: f"{rid} — {sub_pool.loc[sub_pool['Record ID'] == rid, 'Identifier'].values[0]} ({sub_pool.loc[sub_pool['Record ID'] == rid, 'District'].values[0]})",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    row = df_students[df_students["Record ID"] == chosen_rec].iloc[0]
    c_dist = str(row["District"]).upper()
    c_diag = str(row["Diagnosis"])
    c_meta = DISTRICT_META.get(c_dist, DISTRICT_META["KOTA BHARU"])

    left, right = st.columns([5, 7], gap="large")
    with left:
        st.markdown('<div class="kasip-panel">', unsafe_allow_html=True)
        st.markdown("### 👶 Child Information")
        st.markdown(f"- **Record ID:** `{row['Record ID']}`")
        st.markdown(f"- **Identifier:** {row['Identifier']}")
        st.markdown(f"- **Age:** `{row['Age']}` years old")
        st.markdown(f"- **District:** `{c_dist}` (`{c_meta['zone']}`)")
        st.markdown(f"- **Type of Autism:** `{c_diag}`")
        st.markdown(f"- **Required Service:** `{row['Required Service']}`")
        st.markdown(f"- **Status:** `{row['Status']}` (`{row['Date']}`)")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="kasip-panel">', unsafe_allow_html=True)
        st.markdown("### 🏥 Suitable Centre & Therapists Provided")
        st.markdown(
            f'<span class="kasip-badge" style="background:{c_meta["hex"]};">{c_meta["zone"]}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(f"#### ⭐ {c_meta['recommended_centre']}")
        st.markdown(f"**Why Suitable for {c_diag}:** {c_meta['why_suitable']}")
        st.markdown(f"**Therapists Provided:** {c_meta['therapists']}")
        st.markdown(f"**Matched Service:** `{row['Required Service']}`")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.caption("Flip through each module's pages below, or download the standalone interactive HTML flipbook.")
    cols = st.columns(2, gap="large")
    for idx, mod in enumerate(MODULES_4):
        idx_key = f"flip_idx_{mod['key']}"
        cur_p = st.session_state[idx_key]
        total_p = len(mod["pages"])
        p_head, p_sum, p_steps = mod["pages"][cur_p]

        with cols[idx % 2]:
            st.markdown('<div class="kasip-panel">', unsafe_allow_html=True)
            st.markdown(
                f'<span class="kasip-badge" style="background:{mod["color"]};">{mod["code"]} • {mod["domain"]}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(f"### {mod['title']}")
            st.markdown(module_svg(mod["key"], mod["color"], mod["soft_bg"]), unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="flip-preview-box" style="background:{mod['soft_bg']};">
                    <div style="font-weight:700;font-size:15px;margin-bottom:6px;">{html.escape(p_head)}</div>
                    <div style="color:#e3eaf5;font-size:13px;margin-bottom:10px;">{html.escape(p_sum)}</div>
                    <div style="background:#121e32;padding:12px;border-radius:9px;font-size:12.5px;line-height:1.55;">
                        {html.escape(p_steps).replace(chr(10), "<br>")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            n1, n2, n3 = st.columns([1, 1.3, 1])
            if n1.button("◀ Prev", key=f"prev_{mod['key']}", disabled=(cur_p == 0), use_container_width=True):
                st.session_state[idx_key] = cur_p - 1
                st.rerun()
            n2.markdown(
                f"<div style='text-align:center;padding-top:8px;font-weight:700;color:#a9b8d0;'>Page {cur_p + 1} / {total_p}</div>",
                unsafe_allow_html=True,
            )
            if n3.button("Next ▶", key=f"next_{mod['key']}", disabled=(cur_p == total_p - 1), use_container_width=True):
                st.session_state[idx_key] = cur_p + 1
                st.rerun()

            st.download_button(
                label=f"📖 Download {mod['code']} Flipbook (.html)",
                data=build_flipbook_html(mod).encode("utf-8"),
                file_name=f"{mod['code'].replace(' ', '_')}_Flipbook.html",
                mime="text/html",
                key=f"dl_{mod['key']}",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True
