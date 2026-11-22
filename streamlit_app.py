import html
import json
import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Kelantan Autism GIS — Executive & Caregiver Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Theme Palette: Soft Teal + Navy Blue + Lavender
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #CCFBF1 0%, #EDE9FE 52%, #DBEAFE 100%) !important;
        color: #0F172A !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E3A8A 55%, #4C1D95 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.14);
    }

    [data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }

    [data-testid="stSidebar"] .stRadio > label {
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 0.4px;
        text-transform: uppercase;
        color: #99F6E4 !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06) !important;
        padding: 4px 6px;
    }

    .brand-header {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 4px 0;
    }

    .brand-mark {
        width: 52px;
        height: 52px;
        border-radius: 14px;
        background: linear-gradient(135deg, #0D9488 0%, #1E3A8A 60%, #7C3AED 100%);
        color: #FFFFFF;
        font-weight: 800;
        font-size: 18px;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.22);
    }

    .kpi-tile-teal {
        background: linear-gradient(135deg, #0F766E 0%, #0D9488 100%);
        color: #FFFFFF;
        border-radius: 14px;
        padding: 15px 18px;
        box-shadow: 0 4px 14px rgba(13, 148, 136, 0.22);
    }

    .kpi-tile-navy {
        background: linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 100%);
        color: #FFFFFF;
        border-radius: 14px;
        padding: 15px 18px;
        box-shadow: 0 4px 14px rgba(30, 58, 138, 0.22);
    }

    .kpi-tile-lavender {
        background: linear-gradient(135deg, #5B21B6 0%, #7C3AED 100%);
        color: #FFFFFF;
        border-radius: 14px;
        padding: 15px 18px;
        box-shadow: 0 4px 14px rgba(109, 40, 217, 0.22);
    }

    .kpi-label {
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.3px;
        color: rgba(255, 255, 255, 0.92);
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.1;
    }

    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #0F172A;
        margin: 0 0 2px 0;
    }

    .section-sub {
        font-size: 12.5px;
        color: #475569;
        margin: 0 0 10px 0;
    }

    .zone-pill {
        display: inline-block;
        padding: 4px 11px;
        border-radius: 999px;
        font-size: 11.5px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: 0.2px;
    }

    .flip-panel {
        border-radius: 14px;
        padding: 16px;
        border: 1px solid #E2E8F0;
        background: #F8FAFC;
        color: #0F172A;
        margin-top: 10px;
    }

    [data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F766E 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
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
        "badge_bg": "#0D9488",
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
        "badge_bg": "#D97706",
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
        "badge_bg": "#D97706",
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
        "badge_bg": "#BE123C",
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
        "badge_bg": "#BE123C",
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
        "badge_bg": "#BE123C",
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
        "badge_bg": "#D97706",
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
        "color": "#0F766E",
        "soft_bg": "#CCFBF1",
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
        "color": "#1E3A8A",
        "soft_bg": "#DBEAFE",
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
        "color": "#0D9488",
        "soft_bg": "#CCFBF1",
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
        "color": "#6D28D9",
        "soft_bg": "#EDE9FE",
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


def module_animated_html(mod_key: str, accent: str, soft_bg: str, page_idx: int) -> str:
    if mod_key == "AG":
        scene = """
        <style>
          @keyframes floatDrop {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-7px); }
          }
          @keyframes waveBubble {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.12); }
          }
          .kid-float { animation: floatDrop 2.4s ease-in-out infinite; transform-origin: center; }
          .drop-anim { animation: floatDrop 1.8s ease-in-out infinite; }
          .check-pop { animation: waveBubble 2s ease-in-out infinite; transform-origin: 226px 78px; }
        </style>
        <rect x="0" y="0" width="320" height="164" rx="14" fill="#E0F2FE"/>
        <circle cx="285" cy="28" r="16" fill="#FDE047" opacity="0.85"/>
        <path d="M0 132 Q80 120 160 132 T320 128 L320 164 L0 164 Z" fill="#BAE6FD"/>
        <!-- Friendly kid character -->
        <g class="kid-float">
          <circle cx="72" cy="62" r="20" fill="#FDBA74" stroke="#9A3412" stroke-width="2.5"/>
          <path d="M53 56 Q72 36 91 56 Q82 46 72 48 Q62 46 53 56 Z" fill="#451A03"/>
          <circle cx="65" cy="61" r="2.8" fill="#1E293B"/>
          <circle cx="79" cy="61" r="2.8" fill="#1E293B"/>
          <path d="M66 69 Q72 75 78 69" fill="none" stroke="#9A3412" stroke-width="2.5" stroke-linecap="round"/>
          <rect x="54" y="84" width="36" height="34" rx="12" fill="#38BDF8" stroke="#0369A1" stroke-width="2.5"/>
          <circle cx="72" cy="100" r="5" fill="#FFFFFF"/>
        </g>
        <!-- Water drop & soap -->
        <g class="drop-anim">
          <path d="M156 54 Q172 34 188 54 Q188 78 172 90 Q156 78 156 54 Z" fill="#0284C7"/>
          <circle cx="167" cy="56" r="4" fill="#E0F2FE"/>
        </g>
        <!-- Happy star check -->
        <g class="check-pop">
          <circle cx="248" cy="78" r="24" fill="#FFFFFF" stroke="#10B981" stroke-width="3"/>
          <path d="M237 78 L245 86 L260 70" fill="none" stroke="#10B981" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        """
    elif mod_key == "AH":
        scene = """
        <style>
          @keyframes hopKid {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-6px) rotate(2deg); }
          }
          @keyframes pulseArrow {
            0%, 100% { transform: translateX(0px); }
            50% { transform: translateX(5px); }
          }
          .hop-kid { animation: hopKid 2.2s ease-in-out infinite; transform-origin: center; }
          .arrow-move { animation: pulseArrow 1.5s ease-in-out infinite; }
        </style>
        <rect x="0" y="0" width="320" height="164" rx="14" fill="#EEF2FF"/>
        <rect x="0" y="130" width="320" height="34" fill="#C7D2FE"/>
        <!-- FIRST card -->
        <rect x="20" y="34" width="96" height="84" rx="12" fill="#FFFFFF" stroke="#4F46E5" stroke-width="3"/>
        <text x="68" y="56" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#4F46E5">FIRST</text>
        <rect x="44" y="66" width="48" height="36" rx="8" fill="#F59E0B"/>
        <path d="M54 66 Q68 54 82 66" fill="none" stroke="#B45309" stroke-width="3"/>
        <!-- Arrow -->
        <g class="arrow-move">
          <path d="M126 76 L146 76" stroke="#4F46E5" stroke-width="4" stroke-linecap="round"/>
          <polygon points="144,68 158,76 144,84" fill="#4F46E5"/>
        </g>
        <!-- THEN kid -->
        <g class="hop-kid">
          <rect x="168" y="34" width="128" height="84" rx="12" fill="#FFFFFF" stroke="#10B981" stroke-width="3"/>
          <text x="232" y="55" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#059669">THEN PLAY</text>
          <circle cx="232" cy="76" r="14" fill="#FDBA74" stroke="#9A3412" stroke-width="2"/>
          <circle cx="227" cy="75" r="2" fill="#1E293B"/>
          <circle cx="237" cy="75" r="2" fill="#1E293B"/>
          <path d="M227 81 Q232 86 237 81" fill="none" stroke="#9A3412" stroke-width="2" stroke-linecap="round"/>
          <circle cx="212" cy="102" r="7" fill="#F43F5E"/>
          <circle cx="252" cy="102" r="7" fill="#3B82F6"/>
        </g>
        """
    elif mod_key == "AI":
        scene = """
        <style>
          @keyframes spinSun {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
          @keyframes strollKid {
            0%, 100% { transform: translateX(-4px); }
            50% { transform: translateX(6px); }
          }
          .sun-spin { animation: spinSun 12s linear infinite; transform-origin: 54px 46px; }
          .stroll-kid { animation: strollKid 2.5s ease-in-out infinite; }
        </style>
        <rect x="0" y="0" width="320" height="164" rx="14" fill="#CCFBF1"/>
        <g class="sun-spin">
          <circle cx="54" cy="46" r="15" fill="#FBBF24"/>
          <line x1="54" y1="22" x2="54" y2="28" stroke="#F59E0B" stroke-width="3" stroke-linecap="round"/>
          <line x1="54" y1="64" x2="54" y2="70" stroke="#F59E0B" stroke-width="3" stroke-linecap="round"/>
          <line x1="30" y1="46" x2="36" y2="46" stroke="#F59E0B" stroke-width="3" stroke-linecap="round"/>
          <line x1="72" y1="46" x2="78" y2="46" stroke="#F59E0B" stroke-width="3" stroke-linecap="round"/>
        </g>
        <path d="M0 124 Q85 104 170 120 T320 112 L320 164 L0 164 Z" fill="#5EEAD4"/>
        <!-- Walking kid -->
        <g class="stroll-kid">
          <circle cx="155" cy="72" r="16" fill="#FDBA74" stroke="#0F766E" stroke-width="2.5"/>
          <circle cx="150" cy="71" r="2.2" fill="#1E293B"/>
          <circle cx="160" cy="71" r="2.2" fill="#1E293B"/>
          <path d="M150 77 Q155 82 160 77" fill="none" stroke="#0F766E" stroke-width="2" stroke-linecap="round"/>
          <rect x="142" y="90" width="26" height="26" rx="8" fill="#14B8A6"/>
          <line x1="149" y1="116" x2="142" y2="134" stroke="#0F766E" stroke-width="3.5" stroke-linecap="round"/>
          <line x1="161" y1="116" x2="168" y2="134" stroke="#0F766E" stroke-width="3.5" stroke-linecap="round"/>
        </g>
        <!-- Calm headphones icon -->
        <path d="M234 86 A22 22 0 0 1 278 86" fill="none" stroke="#0D9488" stroke-width="4" stroke-linecap="round"/>
        <rect x="228" y="84" width="10" height="20" rx="5" fill="#0D9488"/>
        <rect x="274" y="84" width="10" height="20" rx="5" fill="#0D9488"/>
        """
    else:
        scene = """
        <style>
          @keyframes cardBounce {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-6px); }
          }
          @keyframes talkWave {
            0%, 100% { transform: scale(0.95); }
            50% { transform: scale(1.08); }
          }
          .card-bounce { animation: cardBounce 2.1s ease-in-out infinite; }
          .talk-wave { animation: talkWave 1.8s ease-in-out infinite; transform-origin: 244px 76px; }
        </style>
        <rect x="0" y="0" width="320" height="164" rx="14" fill="#FEF3C7"/>
        <rect x="0" y="132" width="320" height="32" fill="#FDE68A"/>
        <!-- Picture card -->
        <g class="card-bounce">
          <rect x="26" y="34" width="88" height="86" rx="12" fill="#FFFFFF" stroke="#F59E0B" stroke-width="3"/>
          <circle cx="70" cy="66" r="15" fill="#38BDF8"/>
          <rect x="44" y="88" width="52" height="14" rx="7" fill="#FDE68A"/>
          <text x="70" y="99" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#92400E">PECS CARD</text>
        </g>
        <path d="M126 78 L156 78" stroke="#D97706" stroke-width="4" stroke-linecap="round"/>
        <polygon points="154,70 168,78 154,86" fill="#D97706"/>
        <!-- Kid speaking -->
        <g class="talk-wave">
          <circle cx="236" cy="74" r="22" fill="#FDBA74" stroke="#B45309" stroke-width="2.5"/>
          <circle cx="229" cy="72" r="2.5" fill="#1E293B"/>
          <circle cx="243" cy="72" r="2.5" fill="#1E293B"/>
          <ellipse cx="236" cy="82" rx="6" ry="4" fill="#EF4444"/>
          <circle cx="272" cy="44" r="6" fill="#F59E0B" opacity="0.7"/>
          <circle cx="286" cy="36" r="4" fill="#F59E0B" opacity="0.5"/>
        </g>
        """
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<style>
  html, body {{
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: 'Segoe UI', Arial, sans-serif;
  }}
  .wrap {{
    background: {soft_bg};
    border: 2px solid {accent}33;
    border-radius: 14px;
    padding: 10px;
  }}
  .caption {{
    margin-top: 6px;
    font-size: 12px;
    font-weight: 700;
    color: #1E293B;
    text-align: center;
  }}
</style>
</head>
<body>
  <div class="wrap">
    <svg viewBox="0 0 320 164" width="100%" height="156" xmlns="http://www.w3.org/2000/svg" style="display:block;border-radius:12px;">
      {scene}
    </svg>
    <div class="caption">Animated Guide • Page {page_idx + 1}</div>
  </div>
</body>
</html>
"""
def build_flipbook_html(mod: dict) -> str:
    title_esc = html.escape(f"{mod['code']}: {mod['title']}")
    domain_esc = html.escape(mod["domain"])
    accent = mod["color"]
    soft_bg = mod["soft_bg"]
    svg_art = module_animated_html(mod["key"], accent, soft_bg, 0)

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
    color: #1E293B;
    display: flex;
    justify-content: center;
  }}
  .book-shell {{
    max-width: 720px;
    width: 100%;
    background: #FFFFFF;
    border-radius: 18px;
    padding: 26px;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
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
  h1 {{ margin: 10px 0 4px 0; font-size: 24px; }}
  .domain {{ color: #475569; font-size: 14px; margin-bottom: 16px; }}
  .page-box {{
    background: {soft_bg};
    border-radius: 14px;
    padding: 20px;
    margin-top: 16px;
    min-height: 170px;
  }}
  .page-heading {{ font-size: 18px; font-weight: 700; margin-bottom: 8px; }}
  .page-summary {{ font-size: 15px; margin-bottom: 12px; line-height: 1.5; }}
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
  button:disabled {{ background: #CBD5E1; cursor: not-allowed; }}
  .indicator {{ font-weight: 700; color: #334155; }}
</style>
</head>
<body>
  <div class="book-shell">
    <span class="top-tag">INTERACTIVE FLIPBOOK</span>
    <h1>{title_esc}</h1>
    <div class="domain">Focus Domain: {domain_esc}</div>
    {svg_art}
    <div class="page-box">
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
      render();
    }}
  }}
  render();
</script>
</body>
</html>
"""


def module_animated_html(mod_key: str, accent: str, soft_bg: str, page_idx: int) -> str:
    if mod_key == "AG":
        scene = """
        <style>
          @keyframes floatDrop { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-7px); } }
          @keyframes popBadge { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
          .kid-float { animation: floatDrop 2.4s ease-in-out infinite; }
          .drop-anim { animation: floatDrop 1.8s ease-in-out infinite; }
          .check-pop { animation: popBadge 2.1s ease-in-out infinite; transform-origin: 252px 80px; }
        </style>
        <rect x="0" y="0" width="320" height="164" rx="14" fill="#CCFBF1"/>
        <circle cx="284" cy="28" r="14" fill="#99F6E4"/>
        <path d="M0 132 Q80 120 160 132 T320 128 L320 164 L0 164 Z" fill="#5EEAD4"/>
        <g class="kid-float">
          <circle cx="72" cy="62" r="20" fill="#FDBA74" stroke="#0F172A" stroke-width="2.5"/>
          <path d="M53 56 Q72 36 91 56 Q82 46 72 48 Q62 46 53 56 Z" fill="#1E293B"/>
          <circle cx="65" cy="61" r="2.8" fill="#0F172A"/>
          <circle cx="79" cy="61" r="2.8" fill="#0F172A"/>
          <path d="M66 69 Q72 75 78 69" fill="none" stroke="#0F172A" stroke-width="2.5" stroke-linecap="round"/>
          <rect x="54" y="84" width="36" height="34" rx="12" fill="#0F766E" stroke="#1E3A8A" stroke-width="2"/>
          <circle cx="72" cy="100" r="5" fill="#FFFFFF"/>
        </g>
        <g class="drop-anim">
          <path d="M156 54 Q172 34 188 54 Q188 78 172 90 Q156 78 156 54 Z" fill="#1E3A8A"/>
          <circle cx="167" cy="56" r="4" fill="#DBEAFE"/>
        </g>
        <g class="check-pop">
          <circle cx="252" cy="80" r="23" fill="#FFFFFF" stroke="#0D9488" stroke-width="3"/>
          <path d="M241 80 L249 88 L264 72" fill="none" stroke="#0D9488" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
        </g>
        """
    elif mod_key == "AH":
        scene = """
        <style>
          @keyframes hopKid { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-6px); } }
          @keyframes slideArrow { 0%, 100% { transform: translateX(0px); } 50% { transform: translateX(5px); } }
          .hop-kid { animation: hopKid 2.2s ease-in-out infinite; }
          .arrow-move { animation: slideArrow 1.5s ease-in-out infinite; }
        </style>
        <rect x="0" y="0" width="320" height="164" rx="14" fill="#DBEAFE"/>
        <rect x="0" y="130" width="320" height="34" fill="#BFDBFE"/>
        <rect x="20" y="34" width="96" height="84" rx="12" fill="#FFFFFF" stroke="#1E3A8A" stroke-width="2.5"/>
        <text x="68" y="56" text-anchor="middle" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="12" font-weight="800" fill="#1E3A8A">FIRST</text>
        <rect x="44" y="66" width="48" height="36" rx="8" fill="#0D9488"/>
        <path d="M54 66 Q68 54 82 66" fill="none" stroke="#0F172A" stroke-width="2.5"/>
        <g class="arrow-move">
          <path d="M126 76 L146 76" stroke="#1E3A8A" stroke-width="3.5" stroke-linecap="round"/>
          <polygon points="144,68 158,76 144,84" fill="#1E3A8A"/>
        </g>
        <g class="hop-kid">
          <rect x="168" y="34" width="128" height="84" rx="12" fill="#FFFFFF" stroke="#6D28D9" stroke-width="2.5"/>
          <text x="232" y="55" text-anchor="middle" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="12" font-weight="800" fill="#5B21B6">THEN PLAY</text>
          <circle cx="232" cy="76" r="14" fill="#FDBA74" stroke="#0F172A" stroke-width="2"/>
          <circle cx="227" cy="75" r="2" fill="#0F172A"/>
          <circle cx="237" cy="75" r="2" fill="#0F172A"/>
          <path d="M227 81 Q232 86 237 81" fill="none" stroke="#0F172A" stroke-width="2" stroke-linecap="round"/>
          <circle cx="212" cy="102" r="6.5" fill="#0D9488"/>
          <circle cx="252" cy="102" r="6.5" fill="#7C3AED"/>
        </g>
        """
    elif mod_key == "AI":
        scene = """
        <style>
          @keyframes spinSun { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
          @keyframes strollKid { 0%, 100% { transform: translateX(-4px); } 50% { transform: translateX(6px); } }
          .sun-spin { animation: spinSun 14s linear infinite; transform-origin: 54px 46px; }
          .stroll-kid { animation: strollKid 2.5s ease-in-out infinite; }
        </style>
        <rect x="0" y="0" width="320" height="164" rx="14" fill="#CCFBF1"/>
        <g class="sun-spin">
          <circle cx="54" cy="46" r="14" fill="#0D9488"/>
          <line x1="54" y1="23" x2="54" y2="29" stroke="#0F766E" stroke-width="3" stroke-linecap="round"/>
          <line x1="54" y1="63" x2="54" y2="69" stroke="#0F766E" stroke-width="3" stroke-linecap="round"/>
          <line x1="31" y1="46" x2="37" y2="46" stroke="#0F766E" stroke-width="3" stroke-linecap="round"/>
          <line x1="71" y1="46" x2="77" y2="46" stroke="#0F766E" stroke-width="3" stroke-linecap="round"/>
        </g>
        <path d="M0 124 Q85 104 170 120 T320 112 L320 164 L0 164 Z" fill="#99F6E4"/>
        <g class="stroll-kid">
          <circle cx="155" cy="72" r="16" fill="#FDBA74" stroke="#0F172A" stroke-width="2.2"/>
          <circle cx="150" cy="71" r="2.2" fill="#0F172A"/>
          <circle cx="160" cy="71" r="2.2" fill="#0F172A"/>
          <path d="M150 77 Q155 82 160 77" fill="none" stroke="#0F172A" stroke-width="2" stroke-linecap="round"/>
          <rect x="142" y="90" width="26" height="26" rx="8" fill="#1E3A8A"/>
          <line x1="149" y1="116" x2="142" y2="134" stroke="#0F172A" stroke-width="3.2" stroke-linecap="round"/>
          <line x1="161" y1="116" x2="168" y2="134" stroke="#0F172A" stroke-width="3.2" stroke-linecap="round"/>
        </g>
        <path d="M234 86 A22 22 0 0 1 278 86" fill="none" stroke="#6D28D9" stroke-width="4" stroke-linecap="round"/>
        <rect x="228" y="84" width="10" height="20" rx="5" fill="#6D28D9"/>
        <rect x="274" y="84" width="10" height="20" rx="5" fill="#6D28D9"/>
        """
    else:
        scene = """
        <style>
          @keyframes cardBounce { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-6px); } }
          @keyframes wavePulse { 0%, 100% { transform: scale(0.96); } 50% { transform: scale(1.07); } }
          .card-bounce { animation: cardBounce 2.1s ease-in-out infinite; }
          .talk-wave { animation: wavePulse 1.8s ease-in-out infinite; transform-origin: 244px 76px; }
        </style>
        <rect x="0" y="0" width="320" height="164" rx="14" fill="#EDE9FE"/>
        <rect x="0" y="132" width="320" height="32" fill="#DDD6FE"/>
        <g class="card-bounce">
          <rect x="26" y="34" width="90" height="86" rx="12" fill="#FFFFFF" stroke="#6D28D9" stroke-width="2.5"/>
          <circle cx="71" cy="66" r="15" fill="#0D9488"/>
          <rect x="42" y="88" width="58" height="15" rx="7.5" fill="#EDE9FE"/>
          <text x="71" y="99" text-anchor="middle" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="9.5" font-weight="800" fill="#5B21B6">PECS CARD</text>
        </g>
        <path d="M126 78 L156 78" stroke="#1E3A8A" stroke-width="3.5" stroke-linecap="round"/>
        <polygon points="154,70 168,78 154,86" fill="#1E3A8A"/>
        <g class="talk-wave">
          <circle cx="236" cy="74" r="22" fill="#FDBA74" stroke="#0F172A" stroke-width="2.2"/>
          <circle cx="229" cy="72" r="2.5" fill="#0F172A"/>
          <circle cx="243" cy="72" r="2.5" fill="#0F172A"/>
          <ellipse cx="236" cy="82" rx="6" ry="4" fill="#6D28D9"/>
          <circle cx="272" cy="44" r="5.5" fill="#0D9488" opacity="0.8"/>
          <circle cx="286" cy="36" r="3.8" fill="#1E3A8A" opacity="0.65"/>
        </g>
        """
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<style>
  html, body {{
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif;
  }}
  .wrap {{
    background: {soft_bg};
    border: 1.5px solid {accent}44;
    border-radius: 14px;
    padding: 10px;
  }}
  .caption {{
    margin-top: 6px;
    font-size: 12px;
    font-weight: 700;
    color: #0F172A;
    text-align: center;
  }}
</style>
</head>
<body>
  <div class="wrap">
    <svg viewBox="0 0 320 164" width="100%" height="156" xmlns="http://www.w3.org/2000/svg" style="display:block;border-radius:12px;">
      {scene}
    </svg>
    <div class="caption">Animated Kids Guide • Page {page_idx + 1}</div>
  </div>
</body>
</html>
"""

def build_flipbook_html(mod: dict) -> str:
    title_esc = html.escape(f"{mod['code']}: {mod['title']}")
    domain_esc = html.escape(mod["domain"])
    accent = mod["color"]
    soft_bg = mod["soft_bg"]
    svg_art = module_animated_html(mod["key"], accent, soft_bg, 0)

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
    font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif;
    background: linear-gradient(135deg, #CCFBF1 0%, #EDE9FE 52%, #DBEAFE 100%);
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
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
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
  h1 {{ margin: 10px 0 4px 0; font-size: 24px; }}
  .domain {{ color: #475569; font-size: 14px; margin-bottom: 16px; }}
  .page-box {{
    background: {soft_bg};
    border-radius: 14px;
    padding: 20px;
    margin-top: 16px;
    min-height: 170px;
  }}
  .page-heading {{ font-size: 18px; font-weight: 700; margin-bottom: 8px; }}
  .page-summary {{ font-size: 15px; margin-bottom: 12px; line-height: 1.5; }}
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
  button:disabled {{ background: #CBD5E1; cursor: not-allowed; }}
  .indicator {{ font-weight: 700; color: #334155; }}
</style>
</head>
<body>
  <div class="book-shell">
    <span class="top-tag">INTERACTIVE FLIPBOOK</span>
    <h1>{title_esc}</h1>
    <div class="domain">Focus Domain: {domain_esc}</div>
    {svg_art}
    <div class="page-box">
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
      render();
    }}
  }}
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

st.sidebar.markdown("### ⚡ Kelantan GIS")
page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Student Registry",
        "Child & Centre Matcher",
        "4 Flipbook Modules",
    ],
)

counts_by_dist = df_students["District"].value_counts().to_dict()

# ==============================================================================
# PAGE 1: EXECUTIVE DASHBOARD (SOFT TEAL + NAVY BLUE + LAVENDER)
# ==============================================================================
if page == "Dashboard":
    total_students = len(df_students)
    verified_cnt = int((df_students["Status"] == "Verified Active").sum())
    red_zones = sum(1 for v in DISTRICT_INFO.values() if v["zone"] == "Red Zone")

    top_l, top_r = st.columns([4, 8], gap="medium")
    with top_l:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="brand-header">
                    <div class="brand-mark">KA</div>
                    <div>
                        <div style="font-size:18px;font-weight:800;color:#0F172A;">Kelantan Autism GIS</div>
                        <div style="font-size:11px;font-weight:700;letter-spacing:0.6px;color:#0F766E;">SPATIAL & CAREGIVER ANALYTICS</div>
                        <div style="font-size:12.5px;color:#475569;margin-top:3px;">{total_students} Registry Records • 7 Districts</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with top_r:
        with st.container(border=True):
            h_l, h_r = st.columns([8, 4], vertical_alignment="center")
            with h_l:
                st.markdown('<div class="section-title">Kelantan Zone & Registry Summary</div>', unsafe_allow_html=True)
                st.markdown('<div class="section-sub">District student distribution, diagnosis mix, and intervention demand</div>', unsafe_allow_html=True)
            with h_r:
                st.download_button(
                    label="⬇ Download CSV",
                    data=df_students.to_csv(index=False).encode("utf-8"),
                    file_name="kelantan_student_registry.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            k1, k2, k3 = st.columns(3, gap="medium")
            with k1:
                st.markdown(
                    f'<div class="kpi-tile-teal"><div class="kpi-label">Total Students</div><div class="kpi-value">{total_students}</div></div>',
                    unsafe_allow_html=True,
                )
            with k2:
                st.markdown(
                    f'<div class="kpi-tile-navy"><div class="kpi-label">Verified Active</div><div class="kpi-value">{verified_cnt}</div></div>',
                    unsafe_allow_html=True,
                )
            with k3:
                st.markdown(
                    f'<div class="kpi-tile-lavender"><div class="kpi-label">Red Zone Districts</div><div class="kpi-value">{red_zones}</div></div>',
                    unsafe_allow_html=True,
                )

    mid_l, mid_r = st.columns([7, 5], gap="medium")

    dist_df = df_students.groupby("District").size().reset_index(name="Students")
    for d_name in DISTRICT_INFO:
        if d_name not in dist_df["District"].values:
            dist_df = pd.concat([dist_df, pd.DataFrame([{"District": d_name, "Students": 0}])], ignore_index=True)
    dist_df["Order"] = dist_df["District"].map({k: i for i, k in enumerate(DISTRICT_INFO.keys())})
    dist_df = dist_df.sort_values("Order")

    with mid_l:
        with st.container(border=True):
            st.markdown('<div class="section-title">Students Across Kelantan Districts</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-sub">Registered student count per administrative district</div>', unsafe_allow_html=True)
            area_base = alt.Chart(dist_df).encode(
                x=alt.X(
                    "District:N",
                    sort=list(DISTRICT_INFO.keys()),
                    axis=alt.Axis(labelAngle=0, labelColor="#0F172A", labelFontSize=11, title=None),
                ),
                y=alt.Y(
                    "Students:Q",
                    axis=alt.Axis(labelColor="#0F172A", title=None, gridColor="#E2E8F0"),
                ),
                tooltip=["District", "Students"],
            )
            area_layer = area_base.mark_area(
                line={"color": "#1E3A8A", "strokeWidth": 2.5},
                color=alt.Gradient(
                    gradient="linear",
                    stops=[
                        alt.GradientStop(color="rgba(13, 148, 136, 0.36)", offset=0),
                        alt.GradientStop(color="rgba(124, 58, 237, 0.06)", offset=1),
                    ],
                    x1=1, x2=1, y1=1, y2=0,
                ),
            )
            pts_layer = area_base.mark_point(size=80, filled=True, color="#FFFFFF", stroke="#6D28D9", strokeWidth=2.5)
            txt_layer = area_base.mark_text(dy=-13, fontSize=12, fontWeight="bold", color="#0F172A").encode(text="Students:Q")
            st.altair_chart(
                (area_layer + pts_layer + txt_layer)
                .properties(height=245)
                .configure(background="#FFFFFF")
                .configure_view(fill="#FFFFFF", strokeWidth=0),
                use_container_width=True,
            )

    with mid_r:
        with st.container(border=True):
            st.markdown('<div class="section-title">Diagnosis Breakdown</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-sub">Proportion of registered autism profiles</div>', unsafe_allow_html=True)
            diag_df = df_students.groupby("Diagnosis").size().reset_index(name="Count")
            donut = (
                alt.Chart(diag_df)
                .mark_arc(innerRadius=54, outerRadius=84)
                .encode(
                    theta=alt.Theta("Count:Q"),
                    color=alt.Color(
                        "Diagnosis:N",
                        scale=alt.Scale(
                            domain=["Mild Autism", "High-Function Autism", "Severe Autism"],
                            range=["#0D9488", "#1E3A8A", "#7C3AED"],
                        ),
                        legend=alt.Legend(orient="bottom", title=None, labelColor="#0F172A"),
                    ),
                    tooltip=["Diagnosis", "Count"],
                )
                .properties(height=245)
                .configure(background="#FFFFFF")
                .configure_view(fill="#FFFFFF", strokeWidth=0)
            )
            st.altair_chart(donut, use_container_width=True)

    bot_l, bot_r = st.columns([7, 5], gap="medium")

    with bot_l:
        with st.container(border=True):
            st.markdown('<div class="section-title">Service & Verification Rates</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-sub">Verification status and required therapy distribution</div>', unsafe_allow_html=True)

            verified_pct = round((verified_cnt / total_students) * 100) if total_students else 0
            speech_cnt = int((df_students["Required Service"] == "Speech Therapy").sum())
            speech_pct = round((speech_cnt / total_students) * 100) if total_students else 0

            r1, r2, r3 = st.columns(3)
            r1.metric("Verified Rate", f"{verified_pct}%", f"{verified_cnt} students")
            r2.metric("Speech Therapy Share", f"{speech_pct}%", f"{speech_cnt} students")
            r3.metric("Total Therapy Centres", sum(v["centres"] for v in DISTRICT_INFO.values()), "7 districts")

            serv_df = df_students.groupby("Required Service").size().reset_index(name="Students")
            s_bars = (
                alt.Chart(serv_df)
                .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, color="#0F766E")
                .encode(
                    x=alt.X("Required Service:N", axis=alt.Axis(labelAngle=0, labelColor="#0F172A", title=None)),
                    y=alt.Y("Students:Q", axis=alt.Axis(labelColor="#0F172A", title=None, gridColor="#E2E8F0")),
                    tooltip=["Required Service", "Students"],
                )
            )
            s_txt = s_bars.mark_text(dy=-8, fontSize=12, fontWeight="bold", color="#0F172A").encode(text="Students:Q")
            st.altair_chart(
                (s_bars + s_txt)
                .properties(height=180)
                .configure(background="#FFFFFF")
                .configure_view(fill="#FFFFFF", strokeWidth=0),
                use_container_width=True,
            )

    with bot_r:
        with st.container(border=True):
            st.markdown('<div class="section-title">District Zone & Centre Inspector</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-sub">Inspect zone classification, recommended centre, and therapy team</div>', unsafe_allow_html=True)
            selected_dist = st.selectbox(
                "Select District",
                options=list(DISTRICT_INFO.keys()),
                index=list(DISTRICT_INFO.keys()).index(st.session_state["selected_zone_district"]),
                label_visibility="collapsed",
            )
            st.session_state["selected_zone_district"] = selected_dist
            d_info = DISTRICT_INFO[selected_dist]
            d_rows = df_students[df_students["District"] == selected_dist]

            st.markdown(
                f'<span class="zone-pill" style="background:{d_info["badge_bg"]};">{d_info["zone"]}</span> '
                f'<strong style="color:#0F172A;">{selected_dist}</strong> — {len(d_rows)} students • {d_info["centres"]} centres',
                unsafe_allow_html=True,
            )
            st.write(d_info["place_summary"])
            st.markdown(f"**Suitable Centre:** {d_info['recommended_centre']}")
            st.markdown(f"**Therapists:** {d_info['therapists']}")

# ==============================================================================
# PAGE 2: STUDENT REGISTRY (EDIT & INSERT)
# ==============================================================================
elif page == "Student Registry":
    with st.container(border=True):
        st.subheader("Student Registry — Edit & Insert Records")

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

                if st.form_submit_button("Add Record"):
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
        if b1.button("Save Table Edits", type="primary"):
            st.session_state["student_df"] = edited_df.copy()
            st.success("Saved changes to registry!")

        b2.download_button(
            label="Download Updated CSV",
            data=st.session_state["student_df"].to_csv(index=False).encode("utf-8"),
            file_name="kelantan_student_registry_updated.csv",
            mime="text/csv",
        )


# ==============================================================================
# PAGE 3: PARENTS — CHILD & CENTRE MATCHER
# ==============================================================================
elif page == "Child & Centre Matcher":
    with st.container(border=True):
        st.subheader("Child Profile, Suitable Centre & Therapists")

        f1, f2 = st.columns([2, 4])
        dist_filter = f1.selectbox("Filter District", ["ALL"] + list(DISTRICT_INFO.keys()))
        pool_df = df_students if dist_filter == "ALL" else df_students[df_students["District"] == dist_filter]

        selected_rec_id = f2.selectbox(
            "Choose Child Record",
            options=pool_df["Record ID"].tolist(),
            format_func=lambda rid: f"{rid} — {pool_df.loc[pool_df['Record ID'] == rid, 'Identifier'].values[0]} ({pool_df.loc[pool_df['Record ID'] == rid, 'District'].values[0]})",
        )

        child_row = df_students[df_students["Record ID"] == selected_rec_id].iloc[0]
        c_dist = str(child_row["District"]).upper()
        c_diag = str(child_row["Diagnosis"])
        c_info = DISTRICT_INFO.get(c_dist, DISTRICT_INFO["KOTA BHARU"])

        left, right = st.columns([5, 7], gap="large")
        with left:
            st.markdown("#### Child Information")
            st.markdown(f"**Record ID:** `{child_row['Record ID']}`")
            st.markdown(f"**Identifier:** {child_row['Identifier']}")
            st.markdown(f"**Age:** `{child_row['Age']}` years old")
            st.markdown(f"**District:** `{c_dist}` (`{c_info['zone']}`)")
            st.markdown(f"**Type of Autism:** `{c_diag}`")
            st.markdown(f"**Required Service:** `{child_row['Required Service']}`")
            st.markdown(f"**Date:** `{child_row['Date']}` | **Status:** `{child_row['Status']}`")

        with right:
            st.markdown("#### Suitable Centre & Therapists")
            st.markdown(
                f'<span class="zone-pill" style="background:{c_info["badge_bg"]};">{c_info["zone"]}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(f"##### {c_info['recommended_centre']}")
            st.markdown(f"**Why Suitable:** {c_info['why_suitable']}")
            st.markdown(f"**Therapists Provided:** {c_info['therapists']}")
            st.markdown(f"**Matched Required Service:** `{child_row['Required Service']}`")


# ==============================================================================
# PAGE 4: PARENTS — 4 INTERACTIVE FLIPBOOK MODULES
# ==============================================================================
else:
    st.subheader("4 Interactive Flipbook Modules")
    cols = st.columns(2, gap="large")
    for idx, mod in enumerate(MODULES_4):
        p_key = f"flip_page_{mod['key']}"
        cur_page = st.session_state[p_key]
        total_pages = len(mod["pages"])
        p_heading, p_summary, p_steps = mod["pages"][cur_page]

        with cols[idx % 2]:
            with st.container(border=True):
                st.markdown(
                    f'<span class="zone-pill" style="background:{mod["color"]};">{mod["code"]} • {mod["domain"]}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"#### {mod['title']}")
                components.html(module_animated_html(mod["key"], mod["color"], mod["soft_bg"], cur_page), height=205)

                st.markdown(
                    f"""
                    <div class="flip-panel" style="margin-top:12px;">
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
                if nav1.button("◀ Prev", key=f"prev_{mod['key']}", disabled=(cur_page == 0), use_container_width=True):
                    st.session_state[p_key] = cur_page - 1
                    st.rerun()
                nav2.markdown(
                    f"<div style='text-align:center;padding-top:8px;font-weight:700;'>Page {cur_page + 1} / {total_pages}</div>",
                    unsafe_allow_html=True,
                )
                if nav3.button("Next ▶", key=f"next_{mod['key']}", disabled=(cur_page == total_pages - 1), use_container_width=True):
                    st.session_state[p_key] = cur_page + 1
                    st.rerun()

                flip_html = build_flipbook_html(mod)
                st.download_button(
                    label=f"Download {mod['code']} Flipbook (.html)",
                    data=flip_html.encode("utf-8"),
                    file_name=f"{mod['code'].replace(' ', '_')}_Flipbook.html",
                    mime="text/html",
                    key=f"dl_flip_{mod['key']}",
                    use_container_width=True,
                )
