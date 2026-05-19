"""
InsureTrack — CYS Caloyeras Insurance Portfolio Manager
Rose Garden Edition · v5.0
"""
import json, os
from datetime import date, datetime
from collections import defaultdict

import streamlit as st
import plotly.graph_objects as go

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
/* KPI nav shortcut buttons — subtle text-link style */
button[kind="secondary"][data-testid="baseButton-secondary"] {{
    background: transparent !important;
}}
div[data-testid="column"] .stButton > button[key^="kpi_"] {{
    background: transparent !important; color: {R['rose']} !important;
    border: none !important; font-size: .68rem !important;
    padding: 0.1rem 0 !important; font-weight: 600 !important;
    text-decoration: underline !important; transform: none !important;
    box-shadow: none !important; margin-top: -4px !important;
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
    border-bottom: 1.5px solid {R['rose_lt']};
    padding-bottom: 6px; margin: 1.2rem 0 0.9rem;
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
    ("📊", "Dashboard",  "dashboard"),
    ("📋", "Policies",   "policies"),
    ("🏘️", "Properties", "properties"),
    ("🚗", "Auto",       "auto"),
    ("➕", "Add / Edit",  "add"),
    ("📄", "Reports",    "reports"),
    ("⚙️", "Settings",  "settings"),
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
    <div style="font-size:1.6rem;font-weight:800;color:{R['text_d']};margin-bottom:.2rem;">
      📊 Dashboard</div>
    <div style="font-size:.85rem;color:{R['text_m']};margin-bottom:1.3rem;">
      {data.get('portfolio_name','')} · {data.get('as_of_date','')}</div>
    """, unsafe_allow_html=True)

    # KPIs — white cards, colored numbers + nav shortcut buttons
    quote_n = sum(1 for p in props if p.get("coverage_status") == "Quote")
    kpi_data = [
        (str(len(props)),          "Total Properties", R['text_d'],  "properties"),
        (str(active_n),            "Insured Active",   "#16a34a",    "properties"),
        (str(uninsu_n),            "Uninsured",        "#dc2626",    "properties"),
        (str(verify_n + quote_n),  "Verify / Quote",   "#d97706",    "properties"),
        (f"${prem_tot:,.0f}",      "Annual Premium",   R['rose'],    "policies"),
        (str(tot_units),           "Total Units",      R['plum'],    None),
    ]
    cols = st.columns(6)
    for col, (num, lbl, color, nav_page) in zip(cols, kpi_data):
        col.markdown(f"""
        <div class="kpi-tile">
          <div class="kpi-num" style="color:{color};">{num}</div>
          <div class="kpi-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)
        if nav_page:
            if col.button("→ Ver", key=f"kpi_{lbl.replace(' ','_')}", use_container_width=True):
                st.session_state.page = nav_page
                if lbl in ("Uninsured", "Verify / Quote"):
                    st.session_state["prop_open_gaps"] = True
                st.rerun()

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

    if alerts:
        alert_html = "  &nbsp;·&nbsp;  ".join(alerts)
        st.markdown(f"""
        <div style="background:linear-gradient(90deg,{R['red_lt']},{R['amber_lt']});
             border:1.5px solid #fca5a5;border-radius:10px;
             padding:.7rem 1.2rem;margin:.5rem 0 1rem;
             display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
          <span style="font-size:.82rem;color:#7f1d1d;">{alert_html}</span>
          <span style="font-size:.75rem;color:{R['text_m']};margin-left:auto;">
            ↑ Haz clic en "→ Ver" en las tarjetas de arriba para navegar</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:{R['green_lt']};border:1.5px solid #86efac;
             border-radius:10px;padding:.6rem 1.2rem;margin:.5rem 0 1rem;">
          <span style="font-size:.82rem;color:#14532d;">
            ✅ Todo al día — sin alertas urgentes</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1.05, 1], gap="large")

    # ── Renewals ──
    with left:
        st.markdown(f'<div class="sec-hdr">Upcoming Renewals</div>', unsafe_allow_html=True)
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
            color = R['red'] if days <= 60 else (R['amber'] if days <= 180 else R['green'])
            pids  = " · ".join(pol_props_map.get(pol["policy_number"], ["—"]))
            carrier = (pol.get("carrier") or "").split("/")[0].strip()[:24]
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:.5rem .8rem;
                 background:{R['white']};border-radius:8px;
                 border:1px solid {R['rose_lt']};margin-bottom:5px;">
              <div style="min-width:44px;text-align:center;font-weight:800;
                   font-size:.95rem;color:{color};">{days}d</div>
              <div style="flex:1;overflow:hidden;">
                <div style="font-size:.8rem;font-weight:700;color:{R['text_d']};
                     white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                  {pol['policy_number']}</div>
                <div style="font-size:.7rem;color:{R['text_m']};">{carrier} · {pids}</div>
              </div>
              <div style="font-size:.7rem;color:{R['text_m']};white-space:nowrap;">
                {pol['expiration_date']}</div>
            </div>""", unsafe_allow_html=True)

        # Coverage Gaps quick list
        st.markdown(f'<div class="sec-hdr">Coverage Gaps — Priority</div>',
                    unsafe_allow_html=True)
        gaps = sorted(
            [p for p in props if p.get("coverage_status") == "Uninsured"],
            key=lambda p: -(p.get("units") or 0)
        )
        for prop in gaps[:7]:
            units = prop.get("units") or 0
            pri   = "🔴" if units >= 10 else ("🟠" if units >= 4 else "🟡")
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;padding:.45rem .8rem;
                 background:{R['red_lt']};border-radius:8px;
                 border-left:3px solid {R['red']};margin-bottom:4px;">
              <div>{pri}</div>
              <div style="flex:1;">
                <div style="font-size:.8rem;font-weight:700;color:{R['text_d']};">
                  {prop['prop_id']} · {prop['address']}</div>
                <div style="font-size:.7rem;color:{R['text_m']};">
                  {prop['city']} · {units} units</div>
              </div>
            </div>""", unsafe_allow_html=True)
        if len(gaps) > 7:
            st.caption(f"+ {len(gaps)-7} more — see Properties → Coverage Gaps")

    # ── Charts ──
    with right:
        st.markdown(f'<div class="sec-hdr">Carrier Concentration</div>',
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
        st.markdown(f'<div class="sec-hdr">Renewals Next 12 Months</div>',
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
        st.markdown(f'<div class="sec-hdr">Coverage Distribution</div>',
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
    report_html = report.replace("\n", "<br>").replace(" ", "&nbsp;")
    st.markdown(f"""
    <div style="background:{R['white']};border:1.5px solid {R['rose_lt']};border-radius:12px;
         padding:1.4rem 1.6rem;font-family:'Courier New',monospace;font-size:.78rem;
         color:{R['text_d']};line-height:1.65;max-height:420px;overflow-y:auto;
         white-space:pre-wrap;">{report}</div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.5, 3])
    with c1:
        st.download_button(
            "⬇️ Download Summary (.txt)",
            data=report,
            file_name=f"insuretrack_summary_{_today().strftime('%Y%m%d')}.txt",
            mime="text/plain",
        )


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
    if   page == "dashboard":  page_dashboard(data)
    elif page == "policies":   page_policies(data)
    elif page == "properties": page_properties(data)
    elif page == "auto":       page_auto(data)
    elif page == "add":        page_add(data, save_data)
    elif page == "reports":    page_reports(data)
    elif page == "settings":   page_settings(data, save_data)
    else:                      page_dashboard(data)


if __name__ == "__main__":
    main()
