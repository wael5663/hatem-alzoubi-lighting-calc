import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

st.set_page_config(page_title="Hatem Alzoubi Lighting Design", page_icon="💡", layout="centered")

# ==========================================
# LANGUAGE
# ==========================================
LANG = st.sidebar.selectbox("🌐 Select Language / اختر اللغة", ["English", "العربية"])
is_ar = (LANG == "العربية")

if is_ar:
    st.markdown("""
        <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .main, p, span, div, label, h1, h2, h3, h4, h5, h6 {
            direction: rtl !important; text-align: right !important;
        }
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {
            direction: rtl !important; text-align: right !important;
        }
        </style>
    """, unsafe_allow_html=True)

t = {
    "title": "💡 Hatem Alzoubi Lighting Design & Lumen Calculator by Engineer Wael" if not is_ar else "💡 مجموعة حاتم الزعبي للإنارة - حاسبة الإنارة - مهندس وائل",
    "subtitle": "Professional engineering calculator: Automatic fixture sizing, layout distribution, and visual drawing." if not is_ar else "حاسبة هندسية احترافية: تحجيم الوحدات التلقائي، وتوزيع التخطيط، والرسم المرئي.",
    "p1_header": "Phase 1: Space, Dimensions & Target Requirements" if not is_ar else "المرحلة الأولى: المساحة، الأبعاد، ومتطلبات الإضاءة",
    "b_cat": "1. Choose the building category:" if not is_ar else "1. اختر فئة المبنى:",
    "r_type": "2. Choose room type:" if not is_ar else "2. اختر نوع الغرفة:",
    "length": "Length (m):" if not is_ar else "الطول (م):",
    "width": "Width (m):" if not is_ar else "العرض (م):",
    "height": "Ceiling Height (m):" if not is_ar else "ارتفاع السقف (م):",
    "mf": "Maintenance Factor (MF):" if not is_ar else "معامل الصيانة (MF):",
    "mf_help": "0.80 for clean indoor, 0.70 for dusty, 0.65 for industrial." if not is_ar else "0.80 لبيئة نظيفة، 0.70 لبيئة مغبرة، 0.65 لبيئة صناعية.",
    "uf": "Utilization Factor (UF) — auto from room index, adjustable:" if not is_ar else "معامل الاستفادة (UF) — يُحسب تلقائيًا من مؤشر الغرفة، قابل للتعديل:",
    "uf_help": "Fraction of lumens reaching the work plane. Typical 0.4–0.75 depending on room geometry and reflectances." if not is_ar else "نسبة اللومن الواصلة لمستوى العمل. عادة 0.4–0.75 حسب هندسة الغرفة والانعكاسات.",
    "p2_header": "Phase 2: Lighting Types & Layout Design" if not is_ar else "المرحلة الثانية: أنواع الإضاءة وتصميم التخطيط",
    "select_fix": "Select lighting types:" if not is_ar else "اختر أنواع الإضاءة:",
    "p3_header": "Phase 3: Engineering Verification & Quantities" if not is_ar else "المرحلة الثالثة: التحقق الهندسي والكميات",
    "p4_header": "Phase 4: Installation Layout & Spacing Guide" if not is_ar else "المرحلة الرابعة: تخطيط التركيب ودليل المسافات",
    "p5_header": "Phase 5: Visual Layout & Specification Report" if not is_ar else "المرحلة الخامسة: المخطط المرئي وتقرير المواصفات",
}

st.title(t["title"])
st.write(t["subtitle"])

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def uf_from_room_index(K):
    """Approx UF from room index (typical 70/50/20 reflectances, 60° beam)."""
    if K < 0.6:   return 0.40
    if K < 1.0:   return 0.50
    if K < 1.5:   return 0.58
    if K < 2.0:   return 0.63
    if K < 3.0:   return 0.68
    return 0.72

def standard_profile_pieces(total_m, std_len=3.0):
    """Number of standard-length profile pieces to cover total_m."""
    if total_m <= 0: return 0
    return math.ceil(total_m / std_len)

def next_psu_size(required_w):
    sizes = [60, 100, 150, 200, 300, 400, 600, 1000, 1500]
    for s in sizes:
        if s >= required_w:
            return s
    return "Multiple PSUs"

# ==========================================
# PHASE 1
# ==========================================
st.header(t["p1_header"])

building_category = st.selectbox(
    t["b_cat"],
    ["Villa", "Office", "Showroom"] if not is_ar else ["فيلا", "مكتب", "معرض تجاري"]
)

if building_category in ["Villa", "فيلا"]:
    room_type = st.selectbox(t["r_type"],
        ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Dining Room", "Corridor / Stairs"] if not is_ar
        else ["غرفة معيشة", "غرفة نوم", "مطبخ", "حمام", "غرفة طعام", "ممر / درج"])
    lux_standards = {
        "Living Room": 200, "Bedroom": 150, "Kitchen": 300, "Bathroom": 250, "Dining Room": 200, "Corridor / Stairs": 100,
        "غرفة معيشة": 200, "غرفة نوم": 150, "مطبخ": 300, "حمام": 250, "غرفة طعام": 200, "ممر / درج": 100,
    }
elif building_category in ["Office", "مكتب"]:
    room_type = st.selectbox(t["r_type"],
        ["General Open Office", "Private Office", "Conference Room", "Reception / Lobby", "Corridor"] if not is_ar
        else ["مكتب مفتوح عام", "مكتب خاص", "غرفة اجتماعات", "الاستقبال / اللوبي", "ممر"])
    lux_standards = {
        "General Open Office": 500, "Private Office": 500, "Conference Room": 400, "Reception / Lobby": 300, "Corridor": 150,
        "مكتب مفتوح عام": 500, "مكتب خاص": 500, "غرفة اجتماعات": 400, "الاستقبال / اللوبي": 300, "ممر": 150,
    }
else:
    room_type = st.selectbox(t["r_type"],
        ["General Furniture Exhibition", "Display Window / Feature Zone", "Checkout / Cashier Counter", "Storage / Back Office"] if not is_ar
        else ["معرض مفروشات عام", "واجهة العرض / منطقة مميزة", "منطقة الكشير / المحاسبة", "المستودع / المكتب الخلفي"])
    lux_standards = {
        "General Furniture Exhibition": 400, "Display Window / Feature Zone": 750, "Checkout / Cashier Counter": 500, "Storage / Back Office": 200,
        "معرض مفروشات عام": 400, "واجهة العرض / منطقة مميزة": 750, "منطقة الكشير / المحاسبة": 500, "المستودع / المكتب الخلفي": 200,
    }

col1, col2, col3 = st.columns(3)
with col1: length = st.number_input(t["length"], 0.5, 100.0, 5.0, 0.1)
with col2: width  = st.number_input(t["width"],  0.5, 100.0, 4.0, 0.1)
with col3: height = st.number_input(t["height"], 2.0, 20.0,  3.0, 0.1)

maintenance_factor = st.slider(t["mf"], 0.50, 1.00, 0.80, 0.05, help=t["mf_help"])

# Room Index → auto UF
area = length * width
target_lux = lux_standards[room_type]
work_plane_h = 0.80
hm = max(0.5, height - work_plane_h)
room_index_k = area / (hm * (length + width))
uf_auto = uf_from_room_index(room_index_k)

utilization_factor = st.slider(t["uf"], 0.30, 0.85, round(uf_auto, 2), 0.01, help=t["uf_help"])

total_lumens_required = (area * target_lux) / (utilization_factor * maintenance_factor)

m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
m_col1.metric("Room Area" if not is_ar else "المساحة", f"{area:.2f} m²")
m_col2.metric("Room Index K" if not is_ar else "مؤشر الغرفة K", f"{room_index_k:.2f}")
m_col3.metric("Auto UF" if not is_ar else "UF تلقائي", f"{uf_auto:.2f}")
m_col4.metric("Target Lux" if not is_ar else "الإضاءة المطلوبة", f"{target_lux} lx")
m_col5.metric("Required Lumens" if not is_ar else "اللومن المطلوب", f"{total_lumens_required:,.0f} lm")

st.divider()

# ==========================================
# PHASE 2
# ==========================================
st.header(t["p2_header"])

# Stable English keys independent of UI language
FX_SPOT = "Spot Light"
FX_TRACK = "Magnetic Track Light"
FX_PROFILE = "LED Profile"
FX_HIDDEN = "Hidden Light"

available_fixtures = (
    [FX_SPOT, FX_TRACK, FX_PROFILE, FX_HIDDEN] if not is_ar
    else ["سبوت لايت (إضاءة موجهة)", "تراك لايت مغناطيسي", "بروفايل ليد", "إضاءة مخفية (كشاف شريط)"]
)
label_to_key = {
    "Spot Light": FX_SPOT, "سبوت لايت (إضاءة موجهة)": FX_SPOT,
    "Magnetic Track Light": FX_TRACK, "تراك لايت مغناطيسي": FX_TRACK,
    "LED Profile": FX_PROFILE, "بروفايل ليد": FX_PROFILE,
    "Hidden Light": FX_HIDDEN, "إضاءة مخفية (كشاف شريط)": FX_HIDDEN,
}

selected_labels = st.multiselect(t["select_fix"], options=available_fixtures, default=[available_fixtures[0]])
selected_fixtures = [label_to_key[x] for x in selected_labels]

# Aggregated results
fixture_specs = {}
delivered_lumens_per_type = {}
total_watts = 0.0

spot_qty_summary = 0
rows_grid_summary = cols_grid_summary = 1
track_length_summary = 0.0
track_watts_per_m = 15.0
profile_length_summary = 0.0
profile_watts_per_m = 12.0
profile_model_summary = "N/A"
profile_placement_key = "perimeter"
hidden_length_summary = 0.0
hidden_watts_per_m = 9.6

if not selected_fixtures:
    st.warning("⚠️ Please select at least one lighting type." if not is_ar else "⚠️ يرجى اختيار نوع إضاءة واحد على الأقل.")
else:
    lumens_per_fixture_type = total_lumens_required / len(selected_fixtures)
    st.info(
        f"Target lumens per lighting type: **{lumens_per_fixture_type:,.0f} lm** (distributed equally)." if not is_ar
        else f"اللومن المستهدف لكل نوع إضاءة: **{lumens_per_fixture_type:,.0f} lm** (موزعة بالتساوي)."
    )

    for fx in selected_fixtures:
        expander_title = f"⚙️ Specs for {fx}" if not is_ar else f"⚙️ مواصفات {fx}"
        with st.expander(expander_title, expanded=True):
            fc1, fc2 = st.columns(2)

            # -------------------- SPOT LIGHT --------------------
            if fx == FX_SPOT:
                with fc1:
                    cutout_size = st.selectbox(
                        "Cutout / Frame Size:" if not is_ar else "مقاس الفتحة:",
                        ["7 cm (Mini)", "7.5 cm (Standard)", "9 cm", "10 cm", "12 cm", "Double / Trimless"],
                        key="spot_dim"
                    )
                    spot_lumens_each = st.number_input(
                        "Nominal Lumens per Spot (lm):" if not is_ar else "اللومن لكل سبوت:",
                        50, 3000, 550, 25, key="spot_lumens"
                    )
                    spot_watts_each = st.number_input(
                        "Power per Spot (W):" if not is_ar else "قدرة السبوت (واط):",
                        1.0, 50.0, 7.0, 0.5, key="spot_watts"
                    )
                with fc2:
                    location = st.multiselect(
                        "Installation Location:" if not is_ar else "موقع التركيب:",
                        ["Center Ceiling Grid", "Perimeter", "Above Bed / Sofa", "Corridor Path", "Bathroom / Wet Zone"],
                        default=["Center Ceiling Grid"], key="spot_loc"
                    )

                raw_qty = max(1, math.ceil(lumens_per_fixture_type / spot_lumens_each))

                # Dynamic grid bounds — no artificial 11×11 cap
                max_dim = max(4, int(math.ceil(math.sqrt(raw_qty))) + 3)
                room_ar = length / width
                best_score = float('inf')
                best_qty, best_r, best_c = raw_qty, 1, raw_qty
                for r in range(1, max_dim + 1):
                    for c in range(1, max_dim + 1):
                        total_g = r * c
                        if total_g >= raw_qty:
                            ar_penalty = abs((c / r) - room_ar) * 1.5
                            excess_penalty = (total_g - raw_qty) * 0.4
                            score = ar_penalty + excess_penalty
                            if score < best_score:
                                best_score = score
                                best_qty, best_r, best_c = total_g, r, c

                spot_qty_summary = best_qty
                rows_grid_summary, cols_grid_summary = best_r, best_c
                spot_lumens_delivered = best_qty * spot_lumens_each
                delivered_lumens_per_type[fx] = spot_lumens_delivered
                total_watts += best_qty * spot_watts_each

                fixture_specs[fx] = (
                    f"**Qty:** {best_qty} pcs | **Grid:** {best_r} × {best_c} | **Model:** {cutout_size} | "
                    f"**Delivered:** {spot_lumens_delivered:,.0f} lm | **Load:** {best_qty * spot_watts_each:.0f} W"
                    if not is_ar else
                    f"**الكمية:** {best_qty} | **الشبكة:** {best_r} × {best_c} | **المقاس:** {cutout_size} | "
                    f"**اللومن المزود:** {spot_lumens_delivered:,.0f} lm | **الحمل:** {best_qty * spot_watts_each:.0f} واط"
                )
                st.info(f"📐 Optimized to **{best_qty} spots** in a **{best_r} × {best_c}** grid." if not is_ar
                        else f"📐 تم التحسين إلى **{best_qty} سبوت** في شبكة **{best_r} × {best_c}**.")

            # -------------------- MAGNETIC TRACK --------------------
            elif fx == FX_TRACK:
                with fc1:
                    mount_type = st.selectbox(
                        "Mounting Type:" if not is_ar else "نوع التركيب:",
                        ["Recessed (Trimless)", "Surface Mounted", "Suspended"], key="track_mount"
                    )
                    track_lm_per_m = st.number_input(
                        "Track Output per Meter (lm/m):" if not is_ar else "إضاءة التراك لكل متر (لومن/م):",
                        200, 3000, 1200, 100, key="track_lm"
                    )
                    track_watts_per_m = st.number_input(
                        "Track Power per Meter (W/m):" if not is_ar else "قدرة التراك لكل متر (واط/م):",
                        3.0, 60.0, 15.0, 1.0, key="track_w"
                    )
                with fc2:
                    track_layout = st.selectbox(
                        "Track Layout:" if not is_ar else "تخطيط التراك:",
                        ["Straight Line (Center)", "Parallel Lines (2 runs)", "L-Shape Perimeter", "U-Shape",
                         "Wall Grazing (one wall)"],
                        key="track_layout"
                    )

                # Geometry-first: placement determines physical length
                if track_layout == "Straight Line (Center)":
                    geom_len = max(length, width)
                elif track_layout == "Parallel Lines (2 runs)":
                    geom_len = 2.0 * max(length, width)
                elif track_layout == "L-Shape Perimeter":
                    geom_len = length + width
                elif track_layout == "U-Shape":
                    geom_len = 2.0 * length + width
                else:  # Wall Grazing
                    geom_len = max(length, width)

                required_len_by_lumens = lumens_per_fixture_type / track_lm_per_m
                chosen_len = geom_len  # physical reality wins
                delivered = chosen_len * track_lm_per_m
                delivered_lumens_per_type[fx] = delivered
                total_watts += chosen_len * track_watts_per_m
                track_length_summary = chosen_len

                fixture_specs[fx] = (
                    f"**Length:** {chosen_len:.2f} m | **Type:** {mount_type} | **Layout:** {track_layout} | "
                    f"**Delivered:** {delivered:,.0f} lm | **Load:** {chosen_len * track_watts_per_m:.0f} W"
                    if not is_ar else
                    f"**الطول:** {chosen_len:.2f} م | **النوع:** {mount_type} | **التخطيط:** {track_layout} | "
                    f"**اللومن المزود:** {delivered:,.0f} lm | **الحمل:** {chosen_len * track_watts_per_m:.0f} واط"
                )

                if delivered < lumens_per_fixture_type * 0.95:
                    st.warning(
                        f"⚠️ Layout provides {chosen_len:.2f} m ({delivered:,.0f} lm), below target ({lumens_per_fixture_type:,.0f} lm). "
                        f"Consider raising lm/m or adding another run."
                        if not is_ar else
                        f"⚠️ التخطيط يوفر {chosen_len:.2f} م ({delivered:,.0f} lm)، أقل من الهدف ({lumens_per_fixture_type:,.0f} lm). "
                        f"فكّر برفع اللومن/م أو إضافة خط آخر."
                    )
                st.info(f"📐 Track length **{chosen_len:.2f} m** (required by lumens: {required_len_by_lumens:.2f} m)." if not is_ar
                        else f"📐 طول التراك **{chosen_len:.2f} م** (المطلوب حسب اللومن: {required_len_by_lumens:.2f} م).")

            # -------------------- LED PROFILE --------------------
            elif fx == FX_PROFILE:
                with fc1:
                    profile_model_summary = st.selectbox(
                        "LED Profile Model:" if not is_ar else "موديل البروفايل:",
                        ["508", "617", "619", "2010A", "3010", "2320A", "509", "601", "5012A",
                         "618", "506", "1509", "613B", "1010A", "5313", "6114", "5032"],
                        key="profile_model"
                    )
                    profile_lm_per_m = st.number_input(
                        "Profile Output per Meter (lm/m):" if not is_ar else "إضاءة البروفايل لكل متر (لومن/م):",
                        50, 2500, 150, 25, key="profile_lm"
                    )
                    profile_watts_per_m = st.number_input(
                        "Profile Power per Meter (W/m):" if not is_ar else "قدرة البروفايل لكل متر (واط/م):",
                        3.0, 40.0, 12.0, 1.0, key="profile_w"
                    )
                with fc2:
                    profile_placement = st.selectbox(
                        "Placement Logic:" if not is_ar else "منطق التوزيع:",
                        ["Perimeter Framing", "Parallel Accent Lines", "Center Axis"],
                        key="profile_placement"
                    )

                offset_m = 0.30  # perimeter inset
                if profile_placement == "Perimeter Framing":
                    geom_len = 2 * ((length - 2 * offset_m) + (width - 2 * offset_m))
                    profile_placement_key = "perimeter"
                elif profile_placement == "Parallel Accent Lines":
                    geom_len = 2 * max(length, width)
                    profile_placement_key = "parallel"
                else:
                    geom_len = max(length, width)
                    profile_placement_key = "center"

                required_len_by_lumens = lumens_per_fixture_type / profile_lm_per_m
                chosen_len = geom_len
                delivered = chosen_len * profile_lm_per_m
                delivered_lumens_per_type[fx] = delivered
                total_watts += chosen_len * profile_watts_per_m
                profile_length_summary = chosen_len
                std_pieces = standard_profile_pieces(chosen_len, 3.0)

                fixture_specs[fx] = (
                    f"**Model:** {profile_model_summary} | **Placement:** {profile_placement} | "
                    f"**Length:** {chosen_len:.2f} m ({std_pieces} × 3m) | **Delivered:** {delivered:,.0f} lm | "
                    f"**Load:** {chosen_len * profile_watts_per_m:.0f} W"
                    if not is_ar else
                    f"**الموديل:** {profile_model_summary} | **التوزيع:** {profile_placement} | "
                    f"**الطول:** {chosen_len:.2f} م ({std_pieces} × 3م) | **اللومن المزود:** {delivered:,.0f} lm | "
                    f"**الحمل:** {chosen_len * profile_watts_per_m:.0f} واط"
                )

                if delivered < lumens_per_fixture_type * 0.95:
                    st.warning(
                        f"⚠️ Geometry provides {chosen_len:.2f} m ({delivered:,.0f} lm), below target "
                        f"({lumens_per_fixture_type:,.0f} lm). Raise lm/m or add another run."
                        if not is_ar else
                        f"⚠️ الهندسة توفر {chosen_len:.2f} م ({delivered:,.0f} lm) أقل من الهدف "
                        f"({lumens_per_fixture_type:,.0f} lm). ارفع اللومن/م أو أضف خطًا آخر."
                    )
                st.info(f"📐 Length **{chosen_len:.2f} m** ({std_pieces} standard 3m pieces)." if not is_ar
                        else f"📐 الطول **{chosen_len:.2f} م** ({std_pieces} قطعة قياسية 3م).")

            # -------------------- HIDDEN LIGHT --------------------
            elif fx == FX_HIDDEN:
                with fc1:
                    watt_tier = st.selectbox(
                        "Strip Power Tier:" if not is_ar else "فئة قدرة الشريط:",
                        ["9.6 W/m (Ambient)", "14.4 W/m (Medium)", "18 W/m (High Output)"],
                        key="hidden_watt"
                    )
                    hidden_watts_per_m = float(watt_tier.split()[0])
                    hidden_lm_per_m = st.number_input(
                        "Strip Output per Meter (lm/m):" if not is_ar else "إضاءة الشريط لكل متر (لومن/م):",
                        200, 3000, 1100, 100, key="hidden_lm"
                    )
                with fc2:
                    sides = st.multiselect(
                        "Sides to Cover:" if not is_ar else "الجوانب المغطاة:",
                        ["Side A (Length)", "Side B (Length)", "Side C (Width)", "Side D (Width)"],
                        default=["Side A (Length)", "Side B (Length)", "Side C (Width)", "Side D (Width)"],
                        key="hidden_sides"
                    )

                if not sides:
                    st.error("⚠️ Select at least one side." if not is_ar else "⚠️ اختر جانبًا واحدًا على الأقل.")
                    continue

                geom_len = 0.0
                for s in sides:
                    geom_len += length if "Length" in s else width

                required_len_by_lumens = lumens_per_fixture_type / hidden_lm_per_m
                chosen_len = geom_len
                delivered = chosen_len * hidden_lm_per_m
                delivered_lumens_per_type[fx] = delivered
                total_watts += chosen_len * hidden_watts_per_m
                hidden_length_summary = chosen_len

                fixture_specs[fx] = (
                    f"**Length:** {chosen_len:.2f} m | **Power Tier:** {watt_tier} | "
                    f"**Delivered:** {delivered:,.0f} lm | **Load:** {chosen_len * hidden_watts_per_m:.0f} W"
                    if not is_ar else
                    f"**الطول:** {chosen_len:.2f} م | **الفئة:** {watt_tier} | "
                    f"**اللومن المزود:** {delivered:,.0f} lm | **الحمل:** {chosen_len * hidden_watts_per_m:.0f} واط"
                )
                st.info(f"📐 Hidden strip length **{chosen_len:.2f} m**." if not is_ar
                        else f"📐 طول الشريط المخفي **{chosen_len:.2f} م**.")

# ==========================================
# PHASE 3 — VERIFICATION & BOQ
# ==========================================
if selected_fixtures and delivered_lumens_per_type:
    st.divider()
    st.header(t["p3_header"])

    fixture_lumens_total = sum(delivered_lumens_per_type.values())

    # Actual average lux on work plane
    actual_lux = (fixture_lumens_total * utilization_factor * maintenance_factor) / area if area > 0 else 0
    diff_lux = actual_lux - target_lux

    v1, v2, v3, v4 = st.columns(4)
    v1.metric("Required Lumens" if not is_ar else "اللومن المطلوب", f"{total_lumens_required:,.0f} lm")
    v2.metric("Delivered Lumens" if not is_ar else "اللومن المزود", f"{fixture_lumens_total:,.0f} lm")
    v3.metric("Actual Lux" if not is_ar else "اللوكس الفعلي", f"{actual_lux:.0f} lx", delta=f"{diff_lux:+.0f} lx")
    v4.metric("Total Load" if not is_ar else "الحمل الكلي", f"{total_watts:.0f} W")

    if actual_lux >= target_lux * 1.05:
        st.success(f"✅ Design meets target ({actual_lux:.0f} lx vs {target_lux} lx)." if not is_ar
                   else f"✅ التصميم يحقق الهدف ({actual_lux:.0f} lx مقابل {target_lux} lx).")
    elif actual_lux >= target_lux * 0.90:
        st.warning(f"⚠️ Slightly below target ({actual_lux:.0f} lx vs {target_lux} lx). Within tolerance." if not is_ar
                   else f"⚠️ أقل قليلًا من الهدف ({actual_lux:.0f} lx مقابل {target_lux} lx). ضمن التحمل.")
    else:
        st.error(f"❌ Under-lit ({actual_lux:.0f} lx vs {target_lux} lx). Increase lumens or reduce spacing." if not is_ar
                 else f"❌ إضاءة غير كافية ({actual_lux:.0f} lx مقابل {target_lux} lx). ارفع اللومن أو قلّل التباعد.")

    # SHR check for spot lights
    if spot_qty_summary > 0:
        max_spacing = 0.9 * (height - work_plane_h)  # 60° beam
        if spot_qty_summary > 0 and cols_grid_summary > 0:
            margin_x = 0.65 if (profile_length_summary == 0 and track_length_summary == 0) else 1.0
            margin_y = 0.65 if (profile_length_summary == 0 and track_length_summary == 0) else 0.9
            eff_len = max(0.1, length - 2 * margin_x)
            eff_wid = max(0.1, width - 2 * margin_y)
            step_x = eff_len / (cols_grid_summary + 1)
            step_y = eff_wid / (rows_grid_summary + 1)
            if step_x > max_spacing or step_y > max_spacing:
                st.warning(
                    f"⚠️ Spacing exceeds SHR limit ({max_spacing:.1f} m). Risk of dark spots between fixtures."
                    if not is_ar else
                    f"⚠️ التباعد يتجاوز حد SHR ({max_spacing:.1f} م). خطر بقع داكنة بين الوحدات."
                )

    # BOQ
    st.subheader("🎯 Bill of Quantities" if not is_ar else "🎯 جدول الكميات (BOQ)")
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Spot Lights" if not is_ar else "سبوت لايت",
              f"{spot_qty_summary} pcs" if spot_qty_summary > 0 else "N/A")
    b2.metric("Magnetic Track" if not is_ar else "تراك مغناطيسي",
              f"{track_length_summary:.2f} m" if track_length_summary > 0 else "N/A")
    b3.metric("LED Profile" if not is_ar else "بروفايل ليد",
              f"{profile_length_summary:.2f} m" if profile_length_summary > 0 else "N/A")
    b4.metric("Hidden Strip" if not is_ar else "شريط مخفي",
              f"{hidden_length_summary:.2f} m" if hidden_length_summary > 0 else "N/A")

    # Power & PSU
    st.subheader("⚡ Power & Driver Sizing" if not is_ar else "⚡ حساب القدرة والدرايفر")
    psu_required = total_watts * 1.2
    recommended_psu = next_psu_size(psu_required)
    w1, w2, w3 = st.columns(3)
    w1.metric("Connected Load" if not is_ar else "الحمل الكلي", f"{total_watts:.0f} W")
    w2.metric("Required with 20% margin" if not is_ar else "المطلوب بهامش 20%", f"{psu_required:.0f} W")
    w3.metric("Recommended PSU" if not is_ar else "الـ PSU المقترح",
              f"{recommended_psu} W" if isinstance(recommended_psu, int) else recommended_psu)

    # ==========================================
    # PHASE 4
    # ==========================================
    st.divider()
    st.header(t["p4_header"])

    if spot_qty_summary > 0:
        margin_x = 0.65 if (profile_length_summary == 0 and track_length_summary == 0) else 1.0
        margin_y = 0.65 if (profile_length_summary == 0 and track_length_summary == 0) else 0.9
        eff_len = max(0.1, length - 2 * margin_x)
        eff_wid = max(0.1, width - 2 * margin_y)
        step_x = eff_len / (cols_grid_summary + 1)
        step_y = eff_wid / (rows_grid_summary + 1)
        st.markdown(f"### 🔵 Spot Layout Guide" if not is_ar else f"### 🔵 دليل توزيع السبوت")
        st.info(
            f"- Grid: **{rows_grid_summary} × {cols_grid_summary}**\n"
            f"- First row from left wall: **{(margin_x + step_x) * 100:.1f} cm**\n"
            f"- X spacing: **{step_x * 100:.1f} cm** | Y spacing: **{step_y * 100:.1f} cm**"
            if not is_ar else
            f"- الشبكة: **{rows_grid_summary} × {cols_grid_summary}**\n"
            f"- أول صف من الجدار الأيسر: **{(margin_x + step_x) * 100:.1f} سم**\n"
            f"- تباعد X: **{step_x * 100:.1f} سم** | تباعد Y: **{step_y * 100:.1f} سم**"
        )

    # ==========================================
    # PHASE 5 — DRAWING (English labels only)
    # ==========================================
    st.divider()
    st.header(t["p5_header"])

    fig_h = max(2.5, 7 * (width / length) if length > 0 else 7)
    fig, ax = plt.subplots(figsize=(7, fig_h))

    ax.plot([0, length, length, 0, 0], [0, 0, width, width, 0],
            color='#2C3E50', linewidth=3, label='Room Boundary')

    if spot_qty_summary > 0:
        margin_x = 0.65 if (profile_length_summary == 0 and track_length_summary == 0) else 1.0
        margin_y = 0.65 if (profile_length_summary == 0 and track_length_summary == 0) else 0.9
        eff_len = max(0.1, length - 2 * margin_x)
        eff_wid = max(0.1, width - 2 * margin_y)
        dx = eff_len / (cols_grid_summary + 1)
        dy = eff_wid / (rows_grid_summary + 1)
        x_coords = [margin_x + dx * (i + 1) for i in range(cols_grid_summary)]
        y_coords = [margin_y + dy * (j + 1) for j in range(rows_grid_summary)]
        gx, gy = np.meshgrid(x_coords, y_coords)
        xs = gx.flatten()[:spot_qty_summary]
        ys = gy.flatten()[:spot_qty_summary]
        ax.scatter(xs, ys, color='#E74C3C', s=120, marker='o', zorder=5, label='Spot Light')

    if track_length_summary > 0:
        off = 0.4
        ax.plot([off, length - off], [off, off], color='#8E44AD', linestyle='--', linewidth=3, label='Magnetic Track')
        ax.plot([off, length - off], [width - off, width - off], color='#8E44AD', linestyle='--', linewidth=3)

    if profile_length_summary > 0:
        off = 0.3
        if profile_placement_key == "perimeter":
            ax.plot([off, length - off, length - off, off, off],
                    [off, off, width - off, width - off, off],
                    color='#27AE60', linestyle='-.', linewidth=2.5, label='LED Profile')
        elif profile_placement_key == "parallel":
            ax.plot([off, length - off], [width * 0.12, width * 0.12],
                    color='#27AE60', linestyle='-.', linewidth=2.5, label='LED Profile')
            ax.plot([off, length - off], [width * 0.88, width * 0.88],
                    color='#27AE60', linestyle='-.', linewidth=2.5)
        else:
            ax.plot([length * 0.15, length * 0.85], [width / 2, width / 2],
                    color='#27AE60', linestyle='-.', linewidth=2.5, label='LED Profile')

    if hidden_length_summary > 0:
        ax.fill([0.1, length - 0.1, length - 0.1, 0.1, 0.1],
                [0.1, 0.1, width - 0.1, width - 0.1, 0.1],
                color='#F39C12', alpha=0.15, label='Hidden Light')

    ax.set_xlim(-0.5, length + 0.5)
    ax.set_ylim(-0.5, width + 0.5)
    ax.set_aspect('equal')
    ax.set_title(f"Lighting Layout Plan ({length}m × {width}m)", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Room Length (m)", fontsize=10)
    ax.set_ylabel("Room Width (m)", fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=4, fontsize=8)

    st.pyplot(fig)
    plt.close(fig)

    st.subheader("📋 Detailed Specification" if not is_ar else "📋 المواصفات التفصيلية")
    for item, details in fixture_specs.items():
        st.markdown(f"- **{item}:** {details}")
