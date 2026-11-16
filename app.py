import math
import matplotlib
matplotlib.use('Agg')  # Fixes Streamlit backend server error
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

st.set_page_config(page_title="Hatem Alzoubi Lighting Design", page_icon="💡", layout="centered")

# ==========================================
# LANGUAGE & LOCALIZATION DICTIONARY
# ==========================================
LANG = st.sidebar.selectbox("🌐 Select Language / اختر اللغة", ["English", "العربية"])

is_ar = (LANG == "العربية")

if is_ar:
    st.markdown("""
        <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .main, p, span, div, label, h1, h2, h3, h4, h5, h6 {
            direction: rtl !important;
            text-align: right !important;
        }
        .stSelectbox label, .stNumberInput label, .stSlider label, .stMultiSelect label {
            direction: rtl !important;
            text-align: right !important;
            float: right !important;
        }
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {
            direction: rtl !important;
            text-align: right !important;
        }
        .streamlit-expanderHeader {
            direction: rtl !important;
            text-align: right !important;
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
    "mf": "Maintenance Factor (MF / Light Loss Factor):" if not is_ar else "معامل الصيانة (MF / عامل فقد الإضاءة):",
    "mf_help": "Accounts for luminaire dirt depreciation and lamp lumen output reduction over time. Standard indoor clean environment = 0.80." if not is_ar else "يأخذ في الاعتبار انخفاض اتساخ وحدة الإضاءة وانخفاض إخراج اللومن بمرور الوقت. بيئة داخلية نظيفة قياسية = 0.80.",
    "p2_header": "Phase 2: Lighting Types, CCT & Layout Design" if not is_ar else "المرحلة الثانية: أنواع الإضاءة، درجة الحرارة (CCT)، وتصميم التخطيط",
    "select_fix": "Select lighting types to include in this space:" if not is_ar else "اختر أنواع الإضاءة المراد تضمينها في هذا الفراغ:",
    "cct": "Color Temperature (CCT) — Beam Angle: 60° (Fixed):" if not is_ar else "درجة حرارة اللون (CCT) — زاوية الشعاع: 60° (ثابتة):",
    "p3_header": "Phase 3: Engineering Verification & Quantities" if not is_ar else "المرحلة الثالثة: التحقق الهندسي وكميات المواد",
    "p4_header": "Phase 4: Installation Layout & Spacing Guide" if not is_ar else "المرحلة الرابعة: تخطيط التركيب ودليل المسافات",
    "p5_header": "Phase 5: Visual Floor Plan & Layout Drawing" if not is_ar else "المرحلة الخامسة: مخطط السقف المرئي ورسم التخطيط",
}

st.title(t["title"])
st.write(t["subtitle"])

# ==========================================
# PHASE 1: SPACE, DIMENSIONS & TARGET REQUIREMENTS
# ==========================================
st.header(t["p1_header"])

building_category = st.selectbox(
    t["b_cat"],
    ["Villa", "Office", "Showroom"] if not is_ar else ["فيلا", "مكتب", "معرض تجاري"]
)

if building_category in ["Villa", "فيلا"]:
    room_type = st.selectbox(
        t["r_type"],
        ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Dining Room", "Corridor / Stairs"] if not is_ar else ["غرفة معيشة", "غرفة نوم", "مطبخ", "حمام", "غرفة طعام", "ممر / درج"]
    )
    lux_standards = {
        "Living Room": 200, "Bedroom": 150, "Kitchen": 300, "Bathroom": 250, "Dining Room": 200, "Corridor / Stairs": 100,
        "غرفة معيشة": 200, "غرفة نوم": 150, "مطبخ": 300, "حمام": 250, "غرفة طعام": 200, "ممر / درج": 100
    }
elif building_category in ["Office", "مكتب"]:
    room_type = st.selectbox(
        t["r_type"],
        ["General Open Office", "Private Office", "Conference Room", "Reception / Lobby", "Corridor"] if not is_ar else ["مكتب مفتوح عام", "مكتب خاص", "غرفة اجتماعات", "الاستقبال / اللوبي", "ممر"]
    )
    lux_standards = {
        "General Open Office": 500, "Private Office": 500, "Conference Room": 400, "Reception / Lobby": 300, "Corridor": 150,
        "مكتب مفتوح عام": 500, "مكتب خاص": 500, "غرفة اجتماعات": 400, "الاستقبال / اللوبي": 300, "ممر": 150
    }
else:
    room_type = st.selectbox(
        t["r_type"],
        ["General Furniture Exhibition", "Display Window / Feature Zone", "Checkout / Cashier Counter", "Storage / Back Office"] if not is_ar else ["معرض مفروشات عام", "واجهة العرض / منطقة مميزة", "منطقة الكشير / المحاسبة", "المستودع / المكتب الخلفي"]
    )
    lux_standards = {
        "General Furniture Exhibition": 400, "Display Window / Feature Zone": 750, "Checkout / Cashier Counter": 500, "Storage / Back Office": 200,
        "معرض مفروشات عام": 400, "واجهة العرض / منطقة مميزة": 750, "منطقة الكشير / المحاسبة": 500, "المستودع / المكتب الخلفي": 200
    }

col1, col2, col3 = st.columns(3)
with col1:
    length = st.number_input(t["length"], min_value=0.5, max_value=100.0, value=5.0, step=0.1)
with col2:
    width = st.number_input(t["width"], min_value=0.5, max_value=100.0, value=4.0, step=0.1)
with col3:
    height = st.number_input(t["height"], min_value=2.0, max_value=20.0, value=3.0, step=0.1)

maintenance_factor = st.slider(
    t["mf"],
    min_value=0.50, max_value=1.00, value=0.80, step=0.05,
    help=t["mf_help"]
)

area = length * width
target_lux = lux_standards[room_type]
total_lumens_required = (area * target_lux) / maintenance_factor

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Room Area" if not is_ar else "مساحة الغرفة", f"{area:.2f} m²")
m_col2.metric("Ceiling Height" if not is_ar else "ارتفاع السقف", f"{height:.2f} m")
m_col3.metric("Target Lux" if not is_ar else "الإضاءة المطلوبة", f"{target_lux} lx")
m_col4.metric("Required Lumens" if not is_ar else "إجمالي اللومن المطلوب", f"{total_lumens_required:,.0f} lm")

st.divider()

# ==========================================
# PHASE 2: LIGHTING TYPES, CCT & LAYOUT DESIGN
# ==========================================
st.header(t["p2_header"])

available_fixtures = ["Spot Light", "Magnetic Track Light", "LED Profile", "Hidden Light"] if not is_ar else ["سبوت لايت (إضاءة موجهة)", "تراك لايت مغناطيسي", "بروفايل ليد", "إضاءة مخفية (كشاف شريط)"]

selected_fixtures = st.multiselect(
    t["select_fix"],
    options=available_fixtures,
    default=[available_fixtures[0]]
)

fixture_specs = {}
fixture_lumens_total = 0

spot_qty_summary = 0
rows_grid_summary = 1
cols_grid_summary = 1
track_length_summary = 0.0
profile_length_summary = 0.0
profile_model_summary = "N/A"
profile_placement_summary = "Perimeter Framing"
hidden_length_summary = 0.0
covered_sides_summary = []

if not selected_fixtures:
    st.warning("⚠️ Please select at least one lighting type." if not is_ar else "⚠️ يرجى اختيار نوع إضاءة واحد على الأقل.")
else:
    combination_label = " + ".join(selected_fixtures)
    st.success(f"**Active Design Combination:** {combination_label}" if not is_ar else f"**توليفة التصميم النشطة:** {combination_label}")
    
    lumens_per_fixture_type = total_lumens_required / len(selected_fixtures)

    for fixture in selected_fixtures:
        with st.expander(f"⚙️ Engineering Specs & Layout for {fixture}" if not is_ar else f"⚙️ المواصفات الهندسية والتخطيط لـ {fixture}", expanded=True):
            f_col1, f_col2 = st.columns(2)
            
            cct = st.selectbox(
                t["cct"],
                ["White (أبيض)", "Warm White (أبيض دافئ)", "Desert (ديزرت / أصفر هادئ)"],
                key=f"{fixture}_cct"
            )
            
            if "Spot Light" in fixture or "سبوت" in fixture:
                with f_col1:
                    cutout_size = st.selectbox(
                        "Cutout / Frame Size:" if not is_ar else "مقاس الفتحة / الإطار:",
                        ["7 cm (Mini)", "7.5 cm (Standard)", "9 cm", "10 cm", "12 cm", "Double / Trimless"],
                        key=f"{fixture}_dim"
                    )
                    spot_lumens_each = st.number_input("Nominal Lumens per Spot Light (lm):" if not is_ar else "تدفق اللومن لكل سبوت (لومن):", min_value=50, max_value=2000, value=550, step=25, key=f"{fixture}_lumen_val")
                with f_col2:
                    location = st.multiselect(
                        "Installation Location / Spacing Guide:" if not is_ar else "موقع التركيب / دليل التوزيع:",
                        ["Center Ceiling Grid", "Perimeter / Around Gypsum", "Above Bed / Sofa", "Corridor Path", "Bathroom / Wet Zone"],
                        default=["Center Ceiling Grid"],
                        key=f"{fixture}_loc"
                    )
                
                raw_qty = math.ceil(lumens_per_fixture_type / spot_lumens_each)
                room_aspect_ratio = length / width
                
                best_qty = raw_qty
                best_rows = 1
                best_cols = raw_qty
                best_score = float('inf')

                for r in range(1, 12):
                    for c in range(1, 12):
                        grid_total = r * c
                        if grid_total >= raw_qty:
                            grid_aspect_ratio = c / r
                            excess_penalty = (grid_total - raw_qty) * 0.4
                            ar_penalty = abs(grid_aspect_ratio - room_aspect_ratio) * 1.5
                            score = excess_penalty + ar_penalty
                            
                            if score < best_score:
                                best_score = score
                                best_qty = grid_total
                                best_rows = r
                                best_cols = c

                calculated_qty = best_qty
                spot_qty_summary = calculated_qty
                actual_lumens = calculated_qty * spot_lumens_each
                fixture_lumens_total += actual_lumens
                
                cols_grid_summary = best_cols
                rows_grid_summary = best_rows
                
                fixture_specs[fixture] = f"**Quantity:** {calculated_qty} pcs | **Grid:** {rows_grid_summary} × {cols_grid_summary} | **Model:** {cutout_size} | **Lumens:** {actual_lumens:,} lm" if not is_ar else f"**الكمية:** {calculated_qty} قطعة | **الشبكة:** {rows_grid_summary} × {cols_grid_summary} | **المقاس:** {cutout_size} | **اللومن:** {actual_lumens:,} lm"
                st.info(f"📐 **Design Match:** Optimized to **{calculated_qty} spots** in a **{rows_grid_summary} × {cols_grid_summary}** proportional grid." if not is_ar else f"📐 **توافق التصميم:** تم تحسين الكمية إلى **{calculated_qty} سبوت** في شبكة متناسبة **{rows_grid_summary} × {cols_grid_summary}**.")

            elif "Magnetic Track" in fixture or "تراك" in fixture:
                with f_col1:
                    mount_type = st.selectbox("Track Mounting Type:" if not is_ar else "نوع تركيب التراك:", ["Recessed (Trimless)", "Surface Mounted", "Suspended"], key=f"{fixture}_mount")
                    lumens_per_meter = st.number_input("Track Output per Meter (lm/m):" if not is_ar else "إضاءة التراك لكل متر (لومن/م):", min_value=200, max_value=3000, value=1200, step=100, key=f"{fixture}_lumen_val")
                with f_col2:
                    location = st.multiselect(
                        "Track Layout / Location:" if not is_ar else "موقع وتخطيط التراك:",
                        ["Straight Line (Center)", "Parallel Lines (U-Shape)", "L-Shape Perimeter", "U-Shape / Rectangle", "Wall Grazing"],
                        default=["Parallel Lines (U-Shape)"],
                        key=f"{fixture}_loc"
                    )
                
                calculated_length = round((lumens_per_fixture_type / lumens_per_meter) * 2) / 2
                if calculated_length < 0.5: calculated_length = 0.5
                track_length_summary = calculated_length
                actual_lumens = calculated_length * lumens_per_meter
                fixture_lumens_total += actual_lumens
                
                fixture_specs[fixture] = f"**Track Length:** {calculated_length}m | **Type:** {mount_type} | **Output:** {actual_lumens:,.0f} lm" if not is_ar else f"**طول التراك:** {calculated_length} متر | **النوع:** {mount_type} | **الإضاءة:** {actual_lumens:,.0f} lm"
                st.info(f"📐 Required track length is **{calculated_length} meters**." if not is_ar else f"📐 طول التراك المطلوب هو **{calculated_length} متر**.")

            elif "LED Profile" in fixture or "بروفايل" in fixture:
                with f_col1:
                    profile_model = st.selectbox(
                        "Select LED Profile Model (Catalog):" if not is_ar else "اختر موديل بروفايل الليد (من الكاتالوج):",
                        [
                            "508 (Slim Recessed / Flanged)",
                            "617 (Standard Recessed)",
                            "619 (Recessed Flanged)",
                            "2010A / 2010 (Surface / Recessed Square)",
                            "3010 / 3010A (Wide Recessed)",
                            "2320A (Deep Recessed)",
                            "509 (Mini Channel)",
                            "601 (Corner / Angle Profile)",
                            "5012A (Wall Grazer / Architectural)",
                            "618 (Standard Recessed Series)",
                            "506 (Slim Recessed)",
                            "1509 / 1509A (Square Channel)",
                            "613B (Architectural Channel)",
                            "1010A (Mini Surface)",
                            "5313 (Plaster-in / Trimless Wall-to-Wall)",
                            "6114 (Deep Suspension / Wall-to-Wall)",
                            "5032 / 5032A (Extra Wide Commercial)"
                        ],
                        key=f"{fixture}_model"
                    )
                    profile_model_summary = profile_model
                    lumens_per_meter = st.number_input("Profile Output per Meter (lm/m):" if not is_ar else "إضاءة البروفايل لكل متر (لومن/م):", min_value=50, max_value=2500, value=150, step=25, key=f"{fixture}_lumen_val")
                with f_col2:
                    profile_placement = st.selectbox(
                        "Interior Design Placement Logic:" if not is_ar else "منطق التوزيع الديكوري:",
                        [
                            "Perimeter Framing (Balanced Box around room)", 
                            "Parallel Accent Lines (Symmetrical dual lines)", 
                            "Center Architectural Axis (Single clean center run)"
                        ] if not is_ar else [
                            "إطار محيطي (مربع متوازن حول الغرفة)",
                            "خطوط متوازية متناظرة (خطين مزدوجين)",
                            "محور معماري مركزي (خط منتصف نظيف)"
                        ],
                        key=f"{fixture}_placement"
                    )
                    profile_placement_summary = profile_placement
                
                calculated_length = round((lumens_per_fixture_type / lumens_per_meter) * 2) / 2
                if calculated_length < 0.5: calculated_length = 0.5
                profile_length_summary = calculated_length
                actual_lumens = calculated_length * lumens_per_meter
                fixture_lumens_total += actual_lumens
                
                fixture_specs[fixture] = f"**Profile:** {profile_model} | **Placement:** {profile_placement} | **Length:** {calculated_length}m" if not is_ar else f"**الموديل:** {profile_model} | **
