import math
import io
import csv
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

st.set_page_config(
    page_title="Hatem Alzoubi Lighting Design Pro",
    page_icon="💡",
    layout="wide"
)

# ==========================================
# FIXED ELECTRICAL PARAMETERS — JORDAN (230V / 50Hz)
# ==========================================
SUPPLY_V = 230
SUPPLY_HZ = 50
PF_DEFAULT = 0.90
CABLE_RHO = 0.0175

AMPACITY = {1.0: 11.0, 1.5: 14.5, 2.5: 19.5, 4.0: 26.0,
            6.0: 34.0, 10.0: 46.0, 16.0: 61.0}

# ==========================================
# LANGUAGE & CSS (Mobile Responsive + RTL)
# ==========================================
LANG = st.sidebar.selectbox("🌐 Language / اللغة", ["English", "العربية"])
is_ar = (LANG == "العربية")

# --- Common responsive rules (both languages) ---
COMMON_CSS = """
<style>
/* Never allow sideways scrolling */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    max-width: 100vw;
    overflow-x: hidden;
}
.block-container { max-width: 100% !important; }
img, canvas, svg { max-width: 100% !important; height: auto; }

@media (max-width: 768px) {
    .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        padding-top: 1rem !important;
    }
    h1 { font-size: 1.35rem !important; line-height: 1.4 !important; }
    h2 { font-size: 1.2rem !important; }
    h3 { font-size: 1.05rem !important; }

    /* Let column rows wrap, and stack columns (supports old + new Streamlit testids) */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.5rem !important;
    }
    [data-testid="stColumn"], [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }

    /* Metrics sit two per row to save vertical space. */
    @supports selector(:has(*)) {
        [data-testid="stColumn"]:has([data-testid="stMetric"]),
        [data-testid="column"]:has([data-testid="stMetric"]) {
            flex: 1 1 calc(50% - 0.5rem) !important;
            min-width: calc(50% - 0.5rem) !important;
            width: calc(50% - 0.5rem) !important;
        }
    }

    [data-testid="stMetricValue"] { font-size: 1.3rem !important; }
    [data-testid="stMetricLabel"] p { font-size: 0.8rem !important; }
}
</style>
"""
st.markdown(COMMON_CSS, unsafe_allow_html=True)

# --- Arabic / RTL rules (FIXED FOR MOBILE SIDEBAR) ---
if is_ar:
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

        /* 1. Base direction + font (Removed Sidebar from here to prevent flexbox bugs) */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebarContent"], [data-testid="stMain"], .main {
            direction: rtl !important;
            font-family: 'Cairo', 'Segoe UI', Tahoma, Arial, sans-serif !important;
        }

        /* 2. Fix Arabic Text Overlaps */
        h1, h2, h3, h4, h5, h6, p, label, li, .stMarkdown, .stCaption, .stApp div {
            line-height: 1.6 !important;
            word-break: break-word !important;
        }

        /* 3. Text alignment */
        h1, h2, h3, h4, h5, h6, p, label, li, .stMarkdown, .stCaption,
        [data-testid="stWidgetLabel"], [data-testid="stCaptionContainer"] {
            text-align: right !important;
            unicode-bidi: plaintext;
        }

        /* 4. Mixed Arabic/English/number lines: resolve direction per line */
        [data-testid="stAlert"] p, [data-testid="stAlert"] li,
        [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {
            unicode-bidi: plaintext;
        }

        /* 5. Metrics: numbers LTR so they never get clipped/reversed */
        [data-testid="stMetric"] { text-align: right !important; }
        [data-testid="stMetricValue"], [data-testid="stMetricValue"] div {
            direction: ltr !important; text-align: right !important;
            unicode-bidi: plaintext;
        }
        [data-testid="stMetricLabel"] { direction: rtl !important; text-align: right !important; }
        [data-testid="stMetricDelta"] { direction: ltr !important; justify-content: flex-end; }

        /* 6. Sliders: keep track LTR */
        [data-testid="stSlider"] { direction: ltr !important; }
        [data-testid="stSlider"] [data-testid="stWidgetLabel"],
        [data-testid="stSlider"] label {
            direction: rtl !important; text-align: right !important;
        }

        /* 7. Number inputs: digits LTR */
        [data-testid="stNumberInput"] input {
            direction: ltr !important; text-align: right !important;
        }

        /* 8. Selectbox / multiselect + dropdowns (PREVENTS VERTICAL TEXT) */
        [data-baseweb="select"] > div {
            flex-direction: row-reverse !important; /* Arrow on left */
            flex-wrap: nowrap !important;          /* Stops vertical squishing */
        }
        [data-baseweb="select"] span {
            white-space: nowrap !important;        /* Forces one line */
        }
        div[data-baseweb="popover"], div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li, ul[role="listbox"], li[role="option"] {
            direction: rtl !important; text-align: right !important;
        }

        /* 9. Checkbox */
        [data-testid="stCheckbox"] label { flex-direction: row-reverse; justify-content: flex-end; }

        /* 10. Expanders */
        [data-testid="stExpander"] summary { direction: rtl !important; }

        /* 11. Buttons */
        .stDownloadButton, .stButton { text-align: right !important; }

        /* 12. Small screens */
        @media (max-width: 768px) {
            h1 { text-align: center !important; font-size: 1.4rem !important; }
            [data-testid="stSidebar"] { max-width: 85vw !important; }
            [data-baseweb="select"] div, .stApp input { font-size: 16px !important; } /* stops iOS zoom */
        }

        /* 13. FIX SIDEBAR STUCK ON SCREEN IN RTL MOBILE */
        @media (max-width: 768px) {
            /* Force sidebar to anchor on the right and slide off-screen to the right */
            [data-testid="stSidebar"] {
                right: 0 !important;
                left: auto !important;
                transform: translateX(100%) !important;
                transition: transform 0.3s ease-in-out !important;
            }
            /* When opened by the user, bring it back to the screen */
            [data-testid="stSidebar"][aria-expanded="true"] {
                transform: translateX(0) !important;
            }
            /* Move the 'X' close button to the left side of the RTL sidebar */
            [data-testid="stSidebar"] button[kind="header"] {
                left: 0 !important;
                right: auto !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# SIDEBAR — Electrical
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("⚡ Electrical — Jordan 230V" if not is_ar
                  else "⚡ الكهرباء — الأردن 230V")
st.sidebar.markdown(
    f"**Supply:** `{SUPPLY_V} V / {SUPPLY_HZ} Hz` (fixed)" if not is_ar
    else f"**التغذية:** `{SUPPLY_V} V / {SUPPLY_HZ} هرتز` (ثابتة)"
)
BREAKER_A = st.sidebar.selectbox(
    "Lighting Breaker (A)" if not is_ar else "قاطع الإضاءة (أمبير)",
    [6, 10, 16, 20, 25], index=1
)
CIRCUIT_DERATE = st.sidebar.slider(
    "Circuit Derating (%)" if not is_ar else "تخفيض حمل الدائرة (%)",
    70, 90, 80, 5
)
CABLE_MAX_DROP = st.sidebar.slider(
    "Max Voltage Drop (%)" if not is_ar else "أقصى هبوط جهد (%)",
    2, 5, 3, 1
)

# ==========================================
# HELPERS
# ==========================================
def uf_from_room_index(K):
    if K < 0.6: return 0.40
    if K < 1.0: return 0.50
    if K < 1.5: return 0.58
    if K < 2.0: return 0.63
    if K < 3.0: return 0.68
    return 0.72

def estimate_uniformity(shr, beam_deg, room_index):
    if shr <= 0.5:   u0 = 0.85
    elif shr <= 0.7: u0 = 0.75
    elif shr <= 0.9: u0 = 0.65
    elif shr <= 1.1: u0 = 0.55
    elif shr <= 1.3: u0 = 0.45
    else:            u0 = 0.35
    if beam_deg < 30: u0 -= 0.05
    if room_index < 1.0: u0 += 0.05
    return max(0.20, min(0.95, u0))

def estimate_ugr(beam_deg, lm_per_fixture, room_index, recessed=True):
    if beam_deg <= 24:   base = 17
    elif beam_deg <= 36: base = 18
    elif beam_deg <= 60: base = 19
    elif beam_deg <= 90: base = 21
    else:                base = 23
    if recessed: base -= 1
    if lm_per_fixture > 1000:   base += 2
    elif lm_per_fixture > 700:  base += 1
    if room_index < 1.0:   base += 2
    elif room_index < 2.0: base += 1
    return base

def shr_max_for_beam(beam_deg):
    if beam_deg <= 24:  return 1.10
    if beam_deg <= 36:  return 1.00
    if beam_deg <= 60:  return 0.85
    if beam_deg <= 90:  return 0.75
    return 0.65

def profile_pieces_breakdown(total_m):
    std = [3.0, 2.0, 1.0, 0.5]
    remaining = float(total_m)
    pieces = {}
    for s in std:
        if remaining >= s - 0.01:
            n = int(math.floor(remaining / s + 0.001))
            if n > 0:
                pieces[s] = n
                remaining -= n * s
    if remaining > 0.05:
        smallest = min(std)
        pieces[smallest] = pieces.get(smallest, 0) + 1
    return pieces

def pieces_to_str(pieces):
    if not pieces: return "0 m"
    parts = [f"{n}×{s}m" for s, n in pieces.items()]
    return " + ".join(parts)

def recommend_cable_size(current_A, length_m, voltage, max_drop_pct):
    A_min_vd = (2 * length_m * current_A * CABLE_RHO) / (voltage * max_drop_pct / 100)
    for s in sorted(AMPACITY.keys()):
        if AMPACITY[s] >= current_A and s >= A_min_vd:
            return s, A_min_vd
    return max(AMPACITY.keys()), A_min_vd

def recommend_psu_size(required_w):
    sizes = [60, 100, 150, 200, 300, 400, 600, 1000, 1500]
    for s in sizes:
        if s >= required_w:
            return f"{s} W"
    return f"{math.ceil(required_w / 1000)}× 1000 W"

def safe_div(a, b, default=0):
    return a / b if b else default

def safe_filename(text):
    return re.sub(r'[^\w\-]+', '_', text, flags=re.UNICODE).strip('_') or "room"

ROOM_EN = {
    "غرفة معيشة": "living_room", "غرفة نوم": "bedroom", "مطبخ": "kitchen",
    "حمام": "bathroom", "غرفة طعام": "dining", "ممر / درج": "corridor",
    "مكتب مفتوح عام": "open_office", "مكتب خاص": "private_office",
    "غرفة اجتماعات": "conference", "الاستقبال / اللوبي": "reception",
    "ممر": "office_corridor", "معرض مفروشات عام": "showroom_general",
    "واجهة العرض / منطقة مميزة": "showroom_display",
    "منطقة الكشير / المحاسبة": "cashier", "المستودع / المكتب الخلفي": "back_office",
}

CH_STYLE_AR = {
    "Modern Pendant": "معلقة حديثة", "Crystal": "كريستال",
    "Linear": "خطية", "Ring": "حلقية", "Cluster": "تجمع",
}

# ==========================================
# TITLE
# ==========================================
st.title("Hatem Alzoubi Lighting Design Pro" if not is_ar
         else "مجموعة حاتم الزعبي للإنارة - حاسبة الإنارة - مهندس وائل")
st.caption("Jordan 230V / 50Hz | Interior + Electrical + Lighting Engineering" if not is_ar
           else "مجموعة حاتم الزعبي للإنارة - حاسبة الإنارة - مهندس وائل | الأردن 230V / 50Hz")

# ==========================================
# PHASE 1
# ==========================================
st.header("Phase 1: Space & Target" if not is_ar else "المرحلة 1: الفراغ والهدف")

building_category = st.selectbox(
    "Building Category:" if not is_ar else "فئة المبنى:",
    ["Villa", "Office", "Showroom"] if not is_ar else ["فيلا", "مكتب", "معرض تجاري"]
)

if building_category in ["Villa", "فيلا"]:
    room_type = st.selectbox("Room Type:" if not is_ar else "نوع الغرفة:",
        ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Dining Room",
         "Corridor / Stairs"] if not is_ar
        else ["غرفة معيشة", "غرفة نوم", "مطبخ", "حمام", "غرفة طعام", "ممر / درج"])
    ROOM_DB = {
        "Living Room": (200, 22, 0.0, False), "Bedroom": (150, 22, 0.4, False),
        "Kitchen": (300, 22, 0.9, True), "Bathroom": (250, 25, 0.0, True),
        "Dining Room": (200, 22, 0.75, False), "Corridor / Stairs": (100, 25, 0.0, False),
        "غرفة معيشة": (200, 22, 0.0, False), "غرفة نوم": (150, 22, 0.4, False),
        "مطبخ": (300, 22, 0.9, True), "حمام": (250, 25, 0.0, True),
        "غرفة طعام": (200, 22, 0.75, False), "ممر / درج": (100, 25, 0.0, False),
    }
elif building_category in ["Office", "مكتب"]:
    room_type = st.selectbox("Room Type:" if not is_ar else "نوع الغرفة:",
        ["General Open Office", "Private Office", "Conference Room",
         "Reception / Lobby", "Corridor"] if not is_ar
        else ["مكتب مفتوح عام", "مكتب خاص", "غرفة اجتماعات", "الاستقبال / اللوبي", "ممر"])
    ROOM_DB = {
        "General Open Office": (500, 19, 0.75, False), "Private Office": (500, 19, 0.75, False),
        "Conference Room": (400, 19, 0.75, False), "Reception / Lobby": (300, 22, 0.0, False),
        "Corridor": (150, 25, 0.0, False),
        "مكتب مفتوح عام": (500, 19, 0.75, False), "مكتب خاص": (500, 19, 0.75, False),
        "غرفة اجتماعات": (400, 19, 0.75, False), "الاستقبال / اللوبي": (300, 22, 0.0, False),
        "ممر": (150, 25, 0.0, False),
    }
else:
    room_type = st.selectbox("Room Type:" if not is_ar else "نوع الغرفة:",
        ["General Furniture Exhibition", "Display Window / Feature Zone",
         "Checkout / Cashier Counter", "Storage / Back Office"] if not is_ar
        else ["معرض مفروشات عام", "واجهة العرض / منطقة مميزة",
              "منطقة الكشير / المحاسبة", "المستودع / المكتب الخلفي"])
    ROOM_DB = {
        "General Furniture Exhibition": (400, 22, 0.0, False),
        "Display Window / Feature Zone": (750, 19, 0.0, False),
        "Checkout / Cashier Counter": (500, 22, 0.9, False),
        "Storage / Back Office": (200, 25, 0.75, False),
        "معرض مفروشات عام": (400, 22, 0.0, False),
        "واجهة العرض / منطقة مميزة": (750, 19, 0.0, False),
        "منطقة الكشير / المحاسبة": (500, 22, 0.9, False),
        "المستودع / المكتب الخلفي": (200, 25, 0.75, False),
    }

target_lux, target_ugr, wp_default, wet_room = ROOM_DB[room_type]

c1, c2, c3 = st.columns(3)
with c1: length = st.number_input("Length (m):" if not is_ar else "الطول (م):",
                                  0.5, 100.0, 5.0, 0.1)
with c2: width  = st.number_input("Width (m):" if not is_ar else "العرض (م):",
                                  0.5, 100.0, 4.0, 0.1)
with c3: height = st.number_input("Ceiling Height (m):" if not is_ar else "ارتفاع السقف (م):",
                                  2.0, 20.0, 3.0, 0.1)

work_plane = st.number_input(
    "Work Plane Height (m):" if not is_ar else "ارتفاع مستوى العمل (م):",
    0.0, 1.5, wp_default, 0.05,
    help=f"Default for this room type: {wp_default} m" if not is_ar
         else f"افتراضي لنوع الغرفة: {wp_default} م"
)
maintenance_factor = st.slider(
    "Maintenance Factor (MF):" if not is_ar else "معامل الصيانة (MF):",
    0.50, 1.00, 0.80, 0.05
)

area = length * width
hm = max(0.5, height - work_plane)
room_index_k = safe_div(area, hm * (length + width))
uf_auto = uf_from_room_index(room_index_k)
utilization_factor = st.slider(
    "Utilization Factor (UF):" if not is_ar else "معامل الاستفادة (UF):",
    0.30, 0.85, round(uf_auto, 2), 0.01,
    help=f"Auto from K={room_index_k:.2f}" if not is_ar
         else f"تلقائي من K={room_index_k:.2f}"
)
total_lumens_req = area * target_lux / (utilization_factor * maintenance_factor)

st.markdown("---")
mc1, mc2, mc3 = st.columns(3)
mc1.metric("Area" if not is_ar else "المساحة", f"{area:.1f} m²")
mc2.metric("Room Index K" if not is_ar else "مؤشر الغرفة K", f"{room_index_k:.2f}")
mc3.metric("Target Lux" if not is_ar else "اللوكس المطلوب", f"{target_lux} lx")

mc4, mc5 = st.columns(2)
mc4.metric("UF / MF" if not is_ar else "معامل الاستفادة / الصيانة", f"{utilization_factor:.2f} / {maintenance_factor:.2f}")
mc5.metric("Required Lumens" if not is_ar else "إجمالي اللومن المطلوب", f"{total_lumens_req:,.0f} lm")
st.markdown("---")

# ==========================================
# PHASE 2 — FIXTURES
# ==========================================
st.header("Phase 2: Lighting Fixtures" if not is_ar else "المرحلة 2: وحدات الإضاءة")

FX = {"spot": "Spot Light", "track": "Magnetic Track",
      "profile": "LED Profile", "hidden": "Hidden Light",
      "chandelier": "Chandelier"}
FX_AR = {"spot": "سبوت لايت", "track": "تراك مغناطيسي",
         "profile": "بروفايل ليد", "hidden": "إضاءة مخفية",
         "chandelier": "ثريا (نجفة)"}
fx_label = lambda k: FX[k] if not is_ar else FX_AR[k]

sel_keys = st.multiselect(
    "Select fixture types:" if not is_ar else "اختر أنواع الوحدات:",
    options=list(FX.keys()), format_func=fx_label, default=["spot"]
)

CCT_OPTIONS = {"2700K Warm": 2700, "3000K Warm White": 3000,
               "4000K Neutral": 4000, "5000K Cool": 5000, "6500K Daylight": 6500}
CRI_OPTIONS = {"Ra ≥ 80": 80, "Ra ≥ 90": 90, "Ra ≥ 95": 95}
BEAM_OPTIONS = {"15° Narrow": 15, "24° Spot": 24,
                "36° Flood": 36, "60° Wide": 60, "90° Very Wide": 90}

results = {}
total_watts = 0.0
total_lumens = 0.0

if not sel_keys:
    st.warning("⚠️ Select at least one fixture type." if not is_ar
               else "⚠️ اختر نوعًا واحدًا على الأقل.")
else:
    st.subheader("⚖️ Lumens Distribution Between Types" if not is_ar
                 else "⚖️ توزيع اللومن بين الأنواع")
    st.caption("Adjust the share of total lumens each type should provide." if not is_ar
               else "عدّل نسبة مساهمة كل نوع من إجمالي اللومن.")
    weights = {}
    default_w = round(100 / len(sel_keys))
    wcols = st.columns(len(sel_keys))
    for i, fx in enumerate(sel_keys):
        with wcols[i]:
            weights[fx] = st.number_input(
                f"{fx_label(fx)} (%)", min_value=1, max_value=100,
                value=default_w, step=5, key=f"{fx}_weight"
            )
    total_w = sum(weights.values())
    shares = {fx: weights[fx] / total_w for fx in sel_keys}
    lumens_target = {fx: total_lumens_req * shares[fx] for fx in sel_keys}
    st.caption(
        " | ".join([f"{fx_label(fx)}: {shares[fx]*100:.0f}%" for fx in sel_keys])
    )
    st.divider()

    for fx in sel_keys:
        with st.expander(f"⚙️ {fx_label(fx)}", expanded=True):
            fc1, fc2 = st.columns(2)
            with fc1:
                cct_label = st.selectbox("CCT:" if not is_ar else "CCT:",
                                          list(CCT_OPTIONS.keys()), key=f"{fx}_cct")
                cri_label = st.selectbox("CRI:" if not is_ar else "CRI:",
                                          list(CRI_OPTIONS.keys()), key=f"{fx}_cri")

                if fx == "chandelier":
                    beam_deg = 90
                    pf = st.number_input(
                        "Power Factor:" if not is_ar else "معامل القدرة:",
                        0.50, 1.00, PF_DEFAULT, 0.01, key=f"{fx}_pf",
                        help="Typical LED driver PF = 0.90."
                    )
                else:
                    beam_label = st.selectbox("Beam Angle:" if not is_ar else "زاوية الشعاع:",
                                               list(BEAM_OPTIONS.keys()), key=f"{fx}_beam")
                    beam_deg = BEAM_OPTIONS[beam_label]
                    pf = st.number_input(
                        "Power Factor:" if not is_ar else "معامل القدرة:",
                        0.50, 1.00, PF_DEFAULT, 0.01, key=f"{fx}_pf",
                        help="Typical LED driver PF = 0.90. Use 0.95 for premium."
                        if not is_ar else "PF نموذجي = 0.90، الممتاز = 0.95."
                    )

            if fx == "spot":
                with fc2:
                    cutout = st.selectbox("Cutout:" if not is_ar else "الفتحة:",
                                           ["7 cm", "7.5 cm", "9 cm", "10 cm", "12 cm"],
                                           key="spot_cutout")
                    lm_each = st.number_input("lm per spot:" if not is_ar else "لومن/سبوت:",
                                               50, 3000, 550, 25, key="spot_lm")
                    w_each = st.number_input("W per spot:" if not is_ar else "واط/سبوت:",
                                              1.0, 50.0, 7.0, 0.5, key="spot_w")
                    recessed = st.checkbox("Recessed" if not is_ar else "مدمج",
                                            True, key="spot_recessed")

                raw_qty = max(1, math.ceil(lumens_target[fx] / lm_each))
                max_density_area = 2.5 if building_category in ["Villa", "فيلا"] else 2.0
                max_allowed_spots = max(4, int(area / max_density_area))

                if raw_qty > max_allowed_spots:
                    st.warning(
                        f"⚠️ **Density Control:** The math requires {raw_qty} spots, but that is too dense for a {area:.1f} m² room. "
                        f"Quantity has been capped at **{max_allowed_spots} spots** to protect the interior design."
                        if not is_ar else
                        f"⚠️ **التحكم بالكثافة:** الحساب يتطلب {raw_qty} سبوت، لكن هذا عدد كبير جداً لغرفة {area:.1f} م². "
                        f"تم تحديد الكمية بـ **{max_allowed_spots} سبوت** للحفاظ على التصميم الداخلي."
                    )
                    raw_qty = max_allowed_spots
                    recommended_lm = math.ceil(lumens_target[fx] / raw_qty)
                    st.info(
                        f"💡 **Recommendation:** Use spots of at least **{recommended_lm} lm** each, "
                        f"or reduce the spot weight (%) above."
                        if not is_ar else
                        f"💡 **توصية:** استخدم سبوتات بقوة **{recommended_lm} لومن** على الأقل."
                    )

                max_dim = max(4, int(math.ceil(math.sqrt(raw_qty))) + 3)
                room_ar = length / width
                shr_lim = shr_max_for_beam(beam_deg)

                best = None
                best_score = float('inf')
                for r in range(1, max_dim + 1):
                    for c in range(1, max_dim + 1):
                        tg = r * c
                        if tg < raw_qty: continue
                        step_x = length / c
                        step_y = width / r
                        margin_x = step_x / 2
                        margin_y = step_y / 2
                        if margin_x < 0.30 or margin_y < 0.30: continue
                        if (step_x / hm) > shr_lim or (step_y / hm) > shr_lim: continue
                        score = abs((c / r) - room_ar) * 1.5 + (tg - raw_qty) * 0.4
                        if score < best_score:
                            best_score = score
                            best = (tg, r, c, step_x, step_y, margin_x, margin_y)

                if best is None:
                    for r in range(1, max_dim + 1):
                        for c in range(1, max_dim + 1):
                            tg = r * c
                            if tg < raw_qty: continue
                            step_x = length / c
                            step_y = width / r
                            margin_x = step_x / 2
                            margin_y = step_y / 2
                            score = abs((c / r) - room_ar) * 1.5 + (tg - raw_qty) * 0.4
                            if score < best_score:
                                best_score = score
                                best = (tg, r, c, step_x, step_y, margin_x, margin_y)

                    if best:
                        st.warning(
                            "⚠️ SHR limit ignored slightly to fit a full-room grid." if not is_ar
                            else "⚠️ تم تجاهل حد SHR قليلاً لتغطية الغرفة بالكامل."
                        )
                    else:
                        st.error("⚠️ Could not find a suitable grid." if not is_ar else "⚠️ لم يتم العثور على شبكة مناسبة.")
                        continue

                qty, rows, cols, step_x, step_y, margin_x, margin_y = best
                delivered_lm = qty * lm_each
                watts = qty * w_each
                shr_actual = max(step_x / hm, step_y / hm)
                u0 = estimate_uniformity(shr_actual, beam_deg, room_index_k)
                ugr = estimate_ugr(beam_deg, lm_each, room_index_k, recessed)

                results["spot"] = dict(
                    qty=qty, rows=rows, cols=cols, lm=delivered_lm, watts=watts,
                    lm_each=lm_each, w_each=w_each, shr=shr_actual, u0=u0, ugr=ugr,
                    beam=beam_deg, cct=CCT_OPTIONS[cct_label], cri=CRI_OPTIONS[cri_label],
                    pf=pf, margin_x=margin_x, margin_y=margin_y,
                    step_x=step_x, step_y=step_y, cutout=cutout,
                    shr_lim=shr_lim
                )
                total_watts += watts
                total_lumens += delivered_lm

                st.info(
                    f"📐 **{qty} spots** in **{rows}×{cols}** | SHR {shr_actual:.2f} "
                    f"(limit {shr_lim:.2f}) | U₀ ≈ {u0:.2f} | UGR ≈ {ugr}"
                    if not is_ar else
                    f"📐 **{qty} سبوت** شبكة **{rows}×{cols}** | SHR {shr_actual:.2f} "
                    f"(الحد {shr_lim:.2f}) | U₀ ≈ {u0:.2f} | UGR ≈ {ugr}"
                )

            elif fx == "chandelier":
                with fc2:
                    ch_label_fn = (lambda s: s) if not is_ar else (lambda s: CH_STYLE_AR.get(s, s))
                    ch_type = st.selectbox(
                        "Chandelier Style:" if not is_ar else "ستايل الثريا:",
                        list(CH_STYLE_AR.keys()),
                        format_func=ch_label_fn,
                        key="ch_type"
                    )
                    ch_lm = st.number_input("Total Lumens (lm):" if not is_ar else "إجمالي اللومن:",
                                            100, 20000, 3000, 100, key="ch_lm")
                    ch_w = st.number_input("Total Power (W):" if not is_ar else "إجمالي الواط:",
                                           5.0, 500.0, 60.0, 5.0, key="ch_w")

                qty = 1
                delivered_lm = ch_lm
                watts = ch_w
                share_pct = shares[fx] * 100

                if delivered_lm < lumens_target[fx] * 0.8:
                    st.warning(
                        f"⚠️ Chandelier output ({delivered_lm} lm) is lower than the target "
                        f"({lumens_target[fx]:.0f} lm) for its {share_pct:.0f}% share."
                        if not is_ar else
                        f"⚠️ لومن الثريا ({delivered_lm} lm) أقل من المستهدف "
                        f"({lumens_target[fx]:.0f} lm) لنسبتها ({share_pct:.0f}%)."
                    )

                results["chandelier"] = dict(
                    qty=1, lm=delivered_lm, watts=watts, ch_type=ch_type,
                    cct=CCT_OPTIONS[cct_label], cri=CRI_OPTIONS[cri_label],
                    pf=pf, beam=beam_deg
                )
                total_watts += watts
                total_lumens += delivered_lm

                ch_disp = CH_STYLE_AR.get(ch_type, ch_type) if is_ar else ch_type
                st.info(
                    f"📐 **1 Chandelier** ({ch_type}) | {delivered_lm:,.0f} lm | {watts:.0f} W"
                    if not is_ar else
                    f"📐 **ثريا واحدة** ({ch_disp}) | {delivered_lm:,.0f} lm | {watts:.0f} واط"
                )

            elif fx == "track":
                with fc2:
                    mount = st.selectbox("Mounting:" if not is_ar else "التركيب:",
                                          ["Recessed", "Surface", "Suspended"],
                                          key="track_mount")
                    track_lm_m = st.number_input("lm/m:" if not is_ar else "لومن/م:",
                                                  200, 3000, 1200, 100, key="track_lm")
                    track_w_m = st.number_input("W/m:" if not is_ar else "واط/م:",
                                                  3.0, 60.0, 15.0, 1.0, key="track_w")
                    layout = st.selectbox("Layout:" if not is_ar else "التخطيط:",
                                            ["Straight (Center)", "Parallel (2)",
                                             "L-Shape", "U-Shape"], key="track_layout")

                if layout == "Straight (Center)":   geom = max(length, width)
                elif layout == "Parallel (2)":      geom = 2 * max(length, width)
                elif layout == "L-Shape":           geom = length + width
                else:                               geom = 2 * length + width

                delivered_lm = geom * track_lm_m
                watts = geom * track_w_m
                results["track"] = dict(
                    length=geom, lm=delivered_lm, watts=watts,
                    lm_m=track_lm_m, w_m=track_w_m, layout=layout, mount=mount,
                    cct=CCT_OPTIONS[cct_label], cri=CRI_OPTIONS[cri_label],
                    beam=beam_deg, pf=pf
                )
                total_watts += watts
                total_lumens += delivered_lm
                st.info(
                    f"📐 **{geom:.2f} m** | {delivered_lm:,.0f} lm | {watts:.0f} W"
                    if not is_ar else f"📐 **{geom:.2f} م** | {delivered_lm:,.0f} lm | {watts:.0f} واط"
                )

            elif fx == "profile":
                with fc2:
                    model = st.selectbox("Model:" if not is_ar else "الموديل:",
                                          ["508", "617", "619", "2010A", "3010",
                                           "2320A", "509", "601", "5012A", "618",
                                           "506", "1509", "5313"], key="profile_model")
                    prof_lm_m = st.number_input("lm/m:" if not is_ar else "لومن/م:",
                                                  50, 2500, 150, 25, key="prof_lm")
                    prof_w_m = st.number_input("W/m:" if not is_ar else "واط/م:",
                                                 3.0, 40.0, 12.0, 1.0, key="prof_w")
                    placement = st.selectbox("Placement:" if not is_ar else "التوزيع:",
                                              ["Perimeter", "Parallel Lines", "Center Axis"],
                                              key="prof_place")

                off = 0.30
                if placement == "Perimeter":
                    geom = 2 * (max(0.0, length - 2 * off) + max(0.0, width - 2 * off))
                elif placement == "Parallel Lines":
                    geom = 2 * max(length, width)
                else:
                    geom = max(length, width)

                delivered_lm = geom * prof_lm_m
                watts = geom * prof_w_m
                pieces = profile_pieces_breakdown(geom)
                results["profile"] = dict(
                    length=geom, lm=delivered_lm, watts=watts,
                    lm_m=prof_lm_m, w_m=prof_w_m, pieces=pieces,
                    model=model, placement=placement,
                    cct=CCT_OPTIONS[cct_label], cri=CRI_OPTIONS[cri_label],
                    beam=beam_deg, pf=pf
                )
                total_watts += watts
                total_lumens += delivered_lm
                st.info(
                    f"📐 **{geom:.2f} m** → {pieces_to_str(pieces)} | "
                    f"{delivered_lm:,.0f} lm | {watts:.0f} W"
                    if not is_ar else
                    f"📐 **{geom:.2f} م** → {pieces_to_str(pieces)} | "
                    f"{delivered_lm:,.0f} lm | {watts:.0f} واط"
                )

            elif fx == "hidden":
                with fc2:
                    tier = st.selectbox("Strip tier:" if not is_ar else "فئة الشريط:",
                                         ["9.6 W/m", "14.4 W/m", "18 W/m"], key="hid_watt")
                    w_m = float(tier.split()[0])
                    hid_lm_m = st.number_input("lm/m:" if not is_ar else "لومن/م:",
                                                200, 3000, 1100, 100, key="hid_lm")
                    sides = st.multiselect("Sides:" if not is_ar else "الجوانب:",
                                            ["Side A (L)", "Side B (L)",
                                             "Side C (W)", "Side D (W)"],
                                            default=["Side A (L)", "Side B (L)",
                                                     "Side C (W)", "Side D (W)"],
                                            key="hid_sides")
                    strip_v = st.selectbox("Strip Voltage:" if not is_ar else "جهد الشريط:",
                                            [24, 48], key="hid_v")

                if not sides:
                    st.error("⚠️ Select at least one side." if not is_ar
                             else "⚠️ اختر جانبًا واحدًا على الأقل.")
                    continue

                geom = sum(length if s.endswith("(L)") else width for s in sides)
                delivered_lm = geom * hid_lm_m
                watts = geom * w_m
                results["hidden"] = dict(
                    length=geom, lm=delivered_lm, watts=watts,
                    lm_m=hid_lm_m, w_m=w_m, voltage=strip_v,
                    cct=CCT_OPTIONS[cct_label], cri=CRI_OPTIONS[cri_label],
                    beam=beam_deg, pf=pf
                )
                total_watts += watts
                total_lumens += delivered_lm
                st.info(
                    f"📐 **{geom:.2f} m** @ {strip_v}V | {delivered_lm:,.0f} lm | {watts:.0f} W"
                    if not is_ar else
                    f"📐 **{geom:.2f} م** @ {strip_v}V | {delivered_lm:,.0f} lm | {watts:.0f} واط"
                )

# ==========================================
# PHASE 3 — LIGHTING VERIFICATION
# ==========================================
if results:
    st.divider()
    st.header("Phase 3: Lighting Engineering" if not is_ar
              else "المرحلة 3: التحقق الهندسي للإضاءة")

    actual_lux = total_lumens * utilization_factor * maintenance_factor / area
    lux_delta = actual_lux - target_lux

    v1, v2 = st.columns(2)
    v1.metric("Req lm" if not is_ar else "لومن مطلوب", f"{total_lumens_req:,.0f}")
    v2.metric("Delivered lm" if not is_ar else "لومن مزود", f"{total_lumens:,.0f}")

    v3, v4 = st.columns(2)
    v3.metric("Actual Lux" if not is_ar else "لوكس فعلي",
              f"{actual_lux:.0f}", delta=f"{lux_delta:+.0f}")
    v4.metric("Load" if not is_ar else "حمل", f"{total_watts:.0f} W")

    if actual_lux >= target_lux * 1.05:
        st.success(f"✅ Meets target ({actual_lux:.0f}/{target_lux} lx)" if not is_ar
                   else f"✅ يحقق الهدف ({actual_lux:.0f}/{target_lux} lx)")
    elif actual_lux >= target_lux * 0.90:
        st.warning(f"⚠️ Slightly under ({actual_lux:.0f}/{target_lux} lx)" if not is_ar
                   else f"⚠️ أقل قليلًا ({actual_lux:.0f}/{target_lux} lx)")
    else:
        st.error(f"❌ Under-lit ({actual_lux:.0f}/{target_lux} lx)" if not is_ar
                 else f"❌ إضاءة غير كافية ({actual_lux:.0f}/{target_lux} lx)")

    if "spot" in results:
        s = results["spot"]
        st.subheader("🔍 Spot Analysis" if not is_ar else "🔍 تحليل السبوت")

        lim_txt = (lambda v: f"limit {v}") if not is_ar else (lambda v: f"الحد {v}")
        u0_txt  = (lambda v: "≥0.60" if v >= 0.60 else "<0.60")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("SHR" if not is_ar else "SHR", f"{s['shr']:.2f}",
                  delta=lim_txt(f"{s['shr_lim']:.2f}"))
        m2.metric("U₀" if not is_ar else "U₀", f"{s['u0']:.2f}",
                  delta=u0_txt(s['u0']))
        m3.metric("UGR" if not is_ar else "UGR", f"{s['ugr']}",
                  delta=lim_txt(target_ugr))
        m4.metric("Beam" if not is_ar else "الشعاع", f"{s['beam']}°")

    st.caption("📌 Lumen method estimate. Verify with DIALux/Relux for final design." if not is_ar
               else "📌 تقدير بطريقة اللومن. تحقق بـ DIALux/Relux للتصميم النهائي.")

# ==========================================
# PHASE 4 — ELECTRICAL
# ==========================================
if results:
    st.divider()
    st.header("Phase 4: Electrical — 230V System" if not is_ar
              else "المرحلة 4: الكهرباء — نظام 230V")

    pfs = [r['pf'] for r in results.values()]
    pf_system = min(pfs)

    connected_load = total_watts
    design_load = connected_load * 1.20
    current_total = connected_load / (SUPPLY_V * pf_system)

    e1, e2 = st.columns(2)
    e1.metric("Connected" if not is_ar else "الحمل الموصول", f"{connected_load:.0f} W")
    e2.metric("Design +20%" if not is_ar else "التصميم +20%", f"{design_load:.0f} W")

    e3, e4 = st.columns(2)
    e3.metric("PF (worst)" if not is_ar else "PF (الأسوأ)", f"{pf_system:.2f}")
    e4.metric("Current" if not is_ar else "التيار", f"{current_total:.1f} A")

    psu_size = recommend_psu_size(design_load)
    st.info(f"🔋 **Recommended PSU/Driver:** {psu_size} "
            f"(connected × 1.20)" if not is_ar
            else f"🔋 **PSU/Driver المقترح:** {psu_size} "
            f"(الموصول × 1.20)")

    st.subheader("🔌 Circuits & Protection" if not is_ar
                 else "🔌 الدوائر والحماية")
    max_circuit_w = BREAKER_A * SUPPLY_V * pf_system * CIRCUIT_DERATE / 100
    num_circuits = max(1, math.ceil(connected_load / max_circuit_w))
    circuit_current = (connected_load / num_circuits) / (SUPPLY_V * pf_system)

    cc1, cc2 = st.columns(2)
    cc1.metric("Max W/circuit" if not is_ar else "أقصى واط/دائرة", f"{max_circuit_w:.0f}")
    cc2.metric("Circuits" if not is_ar else "عدد الدوائر", f"{num_circuits}")

    cc3, cc4 = st.columns(2)
    cc3.metric("A/circuit" if not is_ar else "أمبير/دائرة", f"{circuit_current:.1f}")
    cc4.metric("MCB Type" if not is_ar else "نوع القاطع", "C-curve")

    st.warning(
        "🛡️ Use **MCB Type C (or D)** — LED drivers draw 20–100× inrush. "
        "Provide **30 mA RCD** per IEC 60364-4-41." if not is_ar
        else "🛡️ استخدم **قاطع Type C (أو D)** — درايفرات LED تسحب 20–100× تيار الإقلاع. "
        "**RCD 30mA** إلزامي حسب IEC 60364-4-41."
    )

    main_run = max(length, width) * 1.2
    cable_size, a_min_vd = recommend_cable_size(
        current_total, main_run, SUPPLY_V, CABLE_MAX_DROP
    )
    st.success(
        f"📏 Main feed: **{cable_size} mm²** copper "
        f"(ampacity {AMPACITY[cable_size]} A, run ~{main_run:.1f} m, "
        f"V-drop check needs ≥{a_min_vd:.2f} mm²)"
        if not is_ar else
        f"📏 الخط الرئيسي: **{cable_size} mm²** نحاس "
        f"(سعة {AMPACITY[cable_size]} A، مسار ~{main_run:.1f} م، "
        f"هبوط الجهد يتطلب ≥{a_min_vd:.2f} mm²)"
    )

    if "hidden" in results:
        h = results["hidden"]
        strip_v = h["voltage"]
        strip_current = h["watts"] / strip_v
        for cross in [1.5, 2.5, 4.0, 6.0]:
            vd = (2 * h["length"] * strip_current * CABLE_RHO) / cross
            pct = vd / strip_v * 100
            if pct <= CABLE_MAX_DROP:
                st.info(
                    f"🔋 LED Strip ({strip_v}V, {strip_current:.1f} A): "
                    f"**{cross} mm²** feed → V-drop {pct:.1f}%"
                    if not is_ar else
                    f"🔋 شريط LED ({strip_v}V، {strip_current:.1f} A): "
                    f"كابل **{cross} mm²** → هبوط {pct:.1f}%"
                )
                break
        else:
            st.warning(
                f"⚠️ {strip_v}V run too long. Split or use 48V." if not is_ar
                else f"⚠️ مسار {strip_v}V طويل. قسّمه أو استخدم 48V."
            )

    if wet_room:
        st.warning(
            "💧 Wet zone: IP44+ fixtures + 30 mA RCD mandatory." if not is_ar
            else "💧 منطقة رطبة: وحدات IP44+ + RCD 30mA إلزامي."
        )

# ==========================================
# PHASE 5 — LAYOUT GUIDE
# ==========================================
if results:
    st.divider()
    st.header("Phase 5: Installation Guide" if not is_ar
              else "المرحلة 5: دليل التركيب")
    if "spot" in results:
        s = results["spot"]
        st.markdown("**🔵 Spot Grid**" if not is_ar else "**🔵 شبكة السبوت**")
        st.info(
            f"- {s['rows']} × {s['cols']} grid\n"
            f"- X step: {s['step_x']*100:.1f} cm | Y step: {s['step_y']*100:.1f} cm\n"
            f"- First row from wall: {s['margin_x']*100:.1f} cm"
            if not is_ar else
            f"- شبكة {s['rows']} × {s['cols']}\n"
            f"- خطوة X: {s['step_x']*100:.1f} سم | خطوة Y: {s['step_y']*100:.1f} سم\n"
            f"- أول صف من الجدار: {s['margin_x']*100:.1f} سم"
        )
    if "profile" in results:
        p = results["profile"]
        st.markdown("**📏 LED Profile**" if not is_ar else "**📏 بروفايل ليد**")
        st.info(
            f"- Model {p['model']} | {p['placement']}\n"
            f"- Length {p['length']:.2f} m → {pieces_to_str(p['pieces'])}"
            if not is_ar else
            f"- موديل {p['model']} | {p['placement']}\n"
            f"- الطول {p['length']:.2f} م → {pieces_to_str(p['pieces'])}"
        )

# ==========================================
# PHASE 6 — DRAWING
# ==========================================
if results:
    st.divider()
    st.header("Phase 6: Layout Drawing" if not is_ar
              else "المرحلة 6: المخطط")

    if is_ar:
        L_ROOM, L_SPOT, L_CH, L_TRACK, L_PROF, L_HID = (
            "الغرفة", "سبوت", "ثريا", "تراك", "بروفايل", "إضاءة مخفية"
        )
        TITLE_TXT = f"مخطط الإنارة ({length}م × {width}م)"
        XLAB, YLAB = "الطول (م)", "العرض (م)"
    else:
        L_ROOM, L_SPOT, L_CH, L_TRACK, L_PROF, L_HID = (
            "Room", "Spot", "Chandelier", "Track", "Profile", "Hidden"
        )
        TITLE_TXT = f"Lighting Layout ({length}m × {width}m)"
        XLAB, YLAB = "Length (m)", "Width (m)"

    fig_h = min(9.0, max(2.5, 7 * safe_div(width, length, 1)))
    fig, ax = plt.subplots(figsize=(7, fig_h))
    ax.plot([0, length, length, 0, 0], [0, 0, width, width, 0],
            color='#2C3E50', linewidth=3, label=L_ROOM)

    if "spot" in results:
        s = results["spot"]
        xc = [s['margin_x'] + s['step_x'] * i for i in range(s['cols'])]
        yc = [s['margin_y'] + s['step_y'] * j for j in range(s['rows'])]
        gx, gy = np.meshgrid(xc, yc)
        ax.scatter(gx.flatten()[:s['qty']], gy.flatten()[:s['qty']],
                   color='#E74C3C', s=120, marker='o', zorder=5, label=L_SPOT)

    if "chandelier" in results:
        ax.scatter([length/2], [width/2], color='#F1C40F', s=600, marker='*',
                   zorder=6, label=L_CH)

    if "track" in results:
        t = results["track"]
        o = 0.4
        lay = t['layout']
        along_x = length >= width
        segs = []
        if lay == "Straight (Center)":
            segs = [([o, length - o], [width / 2] * 2)] if along_x \
                else [([length / 2] * 2, [o, width - o])]
        elif lay == "Parallel (2)":
            segs = [([o, length - o], [width * 0.25] * 2), ([o, length - o], [width * 0.75] * 2)] if along_x \
                else [([length * 0.25] * 2, [o, width - o]), ([length * 0.75] * 2, [o, width - o])]
        elif lay == "L-Shape":
            segs = [([o, length - o], [o, o]), ([o, o], [o, width - o])]
        else:  # U-Shape
            segs = [([o, length - o], [o, o]), ([o, length - o], [width - o, width - o]),
                    ([o, o], [o, width - o])]
        for i, (xs, ys) in enumerate(segs):
            ax.plot(xs, ys, color='#8E44AD', linestyle='--', linewidth=3,
                    label=L_TRACK if i == 0 else None)

    if "profile" in results:
        p = results["profile"]
        off = 0.30
        if p['placement'] == "Perimeter":
            ax.plot([off, length - off, length - off, off, off],
                    [off, off, width - off, width - off, off],
                    color='#27AE60', linestyle='-.', linewidth=2.5, label=L_PROF)
        elif p['placement'] == "Parallel Lines":
            ax.plot([off, length - off], [width * 0.12, width * 0.12],
                    color='#27AE60', linestyle='-.', linewidth=2.5, label=L_PROF)
            ax.plot([off, length - off], [width * 0.88, width * 0.88],
                    color='#27AE60', linestyle='-.', linewidth=2.5)
        else:
            ax.plot([length * 0.15, length * 0.85], [width / 2, width / 2],
                    color='#27AE60', linestyle='-.', linewidth=2.5, label=L_PROF)

    if "hidden" in results:
        ax.fill([0.1, length - 0.1, length - 0.1, 0.1, 0.1],
                [0.1, 0.1, width - 0.1, width - 0.1, 0.1],
                color='#F39C12', alpha=0.15, label=L_HID)

    ax.set_xlim(-0.5, length + 0.5)
    ax.set_ylim(-0.5, width + 0.5)
    ax.set_aspect('equal')
    ax.set_title(TITLE_TXT, fontsize=10)
    ax.set_xlabel(XLAB)
    ax.set_ylabel(YLAB)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18),
              ncol=3, fontsize=8, frameon=False)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# ==========================================
# PHASE 7 — BOQ & EXPORT
# ==========================================
if results:
    st.divider()
    st.header("Phase 7: BOQ & Export" if not is_ar
              else "المرحلة 7: جدول الكميات والتصدير")

    boq_rows = [
        ["Space", f"{building_category} - {room_type}", "", ""],
        ["Dimensions", f"{length}×{width}×{height} m | Area {area:.1f} m²", "", ""],
        ["Work Plane", f"{work_plane} m", "", ""],
        ["Room Index K", f"{room_index_k:.2f}", "", ""],
        ["UF / MF", f"{utilization_factor:.2f} / {maintenance_factor:.2f}", "", ""],
        ["Target / Actual Lux", f"{target_lux} / {actual_lux:.0f} lx", "", ""],
        ["Supply", f"{SUPPLY_V}V / {SUPPLY_HZ}Hz (Jordan)", "", ""],
        ["", "", "", ""],
        ["Item", "Specification", "Quantity", "Load"],
    ]

    if "chandelier" in results:
        c = results["chandelier"]
        ch_boq = CH_STYLE_AR.get(c['ch_type'], c['ch_type']) if is_ar else c['ch_type']
        boq_rows.append([
            "Chandelier",
            f"{ch_boq}, {c['lm']}lm, {c['cct']}K, Ra{c['cri']}, PF {c['pf']:.2f}",
            "1 pc",
            f"{c['watts']:.0f} W"
        ])

    if "spot" in results:
        s = results["spot"]
        boq_rows.append([
            "Spot Light",
            f"{s['lm_each']}lm, {s['beam']}°, {s['cct']}K, Ra{s['cri']}, PF {s['pf']:.2f}, {s['cutout']} cutout",
            f"{s['qty']} pcs ({s['rows']}×{s['cols']})",
            f"{s['watts']:.0f} W"
        ])
    if "track" in results:
        t = results["track"]
        boq_rows.append([
            "Magnetic Track",
            f"{t['lm_m']}lm/m, {t['w_m']}W/m, {t['cct']}K, Ra{t['cri']}, "
            f"{t['beam']}°, PF {t['pf']:.2f}, {t['mount']}, {t['layout']}",
            f"{t['length']:.2f} m",
            f"{t['watts']:.0f} W"
        ])
    if "profile" in results:
        p = results["profile"]
        boq_rows.append([
            "LED Profile",
            f"Model {p['model']}, {p['lm_m']}lm/m, {p['w_m']}W/m, {p['cct']}K, "
            f"Ra{p['cri']}, PF {p['pf']:.2f}, {p['placement']}",
            f"{p['length']:.2f} m ({pieces_to_str(p['pieces'])})",
            f"{p['watts']:.0f} W"
        ])
    if "hidden" in results:
        h = results["hidden"]
        boq_rows.append([
            "Hidden Strip",
            f"{h['w_m']}W/m, {h['lm_m']}lm/m, {h['cct']}K, Ra{h['cri']}, "
            f"PF {h['pf']:.2f}, {h['voltage']}V",
            f"{h['length']:.2f} m",
            f"{h['watts']:.0f} W"
        ])
    boq_rows += [
        ["", "", "", ""],
        ["Connected Load", f"{connected_load:.0f} W", "", ""],
        ["Design Load (+20%)", f"{design_load:.0f} W", "", ""],
        ["System PF (worst)", f"{pf_system:.2f}", "", ""],
        ["Current", f"{current_total:.1f} A @ {SUPPLY_V}V", "", ""],
        ["PSU/Driver", f"{psu_size}", "", ""],
        ["Circuits", f"{num_circuits} × {BREAKER_A}A Type-C", "", ""],
        ["Main Cable", f"{cable_size} mm² Cu (V-drop ≤{CABLE_MAX_DROP}%)", "", ""],
        ["RCD", "30 mA mandatory (IEC 60364-4-41)", "", ""],
    ]

    for row in boq_rows:
        if row[0] and not row[1]:
            st.markdown(f"**{row[0]}**")
        elif row[0]:
            line = f"- **{row[0]}**: {row[1]}"
            if row[2]: line += f" | {row[2]}"
            if row[3]: line += f" | {row[3]}"
            st.markdown(line)

    csv_buf = io.StringIO()
    csv.writer(csv_buf).writerows(boq_rows)

    safe_room = ROOM_EN.get(room_type, safe_filename(room_type))
    st.download_button(
        "📥 Download BOQ (CSV)" if not is_ar else "📥 تحميل جدول الكميات (CSV)",
        data=csv_buf.getvalue().encode('utf-8-sig'),
        file_name=f"lighting_boq_{safe_room}.csv",
        mime="text/csv"
    )
    st.caption(
        "📌 BOQ is preliminary. Verify with photometric study + manufacturer IES files." if not is_ar
        else "📌 الجدول مبدئي. تحقق بدراسة ضوئية وملفات IES من المصنّع."
    )
