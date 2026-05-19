"""
InsureTrack — CYS Caloyeras Insurance Portfolio Manager
Rose Garden Edition · v5.0
"""
import json, os, io
from datetime import date, datetime
from collections import defaultdict

import streamlit as st
import plotly.graph_objects as go

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InsureTrack · CYS",
    page_icon="🌹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Rose Garden palette ─────────────────────────────────────────────────────
R = dict(
    bg        = "#FDF6F0",
    plum      = "#4A1942",
    plum_mid  = "#6B2C61",
    rose      = "#D4547A",
    rose_lt   = "#F2C4CE",
    rose_pale = "#FDE8EE",
    text_d    = "#3B0764",
    text_m    = "#9D8090",
    text_l    = "#C4A0B0",
    white     = "#FFFFFF",
    amber     = "#F59E0B",
    amber_lt  = "#FFFBEB",
    green     = "#22C55E",
    green_lt  = "#F0FDF4",
    red       = "#EF4444",
    red_lt    = "#FEE2E2",
    gray_lt   = "#F3F4F6",
)

# ─── Global CSS ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {{
    background: {R['bg']} !important;
    color: {R['text_d']};
    font-family: 'Inter', 'Segoe UI', sans-serif;
}}
[data-testid="stSidebar"] {{ background: {R['plum']} !important; }}
[data-testid="stSidebar"] * {{ color: #EDD8E8 !important; }}
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ display: none; }}
.block-container {{ padding: 1.5rem 2rem 2rem; max-width: 1400px; }}
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-thumb {{ background: {R['rose_lt']}; border-radius: 3px; }}
.stButton > button {{
    background: {R['rose']} !important; color: {R['white']} !important;
    border: none !important; border-radius: 8px !important;
    padding: 0.45rem 1.2rem !important; font-weight: 600 !important;
    transition: all .18s;
}}
.stButton > button:hover {{
    background: {R['plum']} !important; transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(74,25,66,.25) !important;
}}
/* Sidebar nav — ghost style, not solid rose */
[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important; color: #C4A0B0 !important;
    border: none !important; border-radius: 6px !important;
    text-align: left !important; font-weight: 500 !important;
    padding: 0.45rem 0.8rem !important;
    justify-content: flex-start !important;
    transform: none !important; box-shadow: none !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,.10) !important; color: #fff !important;
    transform: none !important; box-shadow: none !important;
}}
.stTextInput > div > div > input,
.stSelectbox > div > div {{
    border: 1.5px solid {R['rose_lt']} !important;
    border-radius: 8px !important;
    background: {R['white']} !important; color: {R['text_d']} !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {R['rose']} !important;
    box-shadow: 0 0 0 3px rgba(212,84,122,.15) !important;
}}
.stNumberInput > div > div > input,
.stNumberInput input,
div[data-testid="stNumberInput"] input,
div[data-testid="stNumberInput"] > div > input {{
    border: 1.5px solid {R['rose_lt']} !important;
    border-radius: 8px !important;
    background: {R['white']} !important; color: {R['text_d']} !important;
}}
.stTextArea > div > div > textarea,
div[data-testid="stTextArea"] textarea {{
    border: 1.5px solid {R['rose_lt']} !important;
    border-radius: 8px !important;
    background: {R['white']} !important; color: {R['text_d']} !important;
}}
/* Stepper buttons on number inputs */
.stNumberInput button {{
    background: {R['rose_pale']} !important; color: {R['rose']} !important;
    border: none !important; border-radius: 6px !important;
    transform: none !important; box-shadow: none !important;
    padding: 0.2rem 0.5rem !important; font-size: .9rem !important;
}}
.stTabs [data-baseweb="tab-list"] {{
    background: {R['white']}; border-radius: 10px; padding: 4px;
    border: 1.5px solid {R['rose_lt']}; gap: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px !important; color: {R['text_m']} !important;
    font-weight: 600 !important; padding: 0.5rem 1.2rem !important;
}}
.stTabs [aria-selected="true"] {{
    background: {R['plum']} !important; color: {R['white']} !important;
}}
.kpi-tile {{
    background: {R['white']}; border: 1.5px solid {R['rose_lt']};
    border-radius: 12px; padding: 1.1rem 1.3rem; text-align: center;
}}
.kpi-tile .kpi-num {{
    font-size: 2rem; font-weight: 800; line-height: 1.1;
}}
.kpi-tile .kpi-lbl {{
    font-size: 0.68rem; font-weight: 700; letter-spacing: .07em;
    text-transform: uppercase; margin-top: 4px; color: {R['text_m']};
}}
.sec-hdr {{
    font-size: 0.72rem; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: {R['text_m']};
    border-bottom: 2px solid {R['rose_lt']};
    padding-bottom: 6px; margin: 1.2rem 0 0.9rem;
    display: flex; align-items: center; gap: 6px;
}}
/* Richer expanders */
.streamlit-expanderHeader {{
    background: {R['white']} !important;
    border: 1.5px solid {R['rose_lt']} !important;
    border-radius: 10px !important;
    padding: .55rem 1rem !important;
    font-weight: 600 !important; color: {R['text_d']} !important;
    transition: background .15s;
}}
.streamlit-expanderHeader:hover {{
    background: {R['rose_pale']} !important;
    border-color: {R['rose']} !important;
}}
.streamlit-expanderContent {{
    border: 1.5px solid {R['rose_lt']} !important;
    border-top: none !important; border-radius: 0 0 10px 10px !important;
    background: {R['white']} !important; padding: .8rem 1rem !important;
}}
/* Better sidebar logo area */
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown p {{ color: #EDD8E8 !important; }}
/* Page header style */
.page-hdr {{
    font-size: 1.55rem; font-weight: 800; color: {R['text_d']};
    margin-bottom: .15rem; display: flex; align-items: center; gap: .5rem;
}}
.page-sub {{
    font-size: .83rem; color: {R['text_m']}; margin-bottom: 1.1rem;
}}
.badge {{
    display: inline-block; padding: 2px 10px;
    border-radius: 20px; font-size: 0.72rem; font-weight: 700;
}}
.badge-active  {{ background: {R['green_lt']};  color: #15803D; }}
.badge-quote   {{ background: {R['amber_lt']};  color: #92400E; }}
.badge-uninsu  {{ background: {R['red_lt']};    color: #991B1B; }}
.badge-verify  {{ background: {R['amber_lt']};  color: #92400E; }}
.badge-ext     {{ background: {R['gray_lt']};   color: {R['text_m']}; }}
.rg-card-sm {{
    background: {R['white']}; border: 1.5px solid {R['rose_lt']};
    border-radius: 10px; padding: 0.9rem 1.1rem;
}}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  DATA
# ═══════════════════════════════════════════════════════════════════
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "caloyeras", "portfolio.json")

@st.cache_data(ttl=300)
def load_data(path=DATA_PATH):
    with open(path) as f:
        return json.load(f)

def save_data(data, path=DATA_PATH):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    load_data.clear()

def _today():
    return date.today()

def _days_to(date_str):
    if not date_str:
        return None
    try:
        return (datetime.strptime(date_str, "%Y-%m-%d").date() - _today()).days
    except Exception:
        return None

def unique_policies(policies):
    seen, out = set(), []
    for p in policies:
        if p["policy_number"] not in seen:
            seen.add(p["policy_number"])
            out.append(p)
    return out

def total_premium(policies):
    return sum(p.get("premium") or 0 for p in unique_policies(policies))

def coverage_badge(status):
    if status == "Active":
        return '<span class="badge badge-active">✓ Active</span>'
    if status == "Quote":
        return '<span class="badge badge-quote">◎ Quote</span>'
    if status == "Uninsured":
        return '<span class="badge badge-uninsu">✗ Uninsured</span>'
    if "Verify" in status and "External" not in status:
        return '<span class="badge badge-verify">? Verify</span>'
    if "External" in status:
        return '<span class="badge badge-ext">⊙ Ext Owner</span>'
    return f'<span class="badge badge-ext">{status}</span>'


# ─── City → lat/lon lookup (no API key needed) ────────────────────
CITY_COORDS = {
    "Seattle":        (47.6062, -122.3321),
    "Tacoma":         (47.2529, -122.4443),
    "Spokane":        (47.6588, -117.4260),
    "Bellevue":       (47.6101, -122.2015),
    "Renton":         (47.4799, -122.2171),
    "Kent":           (47.3809, -122.2348),
    "Auburn":         (47.3073, -122.2285),
    "Federal Way":    (47.3223, -122.3126),
    "Kirkland":       (47.6815, -122.2087),
    "Redmond":        (47.6740, -122.1215),
    "Everett":        (47.9790, -122.2021),
    "Marysville":     (48.0517, -122.1771),
    "Lynnwood":       (47.8209, -122.3151),
    "Edmonds":        (47.8107, -122.3776),
    "Shoreline":      (47.7543, -122.3416),
    "Burien":         (47.4704, -122.3468),
    "Tukwila":        (47.4740, -122.2612),
    "SeaTac":         (47.4435, -122.2987),
    "Des Moines":     (47.4015, -122.3243),
    "Puyallup":       (47.1854, -122.2929),
    "Lakewood":       (47.1718, -122.5185),
    "Olympia":        (47.0379, -122.9007),
    "Bremerton":      (47.5673, -122.6329),
    "Yakima":         (46.6021, -120.5059),
    "Kennewick":      (46.2112, -119.1372),
    "Richland":       (46.2857, -119.2845),
    "Pasco":          (46.2396, -119.1006),
    "Vancouver":      (45.6387, -122.6615),
    "Bellingham":     (48.7519, -122.4787),
    "Mount Vernon":   (48.4215, -122.3343),
    "Wenatchee":      (47.4235, -120.3103),
    "Ellensburg":     (46.9965, -120.5478),
    "Walla Walla":    (46.0646, -118.3430),
    "Pullman":        (46.7298, -117.1817),
    "Longview":       (46.1382, -122.9382),
    "Centralia":      (46.7165, -122.9543),
    "Port Angeles":   (48.1181, -123.4307),
    "Port Townsend":  (48.1170, -122.7601),
    "Anacortes":      (48.5126, -122.6127),
    "Oak Harbor":     (48.2937, -122.6429),
    "Poulsbo":        (47.7354, -122.6468),
    "Gig Harbor":     (47.3298, -122.5793),
    "Covington":      (47.3584, -122.1079),
    "Maple Valley":   (47.3665, -122.0454),
    "Black Diamond":  (47.3088, -122.0004),
    "Enumclaw":       (47.2018, -121.9918),
    "Bonney Lake":    (47.1779, -122.1801),
    "Sumner":         (47.2040, -122.2290),
    "Pacific":        (47.2640, -122.2526),
    "Milton":         (47.2529, -122.3148),
    "Fife":           (47.2376, -122.3590),
    "Edgewood":       (47.2285, -122.2945),
    "South Hill":     (47.1462, -122.2943),
    "Spanaway":       (47.1015, -122.4285),
    "Graham":         (47.0523, -122.2987),
    "University Place": (47.2126, -122.5435),
    "Steilacoom":     (47.1718, -122.5985),
    "DuPont":         (47.0979, -122.6271),
    "Orting":         (47.0993, -122.2024),
    "Eatonville":     (46.8712, -122.2641),
    "Carbonado":      (47.0843, -122.0546),
    "Wilkeson":       (47.0982, -122.0398),
    "Buckley":        (47.1596, -122.0257),
    "Greenwater":     (47.1337, -121.6338),
    "Ashford":        (46.7599, -122.0227),
    "Yelm":           (46.9415, -122.6143),
    "Roy":            (47.0120, -122.3776),
    "Anderson Island":(47.1543, -122.7048),
    "Vashon":         (47.4418, -122.4709),
    "Bainbridge Island": (47.6426, -122.5381),
    "Fox Island":     (47.2565, -122.6298),
    "Mercer Island":  (47.5707, -122.2221),
    "Medina":         (47.6243, -122.2265),
    "Clyde Hill":     (47.6293, -122.2110),
    "Yarrow Point":   (47.6482, -122.2123),
    "Hunts Point":    (47.6468, -122.2176),
    "Beaux Arts Village": (47.5943, -122.1990),
    "Newcastle":      (47.5293, -122.1601),
    "Sammamish":      (47.6163, -122.0355),
    "Issaquah":       (47.5301, -122.0326),
    "North Bend":     (47.4957, -121.7868),
    "Snoqualmie":     (47.5265, -121.8257),
    "Fall City":      (47.5615, -121.9035),
    "Carnation":      (47.6479, -121.9152),
    "Duvall":         (47.7426, -121.9843),
    "Monroe":         (47.8554, -121.9713),
    "Snohomish":      (47.9129, -122.0985),
    "Gold Bar":       (47.8521, -121.6924),
    "Index":          (47.8193, -121.5526),
    "Sultan":         (47.8654, -121.8124),
    "Startup":        (47.8526, -121.7468),
    "Skykomish":      (47.7101, -121.3563),
    "Leavenworth":    (47.5963, -120.6615),
    "Cashmere":       (47.5218, -120.4682),
    "Chelan":         (47.8393, -120.0182),
    "Manson":         (47.8837, -120.1568),
    "Entiat":         (47.6693, -120.2115),
    "Malaga":         (47.3751, -120.3032),
    "Quincy":         (47.2354, -119.8529),
    "Ephrata":        (47.3179, -119.5527),
    "Moses Lake":     (47.1301, -119.2779),
    "Othello":        (46.8268, -119.1712),
    "Ritzville":      (47.1265, -118.3791),
    "Davenport":      (47.6573, -118.1591),
    "Wilbur":         (47.7554, -118.7032),
    "Grand Coulee":   (47.9393, -118.9757),
    "Electric City":  (47.9260, -119.0135),
    "Coulee City":    (47.6107, -119.2910),
    "Soap Lake":      (47.3882, -119.4985),
    "Cheney":         (47.4873, -117.5782),
    "Deer Park":      (47.9554, -117.4757),
    "Mead":           (47.7690, -117.3535),
    "Medical Lake":   (47.5693, -117.6813),
    "Airway Heights": (47.6457, -117.5921),
    "Spokane Valley": (47.6732, -117.2394),
    "Liberty Lake":   (47.6693, -117.1040),
    "Millwood":       (47.6726, -117.2915),
    "Veradale":       (47.6565, -117.2035),
    "Greenacres":     (47.6640, -117.1610),
    "Otis Orchards":  (47.6943, -117.1029),
    "Newman Lake":    (47.7254, -117.0713),
    "Colbert":        (47.8582, -117.3682),
    "Chattaroy":      (47.8982, -117.3440),
    "Elk":            (47.9415, -117.2835),
    "Clayton":        (47.9921, -117.5593),
    "Ford":           (47.8726, -117.8007),
    "Springdale":     (48.0576, -117.7640),
    "Chewelah":       (48.2776, -117.7157),
    "Colville":       (48.5465, -117.9018),
    "Kettle Falls":   (48.6054, -118.0574),
    "Republic":       (48.6487, -118.7326),
    "Tonasket":       (48.7051, -119.4382),
    "Okanogan":       (48.3598, -119.5729),
    "Omak":           (48.4115, -119.5279),
    "Pateros":        (48.0526, -119.9018),
    "Bridgeport":     (47.9771, -119.6643),
    "Brewster":       (48.0951, -119.7779),
    "Twisp":          (48.3607, -120.1196),
    "Winthrop":       (48.4751, -120.1793),
    "Mazama":         (48.5951, -120.4024),
    "Concrete":       (48.5376, -121.7532),
    "Sedro-Woolley":  (48.5054, -122.2368),
    "Burlington":     (48.4751, -122.3296),
    "Bow":            (48.5426, -122.3793),
    "La Conner":      (48.3943, -122.4982),
    "Coupeville":     (48.2204, -122.6854),
    "Langley":        (48.0418, -122.4076),
    "Clinton":        (47.9715, -122.3593),
    "Freeland":       (48.0001, -122.5168),
    "Greenbank":      (48.1043, -122.5785),
    "Mukilteo":       (47.9490, -122.3040),
    "Mountlake Terrace": (47.7887, -122.3090),
    "Kenmore":        (47.7579, -122.2440),
    "Bothell":        (47.7623, -122.2054),
    "Mill Creek":     (47.8601, -122.2040),
    "Mukilteo":       (47.9490, -122.3040),
    "Woodinville":    (47.7540, -122.1637),
    "Duvall":         (47.7426, -121.9843),
    "Granite Falls":  (48.0840, -121.9724),
    "Arlington":      (48.1968, -122.1196),
    "Stanwood":       (48.2423, -122.3732),
    "Camano Island":  (48.1979, -122.4754),
    "Whidbey Island": (48.2204, -122.6854),
    "Mukilteo":       (47.9490, -122.3040),
}

CHANGELOG_PATH = os.path.join(os.path.dirname(__file__), "data", "caloyeras", "changelog.json")

def load_changelog():
    if os.path.exists(CHANGELOG_PATH):
        try:
            with open(CHANGELOG_PATH) as f:
                return json.load(f)
        except Exception:
            return []
    return []

def log_change(action, detail, user=None):
    changelog = load_changelog()
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user or st.session_state.get("username", "system"),
        "action": action,
        "detail": detail,
    }
    changelog.insert(0, entry)
    # Keep last 500 entries
    changelog = changelog[:500]
    os.makedirs(os.path.dirname(CHANGELOG_PATH), exist_ok=True)
    with open(CHANGELOG_PATH, "w") as f:
        json.dump(changelog, f, indent=2, ensure_ascii=False)

def _get_coords(city, prop_id=""):
    base = CITY_COORDS.get(city)
    if not base:
        # Try partial match
        for k, v in CITY_COORDS.items():
            if city and k.lower().startswith(city.lower()[:4]):
                base = v
                break
    if not base:
        base = (47.6062, -122.3321)  # Default: Seattle
    # Deterministic jitter by prop_id so props don't stack
    seed = sum(ord(c) for c in str(prop_id)) if prop_id else 0
    lat_off = ((seed * 17) % 100 - 50) * 0.0015
    lon_off = ((seed * 31) % 100 - 50) * 0.0015
    return base[0] + lat_off, base[1] + lon_off


# ═══════════════════════════════════════════════════════════════════
#  LOGIN
# ═══════════════════════════════════════════════════════════════════
USERS = {"caloyeras": "cys2026", "admin": "insuretrack"}

def show_login():
    col = st.columns([1, 1.1, 1])[1]
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:{R['white']};border:1.5px solid {R['rose_lt']};
             border-radius:18px;padding:2.5rem;text-align:center;
             box-shadow:0 8px 32px rgba(74,25,66,.12);">
          <div style="font-size:2.4rem;margin-bottom:.4rem;">🌹</div>
          <div style="font-size:1.5rem;font-weight:800;color:{R['text_d']};">InsureTrack</div>
          <div style="font-size:.85rem;color:{R['text_m']};margin-bottom:1.8rem;">
            CYS Caloyeras · Portfolio Manager</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        user = st.text_input("user", placeholder="Username", label_visibility="collapsed",
                             key="li_user")
        pw   = st.text_input("pw", type="password", placeholder="Password",
                             label_visibility="collapsed", key="li_pw")
        if st.button("Sign In →", use_container_width=True):
            if USERS.get(user) == pw:
                st.session_state.logged_in = True
                st.session_state.username  = user
                st.session_state.page      = "dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials.")
        st.markdown(
            f"<div style='text-align:center;font-size:.72rem;color:{R['text_l']};"
            f"margin-top:.6rem;'>v5.0 · Rose Garden</div>",
            unsafe_allow_html=True
        )


# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════
NAV = [
    ("📊", "Dashboard",   "dashboard"),
    ("🗺️", "Mapa",        "map"),
    ("✅", "Tareas",      "tasks"),
    ("📋", "Pólizas",     "policies"),
    ("🏘️", "Propiedades", "properties"),
    ("🚗", "Auto",        "auto"),
    ("📅", "Calendario",  "calendar"),
    ("📈", "Analítica",   "analytics"),
    ("➕", "Add / Edit",  "add"),
    ("📤", "Importar",    "import_data"),
    ("📄", "Reportes",    "reports"),
    ("⚙️", "Settings",   "settings"),
]

def show_sidebar(data):
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:1rem .4rem .8rem;">
          <div style="font-size:1.2rem;font-weight:800;color:{R['white']};">🌹 InsureTrack</div>
          <div style="font-size:.7rem;color:{R['text_l']};margin-top:2px;">
            {data.get('portfolio_name','CYS Caloyeras')}</div>
        </div>
        <hr style="border:none;border-top:1px solid rgba(255,255,255,.12);margin:.2rem 0 .6rem;">
        """, unsafe_allow_html=True)

        cur = st.session_state.get("page", "dashboard")
        for icon, label, key in NAV:
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

        props    = data["properties"]
        active_n = sum(1 for p in props if p.get("coverage_status") == "Active")
        uninsu_n = sum(1 for p in props if p.get("coverage_status") == "Uninsured")
        verify_n = sum(1 for p in props if "Verify" in p.get("coverage_status",""))

        st.markdown(f"""
        <hr style="border:none;border-top:1px solid rgba(255,255,255,.12);margin:.8rem 0 .5rem;">
        <div style="padding:.2rem .4rem;font-size:.7rem;color:{R['text_l']};">
          📦 {len(props)} props · {sum(p.get('units') or 0 for p in props)} units<br>
          ✅ {active_n} insured &nbsp; ⚠️ {uninsu_n + verify_n} gaps
        </div>
        <hr style="border:none;border-top:1px solid rgba(255,255,255,.12);margin:.5rem 0 .4rem;">
        <div style="padding:.1rem .4rem;font-size:.66rem;color:{R['text_l']};">
          v5.0 · Rose Garden · {data.get('as_of_date','')}
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════════════
def page_dashboard(data):
    props    = data["properties"]
    policies = data["policies"]

    active_n  = sum(1 for p in props if p.get("coverage_status") == "Active")
    uninsu_n  = sum(1 for p in props if p.get("coverage_status") == "Uninsured")
    verify_n  = sum(1 for p in props if "Verify" in p.get("coverage_status",""))
    prem_tot  = total_premium(policies)
    tot_units = sum(p.get("units") or 0 for p in props)

    st.markdown(f"""
    <div class="page-hdr">📊 Dashboard</div>
    <div class="page-sub">{data.get('portfolio_name','')} &nbsp;·&nbsp; Actualizado: {data.get('as_of_date','')}</div>
    """, unsafe_allow_html=True)

    # KPIs — white cards with left-border accent + colored numbers
    quote_n = sum(1 for p in props if p.get("coverage_status") == "Quote")
    kpi_data = [
        (str(len(props)),          "Total Properties", R['text_d'],  R['plum']),
        (str(active_n),            "Insured Active",   "#16a34a",    "#16a34a"),
        (str(uninsu_n),            "Uninsured",        "#dc2626",    "#dc2626"),
        (str(verify_n + quote_n),  "Verify / Quote",   "#d97706",    "#d97706"),
        (f"${prem_tot:,.0f}",      "Annual Premium",   R['rose'],    R['rose']),
        (str(tot_units),           "Total Units",      R['plum'],    R['plum_mid']),
    ]
    cols = st.columns(6)
    for col, (num, lbl, color, accent) in zip(cols, kpi_data):
        col.markdown(f"""
        <div style="background:{R['white']};border:1.5px solid {R['rose_lt']};
             border-left:4px solid {accent};border-radius:12px;
             padding:1rem 1.1rem;text-align:center;
             box-shadow:0 2px 8px rgba(74,25,66,.06);">
          <div style="font-size:1.85rem;font-weight:800;line-height:1.1;color:{color};">{num}</div>
          <div style="font-size:0.65rem;font-weight:700;letter-spacing:.08em;
               text-transform:uppercase;margin-top:5px;color:{R['text_m']};">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    # ── Priority Alert Banner ──────────────────────────────────────
    urgent_pols = [p for p in unique_policies(policies)
                   if (_days_to(p.get("expiration_date")) or 999) <= 60
                   and (_days_to(p.get("expiration_date")) or 999) >= 0]
    gap_count   = uninsu_n + verify_n + quote_n
    alerts = []
    if urgent_pols:
        alerts.append(f"⏰ <b>{len(urgent_pols)} póliza{'s' if len(urgent_pols)>1 else ''}</b> "
                      f"vence{'n' if len(urgent_pols)>1 else ''} en menos de 60 días")
    if uninsu_n:
        alerts.append(f"⛔ <b>{uninsu_n} propiedades</b> sin seguro — acción requerida")
    if verify_n:
        alerts.append(f"⚠️ <b>{verify_n} propiedades</b> pendientes de verificación")

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
    if alerts:
        alert_html = "&nbsp;&nbsp;·&nbsp;&nbsp;".join(alerts)
        st.markdown(f"""
        <div style="background:linear-gradient(90deg,#fff1f2,#fffbeb);
             border:1.5px solid #fca5a5;border-radius:12px;
             padding:.8rem 1.4rem;margin-bottom:.8rem;
             display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
          <span style="font-size:1.1rem;">🚨</span>
          <span style="font-size:.82rem;color:#7f1d1d;flex:1;">{alert_html}</span>
        </div>
        """, unsafe_allow_html=True)
        # CTA buttons
        cta1, cta2, cta3 = st.columns([1, 1, 3])
        with cta1:
            if st.button("⛔ Ver propiedades sin seguro", key="cta_uninsu", use_container_width=True):
                st.session_state.page = "properties"
                st.session_state["prop_open_gaps"] = True
                st.rerun()
        with cta2:
            if st.button("📋 Ver pólizas por vencer", key="cta_pol", use_container_width=True):
                st.session_state.page = "policies"
                st.rerun()
    else:
        st.markdown(f"""
        <div style="background:{R['green_lt']};border:1.5px solid #86efac;
             border-radius:12px;padding:.7rem 1.4rem;margin-bottom:.8rem;">
          <span style="font-size:.85rem;color:#14532d;">
            ✅ <b>Todo al día</b> — sin alertas urgentes en el portafolio</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

    left, right = st.columns([1.05, 1], gap="large")

    # ── Renewals ──
    with left:
        st.markdown(f'<div class="sec-hdr">🗓️ Renovaciones Próximas</div>', unsafe_allow_html=True)
        pol_props_map = defaultdict(list)
        for p in policies:
            if p.get("prop_id"):
                pol_props_map[p["policy_number"]].append(p["prop_id"])

        renewals = sorted(
            [p for p in unique_policies(policies) if p.get("expiration_date")],
            key=lambda x: x["expiration_date"]
        )
        for pol in renewals[:12]:
            days = _days_to(pol["expiration_date"])
            if days is None:
                continue
            color   = R['red'] if days <= 60 else (R['amber'] if days <= 180 else R['green'])
            bg      = R['red_lt'] if days <= 60 else (R['amber_lt'] if days <= 180 else R['green_lt'])
            pids    = " · ".join(pol_props_map.get(pol["policy_number"], ["—"]))
            carrier = (pol.get("carrier") or "").split("/")[0].strip()[:24]
            urgency = "⏰" if days <= 60 else ("📅" if days <= 180 else "✅")
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:.55rem .9rem;
                 background:{bg};border-radius:8px;
                 border-left:3px solid {color};margin-bottom:5px;">
              <div style="min-width:48px;text-align:center;">
                <div style="font-weight:800;font-size:.95rem;color:{color};">{days}d</div>
                <div style="font-size:.75rem;">{urgency}</div>
              </div>
              <div style="flex:1;overflow:hidden;">
                <div style="font-size:.8rem;font-weight:700;color:{R['text_d']};
                     white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                  {pol['policy_number']}</div>
                <div style="font-size:.7rem;color:{R['text_m']};">{carrier} · {pids}</div>
              </div>
              <div style="font-size:.7rem;color:{R['text_m']};white-space:nowrap;text-align:right;">
                {pol['expiration_date']}<br>
                <span style="color:{color};font-weight:600;">${pol.get('premium',0):,.0f}</span>
              </div>
            </div>""", unsafe_allow_html=True)

        # Coverage Gaps quick list
        st.markdown(f'<div class="sec-hdr">⛔ Brechas de Cobertura — Prioridad</div>',
                    unsafe_allow_html=True)
        gaps = sorted(
            [p for p in props if p.get("coverage_status") == "Uninsured"],
            key=lambda p: -(p.get("units") or 0)
        )
        for prop in gaps[:7]:
            units = prop.get("units") or 0
            pri   = "🔴 ALTA" if units >= 10 else ("🟠 MEDIA" if units >= 4 else "🟡 BAJA")
            pri_col = R['red'] if units >= 10 else (R['amber'] if units >= 4 else "#ca8a04")
            owner = (prop.get("owner") or "—")[:22]
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:.55rem .9rem;
                 background:{R['red_lt']};border-radius:8px;
                 border-left:3px solid {pri_col};margin-bottom:5px;">
              <div style="font-size:.7rem;font-weight:800;color:{pri_col};min-width:52px;">{pri}</div>
              <div style="flex:1;overflow:hidden;">
                <div style="font-size:.8rem;font-weight:700;color:{R['text_d']};
                     white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                  {prop['prop_id']} · {prop.get('nickname') or prop['address']}</div>
                <div style="font-size:.7rem;color:{R['text_m']};">
                  {prop['city']} · {units} unids · {owner}</div>
              </div>
              <div style="font-size:.7rem;color:{R['red']};font-weight:700;
                   white-space:nowrap;">Sin seguro</div>
            </div>""", unsafe_allow_html=True)
        if len(gaps) > 7:
            st.markdown(f"""<div style="font-size:.75rem;color:{R['text_m']};
                padding:.3rem .8rem;">
                + {len(gaps)-7} más → ir a Propiedades / Coverage Gaps</div>""",
                unsafe_allow_html=True)

    # ── Charts ──
    with right:
        st.markdown(f'<div class="sec-hdr">🏢 Concentración por Asegurador</div>',
                    unsafe_allow_html=True)
        carrier_prem = defaultdict(float)
        for pol in unique_policies(policies):
            c = (pol.get("carrier") or "Unknown").split("/")[0].strip()
            c = c.replace("Insurance Exchange","").replace("Insurance Co","").replace("Ins.","").strip()
            if c.endswith(" "): c = c.strip()
            carrier_prem[c] += pol.get("premium") or 0

        carriers = sorted(carrier_prem.items(), key=lambda x: -x[1])
        labels   = [c[0][:20] for c in carriers]
        values   = [c[1] for c in carriers]
        palette  = [R['plum'], R['rose'], R['amber'], "#7C3AED", "#0EA5E9",
                    "#10B981", "#F97316", R['plum_mid'], R['text_m'], "#64748B"]

        fig = go.Figure(go.Pie(
            labels=labels, values=values, hole=.54,
            marker_colors=palette[:len(labels)],
            textfont_size=10,
            hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            height=250, margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(font_size=9, x=1.02, y=.5, bgcolor="rgba(0,0,0,0)"),
            annotations=[dict(
                text=f"<b>${prem_tot/1000:.0f}K</b>",
                x=.5, y=.5, font_size=14, showarrow=False,
                font_color=R['text_d']
            )]
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Renewal bar chart
        st.markdown(f'<div class="sec-hdr">📆 Renovaciones — Próximos 12 Meses</div>',
                    unsafe_allow_html=True)
        today = _today()
        buckets = defaultdict(float)
        for pol in unique_policies(policies):
            exp = pol.get("expiration_date")
            if not exp: continue
            d     = datetime.strptime(exp, "%Y-%m-%d").date()
            delta = (d.year - today.year) * 12 + d.month - today.month
            if 0 <= delta < 12:
                buckets[d.strftime("%b '%y")] += pol.get("premium") or 0

        if buckets:
            mb = sorted(buckets.items(), key=lambda x: datetime.strptime(x[0], "%b '%y"))
            months = [m[0] for m in mb]
            prems  = [m[1] for m in mb]
            fig2 = go.Figure(go.Bar(
                x=months, y=prems,
                marker_color=[R['red'] if p > 30000 else R['rose'] for p in prems],
                hovertemplate="%{x}<br>$%{y:,.0f}<extra></extra>",
            ))
            fig2.update_layout(
                height=190, margin=dict(l=0, r=0, t=5, b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, tickfont_size=9),
                yaxis=dict(showgrid=True, gridcolor="#F0E8EC",
                           tickformat="$,.0f", tickfont_size=8),
            )
            st.plotly_chart(fig2, use_container_width=True,
                            config={"displayModeBar": False})

        # Coverage status pie
        st.markdown(f'<div class="sec-hdr">🛡️ Distribución de Cobertura</div>',
                    unsafe_allow_html=True)
        status_counts = defaultdict(int)
        for p in props:
            s = p.get("coverage_status","")
            if "External" in s or "Verify" in s:
                status_counts["Verify / External"] += 1
            elif s:
                status_counts[s] += 1
            else:
                status_counts["Unknown"] += 1

        fig3 = go.Figure(go.Pie(
            labels=list(status_counts.keys()),
            values=list(status_counts.values()),
            hole=.4,
            marker_colors=[R['green'], "#991B1B", R['amber'], R['plum'], R['text_m']][:len(status_counts)],
            textfont_size=10,
            hovertemplate="<b>%{label}</b><br>%{value} props<extra></extra>",
        ))
        fig3.update_layout(
            height=190, margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(font_size=9, x=1.02, y=.5, bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════════
#  POLICIES
# ═══════════════════════════════════════════════════════════════════
def page_policies(data):
    props    = data["properties"]
    policies = data["policies"]

    prem_tot = total_premium(policies)
    st.markdown(f"""
    <div style="font-size:1.5rem;font-weight:800;color:{R['text_d']};margin-bottom:.2rem;">
      📋 Policies</div>
    <div style="font-size:.85rem;color:{R['text_m']};margin-bottom:1.2rem;">
      {len(unique_policies(policies))} unique policies · ${prem_tot:,.2f} annual premium</div>
    """, unsafe_allow_html=True)

    pol_props_map = defaultdict(list)
    for p in policies:
        if p.get("prop_id"):
            pol_props_map[p["policy_number"]].append(p["prop_id"])

    fcol1, fcol2, fcol3 = st.columns([2, 1.2, 1.2])
    with fcol1:
        search = st.text_input("s", placeholder="Search policy # or carrier…",
                               label_visibility="collapsed", key="pol_q")
    with fcol2:
        sf = st.selectbox("st", ["All Statuses","Active","Quote","Expired"],
                          label_visibility="collapsed", key="pol_sf")
    with fcol3:
        so = st.selectbox("so", ["Sort: Expiration","Sort: Premium ↓","Sort: Carrier"],
                          label_visibility="collapsed", key="pol_so")

    uniq = unique_policies(policies)
    if search:
        q = search.lower()
        uniq = [p for p in uniq
                if q in p["policy_number"].lower()
                or q in (p.get("carrier") or "").lower()
                or q in (p.get("agency") or "").lower()]
    if sf != "All Statuses":
        uniq = [p for p in uniq if p.get("status") == sf]
    if "Premium" in so:
        uniq.sort(key=lambda x: -(x.get("premium") or 0))
    elif "Carrier" in so:
        uniq.sort(key=lambda x: x.get("carrier") or "")
    else:
        uniq.sort(key=lambda x: x.get("expiration_date") or "")

    st.caption(f"{len(uniq)} policies shown")

    for pol in uniq:
        days    = _days_to(pol.get("expiration_date"))
        status  = pol.get("status","")
        s_color = (R['green'] if status == "Active" else
                   R['amber'] if status == "Quote" else R['red'])
        s_icon  = ("🟢" if status == "Active" else
                   "🟡" if status == "Quote" else
                   "🔴" if status in ("Expired","Cancelled") else "⚪")
        days_str = f"{days}d" if days is not None else "—"
        days_col = (R['red'] if (days or 999) <= 60 else
                    R['amber'] if (days or 999) <= 180 else R['green'])
        days_icon = ("⏰" if (days or 999) <= 60 else
                     "⚡" if (days or 999) <= 180 else "")
        pids     = " · ".join(pol_props_map.get(pol["policy_number"], ["—"]))
        carrier  = (pol.get("carrier") or "")
        prem     = pol.get("premium") or 0

        with st.expander(
            f"{s_icon}  {pol['policy_number']}  ·  {carrier[:28]}  ·  ${prem:,.0f}"
            f"  {days_icon} {days_str}",
            expanded=False
        ):
            r1, r2, r3, r4 = st.columns(4)
            r1.markdown(
                f"**Status**<br>"
                f"<span style='color:{s_color};font-weight:700;'>{status}</span>",
                unsafe_allow_html=True)
            r2.markdown(
                f"**Expires**<br>"
                f"<span style='color:{days_col};font-weight:700;'>"
                f"{pol.get('expiration_date','—')} ({days_str})</span>",
                unsafe_allow_html=True)
            r3.markdown(f"**Premium**<br><b>${prem:,.2f}</b>", unsafe_allow_html=True)
            bldg = pol.get("building_limit")
            r4.markdown(f"**Bldg Limit**<br><b>${bldg:,.0f}</b>" if bldg else
                        "**Bldg Limit**<br>—", unsafe_allow_html=True)

            st.divider()
            d1, d2, d3 = st.columns(3)
            d1.markdown(f"**Type**<br>{pol.get('policy_type','—')}", unsafe_allow_html=True)
            d2.markdown(f"**Agency**<br>{pol.get('agency','—')}", unsafe_allow_html=True)
            d3.markdown(f"**Properties**<br>{pids}", unsafe_allow_html=True)

            d4, d5, d6 = st.columns(3)
            d4.markdown(f"**Ded AOP**<br>{pol.get('ded_aop','—')}", unsafe_allow_html=True)
            d5.markdown(f"**Ded Water**<br>{pol.get('ded_water','—')}", unsafe_allow_html=True)
            d6.markdown(f"**Habitability**<br>{pol.get('habitability','—')}", unsafe_allow_html=True)

            if pol.get("business_income"):
                st.caption(f"BI: {pol['business_income']}")
            if pol.get("liability"):
                st.caption(f"Liability: {pol['liability']}")
            if pol.get("notes"):
                st.warning(f"📝 {pol['notes'][:120]}")


# ═══════════════════════════════════════════════════════════════════
#  PROPERTIES
# ═══════════════════════════════════════════════════════════════════
def page_properties(data):
    props    = data["properties"]
    policies = data["policies"]

    pol_lookup = {}
    for p in policies:
        if p.get("prop_id") and p["prop_id"] not in pol_lookup:
            pol_lookup[p["prop_id"]] = p

    tot_units = sum(p.get("units") or 0 for p in props)
    gap_count = sum(1 for p in props
                    if p.get("coverage_status") not in ("Active",""))

    st.markdown(f"""
    <div style="font-size:1.5rem;font-weight:800;color:{R['text_d']};margin-bottom:.2rem;">
      🏘️ Properties</div>
    <div style="font-size:.85rem;color:{R['text_m']};margin-bottom:1.2rem;">
      {len(props)} properties · {tot_units} units</div>
    """, unsafe_allow_html=True)

    # Auto-open gaps tab if navigated from dashboard alert
    default_tab = 1 if st.session_state.pop("prop_open_gaps", False) else 0

    tab_all, tab_gaps = st.tabs([
        f"  All ({len(props)})  ",
        f"  ⚠️ Coverage Gaps ({gap_count})  ",
    ])

    def prop_card(prop, pol):
        status   = prop.get("coverage_status","")
        days     = _days_to(pol.get("expiration_date")) if pol else None
        days_col = (R['red'] if (days or 999) <= 60 else
                    R['amber'] if (days or 999) <= 180 else R['green'])
        badge    = coverage_badge(status)

        # Status icon for expander title (HTML not supported in title)
        status_icon = ("✅" if status == "Active" else
                       "⛔" if status == "Uninsured" else
                       "◎"  if status == "Quote" else
                       "⚠️" if "Verify" in status or "External" in status else "❓")

        with st.expander(
            f"{status_icon} {prop['prop_id']} · {prop.get('nickname') or prop['address']} · {prop['city']}"
            f" ({prop.get('units') or 0}u)",
            expanded=False
        ):
            r1, r2, r3 = st.columns(3)
            r1.markdown(f"**Address**<br>{prop['address']}, {prop['city']} {prop.get('zip','')}",
                        unsafe_allow_html=True)
            r2.markdown(f"**Owner**<br>{prop.get('owner','—')}", unsafe_allow_html=True)
            r3.markdown(f"**Coverage**<br>{badge}", unsafe_allow_html=True)

            r4, r5, r6 = st.columns(3)
            r4.markdown(f"**Units:** {prop.get('units') or '—'}")
            sqft = prop.get('sqft')
            r5.markdown(f"**Sq Ft:** {f'{sqft:,}' if sqft else '—'}")
            r6.markdown(f"**Type:** {prop.get('type','—')}")

            if pol:
                st.divider()
                p1, p2, p3 = st.columns(3)
                p1.markdown(f"**Policy #**<br>{pol.get('policy_number','—')}",
                            unsafe_allow_html=True)
                p2.markdown(f"**Carrier**<br>{(pol.get('carrier') or '—')[:30]}",
                            unsafe_allow_html=True)
                p3.markdown(
                    f"**Expires**<br>"
                    f"<span style='color:{days_col};font-weight:700;'>"
                    f"{pol.get('expiration_date','—')}"
                    f"{f' ({days}d)' if days is not None else ''}</span>",
                    unsafe_allow_html=True
                )
                p4, p5 = st.columns(2)
                prem = pol.get('premium') or 0
                bldg = pol.get('building_limit') or 0
                p4.markdown(f"**Premium:** ${prem:,.2f}")
                p5.markdown(f"**Bldg Limit:** ${bldg:,.0f}")

            action = prop.get("action_status","")
            if action and action != "None":
                action_color = ("#dc2626" if action == "Needs Attention" else
                                "#d97706" if action == "In Progress" else
                                "#d97706" if action == "Pending Quote" else
                                "#16a34a")
                st.markdown(f"""
                <div style="display:inline-block;padding:3px 12px;border-radius:20px;
                     background:{action_color}20;border:1px solid {action_color};
                     color:{action_color};font-size:.72rem;font-weight:700;margin:.4rem 0;">
                  🔔 {action}
                </div>""", unsafe_allow_html=True)
            if prop.get("notes"):
                st.info(f"📝 {prop['notes']}")
            if prop.get("mortgagee"):
                st.caption(f"Mortgagee: {prop['mortgagee']}")

    # ── All tab ──
    with tab_all:
        c1, c2, c3 = st.columns([2, 1.2, 1.4])
        with c1:
            srch = st.text_input("s2", placeholder="🔍  Buscar por dirección, ciudad, dueño, ID…",
                                 label_visibility="collapsed", key="pr_srch")
        with c2:
            sf2 = st.selectbox("sf2", ["Todos","Active","Uninsured","Quote","Verify"],
                               label_visibility="collapsed", key="pr_sf")
        with c3:
            so2 = st.selectbox("so2",
                ["Ordenar: Default","Unidades ↓","Ciudad A→Z","Dueño A→Z"],
                label_visibility="collapsed", key="pr_so")

        filt = list(props)
        if srch:
            q = srch.lower()
            filt = [p for p in filt
                    if q in p.get("address","").lower()
                    or q in p.get("city","").lower()
                    or q in (p.get("owner") or "").lower()
                    or q in p.get("prop_id","").lower()
                    or q in (p.get("nickname") or "").lower()]
        if sf2 != "Todos":
            if sf2 == "Verify":
                filt = [p for p in filt if "Verify" in p.get("coverage_status","")]
            else:
                filt = [p for p in filt if p.get("coverage_status") == sf2]

        if "Unidades" in so2:
            filt.sort(key=lambda p: -(p.get("units") or 0))
        elif "Ciudad" in so2:
            filt.sort(key=lambda p: p.get("city",""))
        elif "Dueño" in so2:
            filt.sort(key=lambda p: (p.get("owner") or ""))

        # Quick stats summary bar
        vis_active  = sum(1 for p in filt if p.get("coverage_status") == "Active")
        vis_uninsu  = sum(1 for p in filt if p.get("coverage_status") == "Uninsured")
        vis_other   = len(filt) - vis_active - vis_uninsu
        vis_units   = sum(p.get("units") or 0 for p in filt)
        st.markdown(f"""
        <div style="display:flex;gap:16px;padding:.5rem .8rem;background:{R['white']};
             border:1px solid {R['rose_lt']};border-radius:8px;margin-bottom:.6rem;
             font-size:.75rem;flex-wrap:wrap;">
          <span><b>{len(filt)}</b> propiedades</span>
          <span style="color:#16a34a;">✅ <b>{vis_active}</b> aseguradas</span>
          <span style="color:#dc2626;">⛔ <b>{vis_uninsu}</b> sin seguro</span>
          {"<span style='color:#d97706;'>⚠️ <b>" + str(vis_other) + "</b> otros</span>" if vis_other else ""}
          <span style="margin-left:auto;color:{R['text_m']};">🏠 <b>{vis_units}</b> unidades</span>
        </div>
        """, unsafe_allow_html=True)

        for prop in filt:
            prop_card(prop, pol_lookup.get(prop["prop_id"]))

    # ── Coverage Gaps tab ──
    with tab_gaps:
        gap_props = [p for p in props if p.get("coverage_status") not in ("Active","")]
        uninsu  = sorted([p for p in gap_props if p.get("coverage_status") == "Uninsured"],
                         key=lambda p: -(p.get("units") or 0))
        verify  = [p for p in gap_props if "Verify" in p.get("coverage_status","")]
        ext     = [p for p in gap_props if "External" in p.get("coverage_status","")]
        qt      = [p for p in gap_props if p.get("coverage_status") == "Quote"]

        g1, g2, g3, g4 = st.columns(4)
        for col, n, lbl, num_color in [
            (g1, len(uninsu), "Uninsured", "#dc2626"),
            (g2, sum(p.get("units") or 0 for p in uninsu), "Uninsured Units", "#dc2626"),
            (g3, len(verify) + len(ext), "Need Verify", "#d97706"),
            (g4, len(qt), "Unbound Quote", R['plum']),
        ]:
            col.markdown(f"""
            <div class="kpi-tile">
              <div class="kpi-num" style="color:{num_color};">{n}</div>
              <div class="kpi-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if uninsu:
            st.markdown(f'<div class="sec-hdr">⛔ Uninsured — No Policy On File</div>',
                        unsafe_allow_html=True)
            for prop in uninsu:
                units = prop.get("units") or 0
                pri   = "🔴 HIGH" if units >= 10 else ("🟠 MED" if units >= 4 else "🟡 LOW")
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;padding:.6rem .9rem;
                     background:{R['red_lt']};border-radius:8px;
                     border-left:3px solid {R['red']};margin-bottom:5px;">
                  <div style="font-size:.78rem;font-weight:800;min-width:60px;">{pri}</div>
                  <div style="flex:1;">
                    <div style="font-size:.85rem;font-weight:700;color:{R['text_d']};">
                      {prop['prop_id']} · {prop['address']}</div>
                    <div style="font-size:.72rem;color:{R['text_m']};">
                      {prop['city']} · {units} units · {prop.get('owner','—')}</div>
                  </div>
                  <div style="font-size:.72rem;color:#991B1B;font-weight:700;">No policy</div>
                </div>""", unsafe_allow_html=True)

        if verify or ext:
            st.markdown(f'<div class="sec-hdr">⚠️ Verify / External Owner</div>',
                        unsafe_allow_html=True)
            for prop in verify + ext:
                status = prop.get("coverage_status","")
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;padding:.55rem .9rem;
                     background:{R['amber_lt']};border-radius:8px;
                     border-left:3px solid {R['amber']};margin-bottom:5px;">
                  <div style="flex:1;">
                    <div style="font-size:.85rem;font-weight:700;color:{R['text_d']};">
                      {prop['prop_id']} · {prop['address']}</div>
                    <div style="font-size:.72rem;color:{R['text_m']};">
                      {prop['city']} · {prop.get('units') or 0} units</div>
                  </div>
                  <div style="font-size:.72rem;color:#92400E;font-weight:600;
                       max-width:200px;text-align:right;">{status}</div>
                </div>""", unsafe_allow_html=True)
                if prop.get("notes"):
                    st.caption(f"   📝 {prop['notes']}")

        if qt:
            st.markdown(f'<div class="sec-hdr">◎ Quote — Not Yet Bound</div>',
                        unsafe_allow_html=True)
            for prop in qt:
                pol = pol_lookup.get(prop["prop_id"], {})
                st.markdown(f"""
                <div style="padding:.55rem .9rem;background:{R['amber_lt']};
                     border-radius:8px;border-left:3px solid {R['amber']};margin-bottom:5px;">
                  <div style="font-size:.85rem;font-weight:700;color:{R['text_d']};">
                    {prop['prop_id']} · {prop['address']}</div>
                  <div style="font-size:.72rem;color:{R['text_m']};">
                    {prop['city']} · {pol.get('policy_number','—')} ·
                    {pol.get('carrier','—')}</div>
                </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  AUTO
# ═══════════════════════════════════════════════════════════════════
def page_auto(data):
    autos = data.get("auto_policies", [])
    total_ap = sum(a.get("premium") or 0 for a in autos)

    st.markdown(f"""
    <div style="font-size:1.5rem;font-weight:800;color:{R['text_d']};margin-bottom:.2rem;">
      🚗 Auto Policies</div>
    <div style="font-size:.85rem;color:{R['text_m']};margin-bottom:1rem;">
      {len(autos)} pólizas · ${total_ap:,.2f} prima total</div>
    """, unsafe_allow_html=True)

    # Summary KPIs
    urgent_auto = sum(1 for a in autos if (_days_to(a.get("expiration_date")) or 999) <= 60)
    a1, a2, a3, a4 = st.columns(4)
    for col, num, lbl, color in [
        (a1, len(autos),           "Total Pólizas",  R['text_d']),
        (a2, f"${total_ap:,.0f}",  "Prima Total",    R['rose']),
        (a3, urgent_auto or "—",   "Vencen < 60d",   "#dc2626" if urgent_auto else R['text_m']),
        (a4, len(set(a.get("state","") for a in autos if a.get("state"))),
             "Estados",             R['plum']),
    ]:
        col.markdown(f"""
        <div class="kpi-tile">
          <div class="kpi-num" style="color:{color};font-size:1.5rem;">{num}</div>
          <div class="kpi-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    for auto in autos:
        days     = _days_to(auto.get("expiration_date"))
        days_str = f"{days}d" if days is not None else "—"
        days_col = (R['red'] if (days or 999) <= 60 else
                    R['amber'] if (days or 999) <= 180 else R['green'])
        days_icon = "⏰" if (days or 999) <= 60 else ("⚡" if (days or 999) <= 180 else "✅")
        prem    = auto.get("premium") or 0
        vehicle = (auto.get("vehicles") or auto.get("vehicle") or "")
        veh_short = vehicle[:25] if vehicle else auto.get("state","")

        with st.expander(
            f"🚗  {auto.get('insured','')[:24]}  ·  {veh_short}  ·  "
            f"${prem:,.0f}  ·  {days_icon} {days_str}",
            expanded=False
        ):
            r1, r2, r3 = st.columns(3)
            r1.markdown(f"**Insured**<br>{auto.get('insured','—')}", unsafe_allow_html=True)
            r2.markdown(f"**Carrier**<br>{auto.get('carrier','—')}", unsafe_allow_html=True)
            r3.markdown(f"**Agency**<br>{auto.get('agency','—')}", unsafe_allow_html=True)

            r4, r5, r6 = st.columns(3)
            r4.markdown(f"**Effective:** {auto.get('effective_date','—')}")
            r5.markdown(
                f"**Expires:** <span style='color:{days_col};font-weight:700;'>"
                f"{auto.get('expiration_date','—')} ({days_str})</span>",
                unsafe_allow_html=True)
            r6.markdown(f"**Premium:** ${prem:,.2f}")

            st.divider()
            v1, v2 = st.columns([1.5, 1])
            v1.markdown(f"**Vehicles**<br>{auto.get('vehicles','—')}", unsafe_allow_html=True)
            v2.markdown(f"**BI/PD**<br>{auto.get('bipd','—')}", unsafe_allow_html=True)

            v3, v4, v5 = st.columns(3)
            v3.markdown(f"**Comp Ded:** {auto.get('comp_ded','—')}")
            v4.markdown(f"**Coll Ded:** {auto.get('coll_ded','—')}")
            v5.markdown(f"**UM/UIM:** {auto.get('um_uim','—')}")

            if auto.get("vins"):
                st.caption(f"VINs: {auto['vins']}")
            if auto.get("pip_medpay"):
                st.caption(f"PIP/MedPay: {auto['pip_medpay']}")
            if auto.get("notes"):
                st.info(f"📝 {auto['notes']}")


# ═══════════════════════════════════════════════════════════════════
#  REPORTS
# ═══════════════════════════════════════════════════════════════════
def page_reports(data):
    props    = data["properties"]
    policies = data["policies"]
    autos    = data.get("auto_policies", [])

    active_n = sum(1 for p in props if p.get("coverage_status") == "Active")
    uninsu_n = sum(1 for p in props if p.get("coverage_status") == "Uninsured")
    verify_n = sum(1 for p in props if "Verify" in p.get("coverage_status",""))
    prem_tot = total_premium(policies)
    auto_prem= sum(a.get("premium") or 0 for a in autos)
    tot_units= sum(p.get("units") or 0 for p in props)

    st.markdown(f"""
    <div style="font-size:1.5rem;font-weight:800;color:{R['text_d']};margin-bottom:.2rem;">
      📄 Reports</div>
    <div style="font-size:.85rem;color:{R['text_m']};margin-bottom:1.2rem;">
      Executive summaries and data exports</div>
    """, unsafe_allow_html=True)

    today_str = _today().strftime("%B %d, %Y")
    report = f"""INSURETRACK — PORTFOLIO EXECUTIVE SUMMARY
{data.get('portfolio_name','CYS Caloyeras')}
Generated: {today_str}
{'='*60}

PORTFOLIO OVERVIEW
  Total Properties:     {len(props)}
  Total Units:          {tot_units}
  Annual Premium:       ${prem_tot:,.2f}  (property)
  Auto Premium:         ${auto_prem:,.2f}
  TOTAL PREMIUM:        ${prem_tot + auto_prem:,.2f}

COVERAGE STATUS
  Active (Insured):     {active_n}
  Quote (Unbound):      {sum(1 for p in props if p.get('coverage_status')=='Quote')}
  UNINSURED:            {uninsu_n}  ← ACTION REQUIRED
  Need Verification:    {verify_n}

UNINSURED PROPERTIES (sorted by unit count)
"""
    for i, prop in enumerate(
        sorted([p for p in props if p.get("coverage_status") == "Uninsured"],
               key=lambda p: -(p.get("units") or 0)), 1
    ):
        report += (f"  {i:2}. {prop['prop_id']} · {prop['address']}, "
                   f"{prop['city']} ({prop.get('units') or 0} units)\n")

    report += "\nRENEWALS NEXT 90 DAYS\n"
    near = sorted(
        [(p, d) for p in unique_policies(policies)
         if (d := _days_to(p.get("expiration_date"))) is not None and 0 <= d <= 90],
        key=lambda x: x[1]
    )
    if near:
        for pol, d in near:
            report += (f"  {d:3}d · {pol['policy_number']} · "
                       f"{(pol.get('carrier') or '')[:28]} · ${pol.get('premium') or 0:,.0f}\n")
    else:
        report += "  No renewals within 90 days.\n"

    report += f"\n{'='*60}\nConfidential — CYS Caloyeras · InsureTrack v5.0\n"

    st.markdown(f'<div class="sec-hdr">Executive Summary</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{R['white']};border:1.5px solid {R['rose_lt']};border-radius:12px;
         padding:1.4rem 1.6rem;font-family:'Courier New',monospace;font-size:.78rem;
         color:{R['text_d']};line-height:1.65;max-height:420px;overflow-y:auto;
         white-space:pre-wrap;">{report}</div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1.8, 3])
    with c1:
        st.download_button(
            "⬇️ Descargar (.txt)",
            data=report,
            file_name=f"insuretrack_summary_{_today().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            key="dl_txt",
        )
    with c2:
        if HAS_FPDF:
            if st.button("📄 Generar PDF", key="gen_pdf"):
                st.session_state["gen_pdf_now"] = True
        else:
            st.caption("PDF: instala `fpdf2`")

    # PDF generation
    if HAS_FPDF and st.session_state.get("gen_pdf_now"):
        st.session_state.pop("gen_pdf_now", None)
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)

            # Header
            pdf.set_fill_color(74, 25, 66)   # plum
            pdf.rect(0, 0, 210, 28, "F")
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(255, 255, 255)
            pdf.set_xy(10, 7)
            pdf.cell(0, 10, "InsureTrack — Portfolio Summary", ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_xy(10, 19)
            pdf.cell(0, 6, f"{data.get('portfolio_name','CYS Caloyeras')}  ·  {today_str}", ln=True)

            # KPI boxes
            pdf.set_y(35)
            kpi_items = [
                ("Total Properties", str(len(props))),
                ("Insured Active", str(active_n)),
                ("Uninsured", str(uninsu_n)),
                ("Annual Premium", f"${prem_tot:,.0f}"),
                ("Total Units", str(tot_units)),
                ("Auto Premium", f"${auto_prem:,.0f}"),
            ]
            box_w, box_h, gap, cols_n = 55, 20, 5, 3
            start_x = 15
            for i, (lbl, val) in enumerate(kpi_items):
                row = i // cols_n
                col = i % cols_n
                x = start_x + col * (box_w + gap)
                y = 35 + row * (box_h + gap)
                pdf.set_fill_color(253, 246, 240)
                pdf.set_draw_color(242, 196, 206)
                pdf.rect(x, y, box_w, box_h, "FD")
                pdf.set_font("Helvetica", "B", 14)
                pdf.set_text_color(74, 25, 66)
                pdf.set_xy(x + 2, y + 2)
                pdf.cell(box_w - 4, 9, val, align="C")
                pdf.set_font("Helvetica", "", 7)
                pdf.set_text_color(157, 128, 144)
                pdf.set_xy(x + 2, y + 12)
                pdf.cell(box_w - 4, 5, lbl.upper(), align="C")

            y_after_kpis = 35 + 2 * (box_h + gap) + 8

            def section_header(pdf_obj, title, y_pos):
                pdf_obj.set_y(y_pos)
                pdf_obj.set_fill_color(242, 196, 206)
                pdf_obj.rect(10, y_pos, 190, 7, "F")
                pdf_obj.set_font("Helvetica", "B", 9)
                pdf_obj.set_text_color(74, 25, 66)
                pdf_obj.set_xy(12, y_pos + 1)
                pdf_obj.cell(0, 5, title.upper())
                return y_pos + 10

            y = section_header(pdf, "Uninsured Properties", y_after_kpis)
            uninsured_props = sorted([p for p in props if p.get("coverage_status")=="Uninsured"],
                                     key=lambda p: -(p.get("units") or 0))
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(59, 7, 100)
            for p in uninsured_props[:15]:
                pdf.set_x(12)
                pdf.set_y(y)
                txt = f"• {p['prop_id']}  {p.get('address','')}, {p.get('city','')}  ({p.get('units',0)} units)"
                pdf.cell(0, 5, txt[:90], ln=True)
                y += 5
                if y > 270:
                    pdf.add_page(); y = 15

            y = section_header(pdf, "Renewals Next 90 Days", y + 4)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(59, 7, 100)
            if near:
                for pol, d in near:
                    pdf.set_x(12)
                    pdf.set_y(y)
                    carrier_s = (pol.get("carrier") or "")[:25]
                    txt = f"• {d:3}d  {pol['policy_number']}  {carrier_s}  ${pol.get('premium',0):,.0f}"
                    pdf.cell(0, 5, txt[:90], ln=True)
                    y += 5
                    if y > 270:
                        pdf.add_page(); y = 15
            else:
                pdf.set_x(12); pdf.set_y(y)
                pdf.cell(0, 5, "No renewals within 90 days.", ln=True)

            # Footer
            pdf.set_y(-15)
            pdf.set_font("Helvetica", "I", 7)
            pdf.set_text_color(157, 128, 144)
            pdf.cell(0, 10, f"Confidential — CYS Caloyeras · InsureTrack v9.0 · {today_str}", align="C")

            pdf_bytes = pdf.output()
            st.download_button(
                "⬇️ Descargar PDF",
                data=bytes(pdf_bytes),
                file_name=f"insuretrack_portfolio_{_today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                key="dl_pdf_btn",
            )
            st.success("✅ PDF generado. Haz clic en el botón de arriba para descargarlo.")
        except Exception as ex:
            st.error(f"Error generando PDF: {ex}")


# ═══════════════════════════════════════════════════════════════════
#  ADD / EDIT
# ═══════════════════════════════════════════════════════════════════
def page_add(data, save_fn):
    st.markdown(f"""
    <div style="font-size:1.5rem;font-weight:800;color:{R['text_d']};margin-bottom:.2rem;">
      ➕ Add / Edit</div>
    <div style="font-size:.85rem;color:{R['text_m']};margin-bottom:1.2rem;">
      Add new properties, policies, or auto. Edit existing records.</div>
    """, unsafe_allow_html=True)

    st.info(
        "💡 **Heads up:** Changes made here are saved during this session. "
        "On Streamlit Cloud, the server restarts periodically and JSON edits won't persist. "
        "After saving, use the **⬇️ Download portfolio.json** button below to keep your changes."
    )
    col_dl, _ = st.columns([1.5, 3])
    with col_dl:
        st.download_button(
            "⬇️ Download portfolio.json",
            data=json.dumps(data, indent=2, ensure_ascii=False),
            file_name="portfolio.json",
            mime="application/json",
            key="dl_portfolio_top",
        )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏘️ Add Property", "📋 Add Policy", "🚗 Add Auto",
        "✏️ Edit Property", "✏️ Edit Policy"
    ])

    # ── TAB 1: ADD PROPERTY ────────────────────────────────────────
    with tab1:
        st.markdown(f'<div class="sec-hdr">Nueva Propiedad</div>', unsafe_allow_html=True)
        st.caption("Los campos marcados con * son obligatorios.")

        st.markdown(f"""<div style="font-size:.72rem;font-weight:700;color:{R['text_m']};
            text-transform:uppercase;letter-spacing:.07em;margin:.8rem 0 .4rem;">
            📍 Ubicación</div>""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            np_nick  = st.text_input("Nickname / Apodo *",
                placeholder="Ej: Centinela 3632", key="np_nick",
                help="Nombre corto para identificar la propiedad en el sistema")
            np_addr  = st.text_input("Dirección completa *",
                placeholder="Ej: 3632 Centinela Ave", key="np_addr")
            np_city  = st.text_input("Ciudad *",
                placeholder="Ej: Los Angeles", key="np_city")
        with c2:
            np_state = st.text_input("Estado", value="CA", key="np_state")
            np_zip   = st.text_input("ZIP Code", placeholder="Ej: 90066", key="np_zip")
            np_owner = st.text_input("Dueño / LLC",
                placeholder="Ej: John Caloyeras", key="np_owner")

        st.markdown(f"""<div style="font-size:.72rem;font-weight:700;color:{R['text_m']};
            text-transform:uppercase;letter-spacing:.07em;margin:.8rem 0 .4rem;">
            🏗️ Detalles de la propiedad</div>""", unsafe_allow_html=True)
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            np_type  = st.selectbox("Tipo de propiedad",
                ["Residential", "Commercial", "Mixed Use", "Vacant Land"], key="np_type")
        with d2:
            np_units = st.number_input("Unidades", min_value=0, value=1, step=1, key="np_units",
                help="Número de unidades rentables")
        with d3:
            np_sqft  = st.number_input("Sq Ft", min_value=0, value=0, step=100, key="np_sqft")
        with d4:
            np_yr    = st.number_input("Año de construcción",
                min_value=1800, max_value=2030, value=2000, step=1, key="np_yr")

        st.markdown(f"""<div style="font-size:.72rem;font-weight:700;color:{R['text_m']};
            text-transform:uppercase;letter-spacing:.07em;margin:.8rem 0 .4rem;">
            🛡️ Estado de seguro</div>""", unsafe_allow_html=True)
        s1, s2, s3 = st.columns(3)
        with s1:
            np_cov   = st.selectbox("Cobertura actual",
                ["Uninsured","Active","Quote","Verify — Policy on file","External Owner — Verify"],
                key="np_cov",
                help="Estado actual del seguro de esta propiedad")
        with s2:
            np_action = st.selectbox("Acción pendiente",
                ["None","Needs Attention","In Progress","Pending Quote","Resolved"],
                key="np_action",
                help="¿Qué hay que hacer con esta propiedad?")
        with s3:
            np_mort  = st.text_input("Mortgagee / Hipotecante", key="np_mort",
                placeholder="Banco o institución financiera")
        np_notes = st.text_area("Notas adicionales", key="np_notes", height=70,
            placeholder="Ej: Nueva construcción, pendiente de inspección...")

        if st.button("➕ Add Property", key="btn_add_prop", type="primary"):
            if not np_nick or not np_addr or not np_city:
                st.error("Nickname, Address, and City are required.")
            else:
                # Auto-generate next prop ID
                existing_ids = [p["prop_id"] for p in data["properties"]]
                nums = [int(i[1:]) for i in existing_ids if i.startswith("P") and i[1:].isdigit()]
                next_id = f"P{(max(nums)+1):03d}" if nums else "P001"
                new_prop = {
                    "prop_id": next_id,
                    "nickname": np_nick,
                    "address": np_addr,
                    "city": np_city,
                    "state": np_state,
                    "zip": np_zip,
                    "type": np_type,
                    "year_built": int(np_yr) if np_yr else None,
                    "units": int(np_units),
                    "sqft": int(np_sqft) if np_sqft else None,
                    "owner": np_owner,
                    "mortgagee": np_mort,
                    "agent": "",
                    "notes": np_notes,
                    "coverage_status": np_cov,
                    "action_status": np_action if np_action != "None" else "",
                }
                data["properties"].append(new_prop)
                save_fn(data)
                st.success(f"✅ Property {next_id} — {np_nick} added! ({len(data['properties'])} total)")
                st.cache_data.clear()

    # ── TAB 2: ADD POLICY ─────────────────────────────────────────
    with tab2:
        st.markdown(f'<div class="sec-hdr">New Policy</div>', unsafe_allow_html=True)
        prop_opts = {f"{p['prop_id']} — {p['nickname']}": p["prop_id"]
                     for p in data["properties"]}
        c1, c2 = st.columns(2)
        with c1:
            pol_prop    = st.selectbox("Property *", list(prop_opts.keys()), key="pol_prop")
            pol_carrier = st.text_input("Carrier *", key="pol_carrier")
            pol_agency  = st.text_input("Agency / Broker", key="pol_agency")
            pol_num     = st.text_input("Policy Number *", key="pol_num")
            pol_type    = st.selectbox("Policy Type",
                ["Landlord / Dwelling Fire","Commercial Package","BOP",
                 "General Liability","Umbrella","Other"], key="pol_type")
        with c2:
            pol_eff     = st.date_input("Effective Date", key="pol_eff")
            pol_exp     = st.date_input("Expiration Date", key="pol_exp")
            pol_prem    = st.number_input("Annual Premium ($)", min_value=0.0, step=100.0, key="pol_prem")
            pol_bldg    = st.number_input("Building Limit ($)", min_value=0.0, step=1000.0, key="pol_bldg")
            pol_liab    = st.number_input("Liability Limit ($)", min_value=0.0, step=1000.0, key="pol_liab")
            pol_status  = st.selectbox("Status", ["Active","Quote","Expired","Cancelled"], key="pol_status")
        pol_notes = st.text_area("Notes", key="pol_notes", height=70)

        if st.button("➕ Add Policy", key="btn_add_pol", type="primary"):
            if not pol_carrier or not pol_num:
                st.error("Carrier and Policy Number are required.")
            else:
                new_pol = {
                    "prop_id":        prop_opts[pol_prop],
                    "policy_number":  pol_num,
                    "status":         pol_status,
                    "carrier":        pol_carrier,
                    "agency":         pol_agency,
                    "policy_type":    pol_type,
                    "effective_date": str(pol_eff),
                    "expiration_date":str(pol_exp),
                    "premium":        float(pol_prem),
                    "building_limit": float(pol_bldg),
                    "business_income":0,
                    "liability":      float(pol_liab),
                    "ded_aop":        "",
                    "ded_water":      "",
                    "ded_sewer":      "",
                    "inspection":     "",
                    "habitability":   "",
                    "pdf_link":       "",
                    "notes":          pol_notes,
                }
                data["policies"].append(new_pol)
                # Also update property coverage_status to Active if status is Active
                if pol_status == "Active":
                    for p in data["properties"]:
                        if p["prop_id"] == prop_opts[pol_prop]:
                            p["coverage_status"] = "Active"
                elif pol_status == "Quote":
                    for p in data["properties"]:
                        if p["prop_id"] == prop_opts[pol_prop] and p["coverage_status"] == "Uninsured":
                            p["coverage_status"] = "Quote"
                save_fn(data)
                st.success(f"✅ Policy {pol_num} added for {prop_opts[pol_prop]}!")
                st.cache_data.clear()

    # ── TAB 3: ADD AUTO ────────────────────────────────────────────
    with tab3:
        st.markdown(f'<div class="sec-hdr">New Auto Policy</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            au_carrier = st.text_input("Carrier *", key="au_carrier")
            au_num     = st.text_input("Policy Number *", key="au_num")
            au_driver  = st.text_input("Named Insured / Driver", key="au_driver")
            au_vehicle = st.text_input("Vehicle (Year Make Model)", key="au_vehicle")
        with c2:
            au_eff   = st.date_input("Effective Date", key="au_eff")
            au_exp   = st.date_input("Expiration Date", key="au_exp")
            au_prem  = st.number_input("Annual Premium ($)", min_value=0.0, step=50.0, key="au_prem")
            au_liab  = st.text_input("Liability Limits", placeholder="e.g. 100/300/100", key="au_liab")
        au_notes = st.text_area("Notes", key="au_notes", height=70)

        if st.button("➕ Add Auto Policy", key="btn_add_auto", type="primary"):
            if not au_carrier or not au_num:
                st.error("Carrier and Policy Number are required.")
            else:
                new_auto = {
                    "policy_number":  au_num,
                    "carrier":        au_carrier,
                    "named_insured":  au_driver,
                    "vehicle":        au_vehicle,
                    "effective_date": str(au_eff),
                    "expiration_date":str(au_exp),
                    "premium":        float(au_prem),
                    "liability":      au_liab,
                    "notes":          au_notes,
                }
                if "auto_policies" not in data:
                    data["auto_policies"] = []
                data["auto_policies"].append(new_auto)
                save_fn(data)
                st.success(f"✅ Auto policy {au_num} added!")
                st.cache_data.clear()

    # ── TAB 4: EDIT PROPERTY ───────────────────────────────────────
    with tab4:
        st.markdown(f'<div class="sec-hdr">Edit Property</div>', unsafe_allow_html=True)
        prop_list = {f"{p['prop_id']} — {p['nickname']}": i
                     for i, p in enumerate(data["properties"])}
        if not prop_list:
            st.info("No properties found.")
        else:
            sel_prop = st.selectbox("Select property to edit", list(prop_list.keys()), key="ep_sel")
            idx = prop_list[sel_prop]
            p   = data["properties"][idx]

            c1, c2 = st.columns(2)
            with c1:
                ep_nick  = st.text_input("Nickname", value=p.get("nickname",""), key="ep_nick")
                ep_addr  = st.text_input("Address",  value=p.get("address",""),  key="ep_addr")
                ep_city  = st.text_input("City",     value=p.get("city",""),     key="ep_city")
                ep_state = st.text_input("State",    value=p.get("state",""),    key="ep_state")
                ep_zip   = st.text_input("ZIP",      value=p.get("zip",""),      key="ep_zip")
            with c2:
                type_opts = ["Residential","Commercial","Mixed Use","Vacant Land"]
                ep_type  = st.selectbox("Type", type_opts,
                    index=type_opts.index(p.get("type","Residential")) if p.get("type") in type_opts else 0,
                    key="ep_type")
                ep_units = st.number_input("Units", min_value=0, value=int(p.get("units") or 0), key="ep_units")
                ep_sqft  = st.number_input("Sq Ft", min_value=0, value=int(p.get("sqft") or 0), key="ep_sqft")
                ep_yr    = st.number_input("Year Built", min_value=1800, max_value=2030,
                    value=int(p.get("year_built") or 2000), key="ep_yr")
                ep_owner = st.text_input("Owner / LLC", value=p.get("owner",""), key="ep_owner")
                cov_opts = ["Active","Uninsured","Quote","Verify — Policy on file",
                            "External Owner — Verify","Verify — Policy NN1901886 on file"]
                cur_cov  = p.get("coverage_status","Uninsured")
                if cur_cov not in cov_opts:
                    cov_opts.append(cur_cov)
                ep_cov   = st.selectbox("Coverage Status", cov_opts,
                    index=cov_opts.index(cur_cov), key="ep_cov")
                action_opts = ["None","Needs Attention","In Progress","Pending Quote","Resolved"]
                cur_act  = p.get("action_status","") or "None"
                if cur_act not in action_opts: cur_act = "None"
                ep_action = st.selectbox("Action Status", action_opts,
                    index=action_opts.index(cur_act), key="ep_action")
            ep_mort  = st.text_input("Mortgagee", value=p.get("mortgagee",""), key="ep_mort")
            ep_notes = st.text_area("Notes", value=p.get("notes",""), key="ep_notes", height=70)

            col_sv, col_del, _ = st.columns([1, 1, 4])
            with col_sv:
                if st.button("💾 Save Changes", key="ep_save", type="primary"):
                    data["properties"][idx].update({
                        "nickname":        ep_nick,
                        "address":         ep_addr,
                        "city":            ep_city,
                        "state":           ep_state,
                        "zip":             ep_zip,
                        "type":            ep_type,
                        "units":           int(ep_units),
                        "sqft":            int(ep_sqft) if ep_sqft else None,
                        "year_built":      int(ep_yr) if ep_yr else None,
                        "owner":           ep_owner,
                        "mortgagee":       ep_mort,
                        "notes":           ep_notes,
                        "coverage_status": ep_cov,
                        "action_status":   ep_action if ep_action != "None" else "",
                    })
                    save_fn(data)
                    st.success(f"✅ {ep_nick} updated!")
                    st.cache_data.clear()
            with col_del:
                if st.button("🗑️ Delete", key="ep_del"):
                    st.session_state["confirm_del_prop"] = idx

            if st.session_state.get("confirm_del_prop") == idx:
                st.warning(f"⚠️ Delete **{p['prop_id']} — {p.get('nickname','')}**? This cannot be undone.")
                cc1, cc2, _ = st.columns([1,1,4])
                with cc1:
                    if st.button("Yes, delete", key="ep_del_confirm"):
                        data["properties"].pop(idx)
                        save_fn(data)
                        st.session_state.pop("confirm_del_prop", None)
                        st.success("Property deleted.")
                        st.cache_data.clear()
                        st.rerun()
                with cc2:
                    if st.button("Cancel", key="ep_del_cancel"):
                        st.session_state.pop("confirm_del_prop", None)
                        st.rerun()

    # ── TAB 5: EDIT POLICY ─────────────────────────────────────────
    with tab5:
        st.markdown(f'<div class="sec-hdr">Edit Policy</div>', unsafe_allow_html=True)
        pol_list = {f"{pol.get('prop_id','')} · {pol.get('policy_number','')} — {pol.get('carrier','')}": i
                    for i, pol in enumerate(data["policies"])}
        if not pol_list:
            st.info("No policies found.")
        else:
            sel_pol = st.selectbox("Select policy to edit", list(pol_list.keys()), key="epo_sel")
            pidx    = pol_list[sel_pol]
            pol     = data["policies"][pidx]

            c1, c2 = st.columns(2)
            with c1:
                epo_carrier = st.text_input("Carrier", value=pol.get("carrier",""), key="epo_carrier")
                epo_agency  = st.text_input("Agency",  value=pol.get("agency",""),  key="epo_agency")
                epo_num     = st.text_input("Policy Number", value=pol.get("policy_number",""), key="epo_num")
                epo_type    = st.text_input("Policy Type", value=pol.get("policy_type",""), key="epo_type")
            with c2:
                epo_eff  = st.text_input("Effective Date (YYYY-MM-DD)",
                    value=pol.get("effective_date",""), key="epo_eff")
                epo_exp  = st.text_input("Expiration Date (YYYY-MM-DD)",
                    value=pol.get("expiration_date",""), key="epo_exp")
                epo_prem = st.number_input("Annual Premium ($)",
                    min_value=0.0, value=float(pol.get("premium") or 0), step=100.0, key="epo_prem")
                stat_opts = ["Active","Quote","Expired","Cancelled"]
                cur_stat  = pol.get("status","Active")
                epo_stat  = st.selectbox("Status", stat_opts,
                    index=stat_opts.index(cur_stat) if cur_stat in stat_opts else 0, key="epo_stat")
            epo_notes = st.text_area("Notes", value=pol.get("notes",""), key="epo_notes", height=70)

            col_sv2, col_del2, _ = st.columns([1, 1, 4])
            with col_sv2:
                if st.button("💾 Save Changes", key="epo_save", type="primary"):
                    data["policies"][pidx].update({
                        "carrier":        epo_carrier,
                        "agency":         epo_agency,
                        "policy_number":  epo_num,
                        "policy_type":    epo_type,
                        "effective_date": epo_eff,
                        "expiration_date":epo_exp,
                        "premium":        float(epo_prem),
                        "status":         epo_stat,
                        "notes":          epo_notes,
                    })
                    save_fn(data)
                    st.success(f"✅ Policy {epo_num} updated!")
                    st.cache_data.clear()
            with col_del2:
                if st.button("🗑️ Delete", key="epo_del"):
                    st.session_state["confirm_del_pol"] = pidx

            if st.session_state.get("confirm_del_pol") == pidx:
                st.warning(f"⚠️ Delete policy **{pol.get('policy_number','')}**? This cannot be undone.")
                cc3, cc4, _ = st.columns([1,1,4])
                with cc3:
                    if st.button("Yes, delete", key="epo_del_confirm"):
                        data["policies"].pop(pidx)
                        save_fn(data)
                        st.session_state.pop("confirm_del_pol", None)
                        st.success("Policy deleted.")
                        st.cache_data.clear()
                        st.rerun()
                with cc4:
                    if st.button("Cancel", key="epo_del_cancel"):
                        st.session_state.pop("confirm_del_pol", None)
                        st.rerun()


# ═══════════════════════════════════════════════════════════════════
#  MAP
# ═══════════════════════════════════════════════════════════════════
def page_map(data):
    props = data["properties"]

    st.markdown(f"""
    <div class="page-hdr">🗺️ Mapa de Propiedades</div>
    <div class="page-sub">Distribución geográfica del portafolio · {len(props)} propiedades</div>
    """, unsafe_allow_html=True)

    # Filter controls
    fc1, fc2, fc3 = st.columns([2, 1.5, 1.5])
    with fc1:
        srch = st.text_input("Buscar ciudad o propiedad", placeholder="ej. Seattle, Tacoma…",
                             key="map_srch", label_visibility="collapsed")
    with fc2:
        status_opts = ["Todos"] + sorted(set(p.get("coverage_status","") for p in props if p.get("coverage_status","")))
        flt_status  = st.selectbox("Estado", status_opts, key="map_status", label_visibility="collapsed")
    with fc3:
        owner_opts = ["Todos los dueños"] + sorted(set(p.get("owner","") for p in props if p.get("owner","")))
        flt_owner  = st.selectbox("Dueño", owner_opts, key="map_owner", label_visibility="collapsed")

    filtered = [p for p in props if
        (not srch or srch.lower() in (p.get("city","") or "").lower() or
                     srch.lower() in (p.get("nickname","") or "").lower() or
                     srch.lower() in p.get("prop_id","").lower()) and
        (flt_status == "Todos" or p.get("coverage_status","") == flt_status) and
        (flt_owner == "Todos los dueños" or p.get("owner","") == flt_owner)
    ]

    if not filtered:
        st.info("No hay propiedades que coincidan con el filtro.")
        return

    # Build map data
    lats, lons, texts, colors, sizes = [], [], [], [], []
    color_map = {
        "Active":    "#22C55E",
        "Uninsured": "#EF4444",
        "Quote":     "#F59E0B",
    }
    for p in filtered:
        lat, lon = _get_coords(p.get("city",""), p.get("prop_id",""))
        lats.append(lat); lons.append(lon)
        status = p.get("coverage_status","Unknown")
        units  = p.get("units") or 1
        colors.append(color_map.get(status, "#9D8090"))
        sizes.append(max(10, min(30, 8 + units * 1.5)))
        texts.append(
            f"<b>{p['prop_id']}</b><br>"
            f"{p.get('nickname') or p.get('address','')}<br>"
            f"{p.get('city','')}, {p.get('state','')}<br>"
            f"Estado: {status} · {units} unids<br>"
            f"Dueño: {p.get('owner','—')}"
        )

    fig = go.Figure(go.Scattermapbox(
        lat=lats, lon=lons,
        mode="markers",
        marker=dict(size=sizes, color=colors, opacity=0.85),
        text=texts,
        hovertemplate="%{text}<extra></extra>",
    ))
    fig.update_layout(
        mapbox=dict(style="open-street-map", center=dict(lat=47.5, lon=-122.0), zoom=8),
        height=560,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})

    # Legend
    leg_cols = st.columns(4)
    legend = [
        ("#22C55E", "Active"),
        ("#EF4444", "Uninsured"),
        ("#F59E0B", "Quote / Verify"),
        ("#9D8090", "Otro"),
    ]
    for col, (c, lbl) in zip(leg_cols, legend):
        col.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;font-size:.78rem;">'
            f'<div style="width:14px;height:14px;border-radius:50%;background:{c};"></div>'
            f'{lbl}</div>',
            unsafe_allow_html=True
        )

    # Summary table below map
    st.markdown(f'<div class="sec-hdr" style="margin-top:1rem;">Propiedades en mapa ({len(filtered)})</div>',
                unsafe_allow_html=True)
    tbl_cols = st.columns([1, 2, 2, 1.2, 1.2, 1.5])
    hdrs = ["ID", "Nickname", "Ciudad", "Estado", "Unids", "Dueño"]
    for col, h in zip(tbl_cols, hdrs):
        col.markdown(f"<div style='font-size:.68rem;font-weight:700;color:{R['text_m']};text-transform:uppercase;'>{h}</div>",
                     unsafe_allow_html=True)
    for p in filtered[:30]:
        c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 2, 1.2, 1.2, 1.5])
        status = p.get("coverage_status","")
        c1.markdown(f"<div style='font-size:.78rem;font-weight:700;'>{p['prop_id']}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='font-size:.78rem;'>{p.get('nickname') or p.get('address','')[:22]}</div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='font-size:.78rem;'>{p.get('city','')}</div>", unsafe_allow_html=True)
        c4.markdown(coverage_badge(status), unsafe_allow_html=True)
        c5.markdown(f"<div style='font-size:.78rem;'>{p.get('units') or '—'}</div>", unsafe_allow_html=True)
        c6.markdown(f"<div style='font-size:.78rem;color:{R['text_m']};'>{(p.get('owner') or '—')[:18]}</div>", unsafe_allow_html=True)
    if len(filtered) > 30:
        st.caption(f"Mostrando 30 de {len(filtered)} propiedades.")


# ═══════════════════════════════════════════════════════════════════
#  TASKS / ACTION ITEMS
# ═══════════════════════════════════════════════════════════════════
TASKS_PATH = os.path.join(os.path.dirname(__file__), "data", "caloyeras", "tasks.json")

def load_tasks():
    if os.path.exists(TASKS_PATH):
        try:
            with open(TASKS_PATH) as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_tasks(tasks):
    os.makedirs(os.path.dirname(TASKS_PATH), exist_ok=True)
    with open(TASKS_PATH, "w") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

def page_tasks(data, save_fn):
    props    = data["properties"]
    policies = data["policies"]

    st.markdown(f"""
    <div class="page-hdr">✅ Lista de Tareas</div>
    <div class="page-sub">Action items automáticos + tareas manuales del portafolio</div>
    """, unsafe_allow_html=True)

    # ── Auto-generated action items ────────────────────────────────
    auto_items = []

    # Uninsured properties → high priority
    for p in sorted([x for x in props if x.get("coverage_status") == "Uninsured"],
                    key=lambda x: -(x.get("units") or 0)):
        units = p.get("units") or 0
        pri   = "Alta" if units >= 10 else ("Media" if units >= 4 else "Baja")
        auto_items.append({
            "type": "auto",
            "priority": pri,
            "icon": "🔴" if pri == "Alta" else ("🟠" if pri == "Media" else "🟡"),
            "title": f"Obtener seguro para {p['prop_id']} — {p.get('nickname') or p.get('address','')}",
            "detail": f"{p.get('city','')}, {p.get('state','WA')} · {units} unidades · Dueño: {p.get('owner','—')}",
            "category": "Cobertura faltante",
        })

    # Expiring policies ≤ 60 days
    for pol in sorted(unique_policies(policies), key=lambda x: x.get("expiration_date","9999")):
        d = _days_to(pol.get("expiration_date"))
        if d is not None and 0 <= d <= 60:
            carrier = (pol.get("carrier") or "").split("/")[0].strip()[:24]
            auto_items.append({
                "type": "auto",
                "priority": "Alta" if d <= 30 else "Media",
                "icon": "⏰" if d <= 30 else "📅",
                "title": f"Renovar póliza {pol['policy_number']} — {carrier}",
                "detail": f"Vence en {d} días ({pol.get('expiration_date','')})"
                          f" · ${pol.get('premium',0):,.0f}/año",
                "category": "Renovación urgente",
            })

    # Properties with action_status set
    for p in props:
        act = p.get("action_status","").strip()
        if act and act.lower() not in ("", "none", "n/a", "ok", "complete"):
            auto_items.append({
                "type": "auto",
                "priority": "Media",
                "icon": "📌",
                "title": f"{p['prop_id']}: {act}",
                "detail": f"{p.get('nickname') or p.get('address','')} · {p.get('city','')}",
                "category": "Acción pendiente",
            })

    # ── Manual tasks ────────────────────────────────────────────────
    manual_tasks = load_tasks()

    # Stats
    done_n = sum(1 for t in manual_tasks if t.get("done"))
    total_n = len(auto_items) + len(manual_tasks)
    open_n  = len(auto_items) + (len(manual_tasks) - done_n)

    k1, k2, k3 = st.columns(3)
    for col, (num, lbl, color) in zip([k1, k2, k3], [
        (str(total_n), "Total ítems",  R['plum']),
        (str(open_n),  "Pendientes",   R['rose']),
        (str(done_n),  "Completados",  "#16a34a"),
    ]):
        col.markdown(f"""
        <div style="background:{R['white']};border:1.5px solid {R['rose_lt']};
             border-left:4px solid {color};border-radius:10px;padding:.7rem 1rem;text-align:center;">
          <div style="font-size:1.6rem;font-weight:800;color:{color};">{num}</div>
          <div style="font-size:.65rem;font-weight:700;text-transform:uppercase;
               color:{R['text_m']};letter-spacing:.06em;">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

    tab_auto, tab_manual = st.tabs(["🤖 Automáticos", "📝 Manuales"])

    with tab_auto:
        if not auto_items:
            st.markdown(f"""
            <div style="background:{R['green_lt']};border:1.5px solid #86efac;
                 border-radius:12px;padding:1.2rem 1.5rem;margin-top:.5rem;">
              <span style="font-size:.9rem;color:#14532d;">
                🎉 <b>¡Sin items pendientes!</b> El portafolio está al día.</span>
            </div>""", unsafe_allow_html=True)
        else:
            # Group by category
            by_cat = defaultdict(list)
            for item in auto_items:
                by_cat[item["category"]].append(item)
            for cat, items in by_cat.items():
                st.markdown(f'<div class="sec-hdr">{cat} ({len(items)})</div>', unsafe_allow_html=True)
                for item in items:
                    pri_color = R['red'] if item['priority']=="Alta" else (R['amber'] if item['priority']=="Media" else "#ca8a04")
                    pri_bg    = R['red_lt'] if item['priority']=="Alta" else (R['amber_lt'] if item['priority']=="Media" else "#fefce8")
                    st.markdown(f"""
                    <div style="display:flex;align-items:flex-start;gap:10px;
                         padding:.6rem .9rem;background:{pri_bg};
                         border-radius:8px;border-left:3px solid {pri_color};
                         margin-bottom:5px;">
                      <div style="font-size:1.1rem;margin-top:1px;">{item['icon']}</div>
                      <div style="flex:1;">
                        <div style="font-size:.82rem;font-weight:700;color:{R['text_d']};">
                          {item['title']}</div>
                        <div style="font-size:.72rem;color:{R['text_m']};margin-top:2px;">
                          {item['detail']}</div>
                      </div>
                      <div style="font-size:.65rem;font-weight:700;color:{pri_color};
                           text-transform:uppercase;white-space:nowrap;padding-top:3px;">
                        {item['priority']}</div>
                    </div>""", unsafe_allow_html=True)

    with tab_manual:
        # Add new task
        st.markdown(f'<div class="sec-hdr">➕ Nueva Tarea</div>', unsafe_allow_html=True)
        nc1, nc2, nc3 = st.columns([3, 1.2, 1])
        with nc1:
            new_title = st.text_input("Descripción de la tarea", key="task_title",
                                      label_visibility="collapsed", placeholder="ej. Llamar a broker para cotización...")
        with nc2:
            new_pri = st.selectbox("Prioridad", ["Alta","Media","Baja"], key="task_pri",
                                   label_visibility="collapsed")
        with nc3:
            if st.button("➕ Agregar", key="task_add", use_container_width=True):
                if new_title.strip():
                    manual_tasks.append({
                        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                        "title": new_title.strip(),
                        "priority": new_pri,
                        "done": False,
                        "created": datetime.now().strftime("%Y-%m-%d"),
                    })
                    save_tasks(manual_tasks)
                    st.rerun()

        if not manual_tasks:
            st.info("No hay tareas manuales. Agrega una arriba.")
        else:
            # Pending first, then done
            st.markdown(f'<div class="sec-hdr">Pendientes ({len(manual_tasks)-done_n})</div>',
                        unsafe_allow_html=True)
            changed = False
            for i, task in enumerate(manual_tasks):
                if task.get("done"):
                    continue
                pri_color = R['red'] if task['priority']=="Alta" else (R['amber'] if task['priority']=="Media" else "#ca8a04")
                t1, t2, t3 = st.columns([0.3, 5, 1])
                with t1:
                    if st.checkbox("", key=f"tck_{task['id']}", value=False):
                        manual_tasks[i]["done"] = True
                        changed = True
                with t2:
                    st.markdown(
                        f"<div style='padding-top:6px;font-size:.83rem;font-weight:600;"
                        f"color:{R['text_d']};'>{task['title']}</div>",
                        unsafe_allow_html=True
                    )
                with t3:
                    st.markdown(
                        f"<div style='padding-top:6px;font-size:.7rem;font-weight:700;"
                        f"color:{pri_color};text-transform:uppercase;'>{task['priority']}</div>",
                        unsafe_allow_html=True
                    )

            if done_n:
                with st.expander(f"✅ Completadas ({done_n})", expanded=False):
                    for i, task in enumerate(manual_tasks):
                        if not task.get("done"):
                            continue
                        d1, d2, d3 = st.columns([0.3, 5, 1])
                        with d1:
                            if st.checkbox("", key=f"tck_done_{task['id']}", value=True):
                                pass
                            else:
                                manual_tasks[i]["done"] = False
                                changed = True
                        with d2:
                            st.markdown(
                                f"<div style='padding-top:6px;font-size:.83rem;"
                                f"color:{R['text_m']};text-decoration:line-through;'>{task['title']}</div>",
                                unsafe_allow_html=True
                            )
                        with d3:
                            if st.button("🗑️", key=f"del_task_{task['id']}", help="Eliminar"):
                                manual_tasks.pop(i)
                                changed = True
                                break

            if changed:
                save_tasks(manual_tasks)
                st.rerun()


# ═══════════════════════════════════════════════════════════════════
#  ANALYTICS
# ═══════════════════════════════════════════════════════════════════
def page_analytics(data):
    props    = data["properties"]
    policies = data["policies"]

    st.markdown(f"""
    <div class="page-hdr">📈 Analítica</div>
    <div class="page-sub">Costo por unidad, distribución por dueño y métricas del portafolio</div>
    """, unsafe_allow_html=True)

    tab_cost, tab_owner = st.tabs(["💰 Costo por Unidad", "👥 Por Dueño / LLC"])

    # Build policy → properties map
    pol_props = defaultdict(list)
    for p in policies:
        if p.get("prop_id"):
            pol_props[p["policy_number"]].append(p["prop_id"])

    # Build prop_id → premium map (split premium across covered props)
    prop_prem = defaultdict(float)
    for pol in unique_policies(policies):
        covered = pol_props.get(pol["policy_number"], [])
        prem    = pol.get("premium") or 0
        if covered:
            split = prem / len(covered)
            for pid in covered:
                prop_prem[pid] += split
        else:
            # No prop linked, skip
            pass

    with tab_cost:
        st.markdown(f'<div class="sec-hdr">Costo por Unidad — Todas las Propiedades Aseguradas</div>',
                    unsafe_allow_html=True)

        rows = []
        for p in props:
            units  = p.get("units") or 0
            prem   = prop_prem.get(p["prop_id"], 0)
            sqft   = p.get("sqft") or 0
            cpu    = prem / units if units > 0 else 0
            cpsf   = prem / sqft  if sqft  > 0 else 0
            rows.append({
                "prop": p,
                "prem": prem,
                "units": units,
                "cpu": cpu,
                "cpsf": cpsf,
                "sqft": sqft,
            })

        # Sort by cpu descending
        rows_sorted = sorted(rows, key=lambda x: -x["cpu"])

        # KPIs
        insured_rows = [r for r in rows_sorted if r["prem"] > 0]
        if insured_rows:
            avg_cpu = sum(r["cpu"] for r in insured_rows) / len(insured_rows)
            max_cpu = max(r["cpu"] for r in insured_rows)
            min_cpu = min(r["cpu"] for r in insured_rows if r["cpu"] > 0)
            k1, k2, k3 = st.columns(3)
            for col, (num, lbl, color) in zip([k1, k2, k3], [
                (f"${avg_cpu:,.0f}", "CPU Promedio",  R['rose']),
                (f"${max_cpu:,.0f}", "CPU Más Alto",  R['red']),
                (f"${min_cpu:,.0f}", "CPU Más Bajo",  R['green']),
            ]):
                col.markdown(f"""
                <div style="background:{R['white']};border:1.5px solid {R['rose_lt']};
                     border-left:4px solid {color};border-radius:10px;
                     padding:.7rem 1rem;text-align:center;">
                  <div style="font-size:1.6rem;font-weight:800;color:{color};">{num}</div>
                  <div style="font-size:.65rem;font-weight:700;text-transform:uppercase;
                       color:{R['text_m']};letter-spacing:.06em;">{lbl}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

            # Bar chart — CPU by property
            top_rows = insured_rows[:20]
            labels = [r["prop"]["prop_id"] for r in top_rows]
            cpus   = [r["cpu"] for r in top_rows]
            bar_colors = [R['red'] if c > avg_cpu*1.5 else (R['amber'] if c > avg_cpu else R['green'])
                          for c in cpus]
            fig = go.Figure(go.Bar(
                x=labels, y=cpus,
                marker_color=bar_colors,
                text=[f"${c:,.0f}" for c in cpus],
                textposition="outside",
                textfont_size=9,
                hovertemplate="<b>%{x}</b><br>$%{y:,.0f}/unidad<extra></extra>",
            ))
            fig.add_hline(y=avg_cpu, line_dash="dot", line_color=R['plum'],
                          annotation_text=f"Promedio ${avg_cpu:,.0f}",
                          annotation_font_size=10)
            fig.update_layout(
                height=300, margin=dict(l=0, r=0, t=20, b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, tickfont_size=9),
                yaxis=dict(showgrid=True, gridcolor="#F0E8EC",
                           tickformat="$,.0f", tickfont_size=9),
                title=dict(text="Costo por Unidad — Top 20 (ordenado mayor → menor)",
                           font_size=11, x=0),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Table
        hcols = st.columns([1, 2.2, 1.5, 0.8, 1.2, 1.2, 1.4])
        for col, h in zip(hcols, ["ID","Propiedad","Ciudad","Unids","Prima/año","$/unid","$/sqft"]):
            col.markdown(f"<div style='font-size:.67rem;font-weight:700;color:{R['text_m']};text-transform:uppercase;'>{h}</div>",
                         unsafe_allow_html=True)
        for r in rows_sorted:
            c1,c2,c3,c4,c5,c6,c7 = st.columns([1, 2.2, 1.5, 0.8, 1.2, 1.2, 1.4])
            p = r["prop"]
            cpu_color = R['red'] if (r["prem"] > 0 and r["cpu"] > 0 and
                                     r["cpu"] > sum(x["cpu"] for x in insured_rows if x["cpu"]>0)/max(1,len(insured_rows))*1.5) else R['text_d']
            c1.markdown(f"<div style='font-size:.78rem;font-weight:700;'>{p['prop_id']}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div style='font-size:.78rem;'>{p.get('nickname') or p.get('address','')[:22]}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div style='font-size:.78rem;'>{p.get('city','')}</div>", unsafe_allow_html=True)
            c4.markdown(f"<div style='font-size:.78rem;text-align:center;'>{r['units'] or '—'}</div>", unsafe_allow_html=True)
            c5.markdown(f"<div style='font-size:.78rem;'>${r['prem']:,.0f}" if r['prem'] else "<div style='font-size:.78rem;color:#aaa;'>Sin seguro</div>", unsafe_allow_html=True)
            c6.markdown(f"<div style='font-size:.78rem;font-weight:700;color:{cpu_color};'>${r['cpu']:,.0f}" if r['cpu'] else "<div style='font-size:.78rem;color:#aaa;'>—</div>", unsafe_allow_html=True)
            c7.markdown(f"<div style='font-size:.78rem;'>${r['cpsf']:,.2f}" if r['cpsf'] else "<div style='font-size:.78rem;color:#aaa;'>—</div>", unsafe_allow_html=True)

    with tab_owner:
        st.markdown(f'<div class="sec-hdr">Resumen por Dueño / LLC</div>', unsafe_allow_html=True)

        # Group props by owner
        by_owner = defaultdict(list)
        for p in props:
            owner = p.get("owner") or "Sin asignar"
            by_owner[owner].append(p)

        # Sort by total units descending
        owner_summaries = []
        for owner, owned_props in by_owner.items():
            total_units  = sum(p.get("units") or 0 for p in owned_props)
            total_prem   = sum(prop_prem.get(p["prop_id"],0) for p in owned_props)
            active_n     = sum(1 for p in owned_props if p.get("coverage_status")=="Active")
            uninsu_n     = sum(1 for p in owned_props if p.get("coverage_status")=="Uninsured")
            owner_summaries.append({
                "owner": owner,
                "props": owned_props,
                "units": total_units,
                "prem":  total_prem,
                "active": active_n,
                "uninsu": uninsu_n,
                "n": len(owned_props),
            })
        owner_summaries.sort(key=lambda x: -x["units"])

        # Owner bar chart
        if owner_summaries:
            o_labels = [s["owner"][:18] for s in owner_summaries]
            o_units  = [s["units"] for s in owner_summaries]
            o_prems  = [s["prem"] for s in owner_summaries]
            fig_o = go.Figure()
            fig_o.add_trace(go.Bar(name="Unidades", x=o_labels, y=o_units,
                                   marker_color=R['plum'],
                                   hovertemplate="%{x}<br>%{y} unidades<extra></extra>",
                                   yaxis="y"))
            fig_o.add_trace(go.Bar(name="Prima ($)", x=o_labels, y=o_prems,
                                   marker_color=R['rose'],
                                   hovertemplate="%{x}<br>$%{y:,.0f}<extra></extra>",
                                   yaxis="y2",
                                   opacity=0.7))
            fig_o.update_layout(
                height=280, barmode="group",
                margin=dict(l=0, r=50, t=20, b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, tickfont_size=9),
                yaxis=dict(title="Unidades", showgrid=True, gridcolor="#F0E8EC",
                           tickfont_size=9),
                yaxis2=dict(title="Prima ($)", overlaying="y", side="right",
                            tickformat="$,.0f", tickfont_size=9),
                legend=dict(font_size=10, x=0, y=1.05, orientation="h"),
                title=dict(text="Unidades y Prima por Dueño", font_size=11, x=0),
            )
            st.plotly_chart(fig_o, use_container_width=True, config={"displayModeBar": False})

        for s in owner_summaries:
            warn = f"⚠️ {s['uninsu']} sin seguro" if s['uninsu'] else "✅ Completo"
            warn_color = R['amber'] if s['uninsu'] else R['green']
            with st.expander(
                f"👤 {s['owner']}  ·  {s['n']} props  ·  {s['units']} unids  ·  ${s['prem']:,.0f}",
                expanded=False
            ):
                mc1, mc2, mc3, mc4 = st.columns(4)
                mc1.metric("Propiedades", s['n'])
                mc2.metric("Unidades",    s['units'])
                mc3.metric("Prima Total", f"${s['prem']:,.0f}")
                mc4.metric("Estado", warn)
                st.markdown("<hr style='border-color:{};margin:.4rem 0;'>".format(R['rose_lt']),
                            unsafe_allow_html=True)
                for p in sorted(s['props'], key=lambda x: -(x.get("units") or 0)):
                    pc1, pc2, pc3, pc4 = st.columns([1.2, 2.5, 1.5, 1.5])
                    pc1.markdown(f"<div style='font-size:.78rem;font-weight:700;'>{p['prop_id']}</div>", unsafe_allow_html=True)
                    pc2.markdown(f"<div style='font-size:.78rem;'>{p.get('nickname') or p.get('address','')[:22]}, {p.get('city','')}</div>", unsafe_allow_html=True)
                    pc3.markdown(coverage_badge(p.get("coverage_status","")), unsafe_allow_html=True)
                    pc4.markdown(f"<div style='font-size:.78rem;'>${prop_prem.get(p['prop_id'],0):,.0f}</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  CALENDAR
# ═══════════════════════════════════════════════════════════════════
def page_calendar(data):
    policies = data["properties"]
    pols     = data["policies"]

    st.markdown(f"""
    <div class="page-hdr">📅 Calendario de Renovaciones</div>
    <div class="page-sub">Vencimientos de pólizas — próximos 18 meses</div>
    """, unsafe_allow_html=True)

    today   = _today()
    # Month picker
    all_months = []
    for delta in range(18):
        m = today.month + delta
        y = today.year + (m - 1) // 12
        m = ((m - 1) % 12) + 1
        all_months.append((y, m))

    # Build events by month
    events_by_month = defaultdict(list)
    for pol in unique_policies(pols):
        exp = pol.get("expiration_date")
        if not exp:
            continue
        try:
            d = datetime.strptime(exp, "%Y-%m-%d").date()
        except Exception:
            continue
        key = (d.year, d.month)
        if key in [m for m in all_months]:
            days_left = (d - today).days
            carrier   = (pol.get("carrier") or "").split("/")[0].strip()[:20]
            events_by_month[key].append({
                "day": d.day,
                "pol": pol["policy_number"],
                "carrier": carrier,
                "prem": pol.get("premium") or 0,
                "days": days_left,
                "date": exp,
            })

    # Controls
    sc1, sc2 = st.columns([1.5, 3])
    with sc1:
        view_ahead = st.selectbox("Mostrar", ["3 meses","6 meses","12 meses","18 meses"],
                                  index=1, key="cal_view")
    months_to_show = {"3 meses": 3, "6 meses": 6, "12 meses": 12, "18 meses": 18}[view_ahead]

    # Render calendar grid
    MONTH_NAMES = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    months_subset = all_months[:months_to_show]

    # Show 3 months per row
    for row_start in range(0, len(months_subset), 3):
        row_months = months_subset[row_start:row_start+3]
        cols = st.columns(len(row_months))
        for col, (y, m) in zip(cols, row_months):
            events = sorted(events_by_month.get((y, m), []), key=lambda x: x["day"])
            month_total = sum(e["prem"] for e in events)
            urgent      = [e for e in events if e["days"] <= 60]
            hdr_color   = R['red'] if urgent else (R['amber'] if events else R['green'])
            hdr_bg      = R['red_lt'] if urgent else (R['amber_lt'] if events else R['green_lt'])

            with col:
                st.markdown(f"""
                <div style="border:1.5px solid {hdr_color};border-radius:12px;overflow:hidden;
                     margin-bottom:8px;">
                  <div style="background:{hdr_bg};padding:.5rem .8rem;
                       border-bottom:1.5px solid {hdr_color};">
                    <div style="font-weight:800;font-size:.88rem;color:{hdr_color};">
                      {MONTH_NAMES[m-1]} {y}</div>
                    <div style="font-size:.7rem;color:{R['text_m']};">
                      {len(events)} póliza{'s' if len(events)!=1 else ''}{f' · ${month_total:,.0f}' if month_total else ''}</div>
                  </div>
                  <div style="background:{R['white']};padding:.5rem .8rem;">
                """, unsafe_allow_html=True)

                if events:
                    for e in events:
                        dot_color = R['red'] if e['days'] <= 30 else (R['amber'] if e['days'] <= 60 else R['plum'])
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:6px;
                             padding:3px 0;border-bottom:1px solid {R['rose_lt']};">
                          <div style="width:28px;font-size:.72rem;font-weight:800;
                               color:{dot_color};text-align:center;">{e['day']}</div>
                          <div style="flex:1;overflow:hidden;">
                            <div style="font-size:.72rem;font-weight:700;color:{R['text_d']};
                                 white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                              {e['pol']}</div>
                            <div style="font-size:.65rem;color:{R['text_m']};">
                              {e['carrier']} · ${e['prem']:,.0f}</div>
                          </div>
                          <div style="font-size:.65rem;color:{dot_color};font-weight:700;
                               white-space:nowrap;">{e['days']}d</div>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='font-size:.75rem;color:{R['text_m']};padding:.3rem 0;'>Sin vencimientos</div>",
                                unsafe_allow_html=True)

                st.markdown("</div></div>", unsafe_allow_html=True)

    # Summary table
    st.markdown(f'<div class="sec-hdr" style="margin-top:1rem;">Todas las Renovaciones — Próximos {months_to_show} Meses</div>',
                unsafe_allow_html=True)
    all_events = []
    for (y, m) in months_subset:
        for e in events_by_month.get((y, m), []):
            all_events.append(e)
    all_events.sort(key=lambda x: x["date"])

    if all_events:
        sc1, sc2, sc3, sc4 = st.columns([2, 2.5, 1.5, 1.2])
        for col, h in zip([sc1,sc2,sc3,sc4], ["Fecha","Póliza / Carrier","Prima","Días"]):
            col.markdown(f"<div style='font-size:.67rem;font-weight:700;color:{R['text_m']};text-transform:uppercase;'>{h}</div>",
                         unsafe_allow_html=True)
        for e in all_events:
            c1,c2,c3,c4 = st.columns([2, 2.5, 1.5, 1.2])
            d_color = R['red'] if e['days']<=30 else (R['amber'] if e['days']<=60 else R['text_d'])
            c1.markdown(f"<div style='font-size:.78rem;color:{d_color};font-weight:600;'>{e['date']}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div style='font-size:.78rem;'>{e['pol']} · {e['carrier']}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div style='font-size:.78rem;'>${e['prem']:,.0f}</div>", unsafe_allow_html=True)
            c4.markdown(f"<div style='font-size:.78rem;font-weight:700;color:{d_color};'>{e['days']}d</div>", unsafe_allow_html=True)
    else:
        st.info(f"Sin renovaciones en los próximos {months_to_show} meses.")


# ═══════════════════════════════════════════════════════════════════
#  IMPORT CSV / EXCEL
# ═══════════════════════════════════════════════════════════════════
def page_import(data, save_fn):
    st.markdown(f"""
    <div class="page-hdr">📤 Importar Datos</div>
    <div class="page-sub">Carga propiedades o pólizas desde CSV o Excel (.xlsx)</div>
    """, unsafe_allow_html=True)

    if not HAS_PANDAS:
        st.error("⚠️ `pandas` no está instalado. Agrega `pandas>=2.0.0` a requirements.txt y reinicia.")
        return

    tab_props, tab_pols = st.tabs(["🏘️ Propiedades", "📋 Pólizas"])

    PROP_COLS = ["prop_id","nickname","address","city","state","zip","type",
                 "units","sqft","year_built","owner","mortgagee","coverage_status","action_status","notes"]
    POL_COLS  = ["prop_id","policy_number","carrier","agency","policy_type",
                 "effective_date","expiration_date","premium","status","notes"]

    def render_import_tab(entity, required_cols, all_cols, current_list, label):
        st.markdown(f"""
        <div style="background:{R['amber_lt']};border:1.5px solid {R['amber']};
             border-radius:10px;padding:.8rem 1.2rem;margin-bottom:.8rem;font-size:.82rem;color:#78350f;">
          <b>Columnas requeridas:</b> {', '.join(f'<code>{c}</code>' for c in required_cols)}<br>
          <b>Todas las columnas soportadas:</b> {', '.join(f'<code>{c}</code>' for c in all_cols)}
        </div>""", unsafe_allow_html=True)

        uploaded = st.file_uploader(
            f"Subir archivo para {label}",
            type=["csv","xlsx","xls"],
            key=f"upld_{entity}",
            label_visibility="collapsed",
        )
        if uploaded is None:
            st.info(f"Arrastra o selecciona un archivo CSV/Excel con las columnas indicadas.")

            # Template download
            import_template = ",".join(all_cols) + "\n"
            st.download_button(
                f"⬇️ Descargar plantilla CSV para {label}",
                data=import_template,
                file_name=f"insuretrack_{entity}_template.csv",
                mime="text/csv",
                key=f"tmpl_{entity}",
            )
            return

        try:
            if uploaded.name.endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
        except Exception as ex:
            st.error(f"Error leyendo archivo: {ex}")
            return

        st.markdown(f'<div class="sec-hdr">Vista previa — {len(df)} filas, {len(df.columns)} columnas</div>',
                    unsafe_allow_html=True)
        st.dataframe(df.head(20), use_container_width=True)

        # Validate required columns
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"❌ Columnas faltantes: {', '.join(missing)}")
            return

        # Clean and convert
        df = df.where(pd.notnull(df), None)

        # Check for duplicates
        existing_ids = set(r.get(required_cols[0],"") for r in current_list)
        new_rows   = df[~df[required_cols[0]].astype(str).isin(existing_ids)]
        dup_rows   = df[df[required_cols[0]].astype(str).isin(existing_ids)]

        st.markdown(f"""
        <div style="display:flex;gap:12px;margin:.5rem 0;">
          <div style="background:{R['green_lt']};border:1px solid #86efac;border-radius:8px;
               padding:.5rem .9rem;font-size:.82rem;color:#14532d;">
            <b>{len(new_rows)}</b> nuevas {label}
          </div>
          <div style="background:{R['amber_lt']};border:1px solid #fcd34d;border-radius:8px;
               padding:.5rem .9rem;font-size:.82rem;color:#78350f;">
            <b>{len(dup_rows)}</b> ya existen (se omitirán)
          </div>
        </div>""", unsafe_allow_html=True)

        if len(new_rows) == 0:
            st.warning("No hay filas nuevas para importar.")
            return

        if st.button(f"✅ Confirmar importación de {len(new_rows)} {label}", key=f"confirm_{entity}",
                     type="primary", use_container_width=False):
            added = 0
            for _, row in new_rows.iterrows():
                rec = {col: (row[col] if col in row and row[col] is not None else "")
                       for col in all_cols}
                # Type coercions
                for int_col in ["units","sqft","year_built"]:
                    if int_col in rec and rec[int_col] not in (None,""):
                        try: rec[int_col] = int(rec[int_col])
                        except Exception: rec[int_col] = None
                for flt_col in ["premium"]:
                    if flt_col in rec and rec[flt_col] not in (None,""):
                        try: rec[flt_col] = float(rec[flt_col])
                        except Exception: rec[flt_col] = 0.0
                current_list.append(rec)
                added += 1

            if entity == "props":
                data["properties"] = current_list
            else:
                data["policies"] = current_list

            save_fn(data)
            log_change("import", f"Importados {added} {label} desde {uploaded.name}")
            st.success(f"✅ {added} {label} importadas exitosamente.")
            st.cache_data.clear()
            st.rerun()

    with tab_props:
        render_import_tab(
            "props",
            required_cols=["prop_id","address","city"],
            all_cols=PROP_COLS,
            current_list=data["properties"],
            label="propiedades",
        )
    with tab_pols:
        render_import_tab(
            "pols",
            required_cols=["prop_id","policy_number"],
            all_cols=POL_COLS,
            current_list=data["policies"],
            label="pólizas",
        )


# ═══════════════════════════════════════════════════════════════════
#  SETTINGS
# ═══════════════════════════════════════════════════════════════════
def page_settings(data, save_fn):
    st.markdown(f"""
    <div style="font-size:1.5rem;font-weight:800;color:{R['text_d']};margin-bottom:.2rem;">
      ⚙️ Settings</div>
    <div style="font-size:.85rem;color:{R['text_m']};margin-bottom:1.2rem;">
      Portfolio configuration</div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="sec-hdr">Portfolio</div>', unsafe_allow_html=True)
    col, _ = st.columns([1.4, 2])
    with col:
        new_name = st.text_input("Portfolio name", value=data.get("portfolio_name",""),
                                 key="sett_nm")
        new_date = st.text_input("As of date (YYYY-MM-DD)",
                                 value=data.get("as_of_date",""), key="sett_dt")
        if st.button("Save Changes"):
            data["portfolio_name"] = new_name
            data["as_of_date"]     = new_date
            save_fn(data)
            st.success("✓ Saved.")

    st.markdown(f'<div class="sec-hdr">Account</div>', unsafe_allow_html=True)
    col2, _ = st.columns([1, 3])
    with col2:
        st.markdown(f"Signed in as **{st.session_state.get('username','')}**")
        if st.button("Sign Out"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    st.markdown(f'<div class="sec-hdr">Data</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="rg-card-sm" style="font-size:.82rem;color:{R['text_m']};">
      <b>Source:</b> portfolio.json<br>
      <b>Properties:</b> {len(data['properties'])} &nbsp;·&nbsp;
      <b>Policies:</b> {len(unique_policies(data['policies']))} unique &nbsp;·&nbsp;
      <b>Auto:</b> {len(data.get('auto_policies',[]))}
    </div>
    """, unsafe_allow_html=True)

    # ── Email alert config ─────────────────────────────────────────
    st.markdown(f'<div class="sec-hdr">📧 Alertas por Email</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{R['amber_lt']};border:1.5px solid {R['amber']};
         border-radius:10px;padding:.8rem 1.2rem;font-size:.82rem;color:#78350f;margin-bottom:.8rem;">
      Para habilitar alertas automáticas, configura las siguientes variables en
      <code>st.secrets</code> (archivo <code>.streamlit/secrets.toml</code>):<br><br>
      <code>[email]<br>
      smtp_host = "smtp.gmail.com"<br>
      smtp_port = 587<br>
      smtp_user = "tu@email.com"<br>
      smtp_password = "app_password"<br>
      alert_recipient = "caloyeras@email.com"<br>
      days_before_alert = 60</code>
    </div>
    """, unsafe_allow_html=True)

    # Show current email config status
    try:
        email_cfg = st.secrets.get("email", {})
        if email_cfg.get("smtp_host"):
            st.success(f"✅ Email configurado: {email_cfg.get('smtp_user','—')} → {email_cfg.get('alert_recipient','—')}")
        else:
            st.info("📧 Email no configurado. Usa el bloque de código anterior en secrets.toml.")
    except Exception:
        st.info("📧 Email no configurado. Usa el bloque de código anterior en secrets.toml.")

    col_email, _ = st.columns([1.5, 2])
    with col_email:
        if st.button("🔔 Enviar resumen ahora (demo)", key="send_email_demo"):
            st.info("⚠️ Esta funcionalidad requiere configuración SMTP en secrets.toml")

    # ── Changelog ─────────────────────────────────────────────────
    st.markdown(f'<div class="sec-hdr">📜 Historial de Cambios</div>', unsafe_allow_html=True)
    changelog = load_changelog()
    if not changelog:
        st.markdown(f"""
        <div class="rg-card-sm" style="font-size:.82rem;color:{R['text_m']};">
          Sin cambios registrados aún. Los cambios se registran automáticamente al
          importar datos o modificar el portafolio.
        </div>""", unsafe_allow_html=True)
    else:
        # Filter controls
        chg_col1, chg_col2, _ = st.columns([1.5, 1.5, 3])
        with chg_col1:
            chg_limit = st.selectbox("Mostrar", ["Últimos 25","Últimos 50","Todos"], key="chg_limit")
        limit_n = {"Últimos 25": 25, "Últimos 50": 50, "Todos": len(changelog)}[chg_limit]

        for entry in changelog[:limit_n]:
            ts   = entry.get("timestamp","—")
            user = entry.get("user","—")
            act  = entry.get("action","—")
            det  = entry.get("detail","")
            act_icons = {"import":"📤","save":"💾","delete":"🗑️","edit":"✏️"}
            icon = act_icons.get(act, "📌")
            st.markdown(f"""
            <div style="display:flex;gap:10px;padding:.45rem .7rem;
                 background:{R['white']};border:1px solid {R['rose_lt']};
                 border-radius:8px;margin-bottom:4px;align-items:flex-start;">
              <div style="font-size:1rem;min-width:24px;">{icon}</div>
              <div style="flex:1;">
                <div style="font-size:.78rem;font-weight:700;color:{R['text_d']};">
                  {act.title()} — {det[:80]}</div>
                <div style="font-size:.67rem;color:{R['text_m']};">
                  {ts} · {user}</div>
              </div>
            </div>""", unsafe_allow_html=True)

        if len(changelog) > limit_n:
            st.caption(f"Mostrando {limit_n} de {len(changelog)} entradas.")


# ═══════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    if not st.session_state.logged_in:
        show_login()
        return

    data = load_data()
    show_sidebar(data)

    page = st.session_state.get("page", "dashboard")
    if   page == "dashboard":   page_dashboard(data)
    elif page == "map":         page_map(data)
    elif page == "tasks":       page_tasks(data, save_data)
    elif page == "policies":    page_policies(data)
    elif page == "properties":  page_properties(data)
    elif page == "auto":        page_auto(data)
    elif page == "calendar":    page_calendar(data)
    elif page == "analytics":   page_analytics(data)
    elif page == "add":         page_add(data, save_data)
    elif page == "import_data": page_import(data, save_data)
    elif page == "reports":     page_reports(data)
    elif page == "settings":    page_settings(data, save_data)
    else:                       page_dashboard(data)


if __name__ == "__main__":
    main()
