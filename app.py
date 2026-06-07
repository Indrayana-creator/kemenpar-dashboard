import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import base64
from pathlib import Path
from textwrap import dedent

# =========================================================
# 1. PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Kemenparekraf Investment Dashboard",
    page_icon="🇮🇩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. HELPER FUNCTIONS
# =========================================================
def img_to_base64(path_or_paths):
    if isinstance(path_or_paths, str):
        path_or_paths = [path_or_paths]

    for path in path_or_paths:
        path = Path(path)
        if path.exists():
            return base64.b64encode(path.read_bytes()).decode()

    return ""


def image_card_html(title, image_path, tag="Priority DPP"):
    img_base64 = img_to_base64(image_path)

    if not img_base64:
        return (
            f'<div class="dpp-photo-card">'
            f'<div style="padding:20px; color:#CBD5E1;">Foto {title} belum ditemukan.<br>'
            f'<span style="font-size:12px;">Cek file di folder assets/dpp</span></div>'
            f'<div class="dpp-photo-title">{title}</div>'
            f'</div>'
        )

    return (
        f'<div class="dpp-photo-card">'
        f'<img src="data:image/jpeg;base64,{img_base64}">'
        f'<div class="dpp-photo-overlay"></div>'
        f'<div class="dpp-photo-tag">{tag}</div>'
        f'<div class="dpp-photo-title">{title}</div>'
        f'</div>'
    )


def selected_image_html(title, image_path, subtitle):
    img_base64 = img_to_base64(image_path)

    if not img_base64:
        return (
            f'<div class="info-card">'
            f'<b>Foto {title} belum ditemukan.</b><br>'
            f'Pastikan file foto tersedia di folder <b>assets/dpp</b>.'
            f'</div>'
        )

    return (
        f'<div class="selected-dpp-image">'
        f'<img src="data:image/jpeg;base64,{img_base64}">'
        f'<div class="selected-dpp-overlay"></div>'
        f'<div class="selected-dpp-title">{title}</div>'
        f'<div class="selected-dpp-subtitle">{subtitle}</div>'
        f'</div>'
    )


def focus_html_map(html_map, pilihan_dpp):
    if pilihan_dpp == "-- Ringkasan Nasional --":
        html_map = html_map.replace("Tanjung Kelayang", "Bangka Belitung")
        return html_map

    if pilihan_dpp not in DPP_COORDINATES:
        html_map = html_map.replace("Tanjung Kelayang", "Bangka Belitung")
        return html_map

    coord = DPP_COORDINATES[pilihan_dpp]
    lat = coord["lat"]
    lon = coord["lon"]
    zoom = coord["zoom"]

    focus_script = f"""
    <script>
    setTimeout(function() {{
        try {{
            var mapObject = null;

            for (var key in window) {{
                if (key.startsWith("map_") && window[key] && typeof window[key].setView === "function") {{
                    mapObject = window[key];
                    break;
                }}
            }}

            if (mapObject) {{
                mapObject.setView([{lat}, {lon}], {zoom});

                L.circleMarker([{lat}, {lon}], {{
                    radius: 18,
                    color: "#D4AF37",
                    weight: 4,
                    fillColor: "#D4AF37",
                    fillOpacity: 0.20
                }}).addTo(mapObject).bindPopup("<b>{pilihan_dpp}</b><br>Destinasi terpilih").openPopup();
            }}
        }} catch(e) {{
            console.log("Map focus error:", e);
        }}
    }}, 900);
    </script>
    """

    if "</body>" in html_map:
        html_map = html_map.replace("</body>", focus_script + "</body>")
    else:
        html_map += focus_script

    html_map = html_map.replace("Tanjung Kelayang", "Bangka Belitung")

    return html_map


def national_strategy_html():
    return (
        '<div class="strategy-summary-grid">'

        '<div class="strategy-card">'
        '<div class="strategy-number">01 | BUILD</div>'
        '<div class="strategy-title">Zona Akselerasi Infrastruktur</div>'
        '<div class="strategy-tag">Bromo · Bangka Belitung · Wakatobi</div>'
        '<div class="strategy-text">'
        'Demand tinggi, supply sangat rendah, dan gap positif ekstrem. '
        'Strategi utama adalah membangun infrastruktur dari nol atau mempercepat supply: '
        'glamping, eco-lodge, beachfront resort, dive resort, konektivitas, shuttle, dan visitor center.'
        '</div>'
        '</div>'

        '<div class="strategy-card">'
        '<div class="strategy-number">02 | UPGRADE</div>'
        '<div class="strategy-title">Zona Pengendalian Kualitas</div>'
        '<div class="strategy-tag">Labuan Bajo · Borobudur · Raja Ampat · Danau Toba · Mandalika · Likupang</div>'
        '<div class="strategy-text">'
        'Demand kuat dan supply relatif siap. Fokus bukan menambah kapasitas, '
        'tetapi meningkatkan kualitas dan diferensiasi melalui liveaboard, heritage hotel, '
        'eco-dive resort, lakeside resort, sport tourism, dan experience product.'
        '</div>'
        '</div>'

        '<div class="strategy-card">'
        '<div class="strategy-number">03 | PROMOTE</div>'
        '<div class="strategy-title">Zona Aktivasi Promosi</div>'
        '<div class="strategy-tag">Morotai</div>'
        '<div class="strategy-text">'
        'Supply sudah memadai, tetapi demand masih sangat rendah. '
        'Strategi utama adalah meningkatkan visibilitas melalui digital branding, '
        'war heritage tourism, paket wisata tematik, dan penguatan tour operator lokal.'
        '</div>'
        '</div>'

        '</div>'
    )


def detail_recommendation_html(pilihan_dpp, rec):
    items_html = ""

    for i, item in enumerate(rec["items"], start=1):
        items_html += (
            f'<div class="rec-item">'
            f'<div class="rec-item-title">{i}. {item["title"]}</div>'
            f'<div class="rec-item-desc">{item["desc"]}</div>'
            f'</div>'
        )

    return (
        f'<div class="rec-detail-grid">'
        f'<div class="rec-main-card">'
        f'<div class="rec-gap">Gap Score {rec["gap"]} · Strategy {rec["strategy"]}</div>'
        f'<div class="rec-dpp-name">{pilihan_dpp}</div>'
        f'<div class="rec-zone">{rec["zone"]}</div>'
        f'<div class="rec-key">'
        f'<b style="color:#D4AF37;">Strategic Context:</b><br>'
        f'{rec["description"]}'
        f'<br><br>'
        f'<b style="color:#D4AF37;">Key Strategy:</b><br>'
        f'{rec["key"]}'
        f'</div>'
        f'</div>'
        f'<div class="rec-list-card">{items_html}</div>'
        f'</div>'
    )


# =========================================================
# 3. CUSTOM CSS
# =========================================================
st.markdown(dedent("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, span, label {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(212,175,55,0.14), transparent 32%),
        radial-gradient(circle at top right, rgba(30,64,175,0.18), transparent 35%),
        linear-gradient(135deg, #061325 0%, #071A33 45%, #020617 100%) !important;
    color: #F8FAFC !important;
}

/* Sidebar toggle fix */
[data-testid="stHeader"] {
    background: rgba(0,0,0,0) !important;
    visibility: visible !important;
    height: 3rem !important;
    z-index: 999999 !important;
}

[data-testid="stToolbar"] {
    visibility: hidden !important;
}

[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}

button[kind="header"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 92% !important;
}

[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, #061325 0%, #0B1F3A 55%, #020617 100%) !important;
    border-right: 1px solid rgba(212,175,55,0.35) !important;
    min-width: 300px !important;
    max-width: 360px !important;
}

[data-testid="stSidebar"] * {
    color: #F8FAFC !important;
}

.sidebar-title {
    color: #D4AF37 !important;
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 8px;
}

.sidebar-subtitle {
    color: #CBD5E1 !important;
    font-size: 13px;
    line-height: 1.5;
    margin-bottom: 20px;
}

.stSelectbox div[data-baseweb="select"] > div {
    background-color: #F8FAFC !important;
    color: #071A33 !important;
    border-radius: 10px !important;
    border: 1px solid #D4AF37 !important;
}

.stSelectbox div[data-baseweb="select"] span {
    color: #071A33 !important;
}

.hero-card {
    position: relative;
    background:
        linear-gradient(135deg, rgba(7,26,51,0.97), rgba(15,39,71,0.90)),
        url("https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1600&q=80");
    background-size: cover;
    background-position: center;
    border: 1px solid rgba(212,175,55,0.45);
    border-radius: 24px;
    padding: 34px 38px;
    margin-bottom: 26px;
    box-shadow: 0 24px 70px rgba(0,0,0,0.35);
    overflow: hidden;
}

.hero-card::after {
    content: "";
    position: absolute;
    right: -70px;
    top: -70px;
    width: 220px;
    height: 220px;
    border: 2px solid rgba(212,175,55,0.32);
    border-radius: 50%;
}

.hero-top {
    display: flex;
    align-items: center;
    gap: 18px;
    margin-bottom: 18px;
}

.hero-logo {
    width: 74px;
    height: 74px;
    object-fit: contain;
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
    padding: 8px;
    border: 1px solid rgba(212,175,55,0.65);
}

.hero-badge {
    display: inline-block;
    padding: 7px 14px;
    border-radius: 999px;
    background: rgba(212,175,55,0.16);
    border: 1px solid rgba(212,175,55,0.55);
    color: #F7D774 !important;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    line-height: 1.15;
    color: #F8FAFC !important;
    margin: 8px 0 8px 0;
}

.hero-title span {
    color: #D4AF37 !important;
}

.hero-subtitle {
    color: #CBD5E1 !important;
    font-size: 17px;
    max-width: 920px;
    line-height: 1.7;
}

.hero-footer {
    margin-top: 20px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.hero-chip {
    padding: 8px 13px;
    border-radius: 999px;
    background: rgba(15,39,71,0.72);
    border: 1px solid rgba(148,163,184,0.24);
    color: #E2E8F0 !important;
    font-size: 13px;
    font-weight: 600;
}

.section-title {
    display: flex;
    align-items: center;
    gap: 12px;
    color: #F8FAFC !important;
    font-size: 24px;
    font-weight: 800;
    margin: 18px 0 14px 0;
}

.section-title::before {
    content: "";
    width: 8px;
    height: 32px;
    background: linear-gradient(180deg, #F7D774, #D4AF37);
    border-radius: 999px;
}

.kpi-container {
    background:
        linear-gradient(180deg, rgba(15,39,71,0.96), rgba(7,26,51,0.96));
    border: 1px solid rgba(212,175,55,0.38);
    border-radius: 18px;
    padding: 22px 20px;
    text-align: left;
    box-shadow: 0 16px 40px rgba(0,0,0,0.25);
    position: relative;
    overflow: hidden;
    min-height: 132px;
}

.kpi-container::after {
    content: "";
    position: absolute;
    right: -35px;
    top: -35px;
    width: 95px;
    height: 95px;
    border-radius: 50%;
    background: rgba(212,175,55,0.13);
}

.kpi-title {
    font-size: 13px;
    font-weight: 700;
    color: #A7B4C8 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}

.kpi-value {
    font-size: 38px;
    font-weight: 800;
    color: #D4AF37 !important;
    line-height: 1.15;
}

.kpi-note {
    margin-top: 7px;
    color: #CBD5E1 !important;
    font-size: 13px;
}

.chart-card {
    background: rgba(7,26,51,0.72);
    border: 1px solid rgba(212,175,55,0.20);
    border-radius: 18px;
    padding: 18px 18px 4px 18px;
    box-shadow: 0 16px 45px rgba(0,0,0,0.22);
}

.map-card {
    background: rgba(7,26,51,0.78);
    border: 1px solid rgba(212,175,55,0.35);
    border-radius: 20px;
    padding: 12px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.30);
    overflow: hidden;
}

.info-card {
    background: rgba(15,39,71,0.68);
    border: 1px solid rgba(212,175,55,0.22);
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 18px;
    color: #E2E8F0 !important;
    line-height: 1.7;
}

.info-card b {
    color: #D4AF37 !important;
}

/* DPP Photo Gallery */
.dpp-gallery {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 18px;
    margin-top: 12px;
    margin-bottom: 8px;
}

.dpp-photo-card {
    position: relative;
    height: 210px;
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(212,175,55,0.35);
    box-shadow: 0 18px 45px rgba(0,0,0,0.28);
    background: #071A33;
}

.dpp-photo-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.45s ease;
}

.dpp-photo-card:hover img {
    transform: scale(1.08);
}

.dpp-photo-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, transparent 35%, rgba(2,6,23,0.92) 100%);
}

.dpp-photo-title {
    position: absolute;
    left: 16px;
    bottom: 15px;
    color: #F8FAFC !important;
    font-size: 17px;
    font-weight: 800;
}

.dpp-photo-tag {
    position: absolute;
    top: 12px;
    left: 12px;
    padding: 6px 10px;
    border-radius: 999px;
    background: rgba(212,175,55,0.88);
    color: #071A33 !important;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
}

.selected-dpp-image {
    position: relative;
    height: 360px;
    border-radius: 22px;
    overflow: hidden;
    border: 1px solid rgba(212,175,55,0.45);
    box-shadow: 0 22px 60px rgba(0,0,0,0.35);
    margin-bottom: 20px;
}

.selected-dpp-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.selected-dpp-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(2,6,23,0.85), rgba(2,6,23,0.25), rgba(2,6,23,0.05));
}

.selected-dpp-title {
    position: absolute;
    left: 32px;
    bottom: 46px;
    color: #F8FAFC !important;
    font-size: 38px;
    font-weight: 800;
}

.selected-dpp-subtitle {
    position: absolute;
    left: 32px;
    bottom: 24px;
    color: #D4AF37 !important;
    font-size: 15px;
    font-weight: 700;
}

/* Recommendation Cards */
.strategy-summary-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin-top: 14px;
}

.strategy-card {
    background:
        linear-gradient(180deg, rgba(15,39,71,0.96), rgba(7,26,51,0.96));
    border: 1px solid rgba(212,175,55,0.35);
    border-radius: 18px;
    padding: 22px 24px;
    min-height: 260px;
    box-shadow: 0 16px 45px rgba(0,0,0,0.24);
}

.strategy-number {
    color: #D4AF37 !important;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.strategy-title {
    color: #F8FAFC !important;
    font-size: 21px;
    font-weight: 800;
    margin-bottom: 10px;
}

.strategy-tag {
    display: inline-block;
    padding: 6px 11px;
    border-radius: 999px;
    background: rgba(212,175,55,0.14);
    border: 1px solid rgba(212,175,55,0.42);
    color: #F7D774 !important;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 13px;
}

.strategy-text {
    color: #E2E8F0 !important;
    font-size: 14px;
    line-height: 1.7;
}

.rec-detail-grid {
    display: grid;
    grid-template-columns: 0.9fr 1.1fr;
    gap: 20px;
    margin-top: 14px;
}

.rec-main-card {
    background:
        linear-gradient(180deg, rgba(15,39,71,0.98), rgba(7,26,51,0.98));
    border: 1px solid rgba(212,175,55,0.38);
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 16px 45px rgba(0,0,0,0.25);
}

.rec-dpp-name {
    color: #D4AF37 !important;
    font-size: 30px;
    font-weight: 800;
    margin-bottom: 6px;
}

.rec-zone {
    color: #CBD5E1 !important;
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 18px;
}

.rec-gap {
    display: inline-block;
    padding: 8px 13px;
    border-radius: 999px;
    background: rgba(212,175,55,0.16);
    border: 1px solid rgba(212,175,55,0.45);
    color: #F7D774 !important;
    font-weight: 800;
    font-size: 13px;
    margin-bottom: 14px;
}

.rec-key {
    color: #F8FAFC !important;
    font-size: 15px;
    line-height: 1.7;
}

.rec-list-card {
    background:
        linear-gradient(180deg, rgba(15,39,71,0.88), rgba(7,26,51,0.94));
    border: 1px solid rgba(212,175,55,0.25);
    border-radius: 18px;
    padding: 22px 24px;
    box-shadow: 0 16px 45px rgba(0,0,0,0.22);
}

.rec-item {
    border-left: 4px solid #D4AF37;
    padding-left: 15px;
    margin-bottom: 18px;
}

.rec-item-title {
    color: #F8FAFC !important;
    font-size: 17px;
    font-weight: 800;
    margin-bottom: 5px;
}

.rec-item-desc {
    color: #CBD5E1 !important;
    font-size: 14px;
    line-height: 1.65;
}

@media (max-width: 1200px) {
    .dpp-gallery {
        grid-template-columns: repeat(3, 1fr);
    }
}

@media (max-width: 1100px) {
    .strategy-summary-grid {
        grid-template-columns: repeat(1, 1fr);
    }

    .rec-detail-grid {
        grid-template-columns: repeat(1, 1fr);
    }
}

@media (max-width: 768px) {
    .dpp-gallery {
        grid-template-columns: repeat(1, 1fr);
    }
}

hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(212,175,55,0.55), transparent) !important;
    margin: 2.2rem 0 !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""), unsafe_allow_html=True)

# =========================================================
# 4. LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    df = pd.read_csv("final_dashboard_dataset_K3.csv")
    df["DPP"] = df["DPP"].replace({"Tanjung Kelayang": "Bangka Belitung"})
    df["Cluster_K3"] = df["Cluster_K3"].astype(str)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("File 'final_dashboard_dataset_K3.csv' tidak ditemukan. Pastikan file CSV berada di folder yang sama dengan app.py.")
    st.stop()

# =========================================================
# 5. CONFIG
# =========================================================
DPP_IMAGES = {
    "Mandalika": ["assets/dpp/mandalika.jpeg", "assets/dpp/Mandalika - Lombok Indonesia.jpeg"],
    "Morotai": ["assets/dpp/morotai.jpeg", "assets/dpp/morotai.jpg.jpeg"],
    "Raja Ampat": ["assets/dpp/raja_ampat.jpeg", "assets/dpp/Raja Ampat.jpeg"],
    "Wakatobi": ["assets/dpp/wakatobi.jpeg"],
    "Likupang": ["assets/dpp/likupang.jpeg"],
    "Bangka Belitung": ["assets/dpp/bangka_belitung.jpeg", "assets/dpp/Bangka Belitung _ Indonesia.jpeg"],
    "Bromo": ["assets/dpp/bromo.jpeg", "assets/dpp/Bromo Mountain.jpeg"],
    "Borobudur": ["assets/dpp/borobudur.jpeg", "assets/dpp/Candi Borobudur.jpeg"],
    "Danau Toba": ["assets/dpp/danau_toba.jpeg", "assets/dpp/danautoba.jpeg"],
    "Labuan Bajo": ["assets/dpp/labuan_bajo.jpeg", "assets/dpp/labuanbajo.jpeg"]
}

DPP_TAGLINE = {
    "Mandalika": "Premium Sport Tourism Destination",
    "Morotai": "Frontier Marine Tourism",
    "Raja Ampat": "World-Class Marine Biodiversity",
    "Wakatobi": "Eco-Marine Tourism Paradise",
    "Likupang": "Emerging Coastal Destination",
    "Bangka Belitung": "High-Yield Beach Investment Area",
    "Bromo": "Iconic Mountain Tourism",
    "Borobudur": "Cultural Heritage Destination",
    "Danau Toba": "Lake-Based Super Priority Destination",
    "Labuan Bajo": "Premium Island & Komodo Gateway"
}

DPP_COORDINATES = {
    "Mandalika": {"lat": -8.8956, "lon": 116.2939, "zoom": 11},
    "Morotai": {"lat": 2.3500, "lon": 128.3000, "zoom": 9},
    "Raja Ampat": {"lat": -0.2333, "lon": 130.5167, "zoom": 8},
    "Wakatobi": {"lat": -5.3264, "lon": 123.5950, "zoom": 9},
    "Likupang": {"lat": 1.6828, "lon": 125.0624, "zoom": 10},
    "Bangka Belitung": {"lat": -2.5667, "lon": 107.6667, "zoom": 10},
    "Bromo": {"lat": -7.9425, "lon": 112.9530, "zoom": 11},
    "Borobudur": {"lat": -7.6079, "lon": 110.2038, "zoom": 12},
    "Danau Toba": {"lat": 2.6845, "lon": 98.8756, "zoom": 8},
    "Labuan Bajo": {"lat": -8.4960, "lon": 119.8877, "zoom": 11}
}

INVESTMENT_RECOMMENDATIONS = {
    "Bromo": {
        "zone": "Zona Akselerasi Infrastruktur",
        "strategy": "BUILD",
        "gap": "+0.901",
        "description": "Demand sangat tinggi, tetapi supply masih rendah. Fokus utama adalah membangun infrastruktur dan fasilitas pendukung agar daya dukung destinasi tidak tertekan.",
        "key": "Bangun infrastruktur prioritas: glamping, shuttle wisata, viewing deck, dan visitor center.",
        "items": [
            {"title": "Glamping & Eco-Lodge 3–4⭐", "desc": "Glass cabin atau glamping tent dengan view kaldera. Skala butik 20–50 unit di area Cemoro Lawang dan Wonokitri."},
            {"title": "Shuttle Wisata Terorganisir", "desc": "Jeep atau shuttle standar dari Malang dan Probolinggo untuk menekan masalah harga transportasi yang tidak terstandarisasi."},
            {"title": "Viewing Deck & Visitor Center", "desc": "Fasilitas premium seperti toilet bersih, warung terstandar, viewing deck, dan interpretive center ekosistem Tengger."}
        ]
    },
    "Bangka Belitung": {
        "zone": "Zona Akselerasi Infrastruktur",
        "strategy": "BUILD",
        "gap": "+0.659",
        "description": "Demand kuat, tetapi supply belum mengejar. Fokus investasi diarahkan pada akomodasi, F&B, dan layanan island hopping yang lebih standar.",
        "key": "Bangun beachfront resort, dining experience, dan standardisasi boat tourism.",
        "items": [
            {"title": "Beachfront Resort Bintang 4", "desc": "Resort tropis modern 60–100 kamar dengan pool dan sea view. Target utama pasangan dan keluarga kelas menengah atas."},
            {"title": "Seafood Fine Dining & F&B", "desc": "Mengangkat kuliner lokal seperti mie koba dan lempah kuning menjadi experience dining dengan standar kebersihan dan konsistensi rasa."},
            {"title": "Island Hopping Boat Terstandar", "desc": "Standarisasi speedboat ke Pulau Lengkuas dan Batu Berlayar agar harga, keamanan, dan kualitas layanan lebih konsisten."}
        ]
    },
    "Wakatobi": {
        "zone": "Zona Akselerasi Infrastruktur",
        "strategy": "BUILD",
        "gap": "+0.637",
        "description": "Potensi wisata bahari sangat kuat, tetapi supply dan konektivitas masih menjadi hambatan utama.",
        "key": "Prioritas pada dive resort, konektivitas udara, dan marine center.",
        "items": [
            {"title": "Dive Resort Bintang 4–5", "desc": "All-inclusive dive resort butik 20–40 kamar dengan harga premium, meniru benchmark seperti Wakatobi Dive Resort."},
            {"title": "Konektivitas Udara", "desc": "Tambah frekuensi Kendari–Wakatobi atau buka rute Makassar langsung karena akses adalah bottleneck utama investasi."},
            {"title": "Dive Center & Marine Center", "desc": "Sertifikasi PADI internasional dan coral restoration program untuk meningkatkan value proposition destinasi."}
        ]
    },
    "Labuan Bajo": {
        "zone": "Zona Pengendalian Kualitas",
        "strategy": "UPGRADE",
        "gap": "+0.080",
        "description": "Supply relatif siap. Fokus bukan menambah kapasitas daratan secara masif, tetapi menaikkan kualitas dan diferensiasi pengalaman.",
        "key": "Kembangkan liveaboard luxury, premium F&B, dan smart tourism management.",
        "items": [
            {"title": "Liveaboard Luxury", "desc": "Kapal tinggal mewah untuk pengalaman Komodo dan Padar, unik tanpa menambah beban daratan."},
            {"title": "Premium F&B & Sunset Dining", "desc": "Fine dining dengan view pelabuhan dan kuliner NTT seperti ikan serta jagung bose."},
            {"title": "Smart Tourism Management", "desc": "Booking terpusat Taman Nasional Komodo dan digital visitor management untuk mengatur kapasitas kunjungan."}
        ]
    },
    "Borobudur": {
        "zone": "Zona Pengendalian Kualitas",
        "strategy": "UPGRADE",
        "gap": "+0.166",
        "description": "Destinasi sudah kuat dari sisi demand dan supply. Investasi diarahkan pada pengalaman budaya premium dan MICE.",
        "key": "Naikkan value melalui heritage boutique hotel, cultural center, dan MICE.",
        "items": [
            {"title": "Heritage Boutique Hotel 4–5⭐", "desc": "Joglo-style resort sekitar 5 km dari candi untuk mendorong slow travel 2–3 malam dan eksplorasi desa sekitar."},
            {"title": "Cultural Experience Center", "desc": "Workshop batik, meditasi sunrise, dan pertunjukan Ramayana sebagai produk pengalaman budaya."},
            {"title": "MICE Infrastructure", "desc": "Convention center kecil yang terintegrasi dengan resort untuk menargetkan pasar MICE internasional."}
        ]
    },
    "Raja Ampat": {
        "zone": "Zona Pengendalian Kualitas",
        "strategy": "UPGRADE",
        "gap": "+0.194",
        "description": "Demand kuat dan supply relatif tersedia. Fokus pada pariwisata premium berbasis konservasi.",
        "key": "Perkuat eco-resort, marine conservation, dan liveaboard premium.",
        "items": [
            {"title": "Eco-Resort & Dive Lodge 4⭐", "desc": "Resort butik 20–40 kamar berbasis konservasi untuk segmen wisman premium dan dive enthusiast."},
            {"title": "Marine Conservation Program", "desc": "Kolaborasi resort dan NGO untuk coral restoration sebagai unique selling proposition global."},
            {"title": "Akses Liveaboard Premium", "desc": "Kapal liveaboard mewah untuk island hopping ke Wayag, Misool, dan Pianemo."}
        ]
    },
    "Danau Toba": {
        "zone": "Zona Pengendalian Kualitas",
        "strategy": "UPGRADE",
        "gap": "+0.166",
        "description": "Destinasi memiliki potensi kuat untuk wisata danau, budaya Batak, festival, dan MICE.",
        "key": "Kembangkan lakeside resort, cultural trail, dan festival hub.",
        "items": [
            {"title": "Lakeside Resort Bintang 4", "desc": "Resort view danau dengan sentuhan arsitektur Batak untuk wisatawan domestik premium dan MICE."},
            {"title": "Cultural & Heritage Trail", "desc": "Paket wisata budaya Batak seperti Desa Adat Tomok, Huta Bolon, museum, dan tenun ulos."},
            {"title": "Water Sport & Festival Hub", "desc": "Fasilitas jet ski, kayak, sailing, serta venue festival internasional seperti Toba Caldera Festival."}
        ]
    },
    "Mandalika": {
        "zone": "Zona Pengendalian Kualitas",
        "strategy": "UPGRADE",
        "gap": "-0.105",
        "description": "Supply cukup kuat, tetapi perlu anchor attraction di luar musim event besar agar kunjungan lebih stabil.",
        "key": "Dorong sport tourism, hotel mid-range, dan beach club sebagai anchor non-event.",
        "items": [
            {"title": "Sport Tourism Facilities", "desc": "Cycling track, surf school berstandar, dan beach volleyball untuk wisatawan aktif."},
            {"title": "Mid-Range Hotel 3⭐", "desc": "Mengisi hunian off-event, terutama untuk segmen wisatawan domestik non-Jabodetabek."},
            {"title": "Beach Club & Entertainment", "desc": "Lifestyle anchor non-event agar Mandalika tidak hanya bergantung pada musim lomba."}
        ]
    },
    "Likupang": {
        "zone": "Zona Pengendalian Kualitas",
        "strategy": "UPGRADE",
        "gap": "-0.270",
        "description": "Supply relatif cukup. Fokus utama adalah mengemas pengalaman dan konektivitas, bukan menambah hotel.",
        "key": "Kembangkan experience product, koneksi Manado, dan wellness retreat.",
        "items": [
            {"title": "Experience Product", "desc": "Kembangkan paket bahari dan snorkeling berstandar internasional, bukan sekadar menambah hotel."},
            {"title": "Koneksi ke Manado", "desc": "Transport terorganisir Manado–Likupang agar destinasi bisa diposisikan sebagai weekend escape."},
            {"title": "Corporate & Wellness Retreat", "desc": "Manfaatkan ketenangan Likupang untuk retreat tanpa bergantung pada mass tourism."}
        ]
    },
    "Morotai": {
        "zone": "Zona Aktivasi Promosi",
        "strategy": "PROMOTE",
        "gap": "-0.542",
        "description": "Supply sudah memadai, tetapi demand hampir nol. Masalah utama adalah information asymmetry: wisatawan belum tahu harus melakukan apa di Morotai.",
        "key": "Morotai tidak butuh lebih banyak hotel, tetapi butuh visibilitas, branding, dan paket wisata tematik.",
        "items": [
            {"title": "Branding & Digital Marketing", "desc": "Bangun brand story WWII, diving tersembunyi, dan island hopping. Dorong FAM trip, YouTube travel series, Instagram campaign, dan listing global."},
            {"title": "War Heritage Tourism", "desc": "Wreck diving center, war heritage trail, museum mini, dan paket tematik WWII Explorer sebagai USP unik Morotai."},
            {"title": "Paket Wisata Tematik & Tour Operator Lokal", "desc": "Pelatihan tour operator, bundling flight-akomodasi-aktivitas, kerja sama maskapai, dan fokus pada dive enthusiast serta heritage traveler."}
        ]
    }
}

# =========================================================
# 6. SIDEBAR
# =========================================================
logo_base64 = img_to_base64("assets/logo_kemenparekraf.png")

if logo_base64:
    st.sidebar.markdown(
        f'<div style="text-align:center; margin-bottom:18px;">'
        f'<img src="data:image/png;base64,{logo_base64}" style="width:120px;">'
        f'</div>',
        unsafe_allow_html=True
    )

st.sidebar.markdown(
    '<div class="sidebar-title">Navigasi Data</div>'
    '<div class="sidebar-subtitle">'
    'Pilih destinasi untuk melihat detail demand, supply, gap, cluster, peta, dan rekomendasi investasi.'
    '</div>',
    unsafe_allow_html=True
)

pilihan_dpp = st.sidebar.selectbox(
    "Pilih Destinasi Evaluasi:",
    ["-- Ringkasan Nasional --"] + list(df["DPP"].unique())
)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown(
    '<div style="font-size:13px; color:#CBD5E1; line-height:1.6;">'
    '<b style="color:#D4AF37;">Cluster Interpretation</b><br><br>'
    '<span style="color:#D94A38;">●</span> Cluster 0: Zona Akselerasi Infrastruktur<br>'
    '<span style="color:#2FA866;">●</span> Cluster 1: Zona Pengendalian Kualitas<br>'
    '<span style="color:#2F80ED;">●</span> Cluster 2: Zona Aktivasi Promosi'
    '</div>',
    unsafe_allow_html=True
)

if pilihan_dpp == "-- Ringkasan Nasional --":
    df_filtered = df
else:
    df_filtered = df[df["DPP"] == pilihan_dpp]

# =========================================================
# 7. HERO HEADER
# =========================================================
hero_logo_html = ""
if logo_base64:
    hero_logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="hero-logo">'

hero_html = (
    f'<div class="hero-card">'
    f'<div class="hero-top">'
    f'{hero_logo_html}'
    f'<div><div class="hero-badge">Kemenparekraf / Baparekraf Republik Indonesia</div></div>'
    f'</div>'
    f'<div class="hero-title">Emerging Tourism <span>Investment Opportunity</span></div>'
    f'<div class="hero-subtitle">'
    f'Dashboard analisis berbasis data untuk memetakan peluang investasi pariwisata pada '
    f'10 Destinasi Pariwisata Prioritas Indonesia berdasarkan demand, supply, clustering, '
    f'dan demand-supply gap analysis.'
    f'</div>'
    f'<div class="hero-footer">'
    f'<div class="hero-chip">Demand–Supply Scoring</div>'
    f'<div class="hero-chip">K-Means Clustering</div>'
    f'<div class="hero-chip">Gap Analysis</div>'
    f'<div class="hero-chip">Investment Mapping</div>'
    f'</div>'
    f'</div>'
)

st.markdown(hero_html, unsafe_allow_html=True)

# =========================================================
# 8. DPP PHOTO SECTION
# =========================================================
if pilihan_dpp == "-- Ringkasan Nasional --":
    st.markdown('<div class="section-title">Visual Showcase of 10 Priority Destinations</div>', unsafe_allow_html=True)

    gallery_html = '<div class="dpp-gallery">'

    for dpp_name, image_path in DPP_IMAGES.items():
        gallery_html += image_card_html(
            title=dpp_name,
            image_path=image_path,
            tag="Priority DPP"
        )

    gallery_html += '</div>'

    st.markdown(gallery_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

else:
    selected_image_path = DPP_IMAGES.get(pilihan_dpp, "")
    selected_tagline = DPP_TAGLINE.get(pilihan_dpp, "Priority Tourism Destination")

    st.markdown(
        selected_image_html(
            title=pilihan_dpp,
            image_path=selected_image_path,
            subtitle=selected_tagline
        ),
        unsafe_allow_html=True
    )

# =========================================================
# 9. KPI SECTION
# =========================================================
if pilihan_dpp == "-- Ringkasan Nasional --":
    total_dpp = df["DPP"].nunique()
    avg_demand = df["Demand_Score"].mean()
    avg_supply = df["Supply_Score"].mean()
    max_gap_dpp = df.loc[df["Gap_Analysis"].idxmax(), "DPP"]
    max_gap_value = df["Gap_Analysis"].max()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f'<div class="kpi-container">'
            f'<div class="kpi-title">Total DPP Dianalisis</div>'
            f'<div class="kpi-value">{total_dpp}</div>'
            f'<div class="kpi-note">Destinasi prioritas nasional</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f'<div class="kpi-container">'
            f'<div class="kpi-title">Rata-rata Demand</div>'
            f'<div class="kpi-value">{avg_demand:.3f}</div>'
            f'<div class="kpi-note">Indeks daya tarik pasar</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f'<div class="kpi-container">'
            f'<div class="kpi-title">Rata-rata Supply</div>'
            f'<div class="kpi-value">{avg_supply:.3f}</div>'
            f'<div class="kpi-note">Indeks kesiapan destinasi</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f'<div class="kpi-container">'
            f'<div class="kpi-title">Gap Tertinggi</div>'
            f'<div class="kpi-value" style="font-size:26px;">{max_gap_dpp}</div>'
            f'<div class="kpi-note">{max_gap_value:+.3f} | Prioritas supply expansion</div>'
            f'</div>',
            unsafe_allow_html=True
        )

else:
    d_score = df_filtered["Demand_Score"].values[0]
    s_score = df_filtered["Supply_Score"].values[0]
    g_score = df_filtered["Gap_Analysis"].values[0]
    cluster_id_selected = str(df_filtered["Cluster_K3"].values[0])

    if cluster_id_selected == "0":
        cluster_label = "Zona Akselerasi Infrastruktur"
        cluster_note = "demand tinggi, namun kesiapan supply belum memadai"
    elif cluster_id_selected == "1":
        cluster_label = "Zona Pengendalian Kualitas"
        cluster_note = "demand dan supply relatif siap atau seimbang"
    else:
        cluster_label = "Zona Aktivasi Promosi"
        cluster_note = "supply relatif lebih tinggi dibanding demand"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f'<div class="kpi-container">'
            f'<div class="kpi-title">Destinasi</div>'
            f'<div class="kpi-value" style="font-size:28px;">{pilihan_dpp}</div>'
            f'<div class="kpi-note">DPP terpilih</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f'<div class="kpi-container">'
            f'<div class="kpi-title">Indeks Demand</div>'
            f'<div class="kpi-value">{d_score:.3f}</div>'
            f'<div class="kpi-note">Daya tarik pasar</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f'<div class="kpi-container">'
            f'<div class="kpi-title">Kesiapan Supply</div>'
            f'<div class="kpi-value">{s_score:.3f}</div>'
            f'<div class="kpi-note">Kesiapan destinasi</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with col4:
        gap_color = "#D94A38" if g_score > 0.2 else ("#2F80ED" if g_score < -0.2 else "#D4AF37")
        st.markdown(
            f'<div class="kpi-container">'
            f'<div class="kpi-title">Nilai Gap</div>'
            f'<div class="kpi-value" style="color:{gap_color} !important;">{g_score:+.3f}</div>'
            f'<div class="kpi-note">{cluster_label}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        f'<div class="info-card">'
        f'<b>Insight destinasi:</b> {pilihan_dpp} berada pada <b>{cluster_label}</b>. '
        f'Artinya, {cluster_note}. Strategi investasi perlu diarahkan sesuai karakteristik cluster agar intervensi tidak dipukul rata.'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# 10. VISUALIZATION SECTION
# =========================================================
if pilihan_dpp == "-- Ringkasan Nasional --":
    st.markdown('<div class="section-title">Analytical Dashboard Overview</div>', unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

        color_map_scatter = {
            "0": "#D94A38",
            "1": "#2FA866",
            "2": "#2F80ED"
        }

        fig_scatter = px.scatter(
            df,
            x="Demand_Score",
            y="Supply_Score",
            color="Cluster_K3",
            hover_name="DPP",
            color_discrete_map=color_map_scatter
        )

        fig_scatter.update_traces(
            marker=dict(size=18, line=dict(width=1.5, color="#F8FAFC"))
        )

        fig_scatter.update_layout(
            title=dict(
                text="Pemetaan K-Means Demand–Supply",
                font=dict(size=18, color="#F8FAFC", family="Plus Jakarta Sans")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title=dict(text="Demand Score", font=dict(color="#CBD5E1")),
                showgrid=True,
                gridcolor="rgba(148,163,184,0.16)",
                zerolinecolor="rgba(212,175,55,0.45)",
                tickfont=dict(color="#CBD5E1")
            ),
            yaxis=dict(
                title=dict(text="Supply Score", font=dict(color="#CBD5E1")),
                showgrid=True,
                gridcolor="rgba(148,163,184,0.16)",
                zerolinecolor="rgba(212,175,55,0.45)",
                tickfont=dict(color="#CBD5E1")
            ),
            legend=dict(
                title=dict(text="Cluster", font=dict(color="#CBD5E1")),
                font=dict(color="#CBD5E1"),
                bgcolor="rgba(7,26,51,0.55)"
            ),
            margin=dict(l=0, r=10, t=50, b=0)
        )

        st.plotly_chart(fig_scatter, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_chart2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

        df_sorted = df.sort_values("Gap_Analysis")
        df_sorted["Color"] = df_sorted["Gap_Analysis"].apply(
            lambda x: "#D94A38" if x > 0.2 else ("#2F80ED" if x < -0.2 else "#D4AF37")
        )

        fig_bar = px.bar(
            df_sorted,
            x="Gap_Analysis",
            y="DPP",
            orientation="h"
        )

        fig_bar.update_traces(
            marker_color=df_sorted["Color"],
            marker_line_width=0
        )

        fig_bar.add_vline(
            x=0,
            line_width=2,
            line_dash="dash",
            line_color="#D4AF37"
        )

        fig_bar.update_layout(
            title=dict(
                text="Spektrum Demand–Supply Gap",
                font=dict(size=18, color="#F8FAFC", family="Plus Jakarta Sans")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title=dict(text="Nilai Gap", font=dict(color="#CBD5E1")),
                showgrid=True,
                gridcolor="rgba(148,163,184,0.16)",
                tickfont=dict(color="#CBD5E1")
            ),
            yaxis=dict(
                title=dict(text="", font=dict(color="#CBD5E1")),
                tickfont=dict(color="#F8FAFC", size=12)
            ),
            margin=dict(l=0, r=0, t=50, b=0)
        )

        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

# =========================================================
# 11. MAP SECTION
# =========================================================
st.markdown('<div class="section-title">Geospatial Distribution of Tourism Infrastructure</div>', unsafe_allow_html=True)

try:
    with open("Peta_SuperMap_Ikon_Penuh_Cleaned.html", "r", encoding="utf-8") as f:
        html_map = f.read()

    html_map = focus_html_map(html_map, pilihan_dpp)

    st.markdown("<div class='map-card'>", unsafe_allow_html=True)
    components.html(html_map, height=560, scrolling=False)
    st.markdown("</div>", unsafe_allow_html=True)

except FileNotFoundError:
    st.error("File 'Peta_SuperMap_Ikon_Penuh_Cleaned.html' tidak ditemukan. Pastikan file peta berada di folder yang sama dengan app.py.")

# =========================================================
# 12. STRATEGIC INVESTMENT RECOMMENDATIONS
# =========================================================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Strategic Investment Recommendations</div>', unsafe_allow_html=True)

if pilihan_dpp == "-- Ringkasan Nasional --":
    st.markdown(national_strategy_html(), unsafe_allow_html=True)

else:
    rec = INVESTMENT_RECOMMENDATIONS.get(pilihan_dpp)

    if rec is None:
        st.warning(f"Rekomendasi untuk {pilihan_dpp} belum tersedia.")
    else:
        st.markdown(detail_recommendation_html(pilihan_dpp, rec), unsafe_allow_html=True)

# =========================================================
# 13. FOOTER
# =========================================================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center; color:#94A3B8; font-size:13px; padding-bottom:10px;">'
    'Insight. Investment. Impact. | Emerging Tourism Investment Opportunity Mapping'
    '</div>',
    unsafe_allow_html=True
)