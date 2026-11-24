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


    /* Replace black top Streamlit header bar with colorful interlocking puzzle border */
    header[data-testid="stHeader"],
    [data-testid="stToolbar"] {
        background-color: #FFFFFF !important;
        background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMzYiIGhlaWdodD0iNTYiIHZpZXdCb3g9IjAgMCAzMzYgNTYiPgogIDwhLS0gUm93IDEgYmFzZSBzcXVhcmVzICg3IGNvbG9ycyB4IDQ4cHggPSAzMzZweCkgLS0+CiAgPHJlY3QgeD0iMCIgeT0iMCIgd2lkdGg9IjQ4IiBoZWlnaHQ9IjI2IiBmaWxsPSIjRTExRDI0Ii8+CiAgPHJlY3QgeD0iNDgiIHk9IjAiIHdpZHRoPSI0OCIgaGVpZ2h0PSIyNiIgZmlsbD0iI0Y1ODIyMCIvPgogIDxyZWN0IHg9Ijk2IiB5PSIwIiB3aWR0aD0iNDgiIGhlaWdodD0iMjYiIGZpbGw9IiNGOUU0MjQiLz4KICA8cmVjdCB4PSIxNDQiIHk9IjAiIHdpZHRoPSI0OCIgaGVpZ2h0PSIyNiIgZmlsbD0iIzZCQjUzNiIvPgogIDxyZWN0IHg9IjE5MiIgeT0iMCIgd2lkdGg9IjQ4IiBoZWlnaHQ9IjI2IiBmaWxsPSIjNjhDM0U4Ii8+CiAgPHJlY3QgeD0iMjQwIiB5PSIwIiB3aWR0aD0iNDgiIGhlaWdodD0iMjYiIGZpbGw9IiMxQjQ5OUIiLz4KICA8cmVjdCB4PSIyODgiIHk9IjAiIHdpZHRoPSI0OCIgaGVpZ2h0PSIyNiIgZmlsbD0iIzlCNEQ5QiIvPgoKICA8IS0tIFJvdyAxIGhvcml6b250YWwgaW50ZXJsb2NraW5nIHRhYnMgLS0+CiAgPGNpcmNsZSBjeD0iNTEiIGN5PSIxMyIgcj0iNC41IiBmaWxsPSIjRTExRDI0Ii8+CiAgPGNpcmNsZSBjeD0iOTMiIGN5PSIxMyIgcj0iNC41IiBmaWxsPSIjRjlFNDI0Ii8+CiAgPGNpcmNsZSBjeD0iMTQ3IiBjeT0iMTMiIHI9IjQuNSIgZmlsbD0iI0Y5RTQyNCIvPgogIDxjaXJjbGUgY3g9IjE4OSIgY3k9IjEzIiByPSI0LjUiIGZpbGw9IiM2OEMzRTgiLz4KICA8Y2lyY2xlIGN4PSIyNDMiIGN5PSIxMyIgcj0iNC41IiBmaWxsPSIjNjhDM0U4Ii8+CiAgPGNpcmNsZSBjeD0iMjg1IiBjeT0iMTMiIHI9IjQuNSIgZmlsbD0iIzlCNEQ5QiIvPgogIDxjaXJjbGUgY3g9IjMzMyIgY3k9IjEzIiByPSI0LjUiIGZpbGw9IiNFMTFEMjQiLz4KCiAgPCEtLSBSb3cgMiBiYXNlIHNxdWFyZXMgKHNoaWZ0ZWQgY29sb3Igc2VxdWVuY2UgbWF0Y2hpbmcgc2NyZWVuc2hvdCkgLS0+CiAgPHJlY3QgeD0iMCIgeT0iMjYiIHdpZHRoPSI0OCIgaGVpZ2h0PSIyNiIgZmlsbD0iIzY4QzNFOCIvPgogIDxyZWN0IHg9IjQ4IiB5PSIyNiIgd2lkdGg9IjQ4IiBoZWlnaHQ9IjI2IiBmaWxsPSIjMUI0OTlCIi8+CiAgPHJlY3QgeD0iOTYiIHk9IjI2IiB3aWR0aD0iNDgiIGhlaWdodD0iMjYiIGZpbGw9IiM5QjREOUIiLz4KICA8cmVjdCB4PSIxNDQiIHk9IjI2IiB3aWR0aD0iNDgiIGhlaWdodD0iMjYiIGZpbGw9IiNFMTFEMjQiLz4KICA8cmVjdCB4PSIxOTIiIHk9IjI2IiB3aWR0aD0iNDgiIGhlaWdodD0iMjYiIGZpbGw9IiNGNTgyMjAiLz4KICA8cmVjdCB4PSIyNDAiIHk9IjI2IiB3aWR0aD0iNDgiIGhlaWdodD0iMjYiIGZpbGw9IiNGOUU0MjQiLz4KICA8cmVjdCB4PSIyODgiIHk9IjI2IiB3aWR0aD0iNDgiIGhlaWdodD0iMjYiIGZpbGw9IiM2QkI1MzYiLz4KCiAgPCEtLSBSb3cgMiBob3Jpem9udGFsIGludGVybG9ja2luZyB0YWJzIC0tPgogIDxjaXJjbGUgY3g9IjQ1IiBjeT0iMzkiIHI9IjQuNSIgZmlsbD0iIzFCNDk5QiIvPgogIDxjaXJjbGUgY3g9Ijk5IiBjeT0iMzkiIHI9IjQuNSIgZmlsbD0iIzFCNDk5QiIvPgogIDxjaXJjbGUgY3g9IjE0MSIgY3k9IjM5IiByPSI0LjUiIGZpbGw9IiNFMTFEMjQiLz4KICA8Y2lyY2xlIGN4PSIxOTUiIGN5PSIzOSIgcj0iNC41IiBmaWxsPSIjRTExRDI0Ii8+CiAgPGNpcmNsZSBjeD0iMjM3IiBjeT0iMzkiIHI9IjQuNSIgZmlsbD0iI0Y5RTQyNCIvPgogIDxjaXJjbGUgY3g9IjI5MSIgY3k9IjM5IiByPSI0LjUiIGZpbGw9IiNGOUU0MjQiLz4KICA8Y2lyY2xlIGN4PSIzIiBjeT0iMzkiIHI9IjQuNSIgZmlsbD0iIzZCQjUzNiIvPgoKICA8IS0tIFZlcnRpY2FsIGludGVybG9ja2luZyB0YWJzIGJldHdlZW4gUm93IDEgYW5kIFJvdyAyIC0tPgogIDxjaXJjbGUgY3g9IjI0IiBjeT0iMjMiIHI9IjQuNSIgZmlsbD0iIzY4QzNFOCIvPgogIDxjaXJjbGUgY3g9IjcyIiBjeT0iMjkiIHI9IjQuNSIgZmlsbD0iI0Y1ODIyMCIvPgogIDxjaXJjbGUgY3g9IjEyMCIgY3k9IjIzIiByPSI0LjUiIGZpbGw9IiM5QjREOUIiLz4KICA8Y2lyY2xlIGN4PSIxNjgiIGN5PSIyOSIgcj0iNC41IiBmaWxsPSIjNkJCNTM2Ii8+CiAgPGNpcmNsZSBjeD0iMjE2IiBjeT0iMjMiIHI9IjQuNSIgZmlsbD0iI0Y1ODIyMCIvPgogIDxjaXJjbGUgY3g9IjI2NCIgY3k9IjI5IiByPSI0LjUiIGZpbGw9IiMxQjQ5OUIiLz4KICA8Y2lyY2xlIGN4PSIzMTIiIGN5PSIyMyIgcj0iNC41IiBmaWxsPSIjNkJCNTM2Ii8+CgogIDwhLS0gQm90dG9tIHByb3RydWRpbmcgcHV6emxlIHRhYnMgbWF0Y2hpbmcgc2NyZWVuc2hvdCAtLT4KICA8Y2lyY2xlIGN4PSIyNCIgY3k9IjUyIiByPSIzLjgiIGZpbGw9IiM2OEMzRTgiLz4KICA8Y2lyY2xlIGN4PSIxMjAiIGN5PSI1MiIgcj0iMy44IiBmaWxsPSIjOUI0RDlCIi8+CiAgPGNpcmNsZSBjeD0iMjE2IiBjeT0iNTIiIHI9IjMuOCIgZmlsbD0iI0Y1ODIyMCIvPgogIDxjaXJjbGUgY3g9IjMxMiIgY3k9IjUyIiByPSIzLjgiIGZpbGw9IiM2QkI1MzYiLz4KPC9zdmc+") !important;
        background-repeat: repeat-x !important;
        background-position: left top !important;
        background-size: auto 56px !important;
        height: 58px !important;
        border-bottom: none !important;
    }

    /* Ensure top toolbar icons stay clearly readable against the colorful puzzle bar */
    header[data-testid="stHeader"] button,
    header[data-testid="stHeader"] a,
    [data-testid="stToolbar"] button,
    [data-testid="stToolbar"] svg {
        background-color: rgba(255, 255, 255, 0.88) !important;
        color: #0F172A !important;
        fill: #0F172A !important;
        border-radius: 8px !important;
    }

    /* Add clean top spacing so main content sits nicely below the 58px puzzle header */
    [data-testid="stAppViewContainer"] .main .block-container {
        padding-top: 4.3rem !important;
    }

    .stApp {
        background: linear-gradient(135deg, #CCFBF1 0%, #EDE9FE 52%, #DBEAFE 100%) !important;
        color: #0F172A !important;
    }

    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F1F5F9 0%, #EDE9FE 55%, #DBEAFE 100%) !important;
        border-right: 1px solid #CBD5E1 !important;
    }

    [data-testid="stSidebar"] * {
        color: #0F172A !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] > div[role="radiogroup"] {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 8px;
        border: 1px solid #CBD5E1;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    }

    [data-testid="stSidebar"] .stRadio > label {
        font-weight: 800 !important;
        font-size: 11px !important;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        color: #0F766E !important;
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

    
    [data-testid="stMain"] .stButton > button {
        background: linear-gradient(135deg, #0F766E 0%, #1E3A8A 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(15, 23, 42, 0.14) !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        box-shadow: 0 3px 10px rgba(30, 58, 138, 0.16) !important;
    }

    [data-testid="stMain"] .stButton > button * {
        color: #FFFFFF !important;
    }

    [data-testid="stMain"] .stButton > button:hover {
        filter: brightness(1.08);
    }

    [data-testid="stMain"] .stButton > button:disabled {
        background: #E2E8F0 !important;
        color: #64748B !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: none !important;
        opacity: 1 !important;
    }

    [data-testid="stMain"] .stButton > button:disabled * {
        color: #64748B !important;
    }

    [data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F766E 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    @media (max-width: 768px) {
        .kpi-tile-teal, .kpi-tile-navy, .kpi-tile-lavender {
            margin-bottom: 8px;
            padding: 12px 14px;
        }
        .kpi-value {
            font-size: 24px;
        }
        .brand-header {
            gap: 10px;
        }
        .section-title {
            font-size: 15px;
        }
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
        "options": [
            {
                "rank": "1st Option • Best Match",
                "centre": "NASOM Malaysia - Kota Bharu",
                "district": "KOTA BHARU",
                "zone": "Green Zone",
                "badge_bg": "#0D9488",
                "therapists": "Speech-Language Pathologists (SLP), Occupational Therapists (OT), ABA Therapists, Special Educators",
                "reason": "Highest specialist availability and structured therapy programs in Kelantan.",
            },
            {
                "rank": "2nd Option • Nearby Hub",
                "centre": "Wakaf Bharu Care & Intervention Hub",
                "district": "WAKAF BHARU",
                "zone": "Red Zone",
                "badge_bg": "#BE123C",
                "therapists": "Occupational Therapy Practitioners, Daily Living Skills Coaches, Sensory Facilitators",
                "reason": "Convenient nearby option for daily living routines and sensory regulation.",
            },
            {
                "rank": "3rd Option • Outreach Support",
                "centre": "Bachok Autism Outreach Clinic",
                "district": "BACHOK",
                "zone": "Yellow Zone",
                "badge_bg": "#D97706",
                "therapists": "Early Intervention Specialists, Speech Therapy Support, Behavioral Coaches",
                "reason": "Accessible secondary outreach centre for ongoing speech and behavioral support.",
            },
        ],
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
        "options": [
            {
                "rank": "1st Option • Local Priority",
                "centre": "Bachok Autism Outreach Clinic",
                "district": "BACHOK",
                "zone": "Yellow Zone",
                "badge_bg": "#D97706",
                "therapists": "Early Intervention Specialists, Speech Therapy Support, Behavioral Coaches",
                "reason": "Closest local option in Bachok to reduce travel fatigue and keep daily routines steady.",
            },
            {
                "rank": "2nd Option • Specialist Hub",
                "centre": "NASOM Malaysia - Kota Bharu",
                "district": "KOTA BHARU",
                "zone": "Green Zone",
                "badge_bg": "#0D9488",
                "therapists": "Speech-Language Pathologists (SLP), Occupational Therapists (OT), ABA Therapists, Special Educators",
                "reason": "Full multidisciplinary therapy team when specialized SLP/OT/ABA sessions are needed.",
            },
            {
                "rank": "3rd Option • Southern Alternative",
                "centre": "Pasir Puteh Special Needs Center",
                "district": "PASIR PUTEH",
                "zone": "Red Zone",
                "badge_bg": "#BE123C",
                "therapists": "Developmental Therapists, Motor & Play Specialists, Caregiver Counselors",
                "reason": "Additional developmental and play-based support option along the southern route.",
            },
        ],
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
        "options": [
            {
                "rank": "1st Option • Local Priority",
                "centre": "Pasir Mas Early Intervention Centre",
                "district": "PASIR MAS",
                "zone": "Yellow Zone",
                "badge_bg": "#D97706",
                "therapists": "Early Childhood Special Educators, Speech & Language Therapists, Sensory-Motor Therapists",
                "reason": "Provides local early intervention and sensory-motor guidance right in Pasir Mas.",
            },
            {
                "rank": "2nd Option • Border Hub",
                "centre": "Rantau Panjang Autism Support Hub",
                "district": "RANTAU PANJANG",
                "zone": "Yellow Zone",
                "badge_bg": "#D97706",
                "therapists": "Outreach Special Educators, Speech & Communication Coaches, Parent Training Advisors",
                "reason": "Nearby western support hub for outreach educators and caregiver coaching.",
            },
            {
                "rank": "3rd Option • Specialist Hub",
                "centre": "NASOM Malaysia - Kota Bharu",
                "district": "KOTA BHARU",
                "zone": "Green Zone",
                "badge_bg": "#0D9488",
                "therapists": "Speech-Language Pathologists (SLP), Occupational Therapists (OT), ABA Therapists, Special Educators",
                "reason": "Comprehensive specialist hub for intensive therapy escalation.",
            },
        ],
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
        "options": [
            {
                "rank": "1st Option • Closest Local",
                "centre": "Pasir Puteh Special Needs Center",
                "district": "PASIR PUTEH",
                "zone": "Red Zone",
                "badge_bg": "#BE123C",
                "therapists": "Developmental Therapists, Motor & Play Specialists, Caregiver Counselors",
                "reason": "Closest local centre in Pasir Puteh for foundational therapy and family counseling.",
            },
            {
                "rank": "2nd Option • Coastal Option",
                "centre": "Bachok Autism Outreach Clinic",
                "district": "BACHOK",
                "zone": "Yellow Zone",
                "badge_bg": "#D97706",
                "therapists": "Early Intervention Specialists, Speech Therapy Support, Behavioral Coaches",
                "reason": "Secondary option for early intervention and speech support.",
            },
            {
                "rank": "3rd Option • Specialist Hub",
                "centre": "NASOM Malaysia - Kota Bharu",
                "district": "KOTA BHARU",
                "zone": "Green Zone",
                "badge_bg": "#0D9488",
                "therapists": "Speech-Language Pathologists (SLP), Occupational Therapists (OT), ABA Therapists, Special Educators",
                "reason": "Full specialist referral centre when broader therapy bandwidth is needed.",
            },
        ],
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
        "options": [
            {
                "rank": "1st Option • Closest Local",
                "centre": "Wakaf Bharu Care & Intervention Hub",
                "district": "WAKAF BHARU",
                "zone": "Red Zone",
                "badge_bg": "#BE123C",
                "therapists": "Occupational Therapy Practitioners, Daily Living Skills Coaches, Sensory Facilitators",
                "reason": "Local hub focused on daily living skills, sensory routines, and practical carryover.",
            },
            {
                "rank": "2nd Option • Specialist Hub",
                "centre": "NASOM Malaysia - Kota Bharu",
                "district": "KOTA BHARU",
                "zone": "Green Zone",
                "badge_bg": "#0D9488",
                "therapists": "Speech-Language Pathologists (SLP), Occupational Therapists (OT), ABA Therapists, Special Educators",
                "reason": "Nearby specialist hub with SLP, OT, and ABA therapy teams.",
            },
            {
                "rank": "3rd Option • Northern Option",
                "centre": "Tumpat Pediatric Therapy Unit",
                "district": "TUMPAT",
                "zone": "Red Zone",
                "badge_bg": "#BE123C",
                "therapists": "Pediatric Speech Therapists, Play-Based Interventionists, Social Communication Coaches",
                "reason": "Additional pediatric speech and social communication support option.",
            },
        ],
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
        "options": [
            {
                "rank": "1st Option • Closest Local",
                "centre": "Tumpat Pediatric Therapy Unit",
                "district": "TUMPAT",
                "zone": "Red Zone",
                "badge_bg": "#BE123C",
                "therapists": "Pediatric Speech Therapists, Play-Based Interventionists, Social Communication Coaches",
                "reason": "Closest local unit in Tumpat for pediatric speech and play-based communication.",
            },
            {
                "rank": "2nd Option • Nearby Hub",
                "centre": "Wakaf Bharu Care & Intervention Hub",
                "district": "WAKAF BHARU",
                "zone": "Red Zone",
                "badge_bg": "#BE123C",
                "therapists": "Occupational Therapy Practitioners, Daily Living Skills Coaches, Sensory Facilitators",
                "reason": "Nearby option for sensory regulation and daily living coaching.",
            },
            {
                "rank": "3rd Option • Specialist Hub",
                "centre": "NASOM Malaysia - Kota Bharu",
                "district": "KOTA BHARU",
                "zone": "Green Zone",
                "badge_bg": "#0D9488",
                "therapists": "Speech-Language Pathologists (SLP), Occupational Therapists (OT), ABA Therapists, Special Educators",
                "reason": "Main specialist hub for intensive therapy and broader clinical support.",
            },
        ],
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
        "options": [
            {
                "rank": "1st Option • Local Priority",
                "centre": "Rantau Panjang Autism Support Hub",
                "district": "RANTAU PANJANG",
                "zone": "Yellow Zone",
                "badge_bg": "#D97706",
                "therapists": "Outreach Special Educators, Speech & Communication Coaches, Parent Training Advisors",
                "reason": "Reduces travel distance for border families and supports home routines.",
            },
            {
                "rank": "2nd Option • Western Corridor",
                "centre": "Pasir Mas Early Intervention Centre",
                "district": "PASIR MAS",
                "zone": "Yellow Zone",
                "badge_bg": "#D97706",
                "therapists": "Early Childhood Special Educators, Speech & Language Therapists, Sensory-Motor Therapists",
                "reason": "Nearby early intervention and sensory-motor centre in Pasir Mas.",
            },
            {
                "rank": "3rd Option • Specialist Hub",
                "centre": "NASOM Malaysia - Kota Bharu",
                "district": "KOTA BHARU",
                "zone": "Green Zone",
                "badge_bg": "#0D9488",
                "therapists": "Speech-Language Pathologists (SLP), Occupational Therapists (OT), ABA Therapists, Special Educators",
                "reason": "Specialist referral hub for comprehensive SLP, OT, and ABA care.",
            },
        ],
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


def get_parent_kid_phrase(mod_key: str, page_idx: int) -> tuple[str, str]:
    phrases = {
        "AG": [
            ("Parent Shows Cue", "Child Sees: Time for Toilet & Wash"),
            ("Parent Holds Card", "Child Sees: 'Time for toilet.'"),
            ("Parent Guides Steps", "Child Sees: Soap, Rinse & Dry"),
            ("Parent Cheers Effort", "Child Sees: Great Job! ✓"),
        ],
        "AH": [
            ("Parent Sets Routine", "Child Sees: Calm Morning Steps"),
            ("Parent Gives Countdown", "Child Sees: 3... 2... 1... Ready"),
            ("Parent Shows Board", "Child Sees: FIRST Bag → THEN Play"),
            ("Parent Welcomes Calmly", "Child Sees: Safe & Settled Here"),
        ],
        "AI": [
            ("Parent Leads Walk", "Child Sees: Gentle Morning Walk"),
            ("Parent Checks Noise", "Child Sees: Quiet Corner / Ear Cue"),
            ("Parent Models Breath", "Child Sees: Slow Breath & Reset"),
            ("Parent Praises Calm", "Child Sees: Ready to Learn!"),
        ],
        "SK": [
            ("Parent Offers Card", "Child Sees: Picture Card Choice"),
            ("Parent Receives Card", "Child Sees: Kid Gives Card → Gets Item"),
            ("Parent Models Word", "Child Sees: Clear Word + Picture"),
            ("Parent Practices Daily", "Child Sees: Easy Everyday Asking"),
        ],
    }
    mod_list = phrases.get(mod_key, phrases["AG"])
    return mod_list[page_idx % len(mod_list)]


def module_animated_scene_svg(mod_key: str, accent: str, page_idx: int = 0) -> str:
    parent_act, kid_phrase = get_parent_kid_phrase(mod_key, page_idx)
    p_esc = html.escape(parent_act)
    k_esc = html.escape(kid_phrase)

    if mod_key == "AG":
        action_art = """
        <g class="card-pulse">
          <rect x="126" y="40" width="68" height="50" rx="9" fill="#FFFFFF" stroke="#0F766E" stroke-width="2.5"/>
          <path d="M153 49 Q160 41 167 49 Q167 59 160 64 Q153 59 153 49 Z" fill="#1E3A8A"/>
          <rect x="134" y="70" width="52" height="12" rx="6" fill="#CCFBF1"/>
          <text x="160" y="79" text-anchor="middle" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="7.5" font-weight="800" fill="#0F766E">TOILET & WASH</text>
        </g>
        """
        bg_fill, floor_fill, parent_shirt, kid_shirt = "#CCFBF1", "#99F6E4", "#1E3A8A", "#0D9488"
    elif mod_key == "AH":
        action_art = """
        <g class="card-pulse">
          <rect x="118" y="38" width="84" height="52" rx="9" fill="#FFFFFF" stroke="#1E3A8A" stroke-width="2.5"/>
          <text x="160" y="54" text-anchor="middle" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="8" font-weight="800" fill="#1E3A8A">FIRST: BAG</text>
          <path d="M154 61 L164 61" stroke="#6D28D9" stroke-width="2.5" stroke-linecap="round"/>
          <polygon points="163,57 170,61 163,65" fill="#6D28D9"/>
          <text x="160" y="78" text-anchor="middle" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="8" font-weight="800" fill="#6D28D9">THEN: PLAY</text>
        </g>
        """
        bg_fill, floor_fill, parent_shirt, kid_shirt = "#DBEAFE", "#BFDBFE", "#1E3A8A", "#0D9488"
    elif mod_key == "AI":
        action_art = """
        <g class="card-pulse">
          <rect x="122" y="38" width="76" height="52" rx="9" fill="#FFFFFF" stroke="#0D9488" stroke-width="2.5"/>
          <circle cx="145" cy="60" r="10" fill="#CCFBF1" stroke="#0F766E" stroke-width="2"/>
          <path d="M141 60 Q145 55 149 60 Q145 65 141 60 Z" fill="#0F766E"/>
          <text x="172" y="58" text-anchor="middle" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="7.5" font-weight="800" fill="#0F172A">CALM</text>
          <text x="172" y="69" text-anchor="middle" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="7.5" font-weight="800" fill="#0F766E">WALK</text>
          <rect x="130" y="75" width="60" height="10" rx="5" fill="#EDE9FE"/>
          <text x="160" y="83" text-anchor="middle" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="6.8" font-weight="700" fill="#5B21B6">BREATHE & GO</text>
        </g>
        """
        bg_fill, floor_fill, parent_shirt, kid_shirt = "#CCFBF1", "#5EEAD4", "#0F766E", "#1E3A8A"
    else:
        action_art = """
        <g class="card-pulse">
          <rect x="120" y="38" width="80" height="52" rx="9" fill="#FFFFFF" stroke="#6D28D9" stroke-width="2.5"/>
          <text x="160" y="55" text-anchor="middle" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="7.5" font-weight="800" fill="#6D28D9">PECS PHRASE</text>
          <rect x="128" y="61" width="64" height="18" rx="6" fill="#EDE9FE"/>
          <text x="160" y="73" text-anchor="middle" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="8" font-weight="800" fill="#1E3A8A">"I WANT..."</text>
        </g>
        """
        bg_fill, floor_fill, parent_shirt, kid_shirt = "#EDE9FE", "#DDD6FE", "#6D28D9", "#0D9488"

    return f"""
    <style>
      @keyframes parentShow {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-4px); }} }}
      @keyframes kidNotice {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} }}
      @keyframes phrasePop {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-3px); }} }}
      .parent-anim {{ animation: parentShow 2.2s ease-in-out infinite; }}
      .kid-anim {{ animation: kidNotice 2.2s ease-in-out infinite; transform-origin: 256px 76px; }}
      .card-pulse {{ animation: phrasePop 2s ease-in-out infinite; }}
    </style>
    <rect x="0" y="0" width="320" height="164" rx="14" fill="{bg_fill}"/>
    <rect x="0" y="122" width="320" height="42" fill="{floor_fill}"/>
    <rect x="14" y="8" width="292" height="22" rx="11" fill="#0F172A"/>
    <text x="160" y="22" text-anchor="middle" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="9.5" font-weight="700" fill="#FFFFFF">
      {p_esc}  •  {k_esc}
    </text>
    <g class="parent-anim">
      <circle cx="62" cy="62" r="17" fill="#FDBA74" stroke="#0F172A" stroke-width="2.2"/>
      <path d="M46 57 Q62 40 78 57 Q70 49 62 50 Q54 49 46 57 Z" fill="#0F172A"/>
      <circle cx="57" cy="61" r="2.2" fill="#0F172A"/>
      <circle cx="67" cy="61" r="2.2" fill="#0F172A"/>
      <path d="M58 68 Q62 72 66 68" fill="none" stroke="#0F172A" stroke-width="2" stroke-linecap="round"/>
      <rect x="46" y="81" width="32" height="36" rx="10" fill="{parent_shirt}"/>
      <path d="M78 90 L116 70" stroke="#FDBA74" stroke-width="6.5" stroke-linecap="round"/>
      <circle cx="116" cy="70" r="4.5" fill="#FDBA74" stroke="#0F172A" stroke-width="1.5"/>
    </g>
    {action_art}
    <path d="M204 66 L224 66" stroke="#0F172A" stroke-width="2.8" stroke-linecap="round"/>
    <polygon points="222,61 232,66 222,71" fill="#0F172A"/>
    <g class="kid-anim">
      <circle cx="258" cy="70" r="15" fill="#FDBA74" stroke="#0F172A" stroke-width="2.2"/>
      <path d="M244 65 Q258 50 272 65 Q265 58 258 59 Q251 58 244 65 Z" fill="#1E293B"/>
      <circle cx="253" cy="69" r="2.2" fill="#0F172A"/>
      <circle cx="263" cy="69" r="2.2" fill="#0F172A"/>
      <circle cx="258" cy="76" r="3" fill="#0F172A"/>
      <rect x="245" y="87" width="26" height="30" rx="9" fill="{kid_shirt}"/>
    </g>
    <rect x="24" y="131" width="272" height="24" rx="8" fill="#FFFFFF" stroke="{accent}" stroke-width="1.5"/>
    <text x="160" y="147" text-anchor="middle" font-family="Plus Jakarta Sans, Arial, sans-serif" font-size="10" font-weight="800" fill="#0F172A">
      Kid Sees: {k_esc}
    </text>
    """


def module_animated_html(mod_key: str, accent: str, soft_bg: str, page_idx: int) -> str:
    parent_act, kid_phrase = get_parent_kid_phrase(mod_key, page_idx)
    scene = module_animated_scene_svg(mod_key, accent, page_idx)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<style>
  html, body {{ margin: 0; padding: 0; background: transparent; font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif; }}
  .wrap {{ background: {soft_bg}; border: 1.5px solid {accent}44; border-radius: 14px; padding: 8px; box-sizing: border-box; }}
  .caption {{ margin-top: 6px; font-size: 11px; font-weight: 700; color: #0F172A; text-align: center; line-height: 1.35; word-break: break-word; }}
</style>
</head>
<body>
  <div class="wrap">
    <svg viewBox="0 0 320 164" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;height:auto;max-height:152px;border-radius:12px;">
      {scene}
    </svg>
    <div class="caption">{html.escape(parent_act)} → {html.escape(kid_phrase)} (Page {page_idx + 1})</div>
  </div>
</body>
</html>
"""


def build_flipbook_html(mod: dict) -> str:
    title_esc = html.escape(f"{mod['code']}: {mod['title']}")
    domain_esc = html.escape(mod["domain"])
    accent = mod["color"]
    soft_bg = mod["soft_bg"]

    scenes_js_items = []
    for idx_p, (p_title, p_summary, p_steps) in enumerate(mod["pages"]):
        p_act, k_phr = get_parent_kid_phrase(mod["key"], idx_p)
        svg_p = module_animated_scene_svg(mod["key"], accent, idx_p)
        scenes_js_items.append(
            "{"
            f'"heading": "{html.escape(p_title)}", '
            f'"summary": "{html.escape(p_summary)}", '
            f'"steps": "{html.escape(p_steps).replace(chr(10), "<br>")}", '
            f'"badge": "{html.escape(p_act)} → {html.escape(k_phr)} (Page {idx_p + 1})", '
            f'"svg": {json.dumps(svg_p)}'
            "}"
        )
    pages_json = "[" + ", ".join(scenes_js_items) + "]"

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
    margin: 0; padding: 28px; color: #0F172A; display: flex; justify-content: center;
  }}
  .book-shell {{
    max-width: 720px; width: 100%; background: #FFFFFF; border-radius: 18px; padding: 26px;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08); border-top: 8px solid {accent};
  }}
  .top-tag {{ display: inline-block; background: {accent}; color: #FFFFFF; font-weight: 700; font-size: 12px; padding: 5px 12px; border-radius: 999px; }}
  h1 {{ margin: 10px 0 4px 0; font-size: 24px; }}
  .domain {{ color: #475569; font-size: 14px; margin-bottom: 16px; }}
  .anim-card {{ background: {soft_bg}; border: 1.5px solid {accent}44; border-radius: 14px; padding: 12px; }}
  .anim-caption {{ margin-top: 8px; font-size: 12.5px; font-weight: 700; color: #0F172A; text-align: center; }}
  .page-box {{ background: {soft_bg}; border-radius: 14px; padding: 20px; margin-top: 16px; min-height: 170px; }}
  .page-heading {{ font-size: 18px; font-weight: 700; margin-bottom: 8px; }}
  .page-summary {{ font-size: 15px; margin-bottom: 12px; line-height: 1.5; }}
  .page-steps {{ background: #FFFFFF; padding: 14px 16px; border-radius: 10px; line-height: 1.65; font-size: 14px; }}
  .controls {{ display: flex; justify-content: space-between; align-items: center; margin-top: 20px; gap: 12px; }}
  button {{ background: {accent}; color: #FFFFFF; border: none; padding: 10px 18px; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; }}
  button:disabled {{ background: #CBD5E1; cursor: not-allowed; }}
  .indicator {{ font-weight: 700; color: #334155; }}
</style>
</head>
<body>
  <div class="book-shell">
    <span class="top-tag">INTERACTIVE FLIPBOOK</span>
    <h1>{title_esc}</h1>
    <div class="domain">Focus Domain: {domain_esc}</div>
    <div class="anim-card">
      <svg id="animSvg" viewBox="0 0 320 164" width="100%" height="180" xmlns="http://www.w3.org/2000/svg" style="display:block;border-radius:12px;"></svg>
      <div class="anim-caption" id="animCaption"></div>
    </div>
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
    document.getElementById("animSvg").innerHTML = p.svg;
    document.getElementById("animCaption").innerText = p.badge;
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



def kelantan_interactive_map_html(dist_records: list[dict], selected_district: str = "KOTA BHARU", mode_label: str = "Kelantan District Coverage & Centres") -> str:
    d_json = json.dumps(dist_records)
    sel_esc = html.escape(selected_district)
    mode_esc = html.escape(mode_label)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html, body {{
    margin: 0; padding: 0; background: transparent;
    font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif;
    color: #0F172A;
  }}
  .map-card {{
    background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 16px;
    padding: 14px 16px; box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
  }}
  .map-header {{
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 8px; margin-bottom: 10px;
  }}
  .map-title {{ font-size: 15.5px; font-weight: 800; color: #0F172A; }}
  .map-sub {{ font-size: 12px; color: #475569; }}
  #kelantanMap {{
    width: 100%; height: 320px; border-radius: 12px; border: 1px solid #CBD5E1; z-index: 1;
  }}
  .legend-row {{
    display: flex; gap: 14px; flex-wrap: wrap; margin-top: 10px;
    font-size: 12px; font-weight: 700; color: #334155;
  }}
  .lg-item {{ display: flex; align-items: center; gap: 6px; }}
  .lg-dot {{ width: 12px; height: 12px; border-radius: 999px; display: inline-block; }}
</style>
</head>
<body>
  <div class="map-card">
    <div class="map-header">
      <div>
        <div class="map-title">{mode_esc}</div>
        <div class="map-sub">Highlighted district: <strong>{sel_esc}</strong> • Click any circle marker to inspect exact student & centre count</div>
      </div>
    </div>
    <div id="kelantanMap"></div>
    <div class="legend-row">
      <div class="lg-item"><span class="lg-dot" style="background:#0D9488;"></span>Green Zone (Higher Centre Coverage)</div>
      <div class="lg-item"><span class="lg-dot" style="background:#D97706;"></span>Yellow Zone (Moderate Coverage)</div>
      <div class="lg-item"><span class="lg-dot" style="background:#BE123C;"></span>Red Zone (High Deficit / Priority)</div>
    </div>
  </div>
<script>
  const districts = {d_json};
  const selectedName = {json.dumps(selected_district)};
  const map = L.map('kelantanMap').setView([6.05, 102.22], 10);

  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap contributors'
  }}).addTo(map);

  districts.forEach(d => {{
    const isSelected = d.district === selectedName;
    const fillCol = d.zone === "Green Zone" ? "#0D9488" : (d.zone === "Yellow Zone" ? "#D97706" : "#BE123C");
    const radius = Math.max(11, Math.min(26, 8 + d.students * 0.9));

    const circle = L.circleMarker([d.lat, d.lon], {{
      radius: radius,
      fillColor: fillCol,
      color: isSelected ? "#0F172A" : "#FFFFFF",
      weight: isSelected ? 3.5 : 2,
      opacity: 1,
      fillOpacity: 0.86
    }}).addTo(map);

    circle.bindPopup(
      `<div style="font-family:sans-serif;font-size:12.5px;line-height:1.45;">
        <strong>${{d.district}}</strong><br/>
        Zone: <strong>${{d.zone}}</strong><br/>
        Students: <strong>${{d.students}}</strong> • Centres: <strong>${{d.centres}}</strong><br/>
        1st Option: <strong>${{d.recommended_centre}}</strong>
      </div>`
    );

    if (isSelected) {{
      circle.openPopup();
    }}
  }});
</script>
</body>
</html>
"""


def animated_admin_charts_html(dist_records: list[dict], diag_records: list[dict], serv_records: list[dict]) -> str:
    d_json = json.dumps(dist_records)
    g_json = json.dumps(diag_records)
    s_json = json.dumps(serv_records)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<style>
  html, body {{
    margin: 0; padding: 0; background: transparent;
    font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif;
    color: #0F172A;
  }}
  .grid-top {{
    display: grid; grid-template-columns: 1.45fr 1fr; gap: 14px; margin-bottom: 14px;
  }}
  @media (max-width: 768px) {{
    .grid-top {{ grid-template-columns: 1fr; }}
    .card {{ padding: 12px 14px; }}
    .donut-wrap {{ justify-content: center; }}
  }}
  .card {{
    background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 16px;
    padding: 16px 18px; box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
  }}
  .title {{ font-size: 16px; font-weight: 800; color: #0F172A; margin: 0 0 2px 0; }}
  .sub {{ font-size: 12.5px; color: #475569; margin: 0 0 12px 0; }}
  @keyframes growBar {{
    from {{ transform: scaleY(0); }}
    to {{ transform: scaleY(1); }}
  }}
  @keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}
  .bar-anim {{
    transform-box: fill-box;
    transform-origin: bottom;
    animation: growBar 0.85s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  }}
  .label-anim {{
    opacity: 0;
    animation: fadeUp 0.65s ease forwards;
    animation-delay: 0.35s;
  }}
  .donut-wrap {{
    display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  }}
  .legend-list {{
    display: flex; flex-direction: column; gap: 8px; font-size: 13px; font-weight: 700;
  }}
  .legend-item {{
    display: flex; align-items: center; gap: 8px;
  }}
  .dot {{
    width: 12px; height: 12px; border-radius: 999px; flex-shrink: 0;
  }}
  .tooltip-box {{
    margin-top: 8px; font-size: 12px; font-weight: 700; color: #0F766E; min-height: 18px;
  }}
</style>
</head>
<body>
  <div class="grid-top">
    <div class="card">
      <div class="title">Students Across Kelantan Districts</div>
      <div class="sub">Exact animated student count per district (hover any bar for details)</div>
      <svg id="distChart" viewBox="0 0 560 235" width="100%" style="height:auto;max-height:245px;display:block;"></svg>
      <div class="tooltip-box" id="distTip">Hover a district bar to inspect exact student & centre count</div>
    </div>

    <div class="card">
      <div class="title">Diagnosis Breakdown</div>
      <div class="sub">Exact count and share of registered autism profiles</div>
      <div class="donut-wrap">
        <svg id="diagChart" viewBox="0 0 190 190" width="160" style="height:auto;max-width:175px;flex-shrink:0;"></svg>
        <div class="legend-list" id="diagLegend"></div>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="title">Required Therapy Services Demand</div>
    <div class="sub">Clear animated count of students requiring each intervention service</div>
    <svg id="servChart" viewBox="0 0 880 185" width="100%" style="height:auto;max-height:200px;display:block;"></svg>
  </div>

<script>
  const distData = {d_json};
  const diagData = {g_json};
  const servData = {s_json};

  // 1. District Bar Chart with exact integers & gridlines
  (function renderDist() {{
    const svg = document.getElementById("distChart");
    const tip = document.getElementById("distTip");
    const maxVal = Math.max(16, ...distData.map(d => d.students));
    const padL = 38, padR = 16, padT = 26, padB = 38;
    const plotW = 560 - padL - padR;
    const plotH = 235 - padT - padB;
    let htmlStr = "";

    for (let g = 0; g <= 4; g++) {{
      const val = Math.round((maxVal / 4) * g);
      const y = padT + plotH - (val / maxVal) * plotH;
      htmlStr += `<line x1="${{padL}}" y1="${{y}}" x2="${{560 - padR}}" y2="${{y}}" stroke="#E2E8F0" stroke-width="1"/>`;
      htmlStr += `<text x="${{padL - 8}}" y="${{y + 4}}" text-anchor="end" font-size="11" font-weight="700" fill="#475569">${{val}}</text>`;
    }}

    const step = plotW / distData.length;
    const barW = Math.min(46, step * 0.56);
    distData.forEach((d, i) => {{
      const h = (d.students / maxVal) * plotH;
      const x = padL + i * step + (step - barW) / 2;
      const y = padT + plotH - h;
      const fill = d.zone === "Green Zone" ? "#0D9488" : (d.zone === "Yellow Zone" ? "#1E3A8A" : "#6D28D9");
      htmlStr += `<rect class="bar-anim" x="${{x}}" y="${{y}}" width="${{barW}}" height="${{h}}" rx="7" fill="${{fill}}" style="animation-delay:${{(i * 0.07).toFixed(2)}}s;cursor:pointer;" onmouseenter="document.getElementById('distTip').innerText='${{d.district}}: ${{d.students}} students • ${{d.centres}} centres (${{d.zone}})'"/>`;
      htmlStr += `<text class="label-anim" x="${{x + barW / 2}}" y="${{y - 6}}" text-anchor="middle" font-size="12" font-weight="800" fill="#0F172A">${{d.students}}</text>`;
      htmlStr += `<text x="${{x + barW / 2}}" y="${{padT + plotH + 17}}" text-anchor="middle" font-size="9.5" font-weight="800" fill="#0F172A">${{d.short}}</text>`;
    }});
    svg.innerHTML = htmlStr;
  }})();

  // 2. Diagnosis Donut Chart with exact values
  (function renderDiag() {{
    const svg = document.getElementById("diagChart");
    const leg = document.getElementById("diagLegend");
    const total = diagData.reduce((acc, item) => acc + item.count, 0) || 1;
    const colors = ["#0D9488", "#1E3A8A", "#6D28D9"];
    const cx = 95, cy = 95, r = 64, strokeW = 24;
    const circ = 2 * Math.PI * r;
    let offset = 0;
    let arcs = `<circle cx="${{cx}}" cy="${{cy}}" r="${{r}}" fill="none" stroke="#F1F5F9" stroke-width="${{strokeW}}"/>`;
    let legendHtml = "";

    diagData.forEach((item, idx) => {{
      const frac = item.count / total;
      const dash = frac * circ;
      const col = colors[idx % colors.length];
      arcs += `<circle cx="${{cx}}" cy="${{cy}}" r="${{r}}" fill="none" stroke="${{col}}" stroke-width="${{strokeW}}" stroke-dasharray="${{dash}} ${{circ}}" stroke-dashoffset="${{-offset}}" transform="rotate(-90 ${{cx}} ${{cy}})"/>`;
      offset += dash;
      const pct = Math.round(frac * 100);
      legendHtml += `<div class="legend-item"><span class="dot" style="background:${{col}};"></span><span>${{item.label}}: <strong>${{item.count}}</strong> (${{pct}}%)</span></div>`;
    }});

    arcs += `<text x="${{cx}}" y="${{cy - 2}}" text-anchor="middle" font-size="18" font-weight="800" fill="#0F172A">${{total}}</text>`;
    arcs += `<text x="${{cx}}" y="${{cy + 15}}" text-anchor="middle" font-size="10" font-weight="700" fill="#475569">TOTAL</text>`;
    svg.innerHTML = arcs;
    leg.innerHTML = legendHtml;
  }})();

  // 3. Service Demand Chart with exact counts
  (function renderServ() {{
    const svg = document.getElementById("servChart");
    const maxVal = Math.max(30, ...servData.map(s => s.students));
    const padL = 42, padR = 20, padT = 24, padB = 34;
    const plotW = 880 - padL - padR;
    const plotH = 185 - padT - padB;
    const palette = ["#0F766E", "#1E3A8A", "#6D28D9", "#0D9488"];
    let htmlStr = "";

    for (let g = 0; g <= 3; g++) {{
      const val = Math.round((maxVal / 3) * g);
      const y = padT + plotH - (val / maxVal) * plotH;
      htmlStr += `<line x1="${{padL}}" y1="${{y}}" x2="${{880 - padR}}" y2="${{y}}" stroke="#E2E8F0" stroke-width="1"/>`;
      htmlStr += `<text x="${{padL - 8}}" y="${{y + 4}}" text-anchor="end" font-size="11" font-weight="700" fill="#475569">${{val}}</text>`;
    }}

    const step = plotW / servData.length;
    const barW = Math.min(90, step * 0.45);
    servData.forEach((s, i) => {{
      const h = (s.students / maxVal) * plotH;
      const x = padL + i * step + (step - barW) / 2;
      const y = padT + plotH - h;
      const col = palette[i % palette.length];
      htmlStr += `<rect class="bar-anim" x="${{x}}" y="${{y}}" width="${{barW}}" height="${{h}}" rx="8" fill="${{col}}" style="animation-delay:${{(i * 0.1).toFixed(2)}}s;"/>`;
      htmlStr += `<text class="label-anim" x="${{x + barW / 2}}" y="${{y - 6}}" text-anchor="middle" font-size="12.5" font-weight="800" fill="#0F172A">${{s.students}}</text>`;
      htmlStr += `<text x="${{x + barW / 2}}" y="${{padT + plotH + 18}}" text-anchor="middle" font-size="11" font-weight="800" fill="#0F172A">${{s.service}}</text>`;
    }});
    svg.innerHTML = htmlStr;
  }})();
</script>
</body>
</html>
"""


def animated_centre_options_html(child_name: str, age: int, district: str, diagnosis: str, service: str, options: list[dict]) -> str:
    c_esc = html.escape(child_name.strip() or "Child")
    d_esc = html.escape(district)
    g_esc = html.escape(diagnosis)
    s_esc = html.escape(service)

    cards_html = ""
    for idx, opt in enumerate(options):
        delay = idx * 0.18
        cards_html += f"""
        <div class="pop-card" style="animation-delay:{delay:.2f}s;border-top:6px solid {opt['badge_bg']};">
          <div class="rank-pill" style="background:{opt['badge_bg']};">{html.escape(opt['rank'])}</div>
          <div class="centre-name">{html.escape(opt['centre'])}</div>
          <div class="meta-line"><strong>District:</strong> {html.escape(opt['district'])} • <span style="color:{opt['badge_bg']};">{html.escape(opt['zone'])}</span></div>
          <div class="meta-line"><strong>Therapists:</strong> {html.escape(opt['therapists'])}</div>
          <div class="reason-box">{html.escape(opt['reason'])}</div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<style>
  html, body {{
    margin: 0; padding: 0; background: transparent;
    font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif;
    color: #0F172A;
  }}
  @keyframes popInOption {{
    0% {{ opacity: 0; transform: translateY(22px) scale(0.95); }}
    70% {{ opacity: 1; transform: translateY(-4px) scale(1.01); }}
    100% {{ opacity: 1; transform: translateY(0) scale(1); }}
  }}
  .banner {{
    background: linear-gradient(135deg, #0F766E 0%, #1E3A8A 60%, #6D28D9 100%);
    color: #FFFFFF; border-radius: 14px; padding: 12px 16px; margin-bottom: 14px;
    font-size: 13px; font-weight: 700;
  }}
  .options-grid {{
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;
  }}
  .pop-card {{
    opacity: 0;
    animation: popInOption 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 14px;
    padding: 14px; box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
    display: flex; flex-direction: column; gap: 8px;
  }}
  .rank-pill {{
    display: inline-block; align-self: flex-start; color: #FFFFFF;
    font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 999px;
  }}
  .centre-name {{ font-size: 15.5px; font-weight: 800; color: #0F172A; line-height: 1.25; }}
  .meta-line {{ font-size: 12px; color: #334155; line-height: 1.4; }}
  .reason-box {{
    margin-top: auto; background: #F8FAFC; border: 1px solid #E2E8F0;
    border-radius: 10px; padding: 9px 10px; font-size: 12px; color: #0F172A; line-height: 1.45;
  }}
  @media (max-width: 780px) {{
    .options-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
  <div class="banner">
    Recommended Centres for <strong>{c_esc}</strong> (Age {age}) • {d_esc} • {g_esc} • {s_esc}
  </div>
  <div class="options-grid">
    {cards_html}
  </div>
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

if "parent_submitted_profile" not in st.session_state:
    st.session_state["parent_submitted_profile"] = {
        "kid_name": "Aisyah Humaira",
        "age": 6,
        "district": "KOTA BHARU",
        "diagnosis": "Mild Autism",
        "service": "Speech Therapy",
    }

for mod in MODULES_4:
    p_key = f"flip_page_{mod['key']}"
    if p_key not in st.session_state:
        st.session_state[p_key] = 0

df_students = st.session_state["student_df"].copy()

# Sidebar styled cleanly in light pill/rail aesthetic with teal/navy/lavender accents
st.sidebar.markdown(
    """
    <div style="text-align:center;padding:6px 0 12px 0;">
        <div style="width:54px;height:54px;margin:0 auto 6px auto;border-radius:999px;background:linear-gradient(135deg,#0D9488 0%,#1E3A8A 65%,#6D28D9 100%);color:#FFFFFF;font-size:22px;font-weight:800;display:flex;align-items:center;justify-content:center;box-shadow:0 6px 14px rgba(15,23,42,0.16);">
            KA
        </div>
        <div style="font-size:13px;font-weight:800;color:#0F172A;">Kelantan GIS</div>
        <div style="font-size:10px;font-weight:700;letter-spacing:1px;color:#0F766E;">ADMIN & PARENTS</div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "PORTAL & MODULES",
    [
        "Admin Dashboard",
        "Parents Portal",
        "Student Registry",
        "4 Flipbook Modules",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="font-size:11px;font-weight:700;color:#475569;line-height:1.5;">
        • <strong>Admin Dashboard:</strong> Accurate counts & animated charts<br>
        • <strong>Parents Portal:</strong> Child form + 1st/2nd/3rd centre pop-up<br>
        • <strong>Student Registry:</strong> Add & edit student records<br>
        • <strong>4 Flipbook Modules:</strong> Parent shows → Kid sees
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# PAGE 1: ADMIN DASHBOARD (ACCURATE COUNTS + ANIMATED GRAPHS)
# ==============================================================================
if page == "Admin Dashboard":
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
                        <div style="font-size:11px;font-weight:700;letter-spacing:0.6px;color:#0F766E;">ADMIN ANALYTICS PORTAL</div>
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
                st.markdown('<div class="section-title">Registry & Zone Overview</div>', unsafe_allow_html=True)
                st.markdown('<div class="section-sub">Exact counts across Kelantan districts, diagnoses, and therapy needs</div>', unsafe_allow_html=True)
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

    short_names = {
        "KOTA BHARU": "K.BHARU",
        "BACHOK": "BACHOK",
        "PASIR MAS": "P.MAS",
        "PASIR PUTEH": "P.PUTEH",
        "WAKAF BHARU": "W.BHARU",
        "TUMPAT": "TUMPAT",
        "RANTAU PANJANG": "R.PANJANG",
    }

    dist_records = []
    for d_name, info in DISTRICT_INFO.items():
        cnt = int((df_students["District"] == d_name).sum())
        dist_records.append({
            "district": d_name,
            "short": short_names.get(d_name, d_name[:8]),
            "students": cnt,
            "centres": info["centres"],
            "zone": info["zone"],
            "lat": info["lat"],
            "lon": info["lon"],
            "recommended_centre": info["recommended_centre"],
        })

    diag_order = ["Mild Autism", "High-Function Autism", "Severe Autism"]
    diag_records = [
        {"label": g, "count": int((df_students["Diagnosis"] == g).sum())}
        for g in diag_order
    ]

    serv_order = ["Speech Therapy", "ABA Therapy", "Occupational Sensory", "Early Intervention"]
    serv_records = [
        {"service": s, "students": int((df_students["Required Service"] == s).sum())}
        for s in serv_order
    ]

    components.html(
        animated_admin_charts_html(dist_records, diag_records, serv_records),
        height=760,
        scrolling=False,
    )

    with st.container(border=True):
        st.markdown('<div class="section-title">District Zone & Centre Inspector</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Select any district to inspect exact student count, zone status, and therapy options</div>', unsafe_allow_html=True)
        selected_dist = st.selectbox(
            "Select District",
            options=list(DISTRICT_INFO.keys()),
            index=list(DISTRICT_INFO.keys()).index(st.session_state["selected_zone_district"]),
            label_visibility="collapsed",
        )
        st.session_state["selected_zone_district"] = selected_dist
        d_info = DISTRICT_INFO[selected_dist]
        d_count = int((df_students["District"] == selected_dist).sum())

        st.markdown(
            f'<span class="zone-pill" style="background:{d_info["badge_bg"]};">{d_info["zone"]}</span> '
            f'<strong style="color:#0F172A;">{selected_dist}</strong> — <strong>{d_count}</strong> students • <strong>{d_info["centres"]}</strong> centres',
            unsafe_allow_html=True,
        )
        st.write(d_info["place_summary"])
        st.markdown(f"**1st Choice Centre:** {d_info['recommended_centre']}  |  **Therapists:** {d_info['therapists']}")

    components.html(
        kelantan_interactive_map_html(
            dist_records=dist_records,
            selected_district=st.session_state["selected_zone_district"],
            mode_label="Kelantan District Map — Student Load, Zone Status & Centres",
        ),
        height=425,
    )


# ==============================================================================
# PAGE 2: PARENTS PORTAL (CHILD INFO FORM + 1ST, 2ND, 3RD CENTRE POP-UP)
# ==============================================================================
elif page == "Parents Portal":
    with st.container(border=True):
        st.subheader("Parents Portal — Child Details & Suitable Centre Options")
        st.caption("Enter your child's name and details below. When you submit, the 1st, 2nd, and 3rd suitable centres pop up with animation.")

        cur_prof = st.session_state["parent_submitted_profile"]

        with st.form("parents_child_matcher_form"):
            p1, p2, p3 = st.columns(3)
            kid_name_in = p1.text_input("Child's Name", value=cur_prof["kid_name"], placeholder="e.g., Aisyah Humaira")
            kid_age_in = p2.number_input("Child's Age", min_value=1, max_value=21, value=int(cur_prof["age"]))
            kid_dist_in = p3.selectbox(
                "District in Kelantan",
                options=list(DISTRICT_INFO.keys()),
                index=list(DISTRICT_INFO.keys()).index(cur_prof["district"]),
            )

            p4, p5 = st.columns(2)
            kid_diag_in = p4.selectbox(
                "Autism Type / Diagnosis",
                options=["Mild Autism", "High-Function Autism", "Severe Autism"],
                index=["Mild Autism", "High-Function Autism", "Severe Autism"].index(cur_prof["diagnosis"]),
            )
            kid_serv_in = p5.selectbox(
                "Required Therapy Service",
                options=["Speech Therapy", "ABA Therapy", "Occupational Sensory", "Early Intervention"],
                index=["Speech Therapy", "ABA Therapy", "Occupational Sensory", "Early Intervention"].index(cur_prof["service"]),
            )

            submitted = st.form_submit_button("Find Suitable Centres (Pop-Up 1st, 2nd & 3rd Options)", type="primary")
            if submitted:
                st.session_state["parent_submitted_profile"] = {
                    "kid_name": kid_name_in.strip() or "Child",
                    "age": int(kid_age_in),
                    "district": kid_dist_in,
                    "diagnosis": kid_diag_in,
                    "service": kid_serv_in,
                }
                st.rerun()

        active_prof = st.session_state["parent_submitted_profile"]
        d_entry = DISTRICT_INFO[active_prof["district"]]
        components.html(
            animated_centre_options_html(
                child_name=active_prof["kid_name"],
                age=active_prof["age"],
                district=active_prof["district"],
                diagnosis=active_prof["diagnosis"],
                service=active_prof["service"],
                options=d_entry["options"],
            ),
            height=780,
            scrolling=False,
        )

        parent_map_records = []
        for d_name, info in DISTRICT_INFO.items():
            cnt = int((df_students["District"] == d_name).sum())
            parent_map_records.append({
                "district": d_name,
                "short": d_name[:8],
                "students": cnt,
                "centres": info["centres"],
                "zone": info["zone"],
                "lat": info["lat"],
                "lon": info["lon"],
                "recommended_centre": info["recommended_centre"],
            })

        components.html(
            kelantan_interactive_map_html(
                dist_records=parent_map_records,
                selected_district=active_prof["district"],
                mode_label=f"Nearby District Map for {active_prof['kid_name']} ({active_prof['district']})",
            ),
            height=425,
        )


# ==============================================================================
# PAGE 3: STUDENT REGISTRY (EDIT & INSERT)
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
# PAGE 4: 4 INTERACTIVE FLIPBOOK MODULES
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
                components.html(module_animated_html(mod["key"], mod["color"], mod["soft_bg"], cur_page), height=215, scrolling=False)

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
