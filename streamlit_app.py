import html
import json
import math
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Kelantan Autism GIS Healthcare Service Management Platform",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "kelantan_autism_gis.db"
EXPECTED_TOTAL_STUDENTS = 106

KELANTAN_DISTRICTS = [
    "Tumpat",
    "Pasir Mas",
    "Kota Bharu",
    "Pasir Puteh",
    "Machang",
    "Tanah Merah",
    "Kuala Krai",
    "Bachok",
    "Jeli",
    "Gua Musang",
]

THERAPY_SERVICES = [
    "Speech Therapy",
    "ABA Therapy",
    "Occupational Sensory",
    "Early Intervention",
]

DIAGNOSIS_CATEGORIES = [
    "Mild Autism",
    "High-Function Autism",
    "Severe Autism",
]

DISTRICT_CENTROIDS = {
    "Kota Bharu": (6.1254, 102.2381),
    "Bachok": (6.0550, 102.3950),
    "Pasir Mas": (6.0480, 102.1420),
    "Tumpat": (6.1950, 102.1650),
    "Pasir Puteh": (5.8361, 102.4042),
    "Machang": (5.7679, 102.2154),
    "Tanah Merah": (5.8080, 102.1470),
    "Kuala Krai": (5.5308, 102.2019),
    "Jeli": (5.7007, 101.8432),
    "Gua Musang": (4.8843, 101.9644),
}

KELANTAN_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"district": "Tumpat", "code": "MY-03-01"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [102.08, 6.24], [102.23, 6.22], [102.22, 6.13],
                    [102.14, 6.12], [102.08, 6.16], [102.08, 6.24],
                ]],
            },
        },
        {
            "type": "Feature",
            "properties": {"district": "Kota Bharu", "code": "MY-03-02"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [102.23, 6.22], [102.35, 6.17], [102.33, 5.95],
                    [102.21, 5.94], [102.20, 6.04], [102.22, 6.13], [102.23, 6.22],
                ]],
            },
        },
        {
            "type": "Feature",
            "properties": {"district": "Bachok", "code": "MY-03-03"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [102.35, 6.17], [102.44, 6.08], [102.47, 5.94],
                    [102.33, 5.95], [102.35, 6.17],
                ]],
            },
        },
        {
            "type": "Feature",
            "properties": {"district": "Pasir Mas", "code": "MY-03-04"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [101.96, 6.06], [102.08, 6.16], [102.14, 6.12],
                    [102.22, 6.13], [102.20, 6.04], [102.21, 5.94],
                    [102.06, 5.92], [101.96, 5.97], [101.96, 6.06],
                ]],
            },
        },
        {
            "type": "Feature",
            "properties": {"district": "Pasir Puteh", "code": "MY-03-05"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [102.33, 5.95], [102.47, 5.94], [102.52, 5.78],
                    [102.36, 5.74], [102.31, 5.83], [102.33, 5.95],
                ]],
            },
        },
        {
            "type": "Feature",
            "properties": {"district": "Machang", "code": "MY-03-06"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [102.21, 5.94], [102.33, 5.95], [102.31, 5.83],
                    [102.36, 5.74], [102.24, 5.68], [102.18, 5.76],
                    [102.18, 5.86], [102.21, 5.94],
                ]],
            },
        },
        {
            "type": "Feature",
            "properties": {"district": "Tanah Merah", "code": "MY-03-07"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [101.96, 5.97], [102.06, 5.92], [102.21, 5.94],
                    [102.18, 5.86], [102.18, 5.76], [102.04, 5.68],
                    [101.94, 5.77], [101.96, 5.97],
                ]],
            },
        },
        {
            "type": "Feature",
            "properties": {"district": "Jeli", "code": "MY-03-08"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [101.70, 5.86], [101.96, 5.97], [101.94, 5.77],
                    [102.04, 5.68], [101.96, 5.48], [101.73, 5.52],
                    [101.66, 5.68], [101.70, 5.86],
                ]],
            },
        },
        {
            "type": "Feature",
            "properties": {"district": "Kuala Krai", "code": "MY-03-09"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [102.04, 5.68], [102.18, 5.76], [102.24, 5.68],
                    [102.36, 5.74], [102.42, 5.45], [102.28, 5.24],
                    [102.06, 5.26], [101.96, 5.48], [102.04, 5.68],
                ]],
            },
        },
        {
            "type": "Feature",
            "properties": {"district": "Gua Musang", "code": "MY-03-10"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [101.73, 5.52], [101.96, 5.48], [102.06, 5.26],
                    [102.28, 5.24], [102.38, 4.92], [102.26, 4.62],
                    [101.88, 4.56], [101.56, 4.74], [101.52, 5.14],
                    [101.66, 5.42], [101.73, 5.52],
                ]],
            },
        },
    ],
}

INITIAL_CENTRES = [
    {
        "centre_name": "NASOM Malaysia - Kota Bharu",
        "category": "NGO Special Education & Therapy",
        "address": "Lot 1420, Jalan Sultan Yahya Petra, Lundang, 15150 Kota Bharu, Kelantan",
        "district": "Kota Bharu",
        "lat": 6.1135,
        "lon": 102.2542,
        "contact": "+609-748 5120",
        "services": "Speech Therapy, ABA Therapy, Occupational Sensory, Early Intervention",
        "hours": "Sun-Thu: 8:00 AM - 5:00 PM",
        "capacity": 45,
    },
    {
        "centre_name": "Hospital Raja Perempuan Zainab II (Pediatric Rehab)",
        "category": "Government Specialist Hospital",
        "address": "Jalan Hospital, Bandar Kota Bharu, 15586 Kota Bharu, Kelantan",
        "district": "Kota Bharu",
        "lat": 6.1258,
        "lon": 102.2456,
        "contact": "+609-745 2000",
        "services": "Speech Therapy, Occupational Sensory, Early Intervention",
        "hours": "Sun-Thu: 8:00 AM - 4:30 PM",
        "capacity": 60,
    },
    {
        "centre_name": "Hospital Universiti Sains Malaysia (HUSM) Child Development Unit",
        "category": "University Teaching Hospital",
        "address": "Jalan Raja Perempuan Zainab II, Kubang Kerian, 16150 Kota Bharu, Kelantan",
        "district": "Kota Bharu",
        "lat": 6.0998,
        "lon": 102.2835,
        "contact": "+609-767 3000",
        "services": "Speech Therapy, ABA Therapy, Occupational Sensory, Early Intervention",
        "hours": "Sun-Thu: 8:00 AM - 5:00 PM",
        "capacity": 55,
    },
    {
        "centre_name": "PDK Cahaya Harapan Pengkalan Chepa",
        "category": "Community-Based Rehabilitation (PDK)",
        "address": "Kampung Baung, Pengkalan Chepa, 16100 Kota Bharu, Kelantan",
        "district": "Kota Bharu",
        "lat": 6.1582,
        "lon": 102.2891,
        "contact": "+609-773 4118",
        "services": "Early Intervention, Occupational Sensory",
        "hours": "Sun-Thu: 8:30 AM - 3:30 PM",
        "capacity": 30,
    },
    {
        "centre_name": "Bachok Autism & Early Intervention Outreach Centre",
        "category": "Community-Based Rehabilitation (PDK)",
        "address": "Jalan Nipah, Bandar Bachok, 16300 Bachok, Kelantan",
        "district": "Bachok",
        "lat": 6.0584,
        "lon": 102.4012,
        "contact": "+609-778 8240",
        "services": "Early Intervention, Speech Therapy, Occupational Sensory",
        "hours": "Sun-Thu: 8:30 AM - 4:00 PM",
        "capacity": 28,
    },
    {
        "centre_name": "PDK Tembila Melawi Care Centre",
        "category": "Community-Based Rehabilitation (PDK)",
        "address": "Kampung Tembila, Melawi, 16310 Bachok, Kelantan",
        "district": "Bachok",
        "lat": 5.9942,
        "lon": 102.4235,
        "contact": "+609-778 9055",
        "services": "Early Intervention, ABA Therapy",
        "hours": "Sun-Thu: 8:30 AM - 3:30 PM",
        "capacity": 22,
    },
    {
        "centre_name": "Pasir Mas Early Intervention & Therapy Centre",
        "category": "Government Health Clinic Rehab",
        "address": "Jalan Hospital, Bandar Pasir Mas, 17000 Pasir Mas, Kelantan",
        "district": "Pasir Mas",
        "lat": 6.0436,
        "lon": 102.1428,
        "contact": "+609-790 9333",
        "services": "Speech Therapy, Early Intervention, Occupational Sensory",
        "hours": "Sun-Thu: 8:00 AM - 4:30 PM",
        "capacity": 32,
    },
    {
        "centre_name": "Rantau Panjang Border Autism Support Hub",
        "category": "Community-Based Rehabilitation (PDK)",
        "address": "Jalan Besar Rantau Panjang, 17200 Pasir Mas, Kelantan",
        "district": "Pasir Mas",
        "lat": 6.0215,
        "lon": 101.9820,
        "contact": "+609-795 0412",
        "services": "Early Intervention, ABA Therapy",
        "hours": "Sun-Thu: 8:30 AM - 4:00 PM",
        "capacity": 24,
    },
    {
        "centre_name": "Tumpat Pediatric Speech & Play Therapy Unit",
        "category": "Government Health Clinic Rehab",
        "address": "Jalan Kelaboran, 16200 Tumpat, Kelantan",
        "district": "Tumpat",
        "lat": 6.1972,
        "lon": 102.1665,
        "contact": "+609-725 7333",
        "services": "Speech Therapy, Early Intervention",
        "hours": "Sun-Thu: 8:00 AM - 4:30 PM",
        "capacity": 25,
    },
    {
        "centre_name": "Wakaf Bharu Sensory & Daily Living Care Hub",
        "category": "Private Therapy Clinic",
        "address": "Lot 312, Pekan Wakaf Bharu, 16250 Tumpat, Kelantan",
        "district": "Tumpat",
        "lat": 6.1205,
        "lon": 102.1984,
        "contact": "+609-719 6420",
        "services": "Occupational Sensory, ABA Therapy, Speech Therapy",
        "hours": "Sun-Thu: 9:00 AM - 5:30 PM",
        "capacity": 26,
    },
    {
        "centre_name": "Pasir Puteh Special Needs & Rehab Centre",
        "category": "Community-Based Rehabilitation (PDK)",
        "address": "Jalan Madrasah, 16800 Pasir Puteh, Kelantan",
        "district": "Pasir Puteh",
        "lat": 5.8385,
        "lon": 102.4021,
        "contact": "+609-786 6210",
        "services": "Early Intervention, Occupational Sensory",
        "hours": "Sun-Thu: 8:30 AM - 4:00 PM",
        "capacity": 24,
    },
    {
        "centre_name": "Machang Community Autism & Child Rehab Unit",
        "category": "Government Hospital Rehab",
        "address": "Jalan Pasir Puteh, 18500 Machang, Kelantan",
        "district": "Machang",
        "lat": 5.7688,
        "lon": 102.2210,
        "contact": "+609-975 2533",
        "services": "Speech Therapy, Occupational Sensory, Early Intervention",
        "hours": "Sun-Thu: 8:00 AM - 4:30 PM",
        "capacity": 26,
    },
    {
        "centre_name": "Tanah Merah Integrated Pediatric Therapy Centre",
        "category": "Government Hospital Rehab",
        "address": "Jalan Hospital, 17500 Tanah Merah, Kelantan",
        "district": "Tanah Merah",
        "lat": 5.8065,
        "lon": 102.1512,
        "contact": "+609-955 7333",
        "services": "Speech Therapy, Early Intervention, ABA Therapy",
        "hours": "Sun-Thu: 8:00 AM - 4:30 PM",
        "capacity": 28,
    },
    {
        "centre_name": "Kuala Krai Specialist Child Development Unit",
        "category": "Government Specialist Hospital",
        "address": "Lebuhraya Kuala Krai - Gua Musang, 18000 Kuala Krai, Kelantan",
        "district": "Kuala Krai",
        "lat": 5.5332,
        "lon": 102.2035,
        "contact": "+609-966 6333",
        "services": "Speech Therapy, Occupational Sensory, Early Intervention",
        "hours": "Sun-Thu: 8:00 AM - 4:30 PM",
        "capacity": 30,
    },
    {
        "centre_name": "Jeli Rural Early Intervention Outreach Clinic",
        "category": "Community-Based Rehabilitation (PDK)",
        "address": "Jalan Jeli - Dabong, 17600 Jeli, Kelantan",
        "district": "Jeli",
        "lat": 5.7018,
        "lon": 101.8450,
        "contact": "+609-944 0288",
        "services": "Early Intervention",
        "hours": "Sun-Thu: 8:30 AM - 3:30 PM",
        "capacity": 16,
    },
    {
        "centre_name": "Gua Musang Southern Pediatric Rehab Unit",
        "category": "Government Hospital Rehab",
        "address": "Bandar Baru Gua Musang, 18300 Gua Musang, Kelantan",
        "district": "Gua Musang",
        "lat": 4.8855,
        "lon": 101.9660,
        "contact": "+609-912 1133",
        "services": "Speech Therapy, Early Intervention",
        "hours": "Sun-Thu: 8:00 AM - 4:30 PM",
        "capacity": 20,
    },
]

MODULES_4 = [
    {
        "key": "AG",
        "code": "Module 01 - AG",
        "title": "Toilet Training & Daily Hygiene",
        "domain": "Self-Care & Independence",
        "color": "#0F294A",
        "accent": "#0D9488",
        "soft_bg": "#E0F2FE",
        "cover_desc": "A structured visual guide to help parents establish calm, predictable bathroom and handwashing routines at home.",
        "pages": [
            (
                "Step 1. Recognizing Readiness & Visual Cues",
                "Introduce clear picture cues before each scheduled bathroom visit.",
                "- Use a laminated toilet visual card at eye level.\n- Keep verbal prompts short and consistent: 'Time for toilet.'\n- Visit at predictable intervals (after meals and before outings).",
            ),
            (
                "Step 2. Calm Bathroom Transition",
                "Ensure the bathroom environment feels safe, warm, and sensory-friendly.",
                "- Use a non-slip footstool so feet are supported.\n- Avoid loud flushing while the child is still seated if sensitive to sound.\n- Praise calm sitting immediately.",
            ),
            (
                "Step 3. 4-Step Handwashing Sequence",
                "Break handwashing into four repeatable steps: Wet, Soap, Scrub (10s), Rinse & Dry.",
                "- Count slowly to 10 together while rubbing soap.\n- Keep towel and soap within easy reach.\n- Model the sequence side-by-side.",
            ),
            (
                "Step 4. Positive Reinforcement & Tracking",
                "Track daily successes gently and respond neutrally to accidents.",
                "- Reward effort immediately with praise or a visual token.\n- Keep a simple daily log to share progress with therapists.",
            ),
        ],
    },
    {
        "key": "AH",
        "code": "Module 02 - AH",
        "title": "Morning & Classroom Transition Routine",
        "domain": "Home & School Transitions",
        "color": "#0D9488",
        "accent": "#0F294A",
        "soft_bg": "#CCFBF1",
        "cover_desc": "Practical strategies using countdowns and First/Then boards to reduce anxiety during morning departures and centre arrivals.",
        "pages": [
            (
                "Step 1. Advance Countdown Cues",
                "Prepare your child 5 minutes and 2 minutes before any activity change.",
                "- Use a visual sand timer or phone countdown.\n- Say clearly: 'In 2 minutes, shoes on.'\n- Allow time to finish the current action.",
            ),
            (
                "Step 2. Using a 'First / Then' Visual Board",
                "Pair a required routine step with a comforting or motivating activity.",
                "- Example: FIRST pack school bag -> THEN hold favourite sensory toy in car.\n- Point to each picture as you speak.",
            ),
            (
                "Step 3. Smooth Centre / School Drop-Off",
                "Establish a brief, predictable goodbye ritual at the centre entrance.",
                "- Greet the therapist or teacher together.\n- Keep goodbye warm, confident, and brief.\n- Hand over the child's daily communication card.",
            ),
            (
                "Step 4. Settling-In Buffer Time",
                "Allow 3-5 minutes of quiet regulation upon arriving in a new room.",
                "- Let your child check their visual schedule before starting table tasks.",
            ),
        ],
    },
    {
        "key": "AI",
        "code": "Module 03 - AI",
        "title": "Morning Walk & Sensory Regulation",
        "domain": "Sensory & Motor Wellness",
        "color": "#1E3A8A",
        "accent": "#0D9488",
        "soft_bg": "#E0F2FE",
        "cover_desc": "Gentle outdoor movement and sensory environment checks to support emotional regulation and focus before therapy.",
        "pages": [
            (
                "Step 1. Predictable Morning Movement",
                "Start the day with a calm 10-minute walk along a familiar path.",
                "- Walk at your child's natural pace.\n- Use rhythmic, reassuring encouragement.\n- Heavy-work movement helps organize the nervous system.",
            ),
            (
                "Step 2. Early Sensory Load Check",
                "Notice environmental triggers such as bright sunlight, traffic noise, or crowds.",
                "- Offer noise-reducing headphones or a cap before distress escalates.\n- Watch for early signs like covering ears or pacing.",
            ),
            (
                "Step 3. Deep Breathing & Grounding Reset",
                "Practice a simple 'Smell the flower, blow the candle' breathing exercise.",
                "- Inhale slowly for 3 seconds, exhale gently for 4 seconds.\n- Repeat 3 times together in a quiet corner.",
            ),
            (
                "Step 4. Transitioning to Focused Learning",
                "Follow movement with a sip of water and a calm seated activity.",
                "- A regulated body improves attention during speech and occupational therapy.",
            ),
        ],
    },
    {
        "key": "SK",
        "code": "Module 04 - SK",
        "title": "Speech & Picture Exchange (PECS)",
        "domain": "Communication & Language",
        "color": "#0F294A",
        "accent": "#0284C7",
        "soft_bg": "#F0F9FF",
        "cover_desc": "Build functional everyday communication using picture exchange cards, clear single-word models, and responsive reinforcement.",
        "pages": [
            (
                "Step 1. Selecting High-Motivation Cards",
                "Begin with 3-4 items your child genuinely wants (water, snack, break, toy).",
                "- Place clear picture cards on a Velcro strip within easy reach.\n- Ensure the child can see and reach the cards independently.",
            ),
            (
                "Step 2. The Picture Exchange Action",
                "Prompt your child to hand the picture card directly into your open hand.",
                "- Immediately honor the request when the card is exchanged.\n- Immediate response teaches that communication works.",
            ),
            (
                "Step 3. Pairing Clear Spoken Models",
                "Speak the target word clearly at the exact moment you receive the card.",
                "- Say 'Water' or 'More snack' clearly.\n- Do not withhold the item if the child cannot yet repeat the word.",
            ),
            (
                "Step 4. Expanding Across Daily Routines",
                "Use picture cards during meals, playtime, and therapy sessions.",
                "- Gradually introduce 'Help' and 'Break' cards to reduce frustration.",
            ),
        ],
    },
]


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_district_name(raw_dist: str) -> str:
    cleaned = " ".join(str(raw_dist or "").strip().split()).title()
    aliases = {
        "Wakaf Bharu": "Tumpat",
        "Rantau Panjang": "Pasir Mas",
        "Kubang Kerian": "Kota Bharu",
        "Pengkalan Chepa": "Kota Bharu",
    }
    mapped = aliases.get(cleaned, cleaned)
    return mapped if mapped in KELANTAN_DISTRICTS else "Kota Bharu"


def normalize_service_name(raw_srv: str) -> str:
    cleaned = " ".join(str(raw_srv or "").strip().split())
    lower = cleaned.lower()
    if "speech" in lower or lower == "st":
        return "Speech Therapy"
    if "aba" in lower:
        return "ABA Therapy"
    if "occupational" in lower or "sensory" in lower or lower in {"ot", "os"}:
        return "Occupational Sensory"
    if "early" in lower or "intervention" in lower or lower == "ei":
        return "Early Intervention"
    return cleaned if cleaned in THERAPY_SERVICES else "Early Intervention"


def normalize_diagnosis_name(raw_diag: str) -> str:
    cleaned = " ".join(str(raw_diag or "").strip().split())
    lower = cleaned.lower()
    if "mild" in lower:
        return "Mild Autism"
    if "high" in lower:
        return "High-Function Autism"
    if "severe" in lower:
        return "Severe Autism"
    return cleaned if cleaned in DIAGNOSIS_CATEGORIES else "Mild Autism"


def build_balanced_106_students_df() -> pd.DataFrame:
    """Build exact 106 student records matching district, diagnosis, and therapy totals."""
    district_targets = [
        ("Tumpat", 30),
        ("Pasir Mas", 29),
        ("Kota Bharu", 16),
        ("Pasir Puteh", 16),
        ("Machang", 3),
        ("Tanah Merah", 3),
        ("Kuala Krai", 3),
        ("Bachok", 2),
        ("Jeli", 2),
        ("Gua Musang", 2),
    ]
    districts_pool = []
    for d_name, cnt in district_targets:
        districts_pool.extend([d_name] * cnt)

    diagnosis_pool = (
        ["Mild Autism"] * 36
        + ["High-Function Autism"] * 35
        + ["Severe Autism"] * 35
    )
    services_pool = (
        ["Speech Therapy"] * 28
        + ["ABA Therapy"] * 26
        + ["Occupational Sensory"] * 26
        + ["Early Intervention"] * 26
    )
    sample_names = [
        "Aisyah Humaira", "Muhammad Adam", "Nurul Izzah", "Ahmad Danial", "Siti Khadijah",
        "Wan Amirul", "Nik Sofea", "Che Muhammad Hakim", "Tengku Zara", "Muhammad Rayyan",
        "Nur Qistina", "Ahmad Harith", "Putri Damia", "Muhammad Iman", "Nur Aleesya",
    ]
    dates = ["2026-01-15", "2026-02-15", "2026-03-15", "2026-04-15", "2026-05-15", "2026-06-15"]
    rows = []
    for i in range(EXPECTED_TOTAL_STUDENTS):
        rec_id = f"KOD-{1000 + i}"
        s_name = f"{sample_names[i % len(sample_names)]} ({rec_id})"
        rows.append({
            "record_id": rec_id,
            "student_name": s_name,
            "age": 4 + (i % 12),
            "district": districts_pool[i],
            "diagnosis": diagnosis_pool[i],
            "required_service": services_pool[i],
            "registered_date": dates[i % len(dates)],
            "status": "Pending Verification" if (i % 5 == 0) else "Verified Active",
        })
    return pd.DataFrame(rows)


def normalize_students_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Ensure every student record is cleaned, deduplicated, and never dropped."""
    if raw_df is None or raw_df.empty:
        return pd.DataFrame(columns=[
            "record_id", "student_name", "age", "district",
            "diagnosis", "required_service", "registered_date", "status",
        ])
    df = raw_df.copy()
    if "record_id" in df.columns:
        df["record_id"] = df["record_id"].astype(str).str.strip()
        df = df.drop_duplicates(subset=["record_id"], keep="first").reset_index(drop=True)
    df["student_name"] = df.get("student_name", "Unnamed Student").fillna("Unnamed Student").astype(str).str.strip()
    df["age"] = pd.to_numeric(df.get("age", 6), errors="coerce").fillna(6).astype(int)
    df["district"] = df.get("district", "Kota Bharu").fillna("Kota Bharu").map(normalize_district_name)
    df["diagnosis"] = df.get("diagnosis", "Mild Autism").fillna("Mild Autism").map(normalize_diagnosis_name)
    df["required_service"] = df.get("required_service", "Early Intervention").fillna("Early Intervention").map(normalize_service_name)
    df["registered_date"] = df.get("registered_date", "2026-01-15").fillna("2026-01-15").astype(str).str.strip()
    df["status"] = df.get("status", "Verified Active").fillna("Verified Active").astype(str).str.strip()
    return df


def init_database():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            record_id TEXT PRIMARY KEY,
            student_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            district TEXT NOT NULL,
            diagnosis TEXT NOT NULL,
            required_service TEXT NOT NULL,
            registered_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS autism_centres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            centre_name TEXT NOT NULL,
            category TEXT NOT NULL,
            address TEXT NOT NULL,
            district TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            contact TEXT NOT NULL,
            services TEXT NOT NULL,
            hours TEXT NOT NULL,
            capacity INTEGER NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS parent_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_code TEXT NOT NULL,
            child_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            diagnosis TEXT NOT NULL,
            residential_address TEXT NOT NULL,
            district TEXT NOT NULL,
            home_lat REAL NOT NULL,
            home_lon REAL NOT NULL,
            required_services TEXT NOT NULL,
            parent_name TEXT NOT NULL,
            parent_contact TEXT NOT NULL,
            recommended_centres_json TEXT NOT NULL,
            selected_centre TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            submitted_at TEXT NOT NULL
        )
        """
    )
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM autism_centres")
    if cur.fetchone()[0] == 0:
        for c in INITIAL_CENTRES:
            cur.execute(
                """
                INSERT INTO autism_centres
                (centre_name, category, address, district, lat, lon, contact, services, hours, capacity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    c["centre_name"], c["category"], c["address"], c["district"],
                    c["lat"], c["lon"], c["contact"], c["services"], c["hours"], c["capacity"],
                ),
            )
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM students")
    if cur.fetchone()[0] == 0:
        seed_df = build_balanced_106_students_df()
        for _, r in seed_df.iterrows():
            cur.execute(
                """
                INSERT INTO students
                (record_id, student_name, age, district, diagnosis, required_service, registered_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    r["record_id"], r["student_name"], int(r["age"]), r["district"],
                    r["diagnosis"], r["required_service"], r["registered_date"], r["status"],
                ),
            )
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM parent_registrations")
    if cur.fetchone()[0] == 0:
        sample_recs = [
            {
                "reg_code": "REG-2026-001",
                "child_name": "Muhammad Rayyan bin Azman",
                "age": 6,
                "diagnosis": "Mild Autism",
                "residential_address": "No. 14, Taman Desa Darulnaim, Pasir Tumboh, 16150 Kota Bharu, Kelantan",
                "district": "Kota Bharu",
                "home_lat": 6.0820,
                "home_lon": 102.2750,
                "required_services": "Speech Therapy, Occupational Sensory",
                "parent_name": "Azman bin Hassan",
                "parent_contact": "019-912 4480",
                "selected_centre": "Hospital Universiti Sains Malaysia (HUSM) Child Development Unit",
                "status": "Approved",
                "submitted_at": "2026-11-18 09:40",
            },
            {
                "reg_code": "REG-2026-002",
                "child_name": "Nurul Qistina binti Rosli",
                "age": 5,
                "diagnosis": "Severe Autism",
                "residential_address": "Lot 88, Kampung Cherang Ruku, 16700 Pasir Puteh, Kelantan",
                "district": "Pasir Puteh",
                "home_lat": 5.8540,
                "home_lon": 102.4620,
                "required_services": "Speech Therapy, ABA Therapy, Early Intervention",
                "parent_name": "Rosli bin Yusoff",
                "parent_contact": "013-984 2219",
                "selected_centre": "Pasir Puteh Special Needs & Rehab Centre",
                "status": "Pending",
                "submitted_at": "2026-11-22 14:15",
            },
        ]
        for sr in sample_recs:
            cur.execute(
                """
                INSERT INTO parent_registrations
                (reg_code, child_name, age, diagnosis, residential_address, district, home_lat, home_lon,
                 required_services, parent_name, parent_contact, recommended_centres_json,
                 selected_centre, status, submitted_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sr["reg_code"], sr["child_name"], sr["age"], sr["diagnosis"], sr["residential_address"],
                    sr["district"], sr["home_lat"], sr["home_lon"], sr["required_services"],
                    sr["parent_name"], sr["parent_contact"], "[]", sr["selected_centre"],
                    sr["status"], sr["submitted_at"],
                ),
            )
        conn.commit()
    conn.close()


init_database()


def load_students_df() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM students ORDER BY record_id ASC", conn)
    conn.close()
    cleaned = normalize_students_df(df)
    if len(cleaned) == 104 and set(cleaned["record_id"]).issubset({f"KOD-{1000 + i}" for i in range(106)}):
        conn = get_conn()
        conn.execute("DELETE FROM students")
        seed_df = build_balanced_106_students_df()
        for _, r in seed_df.iterrows():
            conn.execute(
                """
                INSERT INTO students
                (record_id, student_name, age, district, diagnosis, required_service, registered_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    r["record_id"], r["student_name"], int(r["age"]), r["district"],
                    r["diagnosis"], r["required_service"], r["registered_date"], r["status"],
                ),
            )
        conn.commit()
        conn.close()
        return seed_df
    return cleaned


def load_centres_df() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM autism_centres ORDER BY id ASC", conn)
    conn.close()
    if not df.empty and "district" in df.columns:
        df["district"] = df["district"].map(normalize_district_name)
    return df


def load_registrations_df() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM parent_registrations ORDER BY id DESC", conn)
    conn.close()
    return df


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)


def estimate_home_coordinates(district: str, address_text: str) -> tuple[float, float]:
    base_lat, base_lon = DISTRICT_CENTROIDS.get(district, (6.1254, 102.2381))
    addr_lower = address_text.lower()
    local_anchors = {
        "kubang kerian": (6.0980, 102.2795),
        "pengkalan chepa": (6.1560, 102.2880),
        "pasir tumboh": (6.0815, 102.2760),
        "ketereh": (5.9585, 102.2480),
        "kok lanas": (5.9220, 102.2450),
        "melawi": (5.9950, 102.4210),
        "jelawat": (6.0130, 102.3730),
        "rantau panjang": (6.0205, 101.9810),
        "wakaf bharu": (6.1210, 102.1990),
        "cherang ruku": (5.8530, 102.4600),
        "selising": (5.8930, 102.3290),
        "dabong": (5.3760, 102.0120),
    }
    for kw, coords in local_anchors.items():
        if kw in addr_lower:
            return coords
    seed = sum(ord(ch) for ch in address_text.strip()) if address_text.strip() else 42
    d_lat = ((seed % 19) - 9) * 0.0022
    d_lon = (((seed * 7) % 19) - 9) * 0.0022
    return round(base_lat + d_lat, 5), round(base_lon + d_lon, 5)


def compute_top_3_centres(
    home_lat: float,
    home_lon: float,
    required_services: list[str],
    centres_df: pd.DataFrame,
) -> list[dict]:
    if centres_df.empty:
        return []
    req_set = {s.strip() for s in required_services if s.strip()}
    scored = []
    for _, row in centres_df.iterrows():
        c_lat = float(row["lat"])
        c_lon = float(row["lon"])
        dist_km = haversine_km(home_lat, home_lon, c_lat, c_lon)
        avail_list = [s.strip() for s in str(row["services"]).split(",") if s.strip()]
        avail_set = set(avail_list)
        if req_set:
            matched_services = sorted(req_set.intersection(avail_set))
            service_ratio = len(matched_services) / len(req_set)
        else:
            matched_services = avail_list
            service_ratio = 1.0
        dist_score = max(0.15, 1.0 - (dist_km / 65.0))
        cap = max(1, int(row["capacity"]))
        cap_score = min(1.0, cap / 45.0)
        raw_score = (0.55 * service_ratio + 0.35 * dist_score + 0.10 * cap_score) * 100.0
        suitability_pct = min(99, max(45, int(round(raw_score))))
        match_txt = (
            f"Matches {', '.join(matched_services)}"
            if matched_services
            else "General developmental & referral support"
        )
        reason = (
            f"{suitability_pct}% suitability score (system-generated): {match_txt}; "
            f"located {dist_km:.1f} km from child's residence with {cap}-slot centre capacity."
        )
        scored.append({
            "id": int(row["id"]),
            "centre_name": str(row["centre_name"]),
            "category": str(row["category"]),
            "address": str(row["address"]),
            "district": str(row["district"]),
            "lat": c_lat,
            "lon": c_lon,
            "contact": str(row["contact"]),
            "services": str(row["services"]),
            "hours": str(row["hours"]),
            "capacity": cap,
            "distance_km": dist_km,
            "suitability_pct": suitability_pct,
            "matched_services": matched_services,
            "reason": reason,
        })
    scored.sort(key=lambda x: (-x["suitability_pct"], x["distance_km"]))
    top3 = scored[:3]
    for idx, item in enumerate(top3, start=1):
        item["rank"] = idx
    return top3


def compute_district_accessibility(students_df: pd.DataFrame, centres_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dist in KELANTAN_DISTRICTS:
        if students_df.empty:
            s_cnt = 0
        else:
            s_cnt = int((students_df["district"] == dist).sum())
        c_sub = centres_df[centres_df["district"] == dist] if not centres_df.empty else pd.DataFrame()
        c_cnt = int(len(c_sub))
        cap_sum = int(c_sub["capacity"].sum()) if c_cnt > 0 else 0
        ratio = round(s_cnt / c_cnt, 1) if c_cnt > 0 else float(s_cnt)
        if c_cnt >= 3 or (c_cnt >= 2 and ratio <= 7.5):
            level = "Green"
            status_label = "Good Accessibility"
            gap_status = "Sufficient Coverage"
            fill_hex = "#0D9488"
        elif c_cnt == 2 or (c_cnt == 1 and s_cnt <= 10):
            level = "Yellow"
            status_label = "Moderate Accessibility"
            gap_status = "Moderate Service Gap"
            fill_hex = "#EAB308"
        else:
            level = "Red"
            status_label = "Poor Accessibility (Critical Shortage)"
            gap_status = "Critical Shortage - Priority Expansion"
            fill_hex = "#DC2626"
        lat, lon = DISTRICT_CENTROIDS[dist]
        rows.append({
            "district": dist,
            "students": s_cnt,
            "centres": c_cnt,
            "total_capacity": cap_sum,
            "student_per_centre": ratio,
            "level": level,
            "status_label": status_label,
            "gap_status": gap_status,
            "fill_hex": fill_hex,
            "lat": lat,
            "lon": lon,
        })
    return pd.DataFrame(rows)


def build_therapy_demand_by_district(students_df: pd.DataFrame) -> pd.DataFrame:
    matrix = {dist: {srv: 0 for srv in THERAPY_SERVICES} for dist in KELANTAN_DISTRICTS}
    if not students_df.empty and "district" in students_df.columns and "required_service" in students_df.columns:
        for _, row in students_df.iterrows():
            dist = normalize_district_name(row["district"])
            srv = normalize_service_name(row["required_service"])
            if dist in matrix and srv in matrix[dist]:
                matrix[dist][srv] += 1
    df = pd.DataFrame.from_dict(matrix, orient="index")[THERAPY_SERVICES]
    df.index.name = "District"
    return df


def count_students_in_year(students_df: pd.DataFrame, target_year: int = 2026) -> int:
    if students_df.empty:
        return 0
    if "registered_date" not in students_df.columns:
        return int(len(students_df))
    parsed = pd.to_datetime(students_df["registered_date"], errors="coerce")
    matched = int((parsed.dt.year == target_year).sum())
    return matched if matched > 0 else int(len(students_df))


def _base_vl_config() -> dict:
    return {
        "background": "#FFFFFF",
        "font": "Inter, 'Segoe UI', Arial, sans-serif",
        "view": {"stroke": "transparent", "fill": "#FFFFFF"},
        "axis": {
            "labelColor": "#0F172A",
            "titleColor": "#0F172A",
            "titleFontWeight": "bold",
            "labelFontSize": 12.5,
            "titleFontSize": 13,
            "domainColor": "#CBD5E1",
            "domainWidth": 1,
            "tickColor": "#CBD5E1",
            "gridColor": "#EEF2F6",
        },
        "legend": {
            "labelColor": "#0F172A",
            "titleColor": "#0F172A",
            "labelFontSize": 12.5,
            "titleFontSize": 13,
        },
    }


def render_horizontal_bar_with_labels(
    df: pd.DataFrame,
    category_col: str,
    value_col: str,
    y_title: str | None = None,
    color: str = "#1E3A8A",
    sort_desc: bool = True,
    height: int = 400,
):
    plot_df = df[[category_col, value_col]].copy()
    plot_df[category_col] = plot_df[category_col].astype(str)
    plot_df[value_col] = pd.to_numeric(plot_df[value_col], errors="coerce").fillna(0).astype(int)
    if sort_desc:
        plot_df = plot_df.sort_values(by=[value_col, category_col], ascending=[False, True]).reset_index(drop=True)
    else:
        plot_df = plot_df.reset_index(drop=True)
    max_val = int(plot_df[value_col].max()) if not plot_df.empty else 1
    x_upper = max(1, math.ceil(max_val * 1.16))
    sort_order = plot_df[category_col].tolist()
    bar_size = 24 if len(plot_df) > 6 else 40
    spec = {
        "width": "container",
        "height": height,
        "background": "#FFFFFF",
        "padding": {"top": 14, "right": 34, "bottom": 14, "left": 8},
        "data": {"values": plot_df.to_dict(orient="records")},
        "layer": [
            {
                "mark": {
                    "type": "bar",
                    "color": color,
                    "cornerRadiusTopRight": 5,
                    "cornerRadiusBottomRight": 5,
                    "size": bar_size,
                },
                "encoding": {
                    "y": {
                        "field": category_col,
                        "type": "nominal",
                        "sort": sort_order,
                        "title": y_title,
                        "axis": {
                            "labelLimit": 210,
                            "labelOverlap": False,
                            "labelPadding": 10,
                            "grid": False,
                        },
                    },
                    "x": {
                        "field": value_col,
                        "type": "quantitative",
                        "title": None,
                        "scale": {"domain": [0, x_upper]},
                        "axis": {
                            "labels": False,
                            "ticks": False,
                            "domain": False,
                            "grid": True,
                            "tickCount": 6,
                        },
                    },
                    "tooltip": [
                        {"field": category_col, "type": "nominal", "title": y_title or "Category"},
                        {"field": value_col, "type": "quantitative", "title": "Students"},
                    ],
                },
            },
            {
                "mark": {
                    "type": "text",
                    "align": "left",
                    "baseline": "middle",
                    "dx": 8,
                    "fontSize": 12.5,
                    "fontWeight": "bold",
                    "color": "#0F172A",
                },
                "encoding": {
                    "y": {"field": category_col, "type": "nominal", "sort": sort_order},
                    "x": {"field": value_col, "type": "quantitative"},
                    "text": {"field": value_col, "type": "quantitative"},
                },
            },
        ],
        "config": _base_vl_config(),
    }
    st.vega_lite_chart(plot_df, spec, use_container_width=True)


def render_horizontal_lollipop_chart(
    df: pd.DataFrame,
    category_col: str,
    value_col: str,
    y_title: str | None = None,
    color: str = "#4338CA",
    height: int = 400,
):
    plot_df = df[[category_col, value_col]].copy()
    plot_df[category_col] = plot_df[category_col].astype(str)
    plot_df[value_col] = pd.to_numeric(plot_df[value_col], errors="coerce").fillna(0).astype(int)
    plot_df = plot_df.sort_values(by=[value_col, category_col], ascending=[False, True]).reset_index(drop=True)
    max_val = int(plot_df[value_col].max()) if not plot_df.empty else 1
    x_upper = max(1, math.ceil(max_val * 1.22))
    sort_order = plot_df[category_col].tolist()
    spec = {
        "width": "container",
        "height": height,
        "background": "#FFFFFF",
        "padding": {"top": 14, "right": 34, "bottom": 14, "left": 8},
        "data": {"values": plot_df.to_dict(orient="records")},
        "layer": [
            {
                "mark": {"type": "rule", "color": color, "strokeWidth": 3.2},
                "encoding": {
                    "y": {
                        "field": category_col,
                        "type": "nominal",
                        "sort": sort_order,
                        "title": y_title,
                        "axis": {
                            "labelLimit": 210,
                            "labelOverlap": False,
                            "labelPadding": 10,
                            "grid": False,
                        },
                    },
                    "x": {"datum": 0},
                    "x2": {"field": value_col, "type": "quantitative"},
                },
            },
            {
                "mark": {"type": "point", "filled": True, "color": color, "size": 130},
                "encoding": {
                    "y": {"field": category_col, "type": "nominal", "sort": sort_order},
                    "x": {
                        "field": value_col,
                        "type": "quantitative",
                        "title": None,
                        "scale": {"domain": [0, x_upper]},
                        "axis": {
                            "labels": False,
                            "ticks": False,
                            "domain": False,
                            "grid": True,
                            "tickCount": 5,
                        },
                    },
                    "tooltip": [
                        {"field": category_col, "type": "nominal", "title": y_title or "District"},
                        {"field": value_col, "type": "quantitative", "title": "Centres"},
                    ],
                },
            },
            {
                "mark": {
                    "type": "text",
                    "align": "left",
                    "baseline": "middle",
                    "dx": 11,
                    "fontSize": 12.5,
                    "fontWeight": "bold",
                    "color": "#0F172A",
                },
                "encoding": {
                    "y": {"field": category_col, "type": "nominal", "sort": sort_order},
                    "x": {"field": value_col, "type": "quantitative"},
                    "text": {"field": value_col, "type": "quantitative"},
                },
            },
        ],
        "config": _base_vl_config(),
    }
    st.vega_lite_chart(plot_df, spec, use_container_width=True)


def render_diagnosis_donut_with_legend(diag_counts_df: pd.DataFrame, height: int = 400):
    ordered_cats = ["Mild Autism", "High-Function Autism", "Severe Autism"]
    palette = {
        "Mild Autism": "#0D9488",
        "High-Function Autism": "#0284C7",
        "Severe Autism": "#0F294A",
    }
    count_map = {}
    if not diag_counts_df.empty:
        for _, r in diag_counts_df.iterrows():
            norm_cat = normalize_diagnosis_name(r.iloc[0])
            count_map[norm_cat] = count_map.get(norm_cat, 0) + int(r.iloc[1])
    rows = [{"category": cat, "count": count_map.get(cat, 0)} for cat in ordered_cats]
    for cat, cnt in count_map.items():
        if cat not in ordered_cats:
            rows.append({"category": cat, "count": cnt})
    df_d = pd.DataFrame(rows)
    total_students = int(df_d["count"].sum())
    legend_labels = []
    for _, r in df_d.iterrows():
        c_name = r["category"]
        c_val = int(r["count"])
        pct = (c_val / total_students * 100.0) if total_students > 0 else 0.0
        legend_labels.append(f"{c_name}: {c_val} ({pct:.1f}%)")
    df_d["legend_label"] = legend_labels
    color_range = [palette.get(c, "#64748B") for c in df_d["category"]]
    spec = {
        "width": "container",
        "height": height,
        "background": "#FFFFFF",
        "padding": {"top": 12, "right": 16, "bottom": 12, "left": 16},
        "data": {"values": df_d.to_dict(orient="records")},
        "layer": [
            {
                "mark": {
                    "type": "arc",
                    "innerRadius": 74,
                    "outerRadius": 116,
                    "stroke": "#FFFFFF",
                    "strokeWidth": 2.5,
                },
                "encoding": {
                    "theta": {"field": "count", "type": "quantitative", "stack": True},
                    "color": {
                        "field": "legend_label",
                        "type": "nominal",
                        "sort": legend_labels,
                        "title": None,
                        "scale": {"range": color_range},
                        "legend": {
                            "orient": "right",
                            "direction": "vertical",
                            "labelLimit": 320,
                            "labelFontSize": 12.5,
                            "symbolSize": 130,
                            "rowPadding": 10,
                            "padding": 12,
                        },
                    },
                    "tooltip": [
                        {"field": "category", "type": "nominal", "title": "Diagnosis"},
                        {"field": "count", "type": "quantitative", "title": "Students"},
                    ],
                },
            },
            {
                "mark": {
                    "type": "text",
                    "align": "center",
                    "baseline": "middle",
                    "fontSize": 26,
                    "fontWeight": "bold",
                    "color": "#0F172A",
                    "dy": -10,
                },
                "encoding": {
                    "text": {"datum": str(total_students)},
                },
            },
            {
                "mark": {
                    "type": "text",
                    "align": "center",
                    "baseline": "middle",
                    "fontSize": 13,
                    "fontWeight": "normal",
                    "color": "#475569",
                    "dy": 14,
                },
                "encoding": {
                    "text": {"datum": "Students"},
                },
            },
        ],
        "config": _base_vl_config(),
    }
    st.vega_lite_chart(df_d, spec, use_container_width=True)


def render_therapy_heatmap(wide_df: pd.DataFrame, height: int = 400):
    long_df = wide_df.reset_index().melt(
        id_vars=[wide_df.index.name or "District"],
        value_vars=THERAPY_SERVICES,
        var_name="Service",
        value_name="Demand",
    )
    x_col = wide_df.index.name or "District"
    code_map = {
        "Speech Therapy": "ST",
        "ABA Therapy": "ABA",
        "Occupational Sensory": "OT",
        "Early Intervention": "EI",
    }
    long_df["ServiceCode"] = long_df["Service"].map(lambda s: code_map.get(s, s))
    service_code_order = [code_map[s] for s in THERAPY_SERVICES]
    spec = {
        "width": "container",
        "height": height,
        "background": "#FFFFFF",
        "padding": {"top": 12, "right": 18, "bottom": 12, "left": 8},
        "data": {"values": long_df.to_dict(orient="records")},
        "layer": [
            {
                "mark": {
                    "type": "rect",
                    "stroke": "#FFFFFF",
                    "strokeWidth": 2,
                    "cornerRadius": 3,
                },
                "encoding": {
                    "x": {
                        "field": "ServiceCode",
                        "type": "nominal",
                        "sort": service_code_order,
                        "title": "Therapy Service (ST / ABA / OT / EI)",
                        "axis": {
                            "labelAngle": 0,
                            "labelOverlap": False,
                            "labelPadding": 8,
                            "labelFontSize": 12.5,
                        },
                    },
                    "y": {
                        "field": x_col,
                        "type": "nominal",
                        "sort": KELANTAN_DISTRICTS,
                        "title": None,
                        "axis": {
                            "labelLimit": 160,
                            "labelOverlap": False,
                            "labelPadding": 10,
                            "labelFontSize": 12,
                        },
                    },
                    "color": {
                        "field": "Demand",
                        "type": "quantitative",
                        "title": "Students",
                        "scale": {"range": ["#EFF6FF", "#93C5FD", "#2563EB", "#1E3A8A"]},
                        "legend": {"tickMinStep": 1},
                    },
                    "tooltip": [
                        {"field": x_col, "type": "nominal", "title": "District"},
                        {"field": "Service", "type": "nominal", "title": "Therapy Service"},
                        {"field": "Demand", "type": "quantitative", "title": "Students"},
                    ],
                },
            },
            {
                "mark": {
                    "type": "text",
                    "align": "center",
                    "baseline": "middle",
                    "fontSize": 12.5,
                    "fontWeight": "bold",
                },
                "encoding": {
                    "x": {"field": "ServiceCode", "type": "nominal", "sort": service_code_order},
                    "y": {"field": x_col, "type": "nominal", "sort": KELANTAN_DISTRICTS},
                    "text": {"field": "Demand", "type": "quantitative"},
                    "color": {
                        "condition": {"test": "datum.Demand >= 4", "value": "#FFFFFF"},
                        "value": "#0F172A",
                    },
                },
            },
        ],
        "config": _base_vl_config(),
    }
    st.vega_lite_chart(long_df, spec, use_container_width=True)


def render_accessibility_donut_chart(
    district_name: str,
    students: int,
    total_capacity: int,
    level: str,
    height: int = 285,
):
    if level == "Red":
        status_hex = "#DC2626"
        status_name = "Critical Coverage"
    elif level == "Yellow":
        status_hex = "#EAB308"
        status_name = "Moderate Coverage"
    else:
        status_hex = "#0D9488"
        status_name = "Good Coverage"

    if total_capacity <= 0 and students <= 0:
        donut_rows = [{"Segment": "No Active Demand / Capacity", "Slots": 1, "Color": "#CBD5E1"}]
    elif students <= total_capacity:
        remaining_slots = max(0, total_capacity - students)
        donut_rows = [
            {"Segment": "Registered Autism Students", "Slots": students, "Color": status_hex},
            {"Segment": "Remaining Centre Slot Capacity", "Slots": remaining_slots, "Color": "#E2E8F0"},
        ]
    else:
        unmet_demand = students - total_capacity
        donut_rows = [
            {"Segment": "Covered by Centre Capacity", "Slots": total_capacity, "Color": "#0F294A"},
            {"Segment": "Unmet Student Demand (Shortage)", "Slots": unmet_demand, "Color": "#DC2626"},
        ]
    donut_df = pd.DataFrame(donut_rows)
    domain_labels = donut_df["Segment"].tolist()
    range_colors = donut_df["Color"].tolist()
    spec = {
        "width": "container",
        "background": "#FFFFFF",
        "height": height,
        "padding": {"top": 10, "right": 14, "bottom": 10, "left": 14},
        "mark": {
            "type": "arc",
            "innerRadius": 62,
            "outerRadius": 102,
            "stroke": "#FFFFFF",
            "strokeWidth": 2.5,
        },
        "encoding": {
            "theta": {"field": "Slots", "type": "quantitative", "stack": True},
            "color": {
                "field": "Segment",
                "type": "nominal",
                "scale": {"domain": domain_labels, "range": range_colors},
                "legend": {"orient": "bottom", "labelColor": "#0F172A", "titleColor": "#0F172A"},
            },
            "tooltip": [
                {"field": "Segment", "type": "nominal", "title": "Category"},
                {"field": "Slots", "type": "quantitative", "title": "Count / Slots"},
            ],
        },
        "title": {"text": f"{district_name} ({status_name})", "color": "#0F172A", "fontSize": 13.5},
        "config": _base_vl_config(),
    }
    st.vega_lite_chart(donut_df, spec, use_container_width=True)


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    *, *::before, *::after {
        box-sizing: border-box;
    }

    :root, .stApp {
        --text-color: #0F172A !important;
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        max-width: 100% !important;
        background-color: #FFFFFF !important;
        padding: 16px 18px !important;
    }

    .dashboard-chart-card {
        background: #F8FAFC;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 24px 24px 22px 24px;
        margin-bottom: 18px;
        width: 100%;
    }

    .dashboard-chart-title {
        font-size: clamp(26px, 2.2vw, 32px);
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
        margin: 0 0 6px 0;
    }

    .dashboard-chart-subtitle {
        font-size: 14px;
        font-weight: 500;
        color: #475569;
        line-height: 1.4;
        margin: 0 0 18px 0;
    }

    .dashboard-chart-canvas {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 12px 14px;
        width: 100%;
        min-height: 416px;
    }

    @media (max-width: 900px) {
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
    }

    header[data-testid="stHeader"] {
        background-color: #FFFFFF !important;
        border-bottom: none !important;
        position: relative !important;
        overflow: visible !important;
    }

    header[data-testid="stHeader"]::after {
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        bottom: -14px;
        width: 100%;
        height: 14px;
        pointer-events: none;
        z-index: 5;
        background-color: transparent;
        background-repeat: repeat-x;
        background-position: left bottom;
        background-size: 72px 14px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='72' height='14' viewBox='0 0 72 14'%3E%3Cpath d='M0,1.5 H9.5 A2.5,2.5 0 0,1 14.5,1.5 H24 V4.5 A2.5,2.5 0 0,1 24,9.5 V12.5 H14.5 A2.5,2.5 0 0,0 9.5,12.5 H0 Z' fill='%232563EB'/%3E%3Cpath d='M24,1.5 H33.5 A2.5,2.5 0 0,0 38.5,1.5 H48 V4.5 A2.5,2.5 0 0,0 48,9.5 V12.5 H38.5 A2.5,2.5 0 0,1 33.5,12.5 H24 V9.5 A2.5,2.5 0 0,0 24,4.5 Z' fill='%23EF4444'/%3E%3Cpath d='M48,1.5 H57.5 A2.5,2.5 0 0,1 62.5,1.5 H72 V12.5 H62.5 A2.5,2.5 0 0,0 57.5,12.5 H48 V9.5 A2.5,2.5 0 0,1 48,4.5 Z' fill='%23FACC15'/%3E%3C/svg%3E");
    }

    [data-testid="stSidebar"] {
        background-color: #0F294A !important;
        border-right: 1px solid #1E3A5F !important;
    }

    [data-testid="stSidebar"] * {
        color: #F8FAFC !important;
        opacity: 1 !important;
    }

    .sidebar-brand {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 12px;
        padding: 14px 12px;
        margin-bottom: 14px;
    }

    .sidebar-section-label {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #5EEAD4 !important;
        margin: 14px 0 6px 4px;
    }

    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] .stButton > button * {
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
        background-color: rgba(255, 255, 255, 0.06) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        border-radius: 9px !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"],
    [data-testid="stSidebar"] .stButton > button[kind="primary"] * {
        background-color: #0D9488 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: 1px solid #14B8A6 !important;
    }

    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] h4,
    [data-testid="stMain"] [data-testid="stWidgetLabel"],
    [data-testid="stMain"] [data-testid="stWidgetLabel"] *,
    [data-testid="stMain"] [data-testid="stMetricLabel"],
    [data-testid="stMain"] [data-testid="stMetricLabel"] *,
    [data-testid="stMain"] [data-testid="stMetricValue"],
    [data-testid="stMain"] [data-testid="stMetricValue"] *,
    [data-testid="stMain"] [data-testid="stCaptionContainer"],
    [data-testid="stMain"] [data-testid="stCaptionContainer"] * {
        color: #0F172A !important;
        opacity: 1 !important;
    }

    [data-testid="stMain"] .stButton > button[kind="secondary"],
    [data-testid="stMain"] .stButton > button[kind="secondary"] * {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #94A3B8 !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    [data-testid="stMain"] .stButton > button[kind="primary"],
    [data-testid="stMain"] .stButton > button[kind="primary"] *,
    [data-testid="stMain"] .stFormSubmitButton > button,
    [data-testid="stMain"] .stFormSubmitButton > button *,
    [data-testid="stMain"] [data-testid="stDownloadButton"] > button,
    [data-testid="stMain"] [data-testid="stDownloadButton"] > button * {
        background-color: #0F294A !important;
        color: #FFFFFF !important;
        border: 1px solid #0F294A !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    [data-testid="stMain"] [data-testid="stVegaLiteChart"],
    [data-testid="stMain"] [data-testid="stVegaLiteChart"] > div {
        background-color: #FFFFFF !important;
        border-radius: 8px;
        width: 100% !important;
        padding: 0 !important;
    }

    .gov-header-banner {
        position: relative;
        overflow: hidden;
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }

    .gov-header-banner > div {
        position: relative;
        z-index: 2;
    }

    .dark-summary-banner {
        background: #162438;
        color: #FFFFFF !important;
        border-radius: 10px;
        padding: 13px 16px;
        margin: 10px 0;
        font-size: 13.5px;
        font-weight: 600;
        line-height: 1.45;
    }

    .dark-summary-banner * {
        color: #FFFFFF !important;
    }

    .saved-centre-pill {
        background-color: #E6F4F1;
        color: #0F766E;
        border: 1px solid #0F766E;
        border-radius: 8px;
        padding: 9px 12px;
        font-size: 13px;
        font-weight: 700;
        text-align: center;
    }

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-top: 4px solid #0F294A;
        border-radius: 12px;
        padding: 16px 18px;
        max-width: 100%;
        overflow-wrap: anywhere;
    }

    .kpi-card.teal { border-top-color: #0D9488; }
    .kpi-card.lblue { border-top-color: #0284C7; }
    .kpi-title { font-size: 12px; font-weight: 700; text-transform: uppercase; color: #0F172A; margin-bottom: 6px; }
    .kpi-num { font-size: 30px; font-weight: 800; color: #0F172A; line-height: 1.1; }
    .kpi-sub { font-size: 12px; color: #334155; font-weight: 600; margin-top: 5px; }

    .box6-kpi-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 36px 24px;
        height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    .box6-kpi-number {
        font-size: clamp(54px, 5vw, 72px);
        font-weight: 800;
        color: #0F294A;
        line-height: 1.05;
        margin-bottom: 14px;
    }

    .box6-kpi-label {
        font-size: 16px;
        font-weight: 600;
        color: #334155;
        line-height: 1.45;
    }

    .status-badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 11.5px; font-weight: 700; }
    .badge-approved { background: #CCFBF1; color: #0F172A; border: 1px solid #0D9488; }
    .badge-pending { background: #FEF3C7; color: #0F172A; border: 1px solid #D97706; }
    .badge-rejected { background: #FEE2E2; color: #0F172A; border: 1px solid #DC2626; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Admin Dashboard"
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "Administrator"
if "logged_out" not in st.session_state:
    st.session_state["logged_out"] = False
if "analytics_selected_district" not in st.session_state:
    st.session_state["analytics_selected_district"] = "Kota Bharu"
if "latest_recommendation_context" not in st.session_state:
    init_centres = load_centres_df()
    def_lat, def_lon = 6.1180, 102.2480
    def_top3 = compute_top_3_centres(
        def_lat, def_lon, ["Speech Therapy", "Occupational Sensory"], init_centres
    )
    st.session_state["latest_recommendation_context"] = {
        "reg_code": "REG-PREVIEW",
        "child_name": "Aisyah Humaira",
        "age": 6,
        "diagnosis": "Mild Autism",
        "residential_address": "Jalan Sultan Yahya Petra, 15150 Kota Bharu, Kelantan",
        "district": "Kota Bharu",
        "home_lat": def_lat,
        "home_lon": def_lon,
        "required_services": ["Speech Therapy", "Occupational Sensory"],
        "parent_name": "Noraini binti Ismail",
        "parent_contact": "012-987 6543",
        "top3": def_top3,
        "focused_rank": 0,
        "selected_centre": def_top3[0]["centre_name"] if def_top3 else "",
        "just_submitted": False,
    }
if "open_flipbook_key" not in st.session_state:
    st.session_state["open_flipbook_key"] = None
for m in MODULES_4:
    pk = f"fb_page_{m['key']}"
    if pk not in st.session_state:
        st.session_state[pk] = 0


def navigate_to(page_name: str, role_hint: str | None = None):
    st.session_state["active_page"] = page_name
    st.session_state["logged_out"] = False
    if role_hint:
        st.session_state["user_role"] = role_hint


with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <div style="font-size: 15px;font-weight:800; line-height:1.25;color:#FFFFFF;">Kelantan Autism GIS Portal</div>
            <div style="font-size: 11.5px;color:#99F6E4;font-weight:600;margin-top:2px;">Healthcare Service Management</div>
            <div style="margin-top:10px;padding-top:8px;border-top: 1px solid rgba(255,255,255,0.14); font-size: 11.5px; color:#FFFFFF;">
                Active Role: <strong>{html.escape(st.session_state['user_role'])}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-section-label">ADMIN PORTAL</div>', unsafe_allow_html=True)
    admin_nav = [
        ("Admin Dashboard", "Admin Dashboard"),
        ("Student Registry", "Student Registry"),
        ("Student Registration Records", "Student Registration Records"),
        ("GIS Accessibility Map", "GIS Accessibility Map"),
        ("Autism Centre Management", "Autism Centre Management"),
        ("Accessibility Analytics", "Accessibility Analytics"),
    ]
    for btn_txt, page_target in admin_nav:
        is_active = (st.session_state["active_page"] == page_target) and not st.session_state["logged_out"]
        if st.button(btn_txt, key=f"nav_{page_target}", type="primary" if is_active else "secondary"):
            navigate_to(page_target, "Administrator")
            st.rerun()

    st.markdown('<div class="sidebar-section-label">PARENTS PORTAL</div>', unsafe_allow_html=True)
    parent_nav = [
        ("Parents Dashboard", "Parents Dashboard"),
        ("Child Registration", "Child Registration"),
        ("Find Suitable Centres", "Find Suitable Centres"),
        ("Learning Modules", "Learning Modules"),
        ("Registration History", "Registration History"),
    ]
    for btn_txt, page_target in parent_nav:
        is_active = (st.session_state["active_page"] == page_target) and not st.session_state["logged_out"]
        if st.button(btn_txt, key=f"nav_{page_target}", type="primary" if is_active else "secondary"):
            navigate_to(page_target, "Parent / Guardian")
            st.rerun()

    st.markdown("<hr style='border-color:rgba(255,255,255,0.15);margin:14px 0 10px 0;'>", unsafe_allow_html=True)
    is_settings = (st.session_state["active_page"] == "Settings") and not st.session_state["logged_out"]
    if st.button("Settings", key="nav_Settings", type="primary" if is_settings else "secondary"):
        navigate_to("Settings")
        st.rerun()
    if st.button("Logout", key="nav_Logout", type="secondary"):
        st.session_state["logged_out"] = True
        st.rerun()

if st.session_state["logged_out"]:
    st.markdown(
        """
        <div class="gov-header-banner">
            <div>
                <div style="font-size:20px;font-weight:800;color:#0F172A;">Kelantan Autism GIS Session Signed Out</div>
                <div style="font-size:13px;color:#334155;">Select a portal role below to sign back into the Kelantan Healthcare GIS Management System.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with st.container(border=True):
            st.subheader("Administrator Portal Sign-In")
            st.write("Manage student registries, verify parent registration submissions, update autism centres, and analyze district accessibility gaps.")
            if st.button("Sign In as Administrator", type="primary", use_container_width=True):
                navigate_to("Admin Dashboard", "Administrator")
                st.rerun()
    with c2:
        with st.container(border=True):
            st.subheader("Parents & Guardian Portal Sign-In")
            st.write("Register your child, automatically locate the 3 most suitable autism centres on the Kelantan GIS map, and access interactive flipbook guides.")
            if st.button("Sign In as Parent / Guardian", type="primary", use_container_width=True):
                navigate_to("Parents Dashboard", "Parent / Guardian")
                st.rerun()
    st.stop()


def render_kelantan_choropleth_map(
    access_df: pd.DataFrame,
    centres_df: pd.DataFrame,
    selected_district: str = "All Districts",
    map_height: int = 510,
):
    geojson_str = json.dumps(KELANTAN_GEOJSON)
    access_map = {row["district"]: row.to_dict() for _, row in access_df.iterrows()}
    access_json = json.dumps(access_map)
    centres_json = json.dumps(centres_df.to_dict(orient="records") if not centres_df.empty else [])
    sel_dist_json = json.dumps(selected_district)

    html_code = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
html, body {{
    margin: 0; padding: 0; font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    background: #FFFFFF; color: #0F172A;
}}
#map {{
    width: 100%; height: {map_height - 56}px; border-radius: 10px;
    border: 1px solid #CBD5E1; background: #E2E8F0;
}}
.legend-bar {{
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 10px; padding: 10px 4px 2px 4px;
    font-size: 12px; font-weight: 600; color: #0F172A;
}}
.legend-items {{ display: flex; gap: 14px; flex-wrap: wrap; }}
.lg-item {{ display: flex; align-items: center; gap: 6px; color: #0F172A; }}
.lg-swatch {{ width: 14px; height: 14px; border-radius: 4px; border: 1px solid rgba(0,0,0,0.3); }}
.dist-label {{
    background: rgba(255,255,255,0.94); border: 1px solid #64748B;
    border-radius: 5px; padding: 1px 5px; font-size: 10px; font-weight: 700;
    color: #0F172A; white-space: nowrap; text-align: center;
}}
</style>
</head>
<body>
<div id="map"></div>
<div class="legend-bar">
    <div class="legend-items">
        <div class="lg-item"><span class="lg-swatch" style="background:#0D9488;"></span>Green: Good Accessibility</div>
        <div class="lg-item"><span class="lg-swatch" style="background:#EAB308;"></span>Yellow: Moderate Accessibility</div>
        <div class="lg-item"><span class="lg-swatch" style="background:#DC2626;"></span>Red: Poor Accessibility</div>
        <div class="lg-item"><span class="lg-swatch" style="background:#0F294A; border-radius:999px;"></span>Autism Centre</div>
    </div>
    <div style="color:#0F172A;">Scope: Kelantan State (10 Districts)</div>
</div>
<script>
const kelantanGeo = {geojson_str};
const accessData = {access_json};
const centres = {centres_json};
const selectedDist = {sel_dist_json};
const kelantanBounds = L.latLngBounds([4.50, 101.40], [6.32, 102.62]);
const map = L.map('map', {{
    maxBounds: kelantanBounds,
    maxBoundsViscosity: 0.9,
    minZoom: 8,
    maxZoom: 16
}});
L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '&copy; OpenStreetMap contributors'
}}).addTo(map);
let targetLayer = null;
const geoLayer = L.geoJSON(kelantanGeo, {{
    style: function(feature) {{
        const dName = feature.properties.district;
        const info = accessData[dName] || {{ fill_hex: "#94A3B8" }};
        const isSelected = (selectedDist !== "All Districts" && dName === selectedDist);
        return {{
            fillColor: info.fill_hex,
            weight: isSelected ? 3.5 : 1.8,
            opacity: 1,
            color: isSelected ? "#0F294A" : "#FFFFFF",
            fillOpacity: isSelected ? 0.62 : 0.45
        }};
    }},
    onEachFeature: function(feature, layer) {{
        const dName = feature.properties.district;
        const info = accessData[dName] || {{}};
        if (selectedDist !== "All Districts" && dName === selectedDist) {{
            targetLayer = layer;
        }}
        layer.bindPopup(
            `<div style="font-family:Inter,sans-serif; min-width:210px;line-height:1.45;color:#0F172A;">` +
            `<div style="font-size:14px;font-weight:800;border-bottom:1px solid #CBD5E1;padding-bottom:4px;margin-bottom:6px;">${{dName}} District</div>` +
            `<div><strong>Accessibility:</strong> ${{info.status_label || "N/A"}}</div>` +
            `<div><strong>Registered Students:</strong> ${{info.students ?? 0}}</div>` +
            `<div><strong>Available Centres:</strong> ${{info.centres ?? 0}}</div>` +
            `<div><strong>Total Slot Capacity:</strong> ${{info.total_capacity ?? 0}}</div>` +
            `<div><strong>Student-to-Centre Ratio:</strong> ${{info.student_per_centre ?? 0}}:1</div>` +
            `</div>`
        );
        const center = layer.getBounds().getCenter();
        L.marker(center, {{
            interactive: false,
            icon: L.divIcon({{
                className: "",
                html: `<div class="dist-label">${{dName}} (${{info.students ?? 0}}s / ${{info.centres ?? 0}}c)</div>`,
                iconSize: [125, 20],
                iconAnchor: [62, 10]
            }})
        }}).addTo(map);
    }}
}}).addTo(map);
if (targetLayer) {{
    map.fitBounds(targetLayer.getBounds(), {{ padding: [35, 35] }});
}} else {{
    map.fitBounds(geoLayer.getBounds(), {{ padding: [15, 15] }});
}}
centres.forEach(c => {{
    if (selectedDist !== "All Districts" && c.district !== selectedDist) return;
    const markerIcon = L.divIcon({{
        className: "",
        html: `<div style="width:24px;height:24px;border-radius:999px;background:#0F294A;border:2.5px solid #FFFFFF;color:#FFFFFF;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;">C</div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    }});
    const m = L.marker([c.lat, c.lon], {{ icon: markerIcon }}).addTo(map);
    m.bindPopup(
        `<div style="font-family:Inter,sans-serif;min-width:230px;line-height:1.45;color:#0F172A;">` +
        `<div style="font-size:13.5px;font-weight:800;margin-bottom:4px;">${{c.centre_name}}</div>` +
        `<div style="font-size:11.5px;font-weight:700;margin-bottom:6px;">${{c.category}} - ${{c.district}}</div>` +
        `<div style="font-size:12px;"><strong>Address:</strong> ${{c.address}}</div>` +
        `<div style="font-size:12px;"><strong>Services:</strong> ${{c.services}}</div>` +
        `<div style="font-size:12px;"><strong>Hours:</strong> ${{c.hours}}</div>` +
        `<div style="font-size:12px;"><strong>Contact:</strong> ${{c.contact}} | <strong>Capacity:</strong> ${{c.capacity}}</div>` +
        `</div>`
    );
}});
</script>
</body>
</html>"""
    components.html(html_code, height=map_height, scrolling=False)


def render_recommendation_gis_map(
    access_df: pd.DataFrame,
    rec_ctx: dict,
    map_height: int = 500,
):
    geojson_str = json.dumps(KELANTAN_GEOJSON)
    access_map = {row["district"]: row.to_dict() for _, row in access_df.iterrows()}
    access_json = json.dumps(access_map)
    ctx_json = json.dumps(rec_ctx)

    html_code = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
html, body {{
    margin: 0; padding: 0; font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    background: #FFFFFF; color: #0F172A;
}}
#recMap {{
    width: 100%; height: {map_height - 54}px; border-radius: 10px;
    border: 1px solid #CBD5E1; background: #E2E8F0;
}}
@keyframes dashFlow {{
    to {{ stroke-dashoffset: -36; }}
}}
.house-pin {{
    width: 34px; height: 34px; border-radius: 999px;
    background: #0F294A; border: 3px solid #FFFFFF;
    color: #FFFFFF; font-size: 13px; font-weight: 800;
    display: flex; align-items: center; justify-content: center;
}}
.num-pin {{
    width: 34px; height: 34px; border-radius: 999px;
    border: 3px solid #FFFFFF; color: #FFFFFF;
    font-size: 15px; font-weight: 800;
    display: flex; align-items: center; justify-content: center;
}}
.num-pin.active-focus {{
    transform: scale(1.22);
    border: 3.5px solid #FACC15;
}}
.animated-route {{
    animation: dashFlow 1.2s linear infinite;
}}
.legend-strip {{
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 10px; padding: 9px 4px 2px 4px;
    font-size: 12px; font-weight: 600; color: #0F172A;
}}
</style>
</head>
<body>
<div id="recMap"></div>
<div class="legend-strip">
    <div style="display: flex; gap:14px; flex-wrap:wrap; color:#0F172A;">
        <span><strong>H = Child's Home</strong></span>
        <span><span style="display:inline-block;width:12px;height:12px;border-radius:999px;background:#0D9488;vertical-align:middle;"></span> <strong>#1 Best Match</strong></span>
        <span><span style="display:inline-block;width:12px;height:12px;border-radius:999px;background:#0284C7;vertical-align:middle;"></span> <strong>#2 Second Match</strong></span>
        <span><span style="display:inline-block;width:12px;height:12px;border-radius:999px;background:#0F294A;vertical-align:middle;"></span> <strong>#3 Third Match</strong></span>
    </div>
    <div style="color:#0F172A;">Kelantan GIS Spatial Matcher</div>
</div>
<script>
const kelantanGeo = {geojson_str};
const accessData = {access_json};
const ctx = {ctx_json};
const kelantanBounds = L.latLngBounds([4.50, 101.40], [6.32, 102.62]);
const map = L.map('recMap', {{
    maxBounds: kelantanBounds,
    maxBoundsViscosity: 0.9,
    minZoom: 8,
    maxZoom: 16
}});
L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '&copy; OpenStreetMap contributors'
}}).addTo(map);
L.geoJSON(kelantanGeo, {{
    style: function(feature) {{
        const dName = feature.properties.district;
        const info = accessData[dName] || {{ fill_hex: "#94A3B8" }};
        const isHomeDist = (dName === ctx.district);
        return {{
            fillColor: info.fill_hex,
            weight: isHomeDist ? 2.5 : 1.2,
            opacity: 1,
            color: isHomeDist ? "#0F294A" : "#FFFFFF",
            fillOpacity: isHomeDist ? 0.28 : 0.14
        }};
    }}
}}).addTo(map);
const homeLatLng = [ctx.home_lat, ctx.home_lon];
const houseIcon = L.divIcon({{
    className: "",
    html: `<div class="house-pin" title="Child Residential Location">H</div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17]
}});
const homeMarker = L.marker(homeLatLng, {{ icon: houseIcon, zIndexOffset: 1000 }}).addTo(map);
homeMarker.bindPopup(
    `<div style="font-family:Inter,sans-serif;min-width:210px;line-height:1.45; color:#0F172A;">` +
    `<div style="font-size:13.5px;font-weight:800;">Child's Residential Location</div>` +
    `<div style="font-size:12.5px;font-weight:700;margin:3px 0;">${{ctx.child_name}} (Age ${{ctx.age}})</div>` +
    `<div style="font-size:12px;"><strong>District:</strong> ${{ctx.district}}</div>` +
    `<div style="font-size:12px;"><strong>Address:</strong> ${{ctx.residential_address}}</div>` +
    `<div style="font-size:12px;"><strong>Required:</strong> ${{(ctx.required_services || []).join(", ")}}</div>` +
    `</div>`
);
const rankColors = {{ 1: "#0D9488", 2: "#0284C7", 3: "#0F294A" }};
const allPoints = [homeLatLng];
const centreMarkers = {{}};
(ctx.top3 || []).forEach(c => {{
    const cLatLng = [c.lat, c.lon];
    allPoints.push(cLatLng);
    const col = rankColors[c.rank] || "#0D9488";
    const isFocused = (ctx.focused_rank === c.rank);
    L.polyline([homeLatLng, cLatLng], {{
        color: col,
        weight: isFocused ? 4.5 : 3,
        opacity: isFocused ? 0.95 : 0.78,
        dashArray: "10, 8",
        className: "animated-route"
    }}).addTo(map);
    const midLat = (homeLatLng[0] + cLatLng[0]) / 2;
    const midLon = (homeLatLng[1] + cLatLng[1]) / 2;
    L.marker([midLat, midLon], {{
        interactive: false,
        icon: L.divIcon({{
            className: "",
            html: `<div style="background:#FFFFFF;border:1.5px solid ${{col}}; color:#0F172A; border-radius:999px; padding:1px 7px; font-size:10.5px; font-weight:800; white-space:nowrap;">#${{c.rank}}: ${{c.distance_km}} km</div>`,
            iconSize: [78, 20],
            iconAnchor: [39, 10]
        }})
    }}).addTo(map);
    const focusClass = isFocused ? "active-focus" : "";
    const numIcon = L.divIcon({{
        className: "",
        html: `<div class="num-pin ${{focusClass}}" style="background:${{col}};">${{c.rank}}</div>`,
        iconSize: [34, 34],
        iconAnchor: [17, 17]
    }});
    const m = L.marker(cLatLng, {{ icon: numIcon, zIndexOffset: 900 - c.rank }}).addTo(map);
    m.bindPopup(
        `<div style="font-family:Inter,sans-serif;min-width:240px;line-height:1.45;color:#0F172A;">` +
        `<div style="display:inline-block;background:${{col}}; color:#FFFFFF; font-size:11px; font-weight:800; padding:2px 8px; border-radius:999px; margin-bottom:4px;">#${{c.rank}} - ${{c.suitability_pct}}% Suitability</div>` +
        `<div style="font-size:14px;font-weight:800;">${{c.centre_name}}</div>` +
        `<div style="font-size:12px;font-weight:700;margin:3px 0;">Distance from Home: ${{c.distance_km}} km</div>` +
        `<div style="font-size:12px;"><strong>Address:</strong> ${{c.address}}</div>` +
        `<div style="font-size:12px;"><strong>Services:</strong> ${{c.services}}</div>` +
        `<div style="font-size:12px;"><strong>Operating Hours:</strong> ${{c.hours}}</div>` +
        `<div style="font-size:12px;"><strong>Contact:</strong> ${{c.contact}}</div>` +
        `</div>`
    );
    centreMarkers[c.rank] = m;
}});
if (ctx.focused_rank && centreMarkers[ctx.focused_rank]) {{
    const targetC = ctx.top3.find(x => x.rank === ctx.focused_rank);
    map.setView(homeLatLng, 11);
    setTimeout(() => {{
        map.flyTo([targetC.lat, targetC.lon], 14, {{ animate: true, duration: 1.2 }});
        setTimeout(() => {{ centreMarkers[ctx.focused_rank].openPopup(); }}, 1250);
    }}, 350);
}} else {{
    const groupBounds = L.latLngBounds(allPoints);
    map.fitBounds(groupBounds, {{ padding: [48, 48], maxZoom: 13 }});
    setTimeout(() => {{ homeMarker.openPopup(); }}, 450);
}}
</script>
</body>
</html>"""
    components.html(html_code, height=map_height, scrolling=False)


students_df = load_students_df()
centres_df = load_centres_df()
regs_df = load_registrations_df()
access_df = compute_district_accessibility(students_df, centres_df)
therapy_dist_df = build_therapy_demand_by_district(students_df)
active_page = st.session_state["active_page"]

if active_page == "Admin Dashboard":
    total_students = int(len(students_df))
    verified_students = int((students_df["status"] == "Verified Active").sum()) if not students_df.empty else 0
    total_centres = int(len(centres_df))
    districts_covered = int((access_df["centres"] > 0).sum()) if not access_df.empty else 0

    st.markdown(
        """
        <div class="gov-header-banner">
            <div>
                <div style="font-size:21px;font-weight:800; color:#0F172A;">Executive Healthcare GIS Analytics Dashboard</div>
                <div style="font-size:13px;color:#334155;">State of Kelantan, Malaysia Real-Time Student Registry &amp; Autism Service Centre Intelligence</div>
            </div>
            <div style="background:#E0F2FE; color:#0F172A;padding:6px 12px;border-radius:8px;font-size:12px;font-weight:700;border:1px solid #0284C7;">
                10 Kelantan Districts Monitored
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-title">Total Registered Students</div><div class="kpi-num">{total_students}</div><div class="kpi-sub">Active in SQLite Registry</div></div>',
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f'<div class="kpi-card teal"><div class="kpi-title">Verified Student Records</div><div class="kpi-num">{verified_students}</div><div class="kpi-sub">{round((verified_students / max(1, total_students)) * 100, 1)}% Verification Rate</div></div>',
            unsafe_allow_html=True,
        )
    with k3:
        cap_total = int(centres_df["capacity"].sum()) if not centres_df.empty else 0
        st.markdown(
            f'<div class="kpi-card lblue"><div class="kpi-title">Total Autism Centres</div><div class="kpi-num">{total_centres}</div><div class="kpi-sub">Total Capacity: {cap_total} Slots</div></div>',
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f'<div class="kpi-card teal"><div class="kpi-title">Total Districts Covered</div><div class="kpi-num">{districts_covered} / 10</div><div class="kpi-sub">Kelantan State Districts</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    r1_c1, r1_c2 = st.columns(2, gap="large")
    with r1_c1:
        st.markdown(
            """
            <div class="dashboard-chart-card">
                <div class="dashboard-chart-title">Students by District</div>
                <div class="dashboard-chart-subtitle">Registered autism students across Kelantan districts (highest to lowest).</div>
            """,
            unsafe_allow_html=True,
        )
        render_horizontal_bar_with_labels(
            access_df[["district", "students"]],
            category_col="district",
            value_col="students",
            y_title=None,
            color="#1E3A8A",
            sort_desc=True,
            height=400,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with r1_c2:
        st.markdown(
            """
            <div class="dashboard-chart-card">
                <div class="dashboard-chart-title">Diagnosis Distribution</div>
                <div class="dashboard-chart-subtitle">Breakdown of registered students by autism diagnosis category.</div>
            """,
            unsafe_allow_html=True,
        )
        diag_counts = (
            students_df["diagnosis"].value_counts().reset_index()
            if not students_df.empty
            else pd.DataFrame(columns=["diagnosis", "count"])
        )
        render_diagnosis_donut_with_legend(diag_counts, height=400)
        st.markdown("</div>", unsafe_allow_html=True)

    r2_c1, r2_c2 = st.columns(2, gap="large")
    with r2_c1:
        st.markdown(
            """
            <div class="dashboard-chart-card">
                <div class="dashboard-chart-title">Required Therapy Services</div>
                <div class="dashboard-chart-subtitle">Student demand across required therapy service types.</div>
            """,
            unsafe_allow_html=True,
        )
        serv_counts_series = students_df["required_service"].value_counts() if not students_df.empty else pd.Series(dtype=int)
        extra_servs = [s for s in serv_counts_series.index if s not in THERAPY_SERVICES]
        serv_counts = pd.DataFrame({"Therapy Service": THERAPY_SERVICES + extra_servs})
        serv_counts["Students"] = serv_counts["Therapy Service"].map(lambda s: int(serv_counts_series.get(s, 0)))
        render_horizontal_bar_with_labels(
            serv_counts,
            category_col="Therapy Service",
            value_col="Students",
            y_title=None,
            color="#0284C7",
            sort_desc=True,
            height=400,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with r2_c2:
        st.markdown(
            """
            <div class="dashboard-chart-card">
                <div class="dashboard-chart-title">Autism Centres by District</div>
                <div class="dashboard-chart-subtitle">Active autism service centres per district (highest first).</div>
            """,
            unsafe_allow_html=True,
        )
        render_horizontal_lollipop_chart(
            access_df[["district", "centres"]],
            category_col="district",
            value_col="centres",
            y_title=None,
            color="#4338CA",
            height=400,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    r3_c1, r3_c2 = st.columns(2, gap="large")
    with r3_c1:
        st.markdown(
            """
            <div class="dashboard-chart-card">
                <div class="dashboard-chart-title">Therapy Demand by District</div>
                <div class="dashboard-chart-subtitle">ST: Speech Therapy | ABA: ABA Therapy | OT: Occupational Sensory | EI: Early Intervention</div>
            """,
            unsafe_allow_html=True,
        )
        render_therapy_heatmap(therapy_dist_df, height=400)
        st.markdown("</div>", unsafe_allow_html=True)

    with r3_c2:
        students_2026 = count_students_in_year(students_df, 2026)
        st.markdown(
            f"""
            <div class="dashboard-chart-card">
                <div class="dashboard-chart-title">Registered Students</div>
                <div class="dashboard-chart-subtitle">Annual student registration summary for 2026.</div>
                <div class="box6-kpi-card">
                    <div class="box6-kpi-number">{students_2026}</div>
                    <div class="box6-kpi-label">students registered in 2026</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    with st.expander("Inspect District Therapy Breakdown & Student Records", expanded=False):
        t_col1, t_col2 = st.columns([1.25, 1], gap="medium")
        with t_col1:
            st.markdown("**Select a District Row to Filter Student Records**")
            district_picker_df = therapy_dist_df.reset_index()
            dist_sel_event = st.dataframe(
                district_picker_df,
                key="therapy_district_picker",
                on_select="rerun",
                selection_mode="single-row",
                use_container_width=True,
                hide_index=True,
                height=210,
            )
            sel_d_rows = (dist_sel_event or {}).get("selection", {}).get("rows", [])
            if sel_d_rows:
                selected_district_click = str(district_picker_df.iloc[sel_d_rows[0]]["District"]).strip()
                matched_students = students_df[students_df["district"] == selected_district_click]
                st.markdown(f"**{html.escape(selected_district_click)}** - {len(matched_students)} student record(s)")
                st.dataframe(
                    matched_students[["record_id", "student_name", "required_service", "status"]],
                    use_container_width=True,
                    hide_index=True,
                    height=160,
                )
        with t_col2:
            st.markdown("**2026 Registered Student Records**")
            if not students_df.empty and "registered_date" in students_df.columns:
                parsed_yr = pd.to_datetime(students_df["registered_date"], errors="coerce").dt.year.astype("Int64")
                yr_2026_df = students_df[parsed_yr == 2026]
                st.dataframe(
                    yr_2026_df[["record_id", "student_name", "district", "required_service", "registered_date"]],
                    use_container_width=True,
                    hide_index=True,
                    height=210,
                )

elif active_page == "Student Registry":
    st.markdown(
        """
        <div class="gov-header-banner">
            <div>
                <div style="font-size:21px;font-weight:800;color:#0F172A;">Student Registry Management</div>
                <div style="font-size:13px;color:#334155;">Search, filter, inspect, add, edit, and delete registered autism student records.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        f1, f2, f3 = st.columns([2, 1.2, 1.2])
        search_q = f1.text_input("Search Student by Name or Record ID", placeholder="Type name or KOD-1000...")
        dist_filter = f2.selectbox("Filter by District", ["All Districts"] + KELANTAN_DISTRICTS)
        diag_filter = f3.selectbox("Filter by Diagnosis Category", ["All Categories"] + DIAGNOSIS_CATEGORIES)

        filtered_df = students_df.copy()
        if search_q.strip():
            q = search_q.strip().lower()
            filtered_df = filtered_df[
                filtered_df["student_name"].str.lower().str.contains(q, na=False)
                | filtered_df["record_id"].str.lower().str.contains(q, na=False)
            ]
        if dist_filter != "All Districts":
            filtered_df = filtered_df[filtered_df["district"] == dist_filter]
        if diag_filter != "All Categories":
            filtered_df = filtered_df[filtered_df["diagnosis"] == diag_filter]

        st.markdown(f"**Showing {len(filtered_df)} of {len(students_df)} registered students**")
        st.dataframe(
            filtered_df.rename(
                columns={
                    "record_id": "Record ID",
                    "student_name": "Student Name",
                    "age": "Age",
                    "district": "District",
                    "diagnosis": "Diagnosis Category",
                    "required_service": "Required Therapy",
                    "registered_date": "Registered Date",
                    "status": "Status",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    tab_view, tab_add, tab_edit, tab_del = st.tabs([
        "View Individual Student Profile",
        "Add New Student Record",
        "Edit Existing Record",
        "Delete Record (With Confirmation)",
    ])

    with tab_view:
        with st.container(border=True):
            if not filtered_df.empty:
                sel_rec_id = st.selectbox(
                    "Select Student Record to Inspect",
                    options=filtered_df["record_id"].tolist(),
                    format_func=lambda rid: f"{rid} - {filtered_df[filtered_df['record_id'] == rid]['student_name'].values[0]}",
                )
                s_row = filtered_df[filtered_df["record_id"] == sel_rec_id].iloc[0]
                v1, v2, v3 = st.columns(3)
                v1.metric("Student Name", s_row["student_name"])
                v2.metric("District & Age", f"{s_row['district']} - Age {s_row['age']}")
                v3.metric("Verification Status", s_row["status"])
                st.markdown(
                    f"""
                    <div class="dark-summary-banner">
                        Diagnosis Category: {html.escape(str(s_row['diagnosis']))} &nbsp;|&nbsp;
                        Registered Therapy Requirement: {html.escape(str(s_row['required_service']))} &nbsp;|&nbsp;
                        Date Registered: {html.escape(str(s_row['registered_date']))}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.warning("No student matches the current search/filter criteria.")

    with tab_add:
        with st.container(border=True):
            with st.form("add_student_registry_form", clear_on_submit=True):
                a1, a2, a3, a4 = st.columns(4)
                next_num = 1000 + len(students_df)
                new_rid = a1.text_input("Record ID", value=f"KOD-{next_num}")
                new_sname = a2.text_input("Student Full Name", placeholder="e.g., Ahmad Zikri bin Roslan")
                new_sage = a3.number_input("Age", min_value=1, max_value=21, value=6)
                new_sdist = a4.selectbox("District", KELANTAN_DISTRICTS)

                a5, a6, a7, a8 = st.columns(4)
                new_sdiag = a5.selectbox("Diagnosis Category", DIAGNOSIS_CATEGORIES)
                new_sserv = a6.selectbox("Required Therapy", THERAPY_SERVICES)
                new_sdate = a7.text_input("Registered Date", value=datetime.now().strftime("%Y-%m-%d"))
                new_sstat = a8.selectbox("Status", ["Verified Active", "Pending Verification"])

                if st.form_submit_button("Save New Student Record", type="primary"):
                    if not new_sname.strip() or not new_rid.strip():
                        st.error("Please enter both Record ID and Student Name.")
                    else:
                        conn = get_conn()
                        try:
                            conn.execute(
                                """
                                INSERT INTO students
                                (record_id, student_name, age, district, diagnosis, required_service, registered_date, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    new_rid.strip(), new_sname.strip(), int(new_sage),
                                    normalize_district_name(new_sdist), normalize_diagnosis_name(new_sdiag),
                                    normalize_service_name(new_sserv), new_sdate.strip(), new_sstat,
                                ),
                            )
                            conn.commit()
                            st.success(f"Student record {new_rid.strip()} added to database!")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("Record ID already exists. Please use a unique Record ID.")
                        finally:
                            conn.close()

    with tab_edit:
        with st.container(border=True):
            if not students_df.empty:
                edit_rid = st.selectbox(
                    "Choose Record to Edit",
                    options=students_df["record_id"].tolist(),
                    format_func=lambda rid: f"{rid} - {students_df[students_df['record_id'] == rid]['student_name'].values[0]}",
                    key="edit_student_select",
                )
                cur_s = students_df[students_df["record_id"] == edit_rid].iloc[0]
                with st.form("edit_student_form"):
                    e1, e2, e3 = st.columns(3)
                    ed_name = e1.text_input("Student Name", value=cur_s["student_name"])
                    ed_age = e2.number_input("Age", min_value=1, max_value=21, value=int(cur_s["age"]))
                    ed_dist = e3.selectbox(
                        "District",
                        KELANTAN_DISTRICTS,
                        index=KELANTAN_DISTRICTS.index(cur_s["district"]) if cur_s["district"] in KELANTAN_DISTRICTS else 0,
                    )
                    e4, e5, e6 = st.columns(3)
                    stat_opts = ["Verified Active", "Pending Verification"]
                    ed_diag = e4.selectbox(
                        "Diagnosis Category",
                        DIAGNOSIS_CATEGORIES,
                        index=DIAGNOSIS_CATEGORIES.index(cur_s["diagnosis"]) if cur_s["diagnosis"] in DIAGNOSIS_CATEGORIES else 0,
                    )
                    ed_serv = e5.selectbox(
                        "Required Therapy",
                        THERAPY_SERVICES,
                        index=THERAPY_SERVICES.index(cur_s["required_service"]) if cur_s["required_service"] in THERAPY_SERVICES else 0,
                    )
                    ed_stat = e6.selectbox(
                        "Status",
                        stat_opts,
                        index=stat_opts.index(cur_s["status"]) if cur_s["status"] in stat_opts else 0,
                    )
                    if st.form_submit_button("Update Student Record", type="primary"):
                        conn = get_conn()
                        conn.execute(
                            """
                            UPDATE students
                            SET student_name=?, age=?, district=?, diagnosis=?, required_service=?, status=?
                            WHERE record_id=?
                            """,
                            (
                                ed_name.strip(), int(ed_age), normalize_district_name(ed_dist),
                                normalize_diagnosis_name(ed_diag), normalize_service_name(ed_serv),
                                ed_stat, edit_rid,
                            ),
                        )
                        conn.commit()
                        conn.close()
                        st.success(f"Updated record {edit_rid}!")
                        st.rerun()

    with tab_del:
        with st.container(border=True):
            if not students_df.empty:
                del_rid = st.selectbox(
                    "Select Student Record to Delete",
                    options=students_df["record_id"].tolist(),
                    format_func=lambda rid: f"{rid} - {students_df[students_df['record_id'] == rid]['student_name'].values[0]}",
                    key="del_student_select",
                )
                confirm_del = st.checkbox(f"I confirm that I want to permanently delete student record {del_rid}.")
                if st.button("Delete Selected Student Record", type="primary", disabled=not confirm_del):
                    conn = get_conn()
                    conn.execute("DELETE FROM students WHERE record_id=?", (del_rid,))
                    conn.commit()
                    conn.close()
                    st.success(f"Deleted record {del_rid}.")
                    st.rerun()

elif active_page == "Student Registration Records":
    st.markdown(
        """
        <div class="gov-header-banner">
            <div>
                <div style="font-size:21px;font-weight:800; color:#0F172A;">Parent Registration Submissions &amp; Verification</div>
                <div style="font-size:13px;color:#334155;">Review parent-submitted child profiles, contact details, therapy requirements, and approve or reject placements.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if regs_df.empty:
        st.info("No parent registration submissions found yet.")
    else:
        with st.container(border=True):
            status_f = st.selectbox("Filter by Registration Status", ["All", "Pending", "Approved", "Rejected"])
            view_regs = regs_df if status_f == "All" else regs_df[regs_df["status"] == status_f]
            st.dataframe(
                view_regs[[
                    "reg_code", "child_name", "age", "diagnosis", "district",
                    "required_services", "parent_name", "parent_contact", "selected_centre", "status",
                    "submitted_at",
                ]].rename(
                    columns={
                        "reg_code": "Reg Code",
                        "child_name": "Child Name",
                        "age": "Age",
                        "diagnosis": "Diagnosis",
                        "district": "District",
                        "required_services": "Therapy Required",
                        "parent_name": "Parent Name",
                        "parent_contact": "Contact Number",
                        "selected_centre": "Preferred Centre",
                        "status": "Status",
                        "submitted_at": "Submitted",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

        st.subheader("Inspect Submission & Update Approval Status")
        for _, r in view_regs.iterrows():
            badge_cls = (
                "badge-approved"
                if r["status"] == "Approved"
                else ("badge-rejected" if r["status"] == "Rejected" else "badge-pending")
            )
            with st.container(border=True):
                h1, h2 = st.columns([3.2, 1], vertical_alignment="center")
                with h1:
                    st.markdown(
                        f"**{r['reg_code']} - {r['child_name']}** (Age {r['age']} - {r['diagnosis']}) "
                        f"<span class='status-badge {badge_cls}'>{r['status']}</span>",
                        unsafe_allow_html=True,
                    )
                    st.write(
                        f"**Parent:** {r['parent_name']} ({r['parent_contact']}) | "
                        f"**District:** {r['district']} | **Address:** {r['residential_address']}"
                    )
                    st.write(
                        f"**Required Therapy:** {r['required_services']} | "
                        f"**Selected Preferred Centre:** {r['selected_centre'] or 'Not yet selected'}"
                    )
                    rec_list = []
                    try:
                        rec_list = json.loads(r["recommended_centres_json"]) if r["recommended_centres_json"] else []
                    except Exception:
                        rec_list = []
                    if not rec_list:
                        req_s = [x.strip() for x in str(r["required_services"]).split(",") if x.strip()]
                        rec_list = compute_top_3_centres(float(r["home_lat"]), float(r["home_lon"]), req_s, centres_df)
                    rec_summary = " | ".join(
                        [f"#{x['rank']} {x['centre_name']} ({x['distance_km']} km, {x['suitability_pct']}%)" for x in rec_list]
                    )
                    st.caption(f"System Recommended Centres: {rec_summary}")
                with h2:
                    if st.button("Approve", key=f"app_{r['id']}", type="primary", use_container_width=True):
                        conn = get_conn()
                        conn.execute("UPDATE parent_registrations SET status='Approved' WHERE id=?", (int(r["id"]),))
                        rec_student_id = f"REG-{r['id']}"
                        cur = conn.cursor()
                        cur.execute("SELECT COUNT(*) FROM students WHERE record_id=?", (rec_student_id,))
                        if cur.fetchone()[0] == 0:
                            primary_serv = normalize_service_name(str(r["required_services"]).split(",")[0])
                            conn.execute(
                                """
                                INSERT INTO students
                                (record_id, student_name, age, district, diagnosis, required_service, registered_date, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    rec_student_id, r["child_name"], int(r["age"]),
                                    normalize_district_name(r["district"]), normalize_diagnosis_name(r["diagnosis"]),
                                    primary_serv, datetime.now().strftime("%Y-%m-%d"), "Verified Active",
                                ),
                            )
                        conn.commit()
                        conn.close()
                        st.success(f"{r['reg_code']} approved and synced to Student Registry!")
                        st.rerun()
                    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
                    if st.button("Reject", key=f"rej_{r['id']}", type="secondary", use_container_width=True):
                        conn = get_conn()
                        conn.execute("UPDATE parent_registrations SET status='Rejected' WHERE id=?", (int(r["id"]),))
                        conn.commit()
                        conn.close()
                        st.warning(f"{r['reg_code']} marked as Rejected.")
                        st.rerun()

elif active_page == "GIS Accessibility Map":
    st.markdown(
        """
        <div class="gov-header-banner">
            <div>
                <div style="font-size:21px;font-weight:800; color:#0F172A;">Kelantan District GIS Accessibility Choropleth Map</div>
                <div style="font-size:13px;color:#334155;">District-level boundary choropleth across all 10 Kelantan districts with live autism service centre markers.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        m1, m2 = st.columns([1.4, 2.6], vertical_alignment="center")
        with m1:
            sel_map_dist = st.selectbox("Zoom to Kelantan District", ["All Districts"] + KELANTAN_DISTRICTS)
        with m2:
            st.caption(
                "Click any district boundary polygon to view registered students, available centres, "
                "slot capacity, and accessibility status. "
                "Click any marker to inspect centre operating hours, services, and contact details."
            )
        render_kelantan_choropleth_map(access_df, centres_df, selected_district=sel_map_dist, map_height=530)

    with st.container(border=True):
        st.subheader("District-by-District Spatial Summary (All 10 Kelantan Districts)")
        st.dataframe(
            access_df[["district", "students", "centres", "total_capacity", "student_per_centre", "status_label"]].rename(
                columns={
                    "district": "District",
                    "students": "Registered Students",
                    "centres": "Available Centres",
                    "total_capacity": "Total Capacity",
                    "student_per_centre": "Students per Centre",
                    "status_label": "Accessibility Status",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

elif active_page == "Autism Centre Management":
    st.markdown(
        """
        <div class="gov-header-banner">
            <div>
                <div style="font-size:21px;font-weight:800;color:#0F172A;">Autism Service Centre Management</div>
                <div style="font-size:13px;color:#334155;">Add, edit, and remove autism therapy centres. All updates immediately reflect on the Kelantan GIS Map and recommendation engine.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.subheader(f"Registered Autism Centres in Kelantan ({len(centres_df)} Centres)")
        st.dataframe(
            centres_df[["id", "centre_name", "category", "district", "address", "lat", "lon", "contact", "services", "hours", "capacity"]].rename(
                columns={
                    "id": "ID",
                    "centre_name": "Centre Name",
                    "category": "Category",
                    "district": "District",
                    "address": "Full Address",
                    "lat": "Latitude",
                    "lon": "Longitude",
                    "contact": "Contact Number",
                    "services": "Available Therapy Services",
                    "hours": "Operating Hours",
                    "capacity": "Capacity",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    c_tab1, c_tab2, c_tab3 = st.tabs(["Add New Autism Centre", "Edit Centre Details", "Delete Centre"])
    with c_tab1:
        with st.container(border=True):
            with st.form("add_centre_form", clear_on_submit=True):
                r1a, r1b, r1c = st.columns(3)
                cname = r1a.text_input("Centre Name", placeholder="e.g., Machang Pediatric Therapy Clinic")
                ccat = r1b.selectbox("Centre Category", [
                    "Government Specialist Hospital",
                    "Government Hospital Rehab",
                    "Government Health Clinic Rehab",
                    "University Teaching Hospital",
                    "NGO Special Education & Therapy",
                    "Community-Based Rehabilitation (PDK)",
                    "Private Therapy Clinic",
                ])
                cdist = r1c.selectbox("District", KELANTAN_DISTRICTS)

                r2a, r2b, r2c = st.columns([2, 1, 1])
                caddr = r2a.text_input("Full Address", placeholder="Street, Postcode, District, Kelantan")
                clat = r2b.number_input("Latitude (Kelantan: 4.55 - 6.25)", min_value=4.50, max_value=6.30, value=6.1200, format="%.5f")
                clon = r2c.number_input("Longitude (Kelantan: 101.45 - 102.55)", min_value=101.40, max_value=102.60, value=102.2400, format="%.5f")

                r3a, r3b, r3c = st.columns([1.2, 1.8, 1])
                ccontact = r3a.text_input("Contact Number", placeholder="+609-744 0000")
                cservs = r3b.multiselect("Available Therapy Services", THERAPY_SERVICES, default=["Speech Therapy", "Early Intervention"])
                ccap = r3c.number_input("Centre Capacity (Slots)", min_value=1, max_value=500, value=25)
                chours = st.text_input("Operating Hours", value="Sun-Thu: 8:30 AM - 4:30 PM")

                if st.form_submit_button("Add Centre to GIS Database", type="primary"):
                    if not cname.strip() or not caddr.strip() or not cservs:
                        st.error("Please fill in Centre Name, Address, and at least one therapy service.")
                    else:
                        conn = get_conn()
                        conn.execute(
                            """
                            INSERT INTO autism_centres
                            (centre_name, category, address, district, lat, lon, contact, services, hours, capacity)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                cname.strip(), ccat, caddr.strip(), cdist, float(clat), float(clon),
                                ccontact.strip() or "+609-000 0000", ", ".join(cservs), chours.strip(), int(ccap),
                            ),
                        )
                        conn.commit()
                        conn.close()
                        st.success(f"Added {cname.strip()}! It now appears on the Kelantan GIS Map.")
                        st.rerun()

    with c_tab2:
        with st.container(border=True):
            if not centres_df.empty:
                sel_cid = st.selectbox(
                    "Select Centre to Edit",
                    options=centres_df["id"].tolist(),
                    format_func=lambda cid: f"#{cid} - {centres_df[centres_df['id'] == cid]['centre_name'].values[0]}",
                )
                crow = centres_df[centres_df["id"] == sel_cid].iloc[0]
                with st.form("edit_centre_form"):
                    ec1, ec2, ec3 = st.columns(3)
                    e_cname = ec1.text_input("Centre Name", value=crow["centre_name"])
                    e_ccat = ec2.text_input("Category", value=crow["category"])
                    e_cdist = ec3.selectbox(
                        "District",
                        KELANTAN_DISTRICTS,
                        index=KELANTAN_DISTRICTS.index(crow["district"]) if crow["district"] in KELANTAN_DISTRICTS else 0,
                    )
                    ec4, ec5, ec6 = st.columns([2, 1, 1])
                    e_caddr = ec4.text_input("Full Address", value=crow["address"])
                    e_clat = ec5.number_input("Latitude", min_value=4.50, max_value=6.30, value=float(crow["lat"]), format="%.5f")
                    e_clon = ec6.number_input("Longitude", min_value=101.40, max_value=102.60, value=float(crow["lon"]), format="%.5f")

                    ec7, ec8, ec9 = st.columns([1.2, 1.8, 1])
                    e_ccontact = ec7.text_input("Contact Number", value=crow["contact"])
                    cur_serv_list = [s.strip() for s in str(crow["services"]).split(",") if s.strip() in THERAPY_SERVICES]
                    e_cservs = ec8.multiselect("Available Therapy Services", THERAPY_SERVICES, default=cur_serv_list or ["Early Intervention"])
                    e_ccap = ec9.number_input("Capacity", min_value=1, max_value=500, value=int(crow["capacity"]))
                    e_chours = st.text_input("Operating Hours", value=crow["hours"])

                    if st.form_submit_button("Save Centre Changes", type="primary"):
                        conn = get_conn()
                        conn.execute(
                            """
                            UPDATE autism_centres
                            SET centre_name=?, category=?, address=?, district=?, lat=?, lon=?,
                                contact=?, services=?, hours=?, capacity=?
                            WHERE id=?
                            """,
                            (
                                e_cname.strip(), e_ccat.strip(), e_caddr.strip(), e_cdist,
                                float(e_clat), float(e_clon), e_ccontact.strip(),
                                ", ".join(e_cservs), e_chours.strip(), int(e_ccap), int(sel_cid),
                            ),
                        )
                        conn.commit()
                        conn.close()
                        st.success("Centre updated on map and database!")
                        st.rerun()

    with c_tab3:
        with st.container(border=True):
            if not centres_df.empty:
                del_cid = st.selectbox(
                    "Select Centre to Delete",
                    options=centres_df["id"].tolist(),
                    format_func=lambda cid: f"#{cid} - {centres_df[centres_df['id'] == cid]['centre_name'].values[0]}",
                    key="del_centre_sel",
                )
                confirm_cdel = st.checkbox(f"Confirm permanent deletion of Centre #{del_cid}")
                if st.button("Delete Autism Centre", type="primary", disabled=not confirm_cdel):
                    conn = get_conn()
                    conn.execute("DELETE FROM autism_centres WHERE id=?", (int(del_cid),))
                    conn.commit()
                    conn.close()
                    st.success("Autism centre removed from database and GIS map.")
                    st.rerun()

elif active_page == "Accessibility Analytics":
    st.markdown(
        """
        <div class="gov-header-banner">
            <div>
                <div style="font-size:21px;font-weight:800;color:#0F172A;">Autism Service Accessibility Analysis</div>
                <div style="font-size:13px;color:#334155;">Interactive district-level spatial capacity evaluation comparing registered autism students against autism service centre slot capacity across Kelantan.</div>
            </div>
            <div style="background:#E0F2FE; color:#0F172A;padding:6px 12px;border-radius:8px;font-size:12px;font-weight:700;border:1px solid #0284C7;">
                Interactive District Drill-Down
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    critical_df = access_df[access_df["level"] == "Red"]
    moderate_df = access_df[access_df["level"] == "Yellow"]
    good_df = access_df[access_df["level"] == "Green"]

    g1, g2, g3 = st.columns(3, gap="medium")
    with g1:
        st.markdown(
            f'<div class="kpi-card" style="border-top-color:#DC2626;"><div class="kpi-title">Critical Coverage Districts (Red)</div><div class="kpi-num">{len(critical_df)}</div><div class="kpi-sub">Insufficient Service Capacity</div></div>',
            unsafe_allow_html=True,
        )
    with g2:
        st.markdown(
            f'<div class="kpi-card" style="border-top-color:#EAB308;"><div class="kpi-title">Moderate Coverage Districts (Yellow)</div><div class="kpi-num">{len(moderate_df)}</div><div class="kpi-sub">Limited Specialist Bandwidth</div></div>',
            unsafe_allow_html=True,
        )
    with g3:
        st.markdown(
            f'<div class="kpi-card teal"><div class="kpi-title">Good Coverage Districts (Green)</div><div class="kpi-num">{len(good_df)}</div><div class="kpi-sub">Sufficient Multi-Centre Support</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        sel_top_l, sel_top_r = st.columns([1.4, 2.6], vertical_alignment="center")
        with sel_top_l:
            current_dist = st.session_state["analytics_selected_district"]
            if current_dist not in KELANTAN_DISTRICTS:
                current_dist = KELANTAN_DISTRICTS[0]
            chosen_dist = st.selectbox(
                "Select Kelantan District to Analyze",
                options=KELANTAN_DISTRICTS,
                index=KELANTAN_DISTRICTS.index(current_dist),
                key="analytics_district_selectbox",
            )
            if chosen_dist != st.session_state["analytics_selected_district"]:
                st.session_state["analytics_selected_district"] = chosen_dist
                st.rerun()
        with sel_top_r:
            st.caption("Or click any district button below to dynamically update the donut chart, KPIs, classification badge, analytical explanation, and highlighted table row:")
            row1_cols = st.columns(5)
            for idx, d_name in enumerate(KELANTAN_DISTRICTS[:5]):
                is_sel = (d_name == st.session_state["analytics_selected_district"])
                if row1_cols[idx].button(d_name, key=f"dist_chip_{d_name}", type="primary" if is_sel else "secondary", use_container_width=True):
                    st.session_state["analytics_selected_district"] = d_name
                    st.rerun()
            row2_cols = st.columns(5)
            for idx, d_name in enumerate(KELANTAN_DISTRICTS[5:]):
                is_sel = (d_name == st.session_state["analytics_selected_district"])
                if row2_cols[idx].button(d_name, key=f"dist_chip_{d_name}", type="primary" if is_sel else "secondary", use_container_width=True):
                    st.session_state["analytics_selected_district"] = d_name
                    st.rerun()

    selected_district = st.session_state["analytics_selected_district"]
    dist_row = access_df[access_df["district"] == selected_district].iloc[0]
    d_students = int(dist_row["students"])
    d_centres = int(dist_row["centres"])
    d_capacity = int(dist_row["total_capacity"])
    d_ratio = float(dist_row["student_per_centre"])
    d_level = str(dist_row["level"])

    if d_students > 0:
        coverage_pct = round((d_capacity / d_students) * 100.0, 1)
    elif d_capacity > 0:
        coverage_pct = 100.0
    else:
        coverage_pct = 0.0
    utilization_pct = round((d_students / d_capacity) * 100.0, 1) if d_capacity > 0 else 0.0
    surplus_or_deficit = d_capacity - d_students

    if d_level == "Red":
        class_title = "Critical Coverage"
        badge_bg = "#FEE2E2"
        badge_border = "#DC2626"
        accent_hex = "#DC2626"
        explanation_text = (
            f"<strong>{html.escape(selected_district)}</strong> is classified under <strong>Critical Coverage (Red)</strong> because "
            f"<strong>{d_students} registered autism students</strong> rely on only <strong>{d_centres} autism service centre(s)</strong> "
            f"(<strong>{d_capacity} total slots</strong>, resulting in a <strong>{d_ratio}:1 student-to-centre ratio</strong> and "
            f"<strong>{coverage_pct}% capacity-to-demand coverage</strong>). The high concentration of student demand relative to available "
            f"specialist infrastructure indicates a critical service shortage and priority need for additional autism therapy resources."
        )
    elif d_level == "Yellow":
        class_title = "Moderate Coverage"
        badge_bg = "#FEF3C7"
        badge_border = "#EAB308"
        accent_hex = "#EAB308"
        explanation_text = (
            f"<strong>{html.escape(selected_district)}</strong> is classified under <strong>Moderate Coverage (Yellow)</strong> because "
            f"the district currently operates <strong>{d_centres} autism service centre(s)</strong> providing <strong>{d_capacity} total slots</strong> "
            f"for <strong>{d_students} registered autism students</strong> (<strong>{d_ratio}:1 student-to-centre ratio</strong>, "
            f"<strong>{utilization_pct}% slot utilization</strong>, and <strong>{coverage_pct}% capacity-to-demand ratio</strong>). "
            f"While baseline autism service capacity is available, limited specialist bandwidth may become strained as student registrations grow."
        )
    else:
        class_title = "Good Coverage"
        badge_bg = "#CCFBF1"
        badge_border = "#0D9488"
        accent_hex = "#0D9488"
        explanation_text = (
            f"<strong>{html.escape(selected_district)}</strong> is classified under <strong>Good Coverage (Green)</strong> because "
            f"<strong>{d_centres} active autism service centres</strong> offer <strong>{d_capacity} total slots</strong> against "
            f"<strong>{d_students} registered autism students</strong> (a balanced <strong>{d_ratio}:1 student-to-centre ratio</strong>, "
            f"<strong>{coverage_pct}% capacity-to-demand ratio</strong>, and <strong>{surplus_or_deficit} spare slot(s)</strong>). "
            f"Available autism service capacity is relatively sufficient compared to current registered student demand."
        )

    chart_col, analysis_col = st.columns([1.05, 1.35], gap="medium")
    with chart_col:
        with st.container(border=True):
            st.subheader(f"{selected_district} - Service Accessibility Donut")
            st.caption("Comparison of registered autism students vs. available autism centre slot capacity.")
            render_accessibility_donut_chart(
                district_name=selected_district,
                students=d_students,
                total_capacity=d_capacity,
                level=d_level,
                height=285,
            )

    with analysis_col:
        with st.container(border=True):
            hdr_l, hdr_r = st.columns([2.2, 1.2], vertical_alignment="center")
            with hdr_l:
                st.subheader(f"{selected_district} District Analysis")
            with hdr_r:
                st.markdown(
                    f"""
                    <div style="text-align:right;">
                        <span style="display:inline-block;background:{badge_bg};color:#0F172A; border:1.5px solid {badge_border};
                        padding:5px 12px; border-radius:999px;font-size:12px;font-weight:800;">
                            {class_title} ({d_level})
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            m1, m2, m3 = st.columns(3, gap="small")
            with m1:
                st.markdown(
                    f'<div class="kpi-card" style="padding:12px 12px;"><div class="kpi-title">Registered Students</div>'
                    f'<div class="kpi-num" style="font-size:clamp(18px, 1.6vw, 24px);">{d_students}</div>'
                    f'<div class="kpi-sub">Across {d_centres} Centre(s)</div></div>',
                    unsafe_allow_html=True,
                )
            with m2:
                st.markdown(
                    f'<div class="kpi-card lblue" style="padding:12px 12px;"><div class="kpi-title">Centre Slot Capacity</div>'
                    f'<div class="kpi-num" style="font-size:clamp(18px, 1.6vw, 24px);">{d_capacity}</div>'
                    f'<div class="kpi-sub">Student-to-Centre: {d_ratio}:1</div></div>',
                    unsafe_allow_html=True,
                )
            with m3:
                st.markdown(
                    f'<div class="kpi-card" style="border-top-color:{accent_hex};padding:12px 12px;">'
                    f'<div class="kpi-title">Service Coverage</div>'
                    f'<div class="kpi-num" style="font-size:clamp(18px, 1.6vw, 24px);">{coverage_pct}%</div>'
                    f'<div class="kpi-sub">Capacity vs. Demand</div></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            balance_label = (
                f"+{surplus_or_deficit} Available Buffer Slots"
                if surplus_or_deficit >= 0
                else f"{abs(surplus_or_deficit)} Student Slot Deficit"
            )
            st.markdown(
                f"""
                <div style="box-sizing: border-box;width:100%;max-width:100%;background:#F8FAFC;
                border:1px solid #CBD5E1;border-left:5px solid {accent_hex};
                border-radius:10px;padding:12px 14px; color:#0F172A;
                overflow-wrap:anywhere;word-break:break-word;">
                    <div style="font-size: 12px; font-weight:800;text-transform:uppercase;
                    color:#0F172A;margin-bottom: 6px;line-height:1.35;">
                        Why {html.escape(selected_district)} Is Classified as {class_title} ({balance_label})
                    </div>
                    <div style="font-size: 13px;line-height:1.5;color:#0F172A;">
                        {explanation_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with st.container(border=True):
        st.subheader("Kelantan District Autism Accessibility Dataset (Connected Registry Table)")
        st.caption(
            f"All 10 Kelantan districts derived directly from the active student and centre records. "
            f"Currently highlighted district: {selected_district}."
        )
        tbl_df = access_df.copy()
        tbl_df["Service Coverage (%)"] = tbl_df.apply(
            lambda r: round((r["total_capacity"] / r["students"]) * 100.0, 1)
            if r["students"] > 0
            else (100.0 if r["total_capacity"] > 0 else 0.0),
            axis=1,
        )
        tbl_df["Coverage Classification"] = tbl_df["level"].map({
            "Red": "Critical Coverage (Red)",
            "Yellow": "Moderate Coverage (Yellow)",
            "Green": "Good Coverage (Green)",
        })
        f_col1, f_col2 = st.columns([2, 1.3])
        tbl_search = f_col1.text_input(
            "Search District or Classification in Table",
            placeholder="Filter by district name or Critical / Moderate / Good...",
            key="analytics_table_search",
        )
        tbl_sort = f_col2.selectbox(
            "Sort Dataset By",
            [
                "Default District Order",
                "Highest Registered Students",
                "Highest Centre Slot Capacity",
                "Highest Student-to-Centre Ratio",
                "Lowest Service Coverage (%)",
            ],
            key="analytics_table_sort",
        )
        if tbl_search.strip():
            q_txt = tbl_search.strip().lower()
            tbl_df = tbl_df[
                tbl_df["district"].str.lower().str.contains(q_txt, na=False)
                | tbl_df["Coverage Classification"].str.lower().str.contains(q_txt, na=False)
                | tbl_df["gap_status"].str.lower().str.contains(q_txt, na=False)
            ]
        if tbl_sort == "Highest Registered Students":
            tbl_df = tbl_df.sort_values(by="students", ascending=False)
        elif tbl_sort == "Highest Centre Slot Capacity":
            tbl_df = tbl_df.sort_values(by="total_capacity", ascending=False)
        elif tbl_sort == "Highest Student-to-Centre Ratio":
            tbl_df = tbl_df.sort_values(by=["student_per_centre", "students"], ascending=False)
        elif tbl_sort == "Lowest Service Coverage (%)":
            tbl_df = tbl_df.sort_values(by="Service Coverage (%)", ascending=True)

        display_tbl = tbl_df[[
            "district",
            "students",
            "centres",
            "total_capacity",
            "Service Coverage (%)",
            "student_per_centre",
            "Coverage Classification",
            "gap_status",
        ]].rename(
            columns={
                "district": "District",
                "students": "Registered Students",
                "centres": "Autism Centres",
                "total_capacity": "Centre Slot Capacity",
                "student_per_centre": "Students / Centre Ratio",
                "gap_status": "Accessibility Gap Assessment",
            }
        )

        def highlight_selected_district_row(row):
            if str(row["District"]) == selected_district:
                return ["background-color: #DBEAFE; font-weight: 700; color: #0F172A;"] * len(row)
            return ["background-color: #FFFFFF; color: #0F172A;"] * len(row)

        styled_tbl = display_tbl.style.apply(highlight_selected_district_row, axis=1).format({
            "Service Coverage (%)": "{:.1f}%",
            "Students / Centre Ratio": "{:.1f}",
        })
        st.dataframe(styled_tbl, use_container_width=True, hide_index=True)

elif active_page == "Parents Dashboard":
    st.markdown(
        """
        <div class="gov-header-banner">
            <div>
                <div style="font-size:21px;font-weight:800;color:#0F172A;">Parents &amp; Guardian Support Portal</div>
                <div style="font-size:13px;color:#334155;">Register your child, locate the 3 most suitable autism centres in Kelantan, track application status, and explore home learning modules.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    p1, p2, p3 = st.columns(3, gap="medium")
    with p1:
        with st.container(border=True):
            st.subheader("1. Child Registration")
            st.write("Submit your child's age, diagnosis, residential address, and therapy needs to find the closest suitable centres.")
            if st.button("Open Child Registration Form", type="primary", use_container_width=True):
                navigate_to("Child Registration", "Parent / Guardian")
                st.rerun()
    with p2:
        with st.container(border=True):
            st.subheader("2. Find Suitable Centres")
            st.write("View your home marker, animated routes, km distances, and the top 3 matched centres on the Kelantan GIS map.")
            if st.button("Open GIS Centre Matcher", type="primary", use_container_width=True):
                navigate_to("Find Suitable Centres", "Parent / Guardian")
                st.rerun()
    with p3:
        with st.container(border=True):
            st.subheader("3. Learning Modules")
            st.write("Read 4 interactive page-turning flipbooks covering hygiene, classroom arrival, sensory walk, and PECS communication.")
            if st.button("Explore 4 Flipbook Modules", type="primary", use_container_width=True):
                navigate_to("Learning Modules", "Parent / Guardian")
                st.rerun()

    with st.container(border=True):
        st.subheader("Recent Parent Registration Tracking")
        if regs_df.empty:
            st.info("No registrations submitted yet. Click 'Open Child Registration Form' above to begin.")
        else:
            st.dataframe(
                regs_df[["reg_code", "child_name", "district", "required_services", "selected_centre", "status", "submitted_at"]].rename(
                    columns={
                        "reg_code": "Registration ID",
                        "child_name": "Child Name",
                        "district": "District",
                        "required_services": "Therapy Required",
                        "selected_centre": "Selected Centre",
                        "status": "Approval Status",
                        "submitted_at": "Submitted At",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

elif active_page == "Child Registration":
    st.markdown(
        """
        <div class="gov-header-banner">
            <div>
                <div style="font-size:21px;font-weight:800;color:#0F172A;">Child Registration &amp; Automatic GIS Centre Matching</div>
                <div style="font-size:13px;color:#334155;">Complete your child's registration below. Upon submission, the system will save your record and zoom to your home on the Kelantan GIS map with your top 3 recommended centres.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        with st.form("parent_child_registration_form"):
            c1, c2, c3 = st.columns([1.6, 0.8, 1.2])
            child_name = c1.text_input("Child's Full Name *", placeholder="e.g., Aisyah Humaira binti Ahmad")
            child_age = c2.number_input("Child's Age *", min_value=1, max_value=21, value=6)
            diagnosis_cat = c3.selectbox("Diagnosis Category *", DIAGNOSIS_CATEGORIES)

            c4, c5 = st.columns([2, 1])
            res_address = c4.text_input("Residential Address in Kelantan *", placeholder="e.g., Lot 45, Jalan Kubang Kerian, 16150 Kota Bharu, Kelantan")
            district_in = c5.selectbox("District in Kelantan *", KELANTAN_DISTRICTS)

            req_services = st.multiselect("Required Therapy Services *", THERAPY_SERVICES, default=["Speech Therapy", "Occupational Sensory"])

            p1, p2 = st.columns(2)
            parent_name = p1.text_input("Parent / Guardian Full Name *", placeholder="e.g., Ahmad bin Ismail")
            parent_contact = p2.text_input("Parent Contact Number *", placeholder="e.g., 012-987 6543")

            submitted = st.form_submit_button("Submit and Find Suitable Centres", type="primary", use_container_width=True)

            if submitted:
                errors = []
                if not child_name.strip():
                    errors.append("Child's full name is required.")
                if not res_address.strip():
                    errors.append("Residential address is required.")
                if not req_services:
                    errors.append("Please select at least one required therapy service.")
                if not parent_name.strip():
                    errors.append("Parent's name is required.")
                if not parent_contact.strip() or len(parent_contact.strip()) < 8:
                    errors.append("Please enter a valid parent contact number.")

                if errors:
                    for err in errors:
                        st.error(err)
                elif centres_df.empty:
                    st.error("Insufficient autism centre data in the database. Please ask an administrator to add centre records first.")
                else:
                    home_lat, home_lon = estimate_home_coordinates(district_in, res_address)
                    top3 = compute_top_3_centres(home_lat, home_lon, req_services, centres_df)
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) FROM parent_registrations")
                    next_reg_num = cur.fetchone()[0] + 1
                    reg_code = f"REG-2026-{next_reg_num:03d}"
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    cur.execute(
                        """
                        INSERT INTO parent_registrations
                        (reg_code, child_name, age, diagnosis, residential_address, district, home_lat, home_lon,
                         required_services, parent_name, parent_contact, recommended_centres_json,
                         selected_centre, status, submitted_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
                        """,
                        (
                            reg_code, child_name.strip(), int(child_age), diagnosis_cat,
                            res_address.strip(), district_in, home_lat, home_lon,
                            ", ".join(req_services), parent_name.strip(), parent_contact.strip(),
                            json.dumps(top3), top3[0]["centre_name"] if top3 else "", now_str,
                        ),
                    )
                    conn.commit()
                    conn.close()

                    st.session_state["latest_recommendation_context"] = {
                        "reg_code": reg_code,
                        "child_name": child_name.strip(),
                        "age": int(child_age),
                        "diagnosis": diagnosis_cat,
                        "residential_address": res_address.strip(),
                        "district": district_in,
                        "home_lat": home_lat,
                        "home_lon": home_lon,
                        "required_services": req_services,
                        "parent_name": parent_name.strip(),
                        "parent_contact": parent_contact.strip(),
                        "top3": top3,
                        "focused_rank": 0,
                        "selected_centre": top3[0]["centre_name"] if top3 else "",
                        "just_submitted": True,
                    }
                    navigate_to("Find Suitable Centres", "Parent / Guardian")
                    st.rerun()

elif active_page == "Find Suitable Centres":
    rec_ctx = st.session_state["latest_recommendation_context"]
    live_top3 = compute_top_3_centres(
        rec_ctx["home_lat"],
        rec_ctx["home_lon"],
        rec_ctx["required_services"],
        centres_df,
    )
    rec_ctx["top3"] = live_top3

    st.markdown(
        f"""
        <div class="gov-header-banner">
            <div>
                <div style="font-size:21px;font-weight:800;color:#0F172A;">Kelantan GIS Spatial Centre Recommendation</div>
                <div style="font-size:13px;color:#334155;">
                    Showing residential location and Top 3 matched autism centres for
                    <strong>{html.escape(rec_ctx['child_name'])}</strong>
                    ({html.escape(rec_ctx['district'])})
                </div>
            </div>
            <div style="background:#CCFBF1; color:#0F172A; padding:6px 12px;border-radius:8px;font-size:12px;font-weight:700;border:1px solid #0D9488;">
                Registration ID: {html.escape(rec_ctx['reg_code'])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if rec_ctx.get("just_submitted"):
        st.success(
            f"Registration **{rec_ctx['reg_code']}** saved! The Kelantan GIS map has zoomed to "
            f"**{rec_ctx['child_name']}'s** residential location and calculated distances and suitability "
            f"scores for the 3 best-matched autism centres."
        )
        rec_ctx["just_submitted"] = False

    if not live_top3:
        st.warning("Insufficient autism centre data exists in the database to generate recommendations. Please contact an administrator.")
    else:
        map_col, cards_col = st.columns([1.35, 1], gap="medium")
        with map_col:
            with st.container(border=True):
                top_bar_l, top_bar_r = st.columns([3, 1.3], vertical_alignment="center")
                with top_bar_l:
                    st.subheader("Interactive Kelantan GIS Route & Centre Map")
                with top_bar_r:
                    if st.button("Reset Overview", type="secondary", use_container_width=True):
                        rec_ctx["focused_rank"] = 0
                        st.rerun()
                render_recommendation_gis_map(access_df, rec_ctx, map_height=540)
                st.caption(
                    "Note: The suitability percentage is a system-generated spatial and service "
                    "matching score based on therapy availability, distance from home, and centre slot "
                    "capacity - not a clinical or medical assessment."
                )

        with cards_col:
            st.subheader("Top 3 Recommended Centres")
            rank_badge_colors = {1: "#0D9488", 2: "#0284C7", 3: "#0F294A"}
            for c in live_top3:
                b_col = rank_badge_colors.get(c["rank"], "#0D9488")
                is_selected = (rec_ctx.get("selected_centre") == c["centre_name"])
                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content:space-between; align-items:center;gap:8px;margin-bottom:4px;">
                            <span style="background:{b_col};color:#FFFFFF;font-size:11px;font-weight:800;padding:3px 10px; border-radius:999px;">
                                Recommendation #{c['rank']} - {c['suitability_pct']}% Suitability
                            </span>
                            <span style="font-size:12.5px;font-weight:800; color:#0F172A;">
                                {c['distance_km']} km
                            </span>
                        </div>
                        <div style="font-size: 15.5px;font-weight:800;color:#0F172A;margin-bottom:4px;overflow-wrap:anywhere;">
                            {html.escape(c['centre_name'])}
                        </div>
                        <div style="font-size:12px; color:#0F172A;line-height:1.45;">
                            <strong>Address:</strong> {html.escape(c['address'])}<br>
                            <strong>Available Services:</strong> {html.escape(c['services'])}<br>
                            <strong>Contact:</strong> {html.escape(c['contact'])} &nbsp;|&nbsp;
                            <strong>Hours:</strong> {html.escape(c['hours'])}
                        </div>
                        <div style="margin-top:6px;background:#E6F4F1; border-left:3px solid {b_col};padding:6px 9px;border-radius:6px;font-size: 11.8px;color:#0F172A;">
                            {html.escape(c['reason'])}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                    btn1, btn2 = st.columns(2)
                    if btn1.button("View on GIS Map", key=f"view_map_{c['rank']}", type="secondary", use_container_width=True):
                        rec_ctx["focused_rank"] = c["rank"]
                        st.rerun()
                    if is_selected:
                        btn2.markdown('<div class="saved-centre-pill">Preferred Centre Saved</div>', unsafe_allow_html=True)
                    else:
                        if btn2.button(f"Select Centre #{c['rank']}", key=f"select_centre_{c['rank']}", type="primary", use_container_width=True):
                            rec_ctx["selected_centre"] = c["centre_name"]
                            conn = get_conn()
                            conn.execute(
                                "UPDATE parent_registrations SET selected_centre=? WHERE reg_code=?",
                                (c["centre_name"], rec_ctx["reg_code"]),
                            )
                            conn.commit()
                            conn.close()
                            st.success(f"Saved **{c['centre_name']}** as your preferred centre for {rec_ctx['reg_code']}!")
                            st.rerun()

elif active_page == "Learning Modules":
    st.markdown(
        """
        <div class="gov-header-banner">
            <div>
                <div style="font-size:21px;font-weight:800; color:#0F172A;">Parents Learning Interactive Flipbooks</div>
                <div style="font-size:13px;color:#334155;">Click any module cover to open its interactive page-turning flipbook guide for home routine support.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    open_key = st.session_state["open_flipbook_key"]
    if open_key is None:
        cols = st.columns(2, gap="large")
        for idx, mod in enumerate(MODULES_4):
            with cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style="background:linear-gradient(135deg, {mod['color']} 0%, {mod['accent']} 100%); color:#FFFFFF;border-radius: 10px;padding:22px 20px;margin-bottom:12px;">
                            <div style="font-size: 11px;font-weight:800;letter-spacing:1px;text-transform:uppercase; color:#FFFFFF;">
                                {html.escape(mod['code'])} - {html.escape(mod['domain'])}
                            </div>
                            <div style="font-size:20px;font-weight:800;margin:8px 0 6px 0;line-height:1.25;color:#FFFFFF;">
                                {html.escape(mod['title'])}
                            </div>
                            <div style="font-size: 12.5px; color:#FFFFFF;line-height:1.45;">
                                {html.escape(mod['cover_desc'])}
                            </div>
                            <div style="margin-top:14px;font-size: 11.5px;font-weight:700;background:rgba(255,255,255,0.2); color:#FFFFFF;display:inline-block;padding:4px 10px;border-radius:999px;">
                                4 Interactive Pages: Cover + Step-by-Step Guide
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button(f"Open {mod['title']}", key=f"open_mod_{mod['key']}", type="primary", use_container_width=True):
                        st.session_state["open_flipbook_key"] = mod["key"]
                        st.session_state[f"fb_page_{mod['key']}"] = 0
                        st.rerun()
    else:
        mod = next(m for m in MODULES_4 if m["key"] == open_key)
        p_key = f"fb_page_{mod['key']}"
        cur_p = st.session_state[p_key]
        total_p = len(mod["pages"]) + 1
        if st.button("Back to All 4 Module Covers", type="secondary"):
            st.session_state["open_flipbook_key"] = None
            st.rerun()
        with st.container(border=True):
            if cur_p == 0:
                page_title = f"Cover Page - {mod['title']}"
                page_sub = mod["domain"]
                page_body = mod["cover_desc"]
                page_bullets = "- Click 'Next Page' below to turn to Step 1.\n- Designed for daily home practice alongside therapist guidance."
            else:
                heading, summary, steps = mod["pages"][cur_p - 1]
                page_title = heading
                page_sub = f"{mod['code']} - {mod['title']}"
                page_body = summary
                page_bullets = steps
            bullets_html = "<br>".join(html.escape(line) for line in page_bullets.split("\n"))
            flipbook_visual = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<style>
body {{ margin:0; padding:4px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; background:transparent; }}
@keyframes pageTurnIn {{
    0% {{ opacity: 0; transform: perspective(1000px) rotateY(-14deg) translateX(16px); }}
    100% {{ opacity: 1; transform: perspective(1000px) rotateY(0deg) translateX(0); }}
}}
.book-page {{
    animation: pageTurnIn 0.45s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-left: 8px solid {mod['color']};
    border-radius: 12px;
    padding: 24px 26px;
}}
.badge {{
    display: inline-block; background: {mod['soft_bg']}; color: #0F172A;
    font-size: 11.5px; font-weight: 800; padding: 4px 12px; border-radius: 999px;
    margin-bottom: 10px;
}}
.p-title {{ font-size: 21px; font-weight: 800; color: #0F172A; margin: 0 0 8px 0; }}
.p-summary {{ font-size: 14.5px; color: #0F172A; line-height: 1.55; margin-bottom: 14px; }}
.p-box {{
    background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px;
    padding: 14px 16px; font-size: 13.5px; color: #0F172A; line-height: 1.7;
}}
</style>
</head>
<body>
<div class="book-page">
    <div class="badge">{html.escape(page_sub)} - Page {cur_p + 1} of {total_p}</div>
    <div class="p-title">{html.escape(page_title)}</div>
    <div class="p-summary">{html.escape(page_body)}</div>
    <div class="p-box">{bullets_html}</div>
</div>
</body>
</html>"""
            components.html(flipbook_visual, height=295, scrolling=False)
            nav_l, nav_m, nav_r = st.columns([1, 1.5, 1])
            if nav_l.button("Previous Page", disabled=(cur_p == 0), type="secondary", use_container_width=True):
                st.session_state[p_key] = cur_p - 1
                st.rerun()
            nav_m.markdown(
                f"<div style='text-align:center;padding-top:8px;font-weight:700; color:#0F172A;'>Page {cur_p + 1} of {total_p}</div>",
                unsafe_allow_html=True,
            )
            if nav_r.button("Next Page", disabled=(cur_p == total_p - 1), type="primary", use_container_width=True):
                st.session_state[p_key] = cur_p + 1
                st.rerun()

elif active_page == "Registration History":
    st.markdown(
        """
        <div class="gov-header-banner">
            <div>
                <div style="font-size:21px;font-weight:800; color:#0F172A;">Parent Registration History &amp; Status Tracking</div>
                <div style="font-size:13px;color:#334155;">Track whether your child's registration is Pending, Approved, or Rejected and review your selected autism centre.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if regs_df.empty:
        st.info("No registration records found yet.")
    else:
        for _, r in regs_df.iterrows():
            st_val = r["status"]
            b_cls = (
                "badge-approved"
                if st_val == "Approved"
                else ("badge-rejected" if st_val == "Rejected" else "badge-pending")
            )
            with st.container(border=True):
                c_l, c_r = st.columns([3.2, 1], vertical_alignment="center")
                with c_l:
                    st.markdown(
                        f"**{r['reg_code']} - {r['child_name']}** (Age {r['age']} - {r['diagnosis']}) &nbsp;"
                        f"<span class='status-badge {b_cls}'>{st_val}</span>",
                        unsafe_allow_html=True,
                    )
                    st.write(
                        f"**District:** {r['district']} | **Required Services:** {r['required_services']} | "
                        f"**Selected Centre:** {r['selected_centre'] or 'None selected'}"
                    )
                    st.caption(f"Submitted by {r['parent_name']} ({r['parent_contact']}) on {r['submitted_at']}")
                with c_r:
                    if st.button("View on GIS Map", key=f"hist_map_{r['id']}", type="secondary", use_container_width=True):
                        req_s = [x.strip() for x in str(r["required_services"]).split(",") if x.strip()]
                        top3 = compute_top_3_centres(float(r["home_lat"]), float(r["home_lon"]), req_s, centres_df)
                        st.session_state["latest_recommendation_context"] = {
                            "reg_code": r["reg_code"],
                            "child_name": r["child_name"],
                            "age": int(r["age"]),
                            "diagnosis": r["diagnosis"],
                            "residential_address": r["residential_address"],
                            "district": r["district"],
                            "home_lat": float(r["home_lat"]),
                            "home_lon": float(r["home_lon"]),
                            "required_services": req_s,
                            "parent_name": r["parent_name"],
                            "parent_contact": r["parent_contact"],
                            "top3": top3,
                            "focused_rank": 0,
                            "selected_centre": r["selected_centre"],
                            "just_submitted": False,
                        }
                        navigate_to("Find Suitable Centres", "Parent / Guardian")
                        st.rerun()

elif active_page == "Settings":
    st.markdown(
        """
        <div class="gov-header-banner">
            <div>
                <div style="font-size:21px;font-weight:800; color:#0F172A;">System Settings &amp; Database Maintenance</div>
                <div style="font-size:13px;color:#334155;">Manage user portal permissions and export backups.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.subheader("Active Portal Role & Access Control")
        role_choice = st.radio(
            "Select Active Role",
            ["Administrator", "Parent / Guardian"],
            index=0 if st.session_state["user_role"] == "Administrator" else 1,
            horizontal=True,
        )
        if st.button("Apply Role Setting", type="primary"):
            st.session_state["user_role"] = role_choice
            st.success(f"Active portal role set to {role_choice}.")
            st.rerun()

    with st.container(border=True):
        st.subheader("Database Export")
        d1, d2, d3 = st.columns(3)
        d1.download_button(
            "Export Student Registry (CSV)",
            data=students_df.to_csv(index=False).encode("utf-8"),
            file_name="kelantan_students_registry.csv",
            mime="text/csv",
            use_container_width=True,
        )
        d2.download_button(
            "Export Autism Centres (CSV)",
            data=centres_df.to_csv(index=False).encode("utf-8"),
            file_name="kelantan_autism_centres.csv",
            mime="text/csv",
            use_container_width=True,
        )
        d3.download_button(
            "Export Parent Registrations (CSV)",
            data=regs_df.to_csv(index=False).encode("utf-8"),
            file_name="kelantan_parent_registrations.csv",
            mime="text/csv",
            use_container_width=True,
        )
