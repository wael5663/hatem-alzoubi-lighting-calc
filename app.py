import math
import io
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

st.set_page_config(page_title="Hatem Alzoubi Lighting Design Pro", page_icon="💡", layout="centered")

# ==========================================
# LANGUAGE
# ==========================================
LANG = st.sidebar.selectbox("🌐 Language / اللغة", ["English", "العربية"])
is_ar = (LANG == "العربية")

if is_ar:
    st.markdown("""
        <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .main,
        p, span, div, label, h1, h2, h3, h4, h5, h6 {
            direction: rtl !important; text-align: right !important;
        }
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {
            direction: rtl !important; text-align: right !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# GLOBAL ENGINEERING DEFAULTS (Sidebar)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("⚡ Electrical System / النظام الكهربائي")
SUPPLY_V = st.sidebar.selectbox("Supply Voltage (V):" if not is_ar else "جهد التغذية (V):", [230, 120, 220])
BREAKER_A = st.sidebar.selectbox("Lighting Breaker (A):" if not is_ar else "قاطع الإضاءة (أمبير):", [6, 10, 16])
CIRCUIT_DERATE = st.sidebar.slider("Circuit Derating (%)" if not is_ar else "تخفيض حمل الدائرة (%)", 70, 90, 80, 5)
CABLE_MAX_DROP = st.sidebar.slider("Max Voltage Drop (%)" if not is_ar else "أقصى هبوط جهد (%)", 3, 5, 3, 1)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def uf_from_room_index(K):
    if K < 0.6: return 0.40
    if K < 1.0: return 0.50
    if K < 1.5: return 0.58
    if K < 2.0: return 0.63
    if K < 3.0: return 0.68
    return 0.72

def estimate_uniformity(shr, beam_deg, room_index):
    """Estimate U0 = Emin/Eavg based on SHR (typical manufacturer data)."""
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
    """Empirical UGR estimate based on typical photometric data (CIE 117 principles)."""
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

def voltage_drop(length_m, current_A, cross_section_mm2):
    """V_drop = 2·L·I·ρ/A  (ρ copper ≈ 0.0175 Ω·mm²/m)."""
    rho = 0.0175
    return 2 * length_m * current_A * rho / cross_section_mm2

def recommend_cable_size(current_A, length_m, voltage, max_drop_pct):
    """Minimum cable cross-section based on voltage drop constraint."""
    rho = 0.0175
    A_min = 2 * length_m * current_A * rho / (voltage * max_drop_pct / 100)
    standards = [1.0, 1.5, 2.5, 4.0, 6.0, 10.0, 16.0]
    for s in standards:
        if s >= A_min: return s
    return standards[-1]

def recommend_psu_size(required_w):
    sizes = [60, 100, 150, 200, 300, 400, 600, 1000, 1500]
    for s in sizes:
        if s >= required_w: return s
    return f"{math.ceil(required_w/1000)}× 1000W"

def standard_profile_pieces(total_m, std_len=3.0):
    return math.ceil(total_m / std_len) if total_m > 0 else 0

def safe_div(a, b, default=0):
    return a / b if b != 0 else default

# ==========================================
# PHASE 1: SPACE
# ==========================================
st.title("💡 Hatem Alzoubi Lighting Design Pro" if not is_ar
         else "💡 حاسبة الإنارة الاحترافية – مجموعة حاتم الزعبي")
st.caption("Interior + Electrical + Lighting Engineering Integrated" if not is_ar
           else "هندسة داخلية + كهربائية + إضاءة متكاملة")

st.header("Phase 1: Space & Target" if not is_ar else "المرحلة 1: الفراغ والهدف")

building_category = st.selectbox(
    "Building Category:" if not is_ar else "فئة المبنى:",
    ["Villa", "Office", "Showroom"] if not is_ar else ["فيلا", "مكتب", "معرض تجاري"]
)

if building_category in ["Villa", "فيلا"]:
    room_type = st.selectbox("Room Type:" if not is_ar else "نوع الغرفة:",
        ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Dining Room", "Corridor / Stairs"] if not is_ar
        else ["غرفة معيشة", "غرفة نوم", "مطبخ", "حمام", "غرفة طعام", "ممر / درج"])
    lux_db = {"Living Room": 200, "Bedroom": 150, "Kitchen": 300, "Bathroom": 250,
              "Dining Room": 200, "Corridor / Stairs": 100,
              "غرفة معيشة": 200, "غرفة نوم": 150, "مطبخ": 300, "حمام": 250,
              "غرفة طعام": 200, "ممر / درج": 100}
    ugr_limit = {"Living Room": 22, "Bedroom": 22, "Kitchen": 22, "Bathroom": 25,
                 "Dining Room": 22, "Corridor / Stairs": 25,
                 "غرفة معيشة": 22, "غرفة نوم": 22, "مطبخ": 22, "حمام": 25,
                 "غرفة طعام": 22, "ممر / درج": 25}
    wet_room = room_type in ["Bathroom", "حمام", "Kitchen", "مطبخ"]
elif building_category in ["Office", "مكتب"]:
    room_type = st.selectbox("Room Type:" if not is_ar else "نوع الغرفة:",
        ["General Open Office", "Private Office", "Conference Room", "Reception / Lobby", "Corridor"] if not is_ar
        else ["مكتب مفتوح عام", "مكتب خاص", "غرفة اجتماعات", "الاستقبال / اللوبي", "ممر"])
    lux_db = {"General Open Office": 500, "Private Office": 500, "Conference Room": 400,
              "Reception / Lobby": 300, "Corridor": 150,
              "مكتب مفتوح عام": 500, "مكتب خاص": 500, "غرفة اجتماعات": 400,
              "الاستقبال / اللوبي": 300, "ممر": 150}
    ugr_limit = {"General Open Office": 19, "Private Office": 19, "Conference Room": 19,
                 "Reception / Lobby": 22, "Corridor": 25,
                 "مكتب مفتوح عام": 19, "مكتب خاص": 19, "غرفة اجتماعات": 19,
                 "الاستقبال / اللوبي": 22, "ممر": 25}
    wet_room = False
else:
    room_type = st.selectbox("Room Type:" if not is_ar else "نوع الغرفة:",
        ["General Furniture Exhibition", "Display Window / Feature Zone",
         "Checkout / Cashier Counter", "Storage / Back Office"] if not is_ar
        else ["معرض مفروشات عام", "واجهة العرض / منطقة مميزة",
              "منطقة الكشير / المحاسبة", "المستودع / المكتب الخلفي"])
    lux_db = {"General Furniture Exhibition": 400, "Display Window / Feature Zone": 750,
              "Checkout / Cashier Counter": 500, "Storage / Back Office": 200,
              "معرض مفروشات عام": 400, "واجهة العرض / منطقة مميزة": 750,
              "منطقة الكشير / المحاسبة": 500, "المستودع / المكتب الخلفي": 200}
    ugr_limit = {k: 19 if "Display" in k or "واجهة" in k else 22 for k in lux_db}
    wet_room = False

c1, c2, c3 = st.columns(3)
with c1: length = st.number_input("Length (m):" if not is_ar else "الطول (م):", 0.5, 100.0, 5.0, 0.1)
with c2: width  = st.number_input("Width (m):" if not is_ar else "العرض (م):",  0.5, 100.0, 4.0, 0.1)
with c3: height = st.number_input("Ceiling Height (m):" if not is_ar else "ارتفاع السقف (م):", 2.0, 20.0, 3.0, 0.1)

work_plane = st.number_input("Work Plane Height (m):" if not is_ar else "ارتفاع مستوى العمل (م):",
                             0.0, 1.5, 0.80, 0.05)
maintenance_factor = st.slider("Maintenance Factor (MF):" if not is_ar else "معامل الصيانة (MF):",
                               0.50, 1.00, 0.80, 0.05,
                               help="0.80 clean, 0.70 dusty, 0.65 industrial" if not is_ar
                               else "0.80 نظيف، 0.70 مغبر، 0.65 صناعي")

area = length * width
target_lux = lux_db[room_type]
target_ugr = ugr_limit[room_type]

hm = max(0.5, height - work_plane)
room_index_k = safe_div(area, hm * (length + width))
uf_auto = uf_from_room_index(room_index_k)
utilization_factor = st.slider("Utilization Factor (UF):" if not is_ar else "معامل الاستفادة (UF):",
                               0.30, 0.85, round(uf_auto, 2), 0.01,
                               help=f"Auto from K={room_index_k:.2f}" if not is_ar
                               else f"تلقائي من K={room_index_k:.2f}")

total_lumens_req = area * target_lux / (utilization_factor * maintenance_factor)

mc1, mc2, mc3, mc4, mc5 = st.columns(5)
mc1.metric("Area" if not is_ar else "المساحة", f"{area:.1f} m²")
mc2.metric("Room Index K" if not is_ar else "مؤشر الغرفة K", f"{room_index_k:.2f}")
mc3.metric("Auto UF" if not is_ar else "UF تلقائي", f"{uf_auto:.2f}")
mc4.metric("Target Lux" if not is_ar else "اللوكس المطلوب", f"{target_lux} lx")
mc5.metric("Required Lumens" if not is_ar else "اللومن المطلوب", f"{total_lumens_req:,.0f} lm")

st.divider()

# ==========================================
# PHASE 2: FIXTURES
# ==========================================
st.header("Phase 2: Lighting Fixtures" if not is_ar else "المرحلة 2: وحدات الإضاءة")

FX = {"spot": "Spot Light", "track": "Magnetic Track", "profile": "LED Profile", "hidden": "Hidden Light"}
FX_AR = {"spot": "سبوت لايت", "track": "تراك مغناطيسي", "profile": "بروفايل ليد", "hidden": "إضاءة مخفية"}
fx_label = lambda k: FX[k] if not is_ar else FX_AR[k]

sel_keys = st.multiselect(
    "Select fixture types:" if not is_ar else "اختر أنواع الوحدات:",
    options=list(FX.keys()),
    format_func=fx_label,
    default=["spot"]
)

# Results containers
results = {}
total_watts = 0.0
total_lumens = 0.0

CCT_OPTIONS = {"2700K (Warm)": 2700, "3000K (Warm White)": 3000,
               "4000K (Neutral)": 4000, "5000K (Cool)": 5000, "6500K (Daylight)": 6500}
CRI_OPTIONS = {"Ra ≥ 80 (Standard)": 80, "Ra ≥ 90 (High)": 90, "Ra ≥ 95 (Premium)": 95}
BEAM_OPTIONS = {"15° (Narrow Spot)": 15, "24° (Spot)": 24,
                "36° (Medium Flood)": 36, "60° (Wide Flood)": 60, "90° (Very Wide)": 90}

if not sel_keys:
    st.warning("⚠️ Select at least one fixture type." if not is_ar
               else "⚠️ اختر نوعًا واحدًا على الأقل.")
else:
    lumens_target_per_type = total_lumens_req / len(sel_keys)

    for fx in sel_keys:
        with st.expander(f"⚙️ {fx_label(fx)}", expanded=True):
            fc1, fc2 = st.columns(2)

            # Common optical fields
            with fc1:
                cct_label = st.selectbox("Color Temperature:" if not is_ar else "درجة حرارة اللون:",
                                          list(CCT_OPTIONS.keys()), key=f"{fx}_cct")
                cri_label = st.selectbox("Color Rendering (CRI):" if not is_ar else "تجسيد اللون (CRI):",
                                          list(CRI_OPTIONS.keys()), key=f"{fx}_cri")
                beam_label = st.selectbox("Beam Angle:" if not is_ar else "زاوية الشعاع:",
                                           list(BEAM_OPTIONS.keys()), key=f"{fx}_beam")
                beam_deg = BEAM_OPTIONS[beam_label]

            # ----------------------- SPOT -----------------------
            if fx == "spot":
                with fc2:
                    cutout = st.selectbox("Cutout Size:" if not is_ar else "مقاس الفتحة:",
                                           ["7 cm", "7.5 cm", "9 cm", "10 cm", "12 cm"],
                                           key="spot_cutout")
                    lm_each = st.number_input("Lumens per Spot (lm):" if not is_ar else "اللومن/سبوت:",
                                               50, 3000, 550, 25, key="spot_lm")
                    w_each = st.number_input("Power per Spot (W):" if not is_ar else "القدرة/سبوت (واط):",
                                              1.0, 50.0, 7.0, 0.5, key="spot_w")
                    recessed = st.checkbox("Recessed mounting" if not is_ar else "تركيب مدمج",
                                            value=True, key="spot_recessed")

                raw_qty = max(1, math.ceil(lumens_target_per_type / lm_each))
                max_dim = max(4, int(math.ceil(math.sqrt(raw_qty))) + 3)
                room_ar = length / width
                best = (raw_qty, 1, raw_qty, float('inf'))
                for r in range(1, max_dim + 1):
                    for c in range(1, max_dim + 1):
                        tg = r * c
                        if tg >= raw_qty:
                            score = abs((c / r) - room_ar) * 1.5 + (tg - raw_qty) * 0.4
                            if score < best[3]:
                                best = (tg, r, c, score)

                qty, rows, cols = best[0], best[1], best[2]
                delivered_lm = qty * lm_each
                watts = qty * w_each

                # SHR check (mounting height above work plane)
                margin = 0.65 if len(sel_keys) == 1 else 1.0
                eff_len = max(0.1, length - 2 * margin)
                eff_wid = max(0.1, width - 2 * margin)
                step_x = eff_len / (cols + 1)
                step_y = eff_wid / (rows + 1)
                shr_x = step_x / hm
                shr_y = step_y / hm
                shr = max(shr_x, shr_y)

                u0 = estimate_uniformity(shr, beam_deg, room_index_k)
                ugr = estimate_ugr(beam_deg, lm_each, room_index_k, recessed)

                results["spot"] = dict(
                    qty=qty, rows=rows, cols=cols, lm=delivered_lm, watts=watts,
                    lm_each=lm_each, w_each=w_each, shr=shr, u0=u0, ugr=ugr,
                    beam=beam_deg, cct=CCT_OPTIONS[cct_label], cri=CRI_OPTIONS[cri_label],
                    margin=margin, step_x=step_x, step_y=step_y
                )
                total_watts += watts
                total_lumens += delivered_lm

                st.info(f"📐 **{qty} spots** in **{rows}×{cols}** grid | "
                        f"SHR = {shr:.2f} | U₀ ≈ {u0:.2f} | UGR ≈ {ugr}" if not is_ar
                        else f"📐 **{qty} سبوت** بشبكة **{rows}×{cols}** | "
                        f"SHR = {shr:.2f} | U₀ ≈ {u0:.2f} | UGR ≈ {ugr}")

            # ----------------------- TRACK -----------------------
            elif fx == "track":
                with fc2:
                    mount = st.selectbox("Mounting:" if not is_ar else "التركيب:",
                                          ["Recessed", "Surface", "Suspended"], key="track_mount")
                    track_lm_m = st.number_input("Track lm/m:" if not is_ar else "لومن/م للتراك:",
                                                   200, 3000, 1200, 100, key="track_lm")
                    track_w_m = st.number_input("Track W/m:" if not is_ar else "واط/م للتراك:",
                                                  3.0, 60.0, 15.0, 1.0, key="track_w")
                    layout = st.selectbox("Layout:" if not is_ar else "التخطيط:",
                                            ["Straight (Center)", "Parallel (2 runs)", "L-Shape", "U-Shape"],
                                            key="track_layout")

                if layout == "Straight (Center)":   geom = max(length, width)
                elif layout == "Parallel (2 runs)": geom = 2 * max(length, width)
                elif layout == "L-Shape":            geom = length + width
                else:                                geom = 2 * length + width

                delivered_lm = geom * track_lm_m
                watts = geom * track_w_m
                results["track"] = dict(length=geom, lm=delivered_lm, watts=watts,
                                         lm_m=track_lm_m, w_m=track_w_m, layout=layout)
                total_watts += watts
                total_lumens += delivered_lm

                st.info(f"📐 Track: **{geom:.2f} m** | {delivered_lm:,.0f} lm | {watts:.0f} W"
                        if not is_ar else f"📐 تراك: **{geom:.2f} م** | {delivered_lm:,.0f} lm | {watts:.0f} واط")

            # ----------------------- PROFILE -----------------------
            elif fx == "profile":
                with fc2:
                    model = st.selectbox("Profile Model:" if not is_ar else "موديل البروفايل:",
                                          ["508", "617", "619", "2010A", "3010", "2320A",
                                           "509", "601", "5012A", "618", "506", "1509", "5313"],
                                          key="profile_model")
                    prof_lm_m = st.number_input("Profile lm/m:" if not is_ar else "لومن/م للبروفايل:",
                                                  50, 2500, 150, 25, key="prof_lm")
                    prof_w_m = st.number_input("Profile W/m:" if not is_ar else "واط/م للبروفايل:",
                                                 3.0, 40.0, 12.0, 1.0, key="prof_w")
                    placement = st.selectbox("Placement:" if not is_ar else "التوزيع:",
                                              ["Perimeter", "Parallel Lines", "Center Axis"],
                                              key="prof_place")

                off = 0.30
                if placement == "Perimeter":
                    geom = 2 * ((length - 2 * off) + (width - 2 * off))
                elif placement == "Parallel Lines":
                    geom = 2 * max(length, width)
                else:
                    geom = max(length, width)

                delivered_lm = geom * prof_lm_m
                watts = geom * prof_w_m
                pieces = standard_profile_pieces(geom, 3.0)
                results["profile"] = dict(length=geom, lm=delivered_lm, watts=watts,
                                           lm_m=prof_lm_m, w_m=prof_w_m, pieces=pieces,
                                           model=model, placement=placement)
                total_watts += watts
                total_lumens += delivered_lm

                st.info(f"📐 Profile: **{geom:.2f} m** ({pieces}×3m) | {delivered_lm:,.0f} lm | {watts:.0f} W"
                        if not is_ar else f"📐 بروفايل: **{geom:.2f} م** ({pieces}×3م) | {delivered_lm:,.0f} lm | {watts:.0f} واط")

            # ----------------------- HIDDEN -----------------------
            elif fx == "hidden":
                with fc2:
                    tier = st.selectbox("Strip Power Tier:" if not is_ar else "فئة الشريط:",
                                         ["9.6 W/m", "14.4 W/m", "18 W/m"], key="hid_watt")
                    w_m = float(tier.split()[0])
                    hid_lm_m = st.number_input("Strip lm/m:" if not is_ar else "لومن/م للشريط:",
                                                200, 3000, 1100, 100, key="hid_lm")
                    sides = st.multiselect("Sides covered:" if not is_ar else "الجوانب المغطاة:",
                                            ["Side A (L)", "Side B (L)", "Side C (W)", "Side D (W)"],
                                            default=["Side A (L)", "Side B (L)", "Side C (W)", "Side D (W)"],
                                            key="hid_sides")
                    strip_v = st.selectbox("Strip Voltage:" if not is_ar else "جهد الشريط (V):",
                                            [24, 48], key="hid_v")

                if not sides:
                    st.error("⚠️ Select at least one side." if not is_ar else "⚠️ اختر جانبًا واحدًا على الأقل.")
                    continue

                geom = sum(length if "L" in s else width for s in sides)
                delivered_lm = geom * hid_lm_m
                watts = geom * w_m
                results["hidden"] = dict(length=geom, lm=delivered_lm, watts=watts,
                                          lm_m=hid_lm_m, w_m=w_m, voltage=strip_v)
                total_watts += watts
                total_lumens += delivered_lm

                st.info(f"📐 Hidden: **{geom:.2f} m** | {delivered_lm:,.0f} lm | {watts:.0f} W @ {strip_v}V"
                        if not is_ar else f"📐 مخفي: **{geom:.2f} م** | {delivered_lm:,.0f} lm | {watts:.0f} واط @ {strip_v}V")

# ==========================================
# PHASE 3: LIGHTING ENGINEERING VERIFICATION
# ==========================================
if results:
    st.divider()
    st.header("Phase 3: Lighting Engineering Verification" if not is_ar
              else "المرحلة 3: التحقق الهندسي للإضاءة")

    actual_lux = total_lumens * utilization_factor * maintenance_factor / area if area > 0 else 0
    lux_delta = actual_lux - target_lux

    v1, v2, v3, v4 = st.columns(4)
    v1.metric("Required lm" if not is_ar else "اللومن المطلوب", f"{total_lumens_req:,.0f} lm")
    v2.metric("Delivered lm" if not is_ar else "اللومن المزود", f"{total_lumens:,.0f} lm")
    v3.metric("Actual Lux" if not is_ar else "اللوكس الفعلي",
              f"{actual_lux:.0f} lx", delta=f"{lux_delta:+.0f} lx")
    v4.metric("Total Load" if not is_ar else "الحمل الكلي", f"{total_watts:.0f} W")

    # Compliance check
    if actual_lux >= target_lux * 1.05:
        st.success(f"✅ Meets target ({actual_lux:.0f} / {target_lux} lx)" if not is_ar
                   else f"✅ يحقق الهدف ({actual_lux:.0f} / {target_lux} lx)")
    elif actual_lux >= target_lux * 0.90:
        st.warning(f"⚠️ Slightly under target ({actual_lux:.0f} / {target_lux} lx)" if not is_ar
                   else f"⚠️ أقل قليلًا ({actual_lux:.0f} / {target_lux} lx)")
    else:
        st.error(f"❌ Under-lit ({actual_lux:.0f} / {target_lux} lx)" if not is_ar
                 else f"❌ إضاءة غير كافية ({actual_lux:.0f} / {target_lux} lx)")

    # Per-fixture engineering metrics
    if "spot" in results:
        s = results["spot"]
        st.subheader("🔍 Spot Fixture Analysis" if not is_ar else "🔍 تحليل السبوت")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("SHR (max)" if not is_ar else "SHR (أقصى)", f"{s['shr']:.2f}")
        m2.metric("Uniformity U₀" if not is_ar else "الانتظام U₀", f"{s['u0']:.2f}")
        m3.metric("UGR Estimate" if not is_ar else "تقدير الوهج UGR", f"{s['ugr']}")
        m4.metric("Beam Angle" if not is_ar else "زاوية الشعاع", f"{s['beam']}°")

        if s['ugr'] > target_ugr:
            st.error(f"❌ UGR {s['ugr']} exceeds standard limit {target_ugr}. "
                     f"Try narrower beam or lower lumens/fixture." if not is_ar
                     else f"❌ UGR {s['ugr']} يتجاوز الحد {target_ugr}. "
                     f"جرّب زاوية أضيق أو لومن أقل.")
        else:
            st.success(f"✅ UGR {s['ugr']} within limit {target_ugr}" if not is_ar
                       else f"✅ UGR {s['ugr']} ضمن الحد {target_ugr}")

        if s['u0'] < 0.60:
            st.warning(f"⚠️ Uniformity {s['u0']:.2f} < 0.60 (EN 12464-1 recommendation). "
                       f"Consider reducing spacing or raising quantity." if not is_ar
                       else f"⚠️ الانتظام {s['u0']:.2f} < 0.60 (توصية EN 12464-1). "
                       f"فكّر بتقليل التباعد أو زيادة الكمية.")

    # Lighting engineering disclaimer
    st.caption("📌 Results use lumen method. For final design, verify with DIALux/Relux "
               "photometric simulation." if not is_ar
               else "📌 النتائج بطريقة اللومن. للتصميم النهائي، تحقق بمحاكاة DIALux/Relux.")

# ==========================================
# PHASE 4: ELECTRICAL ENGINEERING
# ==========================================
if results:
    st.divider()
    st.header("Phase 4: Electrical Engineering" if not is_ar
              else "المرحلة 4: الهندسة الكهربائية")

    # Load summary
    connected_load = total_watts
    design_load = connected_load * 1.20  # 20% headroom for drivers/PSU
    psu_required = design_load
    recommended_psu = recommend_psu_size(psu_required)

    e1, e2, e3 = st.columns(3)
    e1.metric("Connected Load" if not is_ar else "الحمل الموصول", f"{connected_load:.0f} W")
    e2.metric("Design Load (+20%)" if not is_ar else "حمل التصميم (+20%)", f"{design_load:.0f} W")
    e3.metric("Recommended PSU" if not is_ar else "PSU المقترح",
              f"{recommended_psu} W" if isinstance(recommended_psu, int) else recommended_psu)

    # Circuit sizing
    st.subheader("🔌 Circuit & Protection" if not is_ar else "🔌 الدوائر والحماية")
    max_circuit_w = BREAKER_A * SUPPLY_V * CIRCUIT_DERATE / 100
    num_circuits = max(1, math.ceil(connected_load / max_circuit_w))
    circuit_load = connected_load / num_circuits
    circuit_current = circuit_load / SUPPLY_V

    cc1, cc2, cc3 = st.columns(3)
    cc1.metric("Max Load/Circuit" if not is_ar else "أقصى حمل/دائرة", f"{max_circuit_w:.0f} W")
    cc2.metric("Circuits Required" if not is_ar else "عدد الدوائر", f"{num_circuits}")
    cc3.metric("Current/Circuit" if not is_ar else "التيار/دائرة", f"{circuit_current:.1f} A")

    # Cable sizing (main feed to first junction)
    main_run_est = max(length, width)  # rough estimate
    recommended_cable = recommend_cable_size(
        connected_load / SUPPLY_V, main_run_est, SUPPLY_V, CABLE_MAX_DROP
    )
    st.info(f"📏 Estimated main cable: **{recommended_cable} mm²** "
            f"(for ~{main_run_est:.1f} m run at {SUPPLY_V}V)" if not is_ar
            else f"📏 الكابل الرئيسي المقدر: **{recommended_cable} mm²** "
            f"(لمسار ~{main_run_est:.1f} م عند {SUPPLY_V}V)")

    # Voltage drop for LED runs
    if "hidden" in results:
        h = results["hidden"]
        strip_v = h["voltage"]
        strip_current = h["watts"] / strip_v
        max_led_run = h["length"]
        # Assume 1.5 mm² for strip feed, check drop
        for cross in [1.5, 2.5, 4.0]:
            vd = voltage_drop(max_led_run, strip_current, cross)
            pct = vd / strip_v * 100
            if pct <= CABLE_MAX_DROP:
                st.info(f"🔋 LED Strip ({strip_v}V): {strip_current:.1f} A, "
                        f"run {max_led_run:.1f} m → **{cross} mm²** cable, "
                        f"V-drop {pct:.1f}%" if not is_ar
                        else f"🔋 شريط LED ({strip_v}V): {strip_current:.1f} أمبير، "
                        f"مسار {max_led_run:.1f} م → كابل **{cross} mm²**، "
                        f"هبوط {pct:.1f}%")
                break
        else:
            st.warning(f"⚠️ LED strip run is too long for {strip_v}V. "
                       f"Split run or use 48V system." if not is_ar
                       else f"⚠️ مسار الشريط طويل جدًا لجهد {strip_v}V. "
                       f"قسّم المسار أو استخدم 48V.")

    # IP rating note
    if wet_room:
        st.warning("💧 Wet zone detected — use IP44+ fixtures and 30mA RCD protection." if not is_ar
                   else "💧 منطقة رطبة — استخدم وحدات IP44+ وحماية RCD 30mA.")

    # Dimming / scene control
    st.subheader("🎛️ Control & Dimming" if not is_ar else "🎛️ التحكم والتعتيم")
    dimming_recommendation = {
        "Living Room": "DALI or 0-10V dimming (multiple scenes)",
        "Bedroom": "TRIAC or 0-10V dimming (warm dim to 1800K)",
        "Kitchen": "0-10V or DALI (task + ambient scenes)",
        "Dining Room": "DALI (dimmer scenes for dining)",
        "Conference Room": "DALI (preset scenes + occupancy)",
        "General Open Office": "DALI with daylight harvesting",
        "غرفة معيشة": "DALI أو 0-10V (مشاهد متعددة)",
        "غرفة نوم": "TRIAC أو 0-10V (تعتيم دافئ حتى 1800K)",
        "مطبخ": "0-10V أو DALI (مشاهد مهام + محيط)",
        "غرفة طعام": "DALI (مشاهد تعتيم للطعام)",
        "غرفة اجتماعات": "DALI (مشاهد جاهزة + حساس حضور)",
        "مكتب مفتوح عام": "DALI مع استغلال ضوء النهار",
    }
    dim_rec = dimming_recommendation.get(room_type, "0-10V basic dimming")
    st.info(f"🎛️ Recommended control: **{dim_rec}**" if not is_ar
            else f"🎛️ التحكم الموصى به: **{dim_rec}**")

# ==========================================
# PHASE 5: LAYOUT GUIDE
# ==========================================
if results:
    st.divider()
    st.header("Phase 5: Installation Layout" if not is_ar else "المرحلة 5: تخطيط التركيب")

    if "spot" in results:
        s = results["spot"]
        st.subheader("🔵 Spot Grid" if not is_ar else "🔵 شبكة السبوت")
        st.info(
            f"- Grid: **{s['rows']} × {s['cols']}**\n"
            f"- X step: **{s['step_x']*100:.1f} cm** | Y step: **{s['step_y']*100:.1f} cm**\n"
            f"- First row from wall: **{(s['margin']+s['step_x'])*100:.1f} cm**"
            if not is_ar else
            f"- الشبكة: **{s['rows']} × {s['cols']}**\n"
            f"- خطوة X: **{s['step_x']*100:.1f} سم** | خطوة Y: **{s['step_y']*100:.1f} سم**\n"
            f"- أول صف من الجدار: **{(s['margin']+s['step_x'])*100:.1f} سم**"
        )

    if "profile" in results:
        p = results["profile"]
        st.subheader("📏 LED Profile" if not is_ar else "📏 بروفايل ليد")
        st.info(f"- Model: **{p['model']}** | Placement: **{p['placement']}**\n"
                f"- Length: **{p['length']:.2f} m** ({p['pieces']} × 3m pieces)"
                if not is_ar else
                f"- الموديل: **{p['model']}** | التوزيع: **{p['placement']}**\n"
                f"- الطول: **{p['length']:.2f} م** ({p['pieces']} × 3م)")

# ==========================================
# PHASE 6: DRAWING
# ==========================================
if results:
    st.divider()
    st.header("Phase 6: Layout Drawing" if not is_ar else "المرحلة 6: المخطط المرئي")

    fig_h = max(2.5, 7 * safe_div(width, length, 1))
    fig, ax = plt.subplots(figsize=(7, fig_h))

    ax.plot([0, length, length, 0, 0], [0, 0, width, width, 0],
            color='#2C3E50', linewidth=3, label='Room')

    if "spot" in results:
        s = results["spot"]
        xc = [s['margin'] + s['step_x'] * (i + 1) for i in range(s['cols'])]
        yc = [s['margin'] + s['step_y'] * (j + 1) for j in range(s['rows'])]
        gx, gy = np.meshgrid(xc, yc)
        ax.scatter(gx.flatten()[:s['qty']], gy.flatten()[:s['qty']],
                   color='#E74C3C', s=120, marker='o', zorder=5, label='Spot')

    if "track" in results:
        t = results["track"]
        ax.plot([0.4, length - 0.4], [0.4, 0.4], color='#8E44AD',
                linestyle='--', linewidth=3, label='Track')
        ax.plot([0.4, length - 0.4], [width - 0.4, width - 0.4],
                color='#8E44AD', linestyle='--', linewidth=3)

    if "profile" in results:
        p = results["profile"]
        off = 0.30
        if p['placement'] == "Perimeter":
            ax.plot([off, length - off, length - off, off, off],
                    [off, off, width - off, width - off, off],
                    color='#27AE60', linestyle='-.', linewidth=2.5, label='Profile')
        elif p['placement'] == "Parallel Lines":
            ax.plot([off, length - off], [width * 0.12, width * 0.12],
                    color='#27AE60', linestyle='-.', linewidth=2.5, label='Profile')
            ax.plot([off, length - off], [width * 0.88, width * 0.88],
                    color='#27AE60', linestyle='-.', linewidth=2.5)
        else:
            ax.plot([length * 0.15, length * 0.85], [width / 2, width / 2],
                    color='#27AE60', linestyle='-.', linewidth=2.5, label='Profile')

    if "hidden" in results:
        ax.fill([0.1, length - 0.1, length - 0.1, 0.1, 0.1],
                [0.1, 0.1, width - 0.1, width - 0.1, 0.1],
                color='#F39C12', alpha=0.15, label='Hidden Light')

    ax.set_xlim(-0.5, length + 0.5)
    ax.set_ylim(-0.5, width + 0.5)
    ax.set_aspect('equal')
    ax.set_title(f"Lighting Layout ({length}m × {width}m)", fontsize=12, fontweight='bold')
    ax.set_xlabel("Length (m)")
    ax.set_ylabel("Width (m)")
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.28), ncol=4, fontsize=8)

    st.pyplot(fig)
    plt.close(fig)

# ==========================================
# PHASE 7: BOQ & EXPORT
# ==========================================
if results:
    st.divider()
    st.header("Phase 7: BOQ & Export" if not is_ar else "المرحلة 7: جدول الكميات والتصدير")

    boq_rows = []
    boq_rows.append(["Space", f"{building_category} - {room_type}", "", ""])
    boq_rows.append(["Dimensions", f"{length}m × {width}m × {height}m", "", ""])
    boq_rows.append(["Room Index K", f"{room_index_k:.2f}", "", ""])
    boq_rows.append(["UF / MF", f"{utilization_factor:.2f} / {maintenance_factor:.2f}", "", ""])
    boq_rows.append(["Target / Actual Lux", f"{target_lux} / {actual_lux:.0f} lx", "", ""])
    boq_rows.append(["", "", "", ""])
    boq_rows.append(["Item", "Specification", "Quantity", "Load"])

    if "spot" in results:
        s = results["spot"]
        boq_rows.append(["Spot Light", f"{s['lm_each']}lm, {s['beam']}°, {s['cct']}K, Ra{s['cri']}",
                         f"{s['qty']} pcs", f"{s['watts']:.0f} W"])
    if "track" in results:
        t = results["track"]
        boq_rows.append(["Magnetic Track", f"{t['lm_m']}lm/m, {t['layout']}",
                         f"{t['length']:.2f} m", f"{t['watts']:.0f} W"])
    if "profile" in results:
        p = results["profile"]
        boq_rows.append(["LED Profile", f"{p['model']} {p['lm_m']}lm/m, {p['placement']}",
                         f"{p['length']:.2f} m ({p['pieces']}×3m)", f"{p['watts']:.0f} W"])
    if "hidden" in results:
        h = results["hidden"]
        boq_rows.append(["Hidden Strip", f"{h['w_m']}W/m, {h['voltage']}V",
                         f"{h['length']:.2f} m", f"{h['watts']:.0f} W"])

    boq_rows.append(["", "", "", ""])
    boq_rows.append(["Connected Load", f"{connected_load:.0f} W", "", ""])
    boq_rows.append(["Design Load (+20%)", f"{design_load:.0f} W", "", ""])
    boq_rows.append(["PSU Recommendation", f"{recommended_psu} W", "", ""])
    boq_rows.append(["Circuits", f"{num_circuits} × {BREAKER_A}A @ {SUPPLY_V}V", "", ""])

    # Display BOQ table
    for row in boq_rows:
        if row[0] and not row[1]:
            st.markdown(f"**{row[0]}**")
        elif row[0]:
            st.markdown(f"- **{row[0]}**: {row[1]} | {row[2]} {('| ' + row[3]) if row[3] else ''}")

    # CSV Export
    csv_buf = io.StringIO()
    writer = csv.writer(csv_buf)
    writer.writerows(boq_rows)
    st.download_button(
        "📥 Download BOQ (CSV)" if not is_ar else "📥 تحميل جدول الكميات (CSV)",
        data=csv_buf.getvalue().encode('utf-8-sig'),
        file_name=f"lighting_boq_{room_type.replace(' ', '_')}.csv",
        mime="text/csv"
    )

    st.caption("📌 BOQ for preliminary procurement. Verify with final photometric study." if not is_ar
               else "📌 جدول الكميات للتوريد المبدئي. تحقق بدراسة ضوئية نهائية.")
