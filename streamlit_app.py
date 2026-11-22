import html
import json
import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Kelantan Autism GIS — Interactive Dashboard",
    page_icon="🌈",
    layout="wide",
)

# Red / Yellow / Blue background theme with high-contrast readable cards
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #FEE2E2 0%, #FEF9C3 50%, #DBEAFE 100%) !important;
        color: #0F172A !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #991B1B 0%, #1E3A8A 100%) !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    .hero-banner {
        background: linear-gradient(120deg, #DC2626 0%, #F59E0B 50%, #2563EB 100%);
        padding: 18px 22px;
        border-radius: 14px;
        color: #FFFFFF;
        margin-bottom: 14px;
        border: 2px solid #FFFFFF;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.16);
    }
    .module-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 8px;
    }
    .flip-card {
        border-radius: 14px;
        padding: 20px;
        border: 2px solid #CBD5E1;
        background: #FFFFFF;
        color: #0F172A;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.92);
        border: 2px solid #2563EB;
        border-radius: 12px;
        padding: 12px 14px;
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0F172A !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DISTRICT_INFO = {
    "KOTA BHARU": {
        "lat": 6.1254,
        "lon": 102.2381,
        "centres": 4,
        "zone": "Green Zone",
        "color": "green",
        "badge_bg": "#10B981",
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
        "badge_bg": "#F59E0B",
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
        "badge_bg": "#F59E0B",
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
        "badge_bg": "#EF4444",
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
        "badge_bg": "#EF4444",
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
        "badge_bg": "#EF4444",
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
        "badge_bg": "#F59E0B",
        "place_summary": "Rantau Panjang Border Zone (14 students to 1 support hub).",
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
        "color": "#0284C7",
        "soft_bg": "#E0F2FE",
        "pages": [
            (
                "Page 1 • Welcome & Goal",
                "Build calm, predictable toilet and handwashing habits at home and at the centre.",
                "• Use clear picture cues for each step.\n• Keep bathroom visits calm and unhurried.\n• Praise effort right after each step.",
            ),
            (
                "Page 2 • Visual Cue Card",
                "Show the toilet visual card before walking into the bathroom.",
                "• Hold or point to the card at eye level.\n• Say a short phrase: 'Time for toilet.'\n• Avoid long explanations during transitions.",
            ),
            (
                "Page 3 • Hygiene & Handwashing",
                "Follow a steady 4-step sequence: sit, wipe/flush, soap, rinse & dry.",
                "• Count gently to 10 or sing a short 10-second song while washing.\n• Keep soap and towel within easy reach.",
            ),
            (
                "Page 4 • Encouragement & Tracking",
                "Celebrate progress and stay patient if an accident happens.",
                "• Use a sticker chart or high-five for completed steps.\n• If an accident happens, stay calm and clean up neutrally.",
            ),
        ],
    },
    {
        "key": "AH",
        "code": "Module AH",
        "title": "Arrival Routine & Classroom Transition",
        "domain": "Home & Learning Transitions",
        "color": "#7C3AED",
        "soft_bg": "#EDE9FE",
        "pages": [
            (
                "Page 1 • Welcome & Goal",
                "Help your child move smoothly from home to car, centre, or classroom.",
                "• Give advance countdowns before changes.\n• Use a 'First / Then' visual board.\n• Keep morning greetings warm and low-pressure.",
            ),
            (
                "Page 2 • Countdown Cue",
                "Let your child know a transition is coming 3 to 5 minutes ahead.",
                "• Use a visual timer or count down slowly.\n• Repeat the cue once when time is almost up.",
            ),
            (
                "Page 3 • 'First / Then' Board",
                "Pair a routine task ('First: Bag & shoes') with a motivating step ('Then: Play').",
                "• Point to 'First' while doing the task.\n• Move to 'Then' right after completion.",
            ),
            (
                "Page 4 • Calm Arrival Check-In",
                "Give a few quiet moments to settle in when arriving at a new space.",
                "• Allow your child to hold a comfort item or visual card.\n• Avoid rushing questions right at the door.",
            ),
        ],
    },
    {
        "key": "AI",
        "code": "Module AI",
        "title": "Morning Walk & Sensory Regulation",
        "domain": "Physical, Motor & Sensory",
        "color": "#059669",
        "soft_bg": "#D1FAE5",
        "pages": [
            (
                "Page 1 • Welcome & Goal",
                "Use gentle morning movement and sensory awareness to support calm focus.",
                "• Walk at your child's comfortable pace.\n• Notice early signs of sensory overload.\n• Include a calm reset before learning tasks.",
            ),
            (
                "Page 2 • Morning Walk Routine",
                "Take a short, predictable walk along a quiet path or yard.",
                "• Focus on steady footsteps and fresh air.\n• Keep talking light and encouraging.",
            ),
            (
                "Page 3 • Sensory Environment Check",
                "Adjust sound, brightness, or crowding before discomfort builds.",
                "• Offer ear defenders/headphones or a quiet corner early.\n• Watch for signs of noise or crowd overload.",
            ),
            (
                "Page 4 • Calm Reset Before Tasks",
                "Take 1–2 minutes for slow breathing, stretching, or water sip.",
                "• A regulated body makes listening and learning easier.",
            ),
        ],
    },
    {
        "key": "SK",
        "code": "Module SK",
        "title": "Speech & Picture Exchange (PECS)",
        "domain": "Communication Support",
        "color": "#D97706",
        "soft_bg": "#FEF3C7",
        "pages": [
            (
                "Page 1 • Welcome & Goal",
                "Support everyday communication using picture cards, gestures, and clear speech.",
                "• Honor picture/card requests immediately.\n• Pair spoken words with visual cues.\n• Keep communication fun and stress-free.",
            ),
            (
                "Page 2 • Exchanging Picture Cards",
                "Teach your child to hand over or tap a card for a desired item.",
                "• Start with 2–3 high-interest items (water, snack, toy, break).\n• Give the item right away so the connection is clear.",
            ),
            (
                "Page 3 • Pairing Clear Spoken Words",
                "Say the target word clearly right as the card is shared.",
                "• Use short, clear models like 'Water' or 'More'.\n• Avoid forcing long sentences if your child feels stuck.",
            ),
            (
                "Page 4 • Daily Home Practice",
                "Keep key communication cards handy during meals, play, and therapy.",
                "• Add new cards gradually as your child's needs and interests grow.",
            ),
        ],
    },
]

EMBEDDED_RECORDS = json.loads("""[{"Record ID": "KOD-1000", "Identifier": "Child Record #1 (Anonymized)", "Age": 4, "District": "KOTA BHARU", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1001", "Identifier": "Child Record #2 (Anonymized)", "Age": 5, "District": "BACHOK", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1002", "Identifier": "Child Record #3 (Anonymized)", "Age": 6, "District": "PASIR MAS", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1003", "Identifier": "Child Record #4 (Anonymized)", "Age": 7, "District": "PASIR PUTEH", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1004", "Identifier": "Child Record #5 (Anonymized)", "Age": 8, "District": "WAKAF BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1005", "Identifier": "Child Record #6 (Anonymized)", "Age": 9, "District": "TUMPAT", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1006", "Identifier": "Child Record #7 (Anonymized)", "Age": 10, "District": "RANTAU PANJANG", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1007", "Identifier": "Child Record #8 (Anonymized)", "Age": 11, "District": "KOTA BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1008", "Identifier": "Child Record #9 (Anonymized)", "Age": 12, "District": "BACHOK", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1009", "Identifier": "Child Record #10 (Anonymized)", "Age": 13, "District": "PASIR MAS", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1010", "Identifier": "Child Record #11 (Anonymized)", "Age": 14, "District": "PASIR PUTEH", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1011", "Identifier": "Child Record #12 (Anonymized)", "Age": 15, "District": "WAKAF BHARU", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1012", "Identifier": "Child Record #13 (Anonymized)", "Age": 4, "District": "TUMPAT", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1013", "Identifier": "Child Record #14 (Anonymized)", "Age": 5, "District": "RANTAU PANJANG", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1014", "Identifier": "Child Record #15 (Anonymized)", "Age": 6, "District": "KOTA BHARU", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1015", "Identifier": "Child Record #16 (Anonymized)", "Age": 7, "District": "BACHOK", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1016", "Identifier": "Child Record #17 (Anonymized)", "Age": 8, "District": "PASIR MAS", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1017", "Identifier": "Child Record #18 (Anonymized)", "Age": 9, "District": "PASIR PUTEH", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1018", "Identifier": "Child Record #19 (Anonymized)", "Age": 10, "District": "WAKAF BHARU", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1019", "Identifier": "Child Record #20 (Anonymized)", "Age": 11, "District": "TUMPAT", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1020", "Identifier": "Child Record #21 (Anonymized)", "Age": 12, "District": "RANTAU PANJANG", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1021", "Identifier": "Child Record #22 (Anonymized)", "Age": 13, "District": "KOTA BHARU", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1022", "Identifier": "Child Record #23 (Anonymized)", "Age": 14, "District": "BACHOK", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1023", "Identifier": "Child Record #24 (Anonymized)", "Age": 15, "District": "PASIR MAS", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1024", "Identifier": "Child Record #25 (Anonymized)", "Age": 4, "District": "PASIR PUTEH", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1025", "Identifier": "Child Record #26 (Anonymized)", "Age": 5, "District": "WAKAF BHARU", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1026", "Identifier": "Child Record #27 (Anonymized)", "Age": 6, "District": "TUMPAT", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1027", "Identifier": "Child Record #28 (Anonymized)", "Age": 7, "District": "RANTAU PANJANG", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1028", "Identifier": "Child Record #29 (Anonymized)", "Age": 8, "District": "KOTA BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1029", "Identifier": "Child Record #30 (Anonymized)", "Age": 9, "District": "BACHOK", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1030", "Identifier": "Child Record #31 (Anonymized)", "Age": 10, "District": "PASIR MAS", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1031", "Identifier": "Child Record #32 (Anonymized)", "Age": 11, "District": "PASIR PUTEH", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1032", "Identifier": "Child Record #33 (Anonymized)", "Age": 12, "District": "WAKAF BHARU", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1033", "Identifier": "Child Record #34 (Anonymized)", "Age": 13, "District": "TUMPAT", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1034", "Identifier": "Child Record #35 (Anonymized)", "Age": 14, "District": "RANTAU PANJANG", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1035", "Identifier": "Child Record #36 (Anonymized)", "Age": 15, "District": "KOTA BHARU", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1036", "Identifier": "Child Record #37 (Anonymized)", "Age": 4, "District": "BACHOK", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1037", "Identifier": "Child Record #38 (Anonymized)", "Age": 5, "District": "PASIR MAS", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1038", "Identifier": "Child Record #39 (Anonymized)", "Age": 6, "District": "PASIR PUTEH", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1039", "Identifier": "Child Record #40 (Anonymized)", "Age": 7, "District": "WAKAF BHARU", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1040", "Identifier": "Child Record #41 (Anonymized)", "Age": 8, "District": "TUMPAT", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1041", "Identifier": "Child Record #42 (Anonymized)", "Age": 9, "District": "RANTAU PANJANG", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1042", "Identifier": "Child Record #43 (Anonymized)", "Age": 10, "District": "KOTA BHARU", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1043", "Identifier": "Child Record #44 (Anonymized)", "Age": 11, "District": "BACHOK", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1044", "Identifier": "Child Record #45 (Anonymized)", "Age": 12, "District": "PASIR MAS", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1045", "Identifier": "Child Record #46 (Anonymized)", "Age": 13, "District": "PASIR PUTEH", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1046", "Identifier": "Child Record #47 (Anonymized)", "Age": 14, "District": "WAKAF BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1047", "Identifier": "Child Record #48 (Anonymized)", "Age": 15, "District": "TUMPAT", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1048", "Identifier": "Child Record #49 (Anonymized)", "Age": 4, "District": "RANTAU PANJANG", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1049", "Identifier": "Child Record #50 (Anonymized)", "Age": 5, "District": "KOTA BHARU", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1050", "Identifier": "Child Record #51 (Anonymized)", "Age": 6, "District": "BACHOK", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1051", "Identifier": "Child Record #52 (Anonymized)", "Age": 7, "District": "PASIR MAS", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1052", "Identifier": "Child Record #53 (Anonymized)", "Age": 8, "District": "PASIR PUTEH", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1053", "Identifier": "Child Record #54 (Anonymized)", "Age": 9, "District": "WAKAF BHARU", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1054", "Identifier": "Child Record #55 (Anonymized)", "Age": 10, "District": "TUMPAT", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1055", "Identifier": "Child Record #56 (Anonymized)", "Age": 11, "District": "RANTAU PANJANG", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1056", "Identifier": "Child Record #57 (Anonymized)", "Age": 12, "District": "KOTA BHARU", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1057", "Identifier": "Child Record #58 (Anonymized)", "Age": 13, "District": "BACHOK", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1058", "Identifier": "Child Record #59 (Anonymized)", "Age": 14, "District": "PASIR MAS", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1059", "Identifier": "Child Record #60 (Anonymized)", "Age": 15, "District": "PASIR PUTEH", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1060", "Identifier": "Child Record #61 (Anonymized)", "Age": 4, "District": "WAKAF BHARU", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1061", "Identifier": "Child Record #62 (Anonymized)", "Age": 5, "District": "TUMPAT", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1062", "Identifier": "Child Record #63 (Anonymized)", "Age": 6, "District": "RANTAU PANJANG", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1063", "Identifier": "Child Record #64 (Anonymized)", "Age": 7, "District": "KOTA BHARU", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1064", "Identifier": "Child Record #65 (Anonymized)", "Age": 8, "District": "BACHOK", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1065", "Identifier": "Child Record #66 (Anonymized)", "Age": 9, "District": "PASIR MAS", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1066", "Identifier": "Child Record #67 (Anonymized)", "Age": 10, "District": "PASIR PUTEH", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1067", "Identifier": "Child Record #68 (Anonymized)", "Age": 11, "District": "WAKAF BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1068", "Identifier": "Child Record #69 (Anonymized)", "Age": 12, "District": "TUMPAT", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1069", "Identifier": "Child Record #70 (Anonymized)", "Age": 13, "District": "RANTAU PANJANG", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1070", "Identifier": "Child Record #71 (Anonymized)", "Age": 14, "District": "KOTA BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1071", "Identifier": "Child Record #72 (Anonymized)", "Age": 15, "District": "BACHOK", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1072", "Identifier": "Child Record #73 (Anonymized)", "Age": 4, "District": "PASIR MAS", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1073", "Identifier": "Child Record #74 (Anonymized)", "Age": 5, "District": "PASIR PUTEH", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1074", "Identifier": "Child Record #75 (Anonymized)", "Age": 6, "District": "WAKAF BHARU", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1075", "Identifier": "Child Record #76 (Anonymized)", "Age": 7, "District": "TUMPAT", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1076", "Identifier": "Child Record #77 (Anonymized)", "Age": 8, "District": "RANTAU PANJANG", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1077", "Identifier": "Child Record #78 (Anonymized)", "Age": 9, "District": "KOTA BHARU", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1078", "Identifier": "Child Record #79 (Anonymized)", "Age": 10, "District": "BACHOK", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1079", "Identifier": "Child Record #80 (Anonymized)", "Age": 11, "District": "PASIR MAS", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1080", "Identifier": "Child Record #81 (Anonymized)", "Age": 12, "District": "PASIR PUTEH", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1081", "Identifier": "Child Record #82 (Anonymized)", "Age": 13, "District": "WAKAF BHARU", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1082", "Identifier": "Child Record #83 (Anonymized)", "Age": 14, "District": "TUMPAT", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1083", "Identifier": "Child Record #84 (Anonymized)", "Age": 15, "District": "RANTAU PANJANG", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1084", "Identifier": "Child Record #85 (Anonymized)", "Age": 4, "District": "KOTA BHARU", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1085", "Identifier": "Child Record #86 (Anonymized)", "Age": 5, "District": "BACHOK", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1086", "Identifier": "Child Record #87 (Anonymized)", "Age": 6, "District": "PASIR MAS", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1087", "Identifier": "Child Record #88 (Anonymized)", "Age": 7, "District": "PASIR PUTEH", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1088", "Identifier": "Child Record #89 (Anonymized)", "Age": 8, "District": "WAKAF BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1089", "Identifier": "Child Record #90 (Anonymized)", "Age": 9, "District": "TUMPAT", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1090", "Identifier": "Child Record #91 (Anonymized)", "Age": 10, "District": "RANTAU PANJANG", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1091", "Identifier": "Child Record #92 (Anonymized)", "Age": 11, "District": "KOTA BHARU", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1092", "Identifier": "Child Record #93 (Anonymized)", "Age": 12, "District": "BACHOK", "Diagnosis": "Severe Autism", "Required Service": "Speech Therapy", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1093", "Identifier": "Child Record #94 (Anonymized)", "Age": 13, "District": "PASIR MAS", "Diagnosis": "Mild Autism", "Required Service": "ABA Therapy", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1094", "Identifier": "Child Record #95 (Anonymized)", "Age": 14, "District": "PASIR PUTEH", "Diagnosis": "High-Function Autism", "Required Service": "Occupational Sensory", "Date": "2026-05-15", "Status": "Verified Active"}, {"Record ID": "KOD-1095", "Identifier": "Child Record #96 (Anonymized)", "Age": 15, "District": "WAKAF BHARU", "Diagnosis": "Severe Autism", "Required Service": "Early Intervention", "Date": "2026-06-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1096", "Identifier": "Child Record #97 (Anonymized)", "Age": 4, "District": "TUMPAT", "Diagnosis": "Mild Autism", "Required Service": "Speech Therapy", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1097", "Identifier": "Child Record #98 (Anonymized)", "Age": 5, "District": "RANTAU PANJANG", "Diagnosis": "High-Function Autism", "Required Service": "ABA Therapy", "Date": "2026-02-15", "Status": "Verified Active"}, {"Record ID": "KOD-1098", "Identifier": "Child Record #99 (Anonymized)", "Age": 6, "District": "KOTA BHARU", "Diagnosis": "Severe Autism", "Required Service": "Occupational Sensory", "Date": "2026-03-15", "Status": "Verified Active"}, {"Record ID": "KOD-1099", "Identifier": "Child Record #100 (Anonymized)", "Age": 7, "District": "BACHOK", "Diagnosis": "Mild Autism", "Required Service": "Early Intervention", "Date": "2026-04-15", "Status": "Verified Active"}, {"Record ID": "KOD-1100", "Identifier": "Child Record #101 (Anonymized)", "Age": 8, "District": "PASIR MAS", "Diagnosis": "High-Function Autism", "Required Service": "Speech Therapy", "Date": "2026-05-15", "Status": "Pending Verification"}, {"Record ID": "KOD-1101", "Identifier": "Child Record #102 (Anonymized)", "Age": 9, "District": "PASIR PUTEH", "Diagnosis": "Severe Autism", "Required Service": "ABA Therapy", "Date": "2026-06-15", "Status": "Verified Active"}, {"Record ID": "KOD-1102", "Identifier": "Child Record #103 (Anonymized)", "Age": 10, "District": "WAKAF BHARU", "Diagnosis": "Mild Autism", "Required Service": "Occupational Sensory", "Date": "2026-01-15", "Status": "Verified Active"}, {"Record ID": "KOD-1103", "Identifier": "Child Record #104 (Anonymized)", "Age": 11, "District": "TUMPAT", "Diagnosis": "High-Function Autism", "Required Service": "Early Intervention", "Date": "2026-02-15", "Status": "Verified Active"}]""")


def labeled_bar_chart(df_counts: pd.DataFrame, x_col: str, y_col: str, bar_color: str, title: str) -> alt.Chart:
    """Creates a clean, high-contrast Altair bar chart with direct numeric labels on every bar."""
    base = alt.Chart(df_counts).encode(
        x=alt.X(f"{x_col}:N", sort="-y", title=x_col, axis=alt.Axis(labelAngle=-25, labelColor="#0F172A", titleColor="#0F172A")),
        y=alt.Y(f"{y_col}:Q", title=y_col, axis=alt.Axis(labelColor="#0F172A", titleColor="#0F172A")),
    )
    bars = base.mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, color=bar_color)
    labels = base.mark_text(dy=-8, fontSize=13, fontWeight="bold", color="#0F172A").encode(
        text=alt.Text(f"{y_col}:Q", format="d")
    )
    return (
        (bars + labels)
        .properties(title=alt.TitleParams(text=title, color="#0F172A", fontSize=15), height=280)
        .configure_view(fill="#FFFFFF", stroke="#CBD5E1")
        .configure(background="#FFFFFF")
    )


def module_svg(mod_key: str, accent: str, soft_bg: str) -> str:
    """Returns a colorful, topic-specific inline SVG illustration for each module."""
    if mod_key == "AG":
        artwork = """
        <rect x="34" y="34" width="76" height="92" rx="14" fill="#FFFFFF" stroke="#0284C7" stroke-width="3"/>
        <circle cx="72" cy="64" r="14" fill="#BAE6FD"/>
        <path d="M54 102 Q72 84 90 102 Z" fill="#38BDF8"/>
        <path d="M148 56 Q168 38 188 56 Q188 84 168 96 Q148 84 148 56 Z" fill="#38BDF8"/>
        <circle cx="226" cy="74" r="24" fill="#FFFFFF" stroke="#0284C7" stroke-width="3"/>
        <path d="M216 74 L223 81 L237 67" fill="none" stroke="#10B981" stroke-width="4" stroke-linecap="round"/>
        """
    elif mod_key == "AH":
        artwork = """
        <rect x="32" y="38" width="96" height="84" rx="12" fill="#FFFFFF" stroke="#7C3AED" stroke-width="3"/>
        <text x="80" y="64" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#7C3AED">FIRST</text>
        <rect x="52" y="74" width="56" height="32" rx="6" fill="#DDD6FE"/>
        <polygon points="144,72 162,80 144,88" fill="#7C3AED"/>
        <rect x="174" y="38" width="96" height="84" rx="12" fill="#FFFFFF" stroke="#10B981" stroke-width="3"/>
        <text x="222" y="64" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#059669">THEN</text>
        <circle cx="222" cy="90" r="16" fill="#A7F3D0"/>
        """
    elif mod_key == "AI":
        artwork = """
        <circle cx="64" cy="54" r="18" fill="#FBBF24"/>
        <path d="M28 124 Q85 96 145 112 T276 96 L276 142 L28 142 Z" fill="#A7F3D0"/>
        <circle cx="152" cy="66" r="11" fill="#047857"/>
        <path d="M152 77 L145 102 L134 118 M152 77 L160 102 L172 115 M152 84 L136 94 M152 84 L168 92" stroke="#047857" stroke-width="4" stroke-linecap="round" fill="none"/>
        <circle cx="235" cy="64" r="20" fill="#FFFFFF" stroke="#10B981" stroke-width="3"/>
        <path d="M225 64 Q235 52 245 64 Q235 76 225 64" fill="#34D399"/>
        """
    else:
        artwork = """
        <rect x="34" y="38" width="84" height="84" rx="12" fill="#FFFFFF" stroke="#D97706" stroke-width="3"/>
        <circle cx="76" cy="70" r="16" fill="#FDE68A"/>
        <rect x="52" y="94" width="48" height="10" rx="5" fill="#F59E0B"/>
        <path d="M132 80 L156 80" stroke="#D97706" stroke-width="4" stroke-linecap="round"/>
        <polygon points="154,72 168,80 154,88" fill="#D97706"/>
        <rect x="178" y="38" width="94" height="84" rx="12" fill="#FFFFFF" stroke="#2563EB" stroke-width="3"/>
        <circle cx="212" cy="70" r="10" fill="#93C5FD"/>
        <circle cx="242" cy="70" r="10" fill="#6EE7B7"/>
        <rect x="196" y="92" width="58" height="12" rx="6" fill="#DBEAFE"/>
        """

    return f"""
    <svg viewBox="0 0 304 156" width="100%" height="156" xmlns="http://www.w3.org/2000/svg" style="border-radius:12px;background:{soft_bg};display:block;">
        {artwork}
    </svg>
    """


def build_flipbook_html(mod: dict) -> str:
    """Generates a standalone interactive HTML flipbook that users can download and open in any browser."""
    title_esc = html.escape(f"{mod['code']}: {mod['title']}")
    domain_esc = html.escape(mod["domain"])
    accent = mod["color"]
    soft_bg = mod["soft_bg"]
    svg_art = module_svg(mod["key"], accent, soft_bg)

    pages_js_items = []
    for p_title, p_summary, p_steps in mod["pages"]:
        pages_js_items.append(
            "{"
            f'"heading": "{html.escape(p_title)}", '
            f'"summary": "{html.escape(p_summary)}", '
            f'"steps": "{html.escape(p_steps).replace(chr(10), "<br>")}"'
            "}"
        )
    pages_json = "[" + ", ".join(pages_js_items) + "]"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title_esc} — Interactive Flipbook</title>
<style>
  body {{
    font-family: 'Segoe UI', Arial, sans-serif;
    background: linear-gradient(135deg, #FEE2E2 0%, #FEF9C3 50%, #DBEAFE 100%);
    margin: 0;
    padding: 28px;
    color: #0F172A;
    display: flex;
    justify-content: center;
  }}
  .book-shell {{
    max-width: 720px;
    width: 100%;
    background: #FFFFFF;
    border-radius: 18px;
    padding: 26px;
    box-shadow: 0 16px 40px rgba(15, 23, 42, 0.14);
    border-top: 8px solid {accent};
  }}
  .top-tag {{
    display: inline-block;
    background: {accent};
    color: #FFFFFF;
    font-weight: 700;
    font-size: 12px;
    padding: 5px 12px;
    border-radius: 999px;
  }}
  h1 {{
    margin: 10px 0 4px 0;
    font-size: 24px;
  }}
  .domain {{
    color: #475569;
    font-size: 14px;
    margin-bottom: 16px;
  }}
  .page-box {{
    background: {soft_bg};
    border-radius: 14px;
    padding: 20px;
    margin-top: 16px;
    min-height: 170px;
    transition: transform 0.25s ease;
  }}
  .page-heading {{
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #0F172A;
  }}
  .page-summary {{
    font-size: 15px;
    margin-bottom: 12px;
    line-height: 1.5;
  }}
  .page-steps {{
    background: #FFFFFF;
    padding: 14px 16px;
    border-radius: 10px;
    line-height: 1.65;
    font-size: 14px;
  }}
  .controls {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
    gap: 12px;
  }}
  button {{
    background: {accent};
    color: #FFFFFF;
    border: none;
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
  }}
  button:disabled {{
    background: #CBD5E1;
    cursor: not-allowed;
  }}
  .indicator {{
    font-weight: 700;
    color: #334155;
  }}
</style>
</head>
<body>
  <div class="book-shell">
    <span class="top-tag">INTERACTIVE FLIPBOOK</span>
    <h1>{title_esc}</h1>
    <div class="domain">Focus Domain: {domain_esc} • Use buttons or Left/Right arrow keys to flip pages</div>
    {svg_art}
    <div class="page-box" id="pageBox">
      <div class="page-heading" id="pageHeading"></div>
      <div class="page-summary" id="pageSummary"></div>
      <div class="page-steps" id="pageSteps"></div>
    </div>
    <div class="controls">
      <button id="prevBtn" onclick="turnPage(-1)">← Previous Page</button>
      <span class="indicator" id="pageIndicator"></span>
      <button id="nextBtn" onclick="turnPage(1)">Next Page →</button>
    </div>
  </div>
<script>
  const pages = {pages_json};
  let idx = 0;

  function render() {{
    const p = pages[idx];
    document.getElementById("pageHeading").innerHTML = p.heading;
    document.getElementById("pageSummary").innerHTML = p.summary;
    document.getElementById("pageSteps").innerHTML = p.steps;
    document.getElementById("pageIndicator").innerText = `Page ${{idx + 1}} of ${{pages.length}}`;
    document.getElementById("prevBtn").disabled = idx === 0;
    document.getElementById("nextBtn").disabled = idx === pages.length - 1;
  }}

  function turnPage(delta) {{
    const nextIdx = idx + delta;
    if (nextIdx >= 0 && nextIdx < pages.length) {{
      idx = nextIdx;
      const box = document.getElementById("pageBox");
      box.style.transform = "scale(0.98)";
      setTimeout(() => {{ box.style.transform = "scale(1)"; }}, 120);
      render();
    }}
  }}

  document.addEventListener("keydown", (e) => {{
    if (e.key === "ArrowRight") turnPage(1);
    if (e.key === "ArrowLeft") turnPage(-1);
  }});

  render();
</script>
</body>
</html>
"""


@st.cache_data
def load_initial_csv(path: str = "Kelantan_Student_Registry_104.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except Exception:
        df = pd.DataFrame(EMBEDDED_RECORDS)
    df["District"] = df["District"].astype(str).str.strip().str.upper()
    return df


if "student_df" not in st.session_state:
    st.session_state["student_df"] = load_initial_csv().copy()

if "selected_zone_district" not in st.session_state:
    st.session_state["selected_zone_district"] = "PASIR PUTEH"

for mod in MODULES_4:
    p_key = f"flip_page_{mod['key']}"
    if p_key not in st.session_state:
        st.session_state[p_key] = 0

df_students = st.session_state["student_df"].copy()

st.markdown(
    """
    <div class="hero-banner">
        <h2 style="margin:0;color:#FFFFFF;">🌈 Kelantan Autism GIS & Support Platform</h2>
        <p style="margin:4px 0 0 0;color:#FFFFFF;font-size:14px;">
            Red • Yellow • Blue Theme • Clear Labeled Charts • Live Student Registry • Tailored Centre Matcher • 4 Flipbooks
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar Multi-Page Navigation
st.sidebar.title("🌈 Navigation")
page = st.sidebar.radio(
    "Choose a Page",
    [
        "1. Kelantan Zone Overview & Analytics",
        "2. Student Registry (Edit & Insert)",
        "3. Parents: Child & Centre Matcher",
        "4. Parents: 4 Interactive Flipbook Modules",
    ],
)

counts_by_dist = df_students["District"].value_counts().to_dict()

# ==============================================================================
# PAGE 1: KELANTAN ZONE OVERVIEW (RED / GREEN / YELLOW) + INSPECTOR + GRAPHS
# ==============================================================================
if page == "1. Kelantan Zone Overview & Analytics":
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Students", len(df_students))
    k2.metric("Verified Active", int((df_students["Status"] == "Verified Active").sum()))
    k3.metric("Pending Verification", int((df_students["Status"] == "Pending Verification").sum()))
    k4.metric("Red Zone Districts", sum(1 for v in DISTRICT_INFO.values() if v["zone"] == "Red Zone"))

    st.divider()
    zone_col, info_col = st.columns([7, 5], gap="large")

    with zone_col:
        st.subheader("🧭 Kelantan District Zone Overview")
        st.caption("Clear summary of Red / Yellow / Green zones, student counts, centre counts, and recommended centres.")

        zone_rows = []
        for dist_name, info in DISTRICT_INFO.items():
            stu_cnt = int(counts_by_dist.get(dist_name, 0))
            zone_rows.append({
                "District": dist_name,
                "Zone": info["zone"],
                "Students": stu_cnt,
                "Centres": info["centres"],
                "Recommended Centre": info["recommended_centre"],
            })
        zone_df = pd.DataFrame(zone_rows)
        st.dataframe(zone_df, width="stretch", hide_index=True)

        st.markdown("#### Quick District Zone Cards")
        dist_items = list(DISTRICT_INFO.items())
        for row_start in range(0, len(dist_items), 2):
            c_left, c_right = st.columns(2)
            for col_slot, (d_name, d_meta) in zip([c_left, c_right], dist_items[row_start:row_start + 2]):
                stu_n = int(counts_by_dist.get(d_name, 0))
                with col_slot:
                    with st.container(border=True):
                        st.markdown(
                            f'<span class="module-badge" style="background:{d_meta["badge_bg"]};">{d_meta["zone"]}</span>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"**{d_name}** — `{stu_n}` students | `{d_meta['centres']}` centres")
                        st.caption(d_meta["recommended_centre"])
                        if st.button(f"Inspect {d_name}", key=f"insp_{d_name}", width="stretch"):
                            st.session_state["selected_zone_district"] = d_name
                            st.rerun()

    with info_col:
        st.subheader("📌 District Inspector")
        selected_dist = st.selectbox(
            "Select a Kelantan district to inspect",
            options=list(DISTRICT_INFO.keys()),
            index=list(DISTRICT_INFO.keys()).index(st.session_state["selected_zone_district"]),
        )
        st.session_state["selected_zone_district"] = selected_dist

        d_info = DISTRICT_INFO[selected_dist]
        d_rows = df_students[df_students["District"] == selected_dist]

        with st.container(border=True):
            st.markdown(
                f'<span class="module-badge" style="background:{d_info["badge_bg"]};">{d_info["zone"]}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(f"### 📍 {selected_dist}")
            st.write(d_info["place_summary"])
            st.markdown(f"- **Coordinates:** `{d_info['lat']}, {d_info['lon']}`")
            st.markdown(f"- **Students:** `{len(d_rows)}` | **Centres:** `{d_info['centres']}`")
            st.markdown(
                f"- **Diagnosis:** Mild `{int((d_rows['Diagnosis'] == 'Mild Autism').sum())}` • "
                f"High-Function `{int((d_rows['Diagnosis'] == 'High-Function Autism').sum())}` • "
                f"Severe `{int((d_rows['Diagnosis'] == 'Severe Autism').sum())}`"
            )
            st.markdown(f"- **Suitable Centre:** {d_info['recommended_centre']}")
            st.markdown(f"- **Therapists:** {d_info['therapists']}")

    st.divider()
    st.subheader("📊 Clear Visual Analytics (With Exact Numbers)")
    g1, g2, g3 = st.columns(3)

    dist_chart_df = df_students.groupby("District").size().reset_index(name="Students")
    serv_chart_df = df_students.groupby("Required Service").size().reset_index(name="Count")
    diag_chart_df = (
        df_students.groupby(["District", "Diagnosis"])
        .size()
        .reset_index(name="Students")
    )

    with g1:
        st.altair_chart(
            labeled_bar_chart(dist_chart_df, "District", "Students", "#DC2626", "Students per District"),
            use_container_width=True,
        )
    with g2:
        diag_stacked = (
            alt.Chart(diag_chart_df)
            .mark_bar()
            .encode(
                x=alt.X("District:N", title="District", axis=alt.Axis(labelAngle=-25, labelColor="#0F172A", titleColor="#0F172A")),
                y=alt.Y("Students:Q", title="Students", axis=alt.Axis(labelColor="#0F172A", titleColor="#0F172A")),
                color=alt.Color(
                    "Diagnosis:N",
                    scale=alt.Scale(
                        domain=["Mild Autism", "High-Function Autism", "Severe Autism"],
                        range=["#2563EB", "#F59E0B", "#DC2626"],
                    ),
                ),
                tooltip=["District", "Diagnosis", "Students"],
            )
            .properties(title=alt.TitleParams(text="Diagnosis by District", color="#0F172A", fontSize=15), height=280)
            .configure_view(fill="#FFFFFF", stroke="#CBD5E1")
            .configure(background="#FFFFFF")
        )
        st.altair_chart(diag_stacked, use_container_width=True)
    with g3:
        st.altair_chart(
            labeled_bar_chart(serv_chart_df, "Required Service", "Count", "#2563EB", "Required Services"),
            use_container_width=True,
        )

# ==============================================================================
# PAGE 2: STUDENT REGISTRY (EDIT & INSERT)
# ==============================================================================
elif page == "2. Student Registry (Edit & Insert)":
    st.subheader("📋 Student Registry — Edit & Insert Records")

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
            new_date = c7.text_input("Date (YYYY-MM-DD)", value="2026-11-23")
            new_status = c8.selectbox("Status", ["Verified Active", "Pending Verification"])

            if st.form_submit_button("✨ Add Record"):
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
                st.success(f"Added {new_id}!")
                st.rerun()

    edited_df = st.data_editor(
        st.session_state["student_df"],
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
        column_config={
            "District": st.column_config.SelectboxColumn("District", options=list(DISTRICT_INFO.keys()), required=True),
            "Diagnosis": st.column_config.SelectboxColumn("Diagnosis", options=["Mild Autism", "High-Function Autism", "Severe Autism"], required=True),
            "Required Service": st.column_config.SelectboxColumn("Required Service", options=["Speech Therapy", "ABA Therapy", "Occupational Sensory", "Early Intervention"], required=True),
            "Status": st.column_config.SelectboxColumn("Status", options=["Verified Active", "Pending Verification"], required=True),
        },
    )

    b1, b2 = st.columns([2, 3])
    if b1.button("💾 Save Table Edits", type="primary"):
        st.session_state["student_df"] = edited_df.copy()
        st.success("Saved changes to registry!")

    b2.download_button(
        label="⬇️ Download Updated CSV",
        data=st.session_state["student_df"].to_csv(index=False).encode("utf-8"),
        file_name="kelantan_student_registry_updated.csv",
        mime="text/csv",
    )

# ==============================================================================
# PAGE 3: PARENTS — CHILD RECORD, AUTISM TYPE, SUITABLE CENTRE & THERAPISTS
# ==============================================================================
elif page == "3. Parents: Child & Centre Matcher":
    st.subheader("🏥 Parents Portal — Child Profile, Suitable Centre & Therapists")

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
        st.markdown("### 👶 Child Information")
        with st.container(border=True):
            st.markdown(f"**Record ID:** `{child_row['Record ID']}`")
            st.markdown(f"**Identifier:** {child_row['Identifier']}")
            st.markdown(f"**Age:** `{child_row['Age']}` years old")
            st.markdown(f"**District:** `{c_dist}` (`{c_info['zone']}`)")
            st.markdown(f"**Type of Autism:** `{c_diag}`")
            st.markdown(f"**Required Service:** `{child_row['Required Service']}`")
            st.markdown(f"**Date:** `{child_row['Date']}` | **Status:** `{child_row['Status']}`")

    with right:
        st.markdown("### 🌟 Suitable Centre & Therapists")
        with st.container(border=True):
            st.markdown(
                f'<span class="module-badge" style="background:{c_info["badge_bg"]};">{c_info["zone"]}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(f"#### ⭐ {c_info['recommended_centre']}")
            st.markdown(f"**Why Suitable:** {c_info['why_suitable']}")
            st.markdown(f"**Therapists Provided:** {c_info['therapists']}")
            st.markdown(f"**Matched Required Service:** `{child_row['Required Service']}`")

# ==============================================================================
# PAGE 4: PARENTS — 4 COLORFUL INTERACTIVE FLIPBOOK MODULES
# ==============================================================================
else:
    st.subheader("📚 4 Interactive Flipbook Modules (Illustrated & Downloadable)")
    st.caption("Flip through pages right here in the dashboard, or download each module as an interactive HTML flipbook.")

    cols = st.columns(2, gap="large")
    for idx, mod in enumerate(MODULES_4):
        p_key = f"flip_page_{mod['key']}"
        cur_page = st.session_state[p_key]
        total_pages = len(mod["pages"])
        p_heading, p_summary, p_steps = mod["pages"][cur_page]

        with cols[idx % 2]:
            with st.container(border=True):
                st.markdown(
                    f'<span class="module-badge" style="background:{mod["color"]};">{mod["code"]} • {mod["domain"]}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"### {mod['title']}")
                st.markdown(module_svg(mod["key"], mod["color"], mod["soft_bg"]), unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div class="flip-card" style="background:{mod['soft_bg']};margin-top:12px;">
                        <div style="font-weight:700;font-size:15px;margin-bottom:6px;">{p_heading}</div>
                        <div style="font-size:13px;margin-bottom:10px;">{p_summary}</div>
                        <div style="background:#FFFFFF;padding:10px 12px;border-radius:8px;font-size:12.5px;line-height:1.55;">
                            {p_steps.replace(chr(10), "<br>")}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                nav1, nav2, nav3 = st.columns([1, 1.4, 1])
                if nav1.button("◀ Prev", key=f"prev_{mod['key']}", disabled=(cur_page == 0), width="stretch"):
                    st.session_state[p_key] = cur_page - 1
                    st.rerun()
                nav2.markdown(
                    f"<div style='text-align:center;padding-top:8px;font-weight:700;'>Page {cur_page + 1} / {total_pages}</div>",
                    unsafe_allow_html=True,
                )
                if nav3.button("Next ▶", key=f"next_{mod['key']}", disabled=(cur_page == total_pages - 1), width="stretch"):
                    st.session_state[p_key] = cur_page + 1
                    st.rerun()

                flip_html = build_flipbook_html(mod)
                st.download_button(
                    label=f"📖 Download {mod['code']} Flipbook (.html)",
                    data=flip_html.encode("utf-8"),
                    file_name=f"{mod['code'].replace(' ', '_')}_Flipbook.html",
                    mime="text/html",
                    key=f"dl_flip_{mod['key']}",
                    width="stretch",
                )
