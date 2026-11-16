import math
import matplotlib
matplotlib.use('Agg')  # Fixes Streamlit backend server error
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# ==========================================
# LANGUAGE & LOCALIZATION DICTIONARY
# ==========================================
LANG = st.sidebar.selectbox("🌐 Select Language / اختر اللغة", ["English", "العربية"])

is_ar = (LANG == "العربية")

# Apply full RTL direction, right-alignment, and Arabic typography styling
if is_ar:
    st.markdown("""
        <style>
        /* Force RTL and Right Alignment across the entire app */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .main, p, span, div, label, h1, h2, h3, h4, h5, h6 {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* Align input labels and widgets */
        .stSelectbox label, .stNumberInput label, .stSlider label, .stMultiSelect label {
            direction: rtl !important;
            text-align: right !important;
            float: right !important;
        }
        
        /* Align metric cards */
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* Fix expander header alignment */
        .streamlit-expanderHeader {
            direction: rtl !important;
            text-align: right !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Dictionary for bilingual text strings
t = {
    "title": "💡 Hatem Alzoubi Lighting Design & Lumen Calculator by Engineer Wael" if not is_ar else "💡 تصميم إضاءة حاتم الزعبي وحاسبة اللومن بواسطة المهندس وائل",
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

st.set_page_config(page_title="Hatem Alzoubi Lighting Design", page_icon="💡", layout="centered")

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
else:  # Showroom / معرض تجاري
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
                
                fixture_specs[fixture] = f"**Quantity:** {calculated_qty} pcs | **Grid:** {rows_grid_summary} × {cols_grid_summary} | **Model:** {cutout_size} | **Lumens:** {actual_lumens:,} lm"
                st.info(f"📐 **Design Match:** Optimized to **{calculated_qty} spots** in a **{rows_grid_summary} × {cols_grid_summary}** proportional grid.")

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
                
                fixture_specs[fixture] = f"**Track Length:** {calculated_length}m | **Type:** {mount_type} | **Output:** {actual_lumens:,.0f} lm"
                st.info(f"📐 Required track length is **{calculated_length} meters**.")

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
                            "خطوط متوازية متسماسة (خطين مزدوجين)",
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
                
                fixture_specs[fixture] = f"**Profile:** {profile_model} | **Placement:** {profile_placement} | **Length:** {calculated_length}m"
                st.info(f"📐 Model **{profile_model_summary}** requires **{calculated_length} meters**.")

            elif "Hidden Light" in fixture or "مخفية" in fixture:
                with f_col1:
                    wattage = st.selectbox("LED Strip Power Tier:" if not is_ar else "فئة استطاعة شريط الليد:", ["9.6 W/m (Ambient)", "14.4 W/m (Medium)", "18 W/m (High Output)"], key=f"{fixture}_watt")
                    lumens_per_meter = st.number_input("Strip Output per Meter (lm/m):" if not is_ar else "إضاءة الشريط لكل متر (لومن/م):", min_value=200, max_value=3000, value=1100, step=100, key=f"{fixture}_lumen_val")
                with f_col2:
                    covered_sides = st.multiselect(
                        "Select Sides to Cover with Hidden Light:" if not is_ar else "اختر الجوانب المراد تغطيتها بالإضاءة المخفية:",
                        ["Side A (Length 1)", "Side B (Length 2)", "Side C (Width 1)", "Side D (Width 2)"] if not is_ar else ["الجانب أ (الطول 1)", "الجانب ب (الطول 2)", "الجانب ج (العرض 1)", "الجانب د (العرض 2)"],
                        default=["Side A (Length 1)", "Side B (Length 2)", "Side C (Width 1)", "Side D (Width 2)"] if not is_ar else ["الجانب أ (الطول 1)", "الجانب ب (الطول 2)", "الجانب ج (العرض 1)", "الجانب د (العرض 2)"],
                        key=f"{fixture}_sides"
                    )
                    covered_sides_summary = covered_sides
                
                side_length_val = length
                side_width_val = width
                calculated_length = 0.0
                for side in covered_sides:
                    calculated_length += side_length_val if ("Length" in side or "الطول" in side) else side_width_val

                if calculated_length == 0:
                    calculated_length = 1.0
                
                hidden_length_summary = calculated_length
                actual_lumens = calculated_length * lumens_per_meter
                fixture_lumens_total += actual_lumens
                
                fixture_specs[fixture] = f"**Hidden Strip Length:** {calculated_length}m | **Output:** {actual_lumens:,.0f} lm"
                st.info(f"📐 Total hidden strip length is **{calculated_length} meters**.")

# ==========================================
# PHASE 3: VERIFICATION & BILL OF QUANTITIES
# ==========================================
if selected_fixtures:
    st.divider()
    st.header(t["p3_header"])

    v_col1, v_col2, v_col3 = st.columns(3)
    v_col1.metric("Required Lumens (inc. MF)" if not is_ar else "اللومن المطلوب", f"{total_lumens_required:,.0f} lm")
    v_col2.metric("Engineered Delivered Lumens" if not is_ar else "اللومن المزود بالحسابات", f"{fixture_lumens_total:,.0f} lm")
    
    diff = fixture_lumens_total - total_lumens_required
    v_col3.metric("Lumen Variance" if not is_ar else "فرق اللومن", f"{diff:+,.0f} lm")

    if fixture_lumens_total >= total_lumens_required:
        st.success(f"✅ **Design Validated:** The automated layout meets or exceeds required lux levels." if not is_ar else f"✅ **تم اعتماد التصميم:** التخطيط التلقائي يلبي أو يتجاوز مستوى الإضاءة المطلوبة.")
    else:
        st.warning(f"⚠️ **Adjustment Recommended:** Output is slightly below target. Consider increasing lumen output." if not is_ar else f"⚠️ **تعديل مقترح:** الإضاءة أقل بقليل من المستهدف. يعزى زيادة استطاعة الوحدات.")

    st.subheader("🎯 Recommended Lighting Bill of Quantities" if not is_ar else "🎯 جدول كميات المواد المقترح (BOQ)")
    
    rec_col1, rec_col2, rec_col3, rec_col4 = st.columns(4)
    with rec_col1:
        st.metric("Spot Lights" if not is_ar else "سبوت لايت", f"{spot_qty_summary} pcs" if spot_qty_summary > 0 else "N/A")
    with rec_col2:
        st.metric("Magnetic Track" if not is_ar else "تراك مغناطيسي", f"{track_length_summary} m" if track_length_summary > 0 else "N/A")
    with rec_col3:
        st.metric("LED Profile" if not is_ar else "بروفايل ليد", f"{profile_length_summary} m" if profile_length_summary > 0 else "N/A")
    with rec_col4:
        st.metric("Hidden Light" if not is_ar else "إضاءة مخفية", f"{hidden_length_summary} m" if hidden_length_summary > 0 else "N/A")

    # ==========================================
    # PHASE 4: INSTALLATION LAYOUT & SPACING GUIDE
    # ==========================================
    st.divider()
    st.header(t["p4_header"])
    st.write(f"Precise architectural positioning relative to room boundaries ({length}m × {width}m)." if not is_ar else f"تحديد المواضع المعمارية بدقة بالنسبة لحدود الغرفة ({length}م × {width}م).")

    if spot_qty_summary > 0:
        space_x_cm = (length * 100) / (cols_grid_summary + 1)
        space_y_cm = (width * 100) / (rows_grid_summary + 1)
        st.markdown(f"### 🔵 Spot Lights Layout Guide ({spot_qty_summary} pcs)" if not is_ar else f"### 🔵 دليل توزيع السبوت لايت ({spot_qty_summary} قطعة)")
        st.info(
            f"- **Grid Configuration:** Proportional **{rows_grid_summary} rows × {cols_grid_summary} columns** matrix.\n"
            f"- **X-axis Spacing:** First row starts at **{space_x_cm / 2:.1f} cm** from the wall, spaced **{space_x_cm:.1f} cm** apart.\n"
            f"- **Y-axis Spacing:** Spaced **{space_y_cm:.1f} cm** center-to-center."
            if not is_ar else
            f"- **تكوين الشبكة:** مصفوفة متناسبة **{rows_grid_summary} صفوف × {cols_grid_summary} أعمدة**.\n"
            f"- **المسافة على محور X:** يبعد الصف الأول **{space_x_cm / 2:.1f} سم** عن الجدار، بمسافة **{space_x_cm:.1f} سم** بين الوحدات.\n"
            f"- **المسافة على محور Y:** المسافة بين المراكز **{space_y_cm:.1f} سم**."
        )

    if profile_length_summary > 0:
        offset_profile = 30
        st.markdown(f"### 📏 LED Profile Layout Guide" if not is_ar else f"### 📏 دليل تركيب بروفايل الليد")
        st.info(
            f"- **Design Strategy:** {profile_placement_summary}.\n"
            f"- **Linear Length:** **{profile_length_summary} meters** configured symmetrically."
            if not is_ar else
            f"- **استراتيجية التصميم:** {profile_placement_summary}.\n"
            f"- **الطول الخطي:** **{profile_length_summary} متر** موزعة بشكل متناظر."
        )

    # ==========================================
    # PHASE 5: VISUAL FLOOR PLAN & LAYOUT DRAWING
    # ==========================================
    st.divider()
    st.header(t["p5_header"])
    st.write("Generated 2D CAD floor plan showing professional lighting positions." if not is_ar else "مخطط سقف CAD ثنائي الأبعاد يوضح مواضع الإضاءة الاحترافية.")

    fig, ax = plt.subplots(figsize=(7, 7 * (width / length) if length > 0 else 7))
    
    ax.plot([0, length, length, 0, 0], [0, 0, width, width, 0], color='#2C3E50', linewidth=3, label='Room Boundary' if not is_ar else 'حدود الغرفة')
    
    if spot_qty_summary > 0:
        dx = length / (cols_grid_summary + 1)
        dy = width / (rows_grid_summary + 1)
        x_coords = [dx * (i + 1) for i in range(cols_grid_summary)]
        y_coords = [dy * (j + 1) for j in range(rows_grid_summary)]
        gx, gy = np.meshgrid(x_coords, y_coords)
        ax.scatter(gx.flatten()[:spot_qty_summary], gy.flatten()[:spot_qty_summary], color='#E74C3C', s=120, marker='o', zorder=5, label='Spot Light' if not is_ar else 'سبوت لايت')

    if track_length_summary > 0:
        offset = 0.4
        ax.plot([offset, length - offset], [offset, offset], color='#8E44AD', linestyle='--', linewidth=3, label='Magnetic Track' if not is_ar else 'تراك مغناطيسي')
        ax.plot([offset, length - offset], [width - offset, width - offset], color='#8E44AD', linestyle='--', linewidth=3)

    if profile_length_summary > 0:
        off = 0.3
        if "Perimeter" in profile_placement_summary or "إطار محيطي" in profile_placement_summary:
            ax.plot([off, length - off, length - off, off, off], [off, off, width - off, width - off, off], color='#27AE60', linestyle='-.', linewidth=2.5, label='LED Profile' if not is_ar else 'بروفايل ليد')
        elif "Parallel" in profile_placement_summary or "خطوط متوازية" in profile_placement_summary:
            ax.plot([off, length - off], [width * 0.33, width * 0.33], color='#27AE60', linestyle='-.', linewidth=2.5, label='LED Profile' if not is_ar else 'بروفايل ليد')
            ax.plot([off, length - off], [width * 0.67, width * 0.67], color='#27AE60', linestyle='-.', linewidth=2.5)
        else:
            ax.plot([length * 0.2, length * 0.8], [width / 2, width / 2], color='#27AE60', linestyle='-.', linewidth=2.5, label='LED Profile' if not is_ar else 'بروفايل ليد')

    if hidden_length_summary > 0:
        ax.fill([0.1, length - 0.1, length - 0.1, 0.1, 0.1], [0.1, 0.1, width - 0.1, width - 0.1, 0.1], color='#F39C12', alpha=0.15, label='Hidden Light' if not is_ar else 'إضاءة مخفية')

    ax.set_xlim(-0.5, length + 0.5)
    ax.set_ylim(-0.5, width + 0.5)
    ax.set_aspect('equal')
    ax.set_title(f"Lighting Layout Plan ({length}m × {width}m)" if not is_ar else f"مخطط توزيع الإضاءة ({length}م × {width}م)", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Room Length (m)" if not is_ar else "طول الغرفة (م)", fontsize=10)
    ax.set_ylabel("Room Width (m)" if not is_ar else "عرض الغرفة (م)", fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1))
    
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("📋 Detailed Specification Report" if not is_ar else "📋 تقرير المواصفات التفصيلي")
    st.write(f"**Space:** {building_category} — {room_type} ({length}m × {width}m × {height}m | Area: {area:.2f} m²)" if not is_ar else f"**الفراغ:** {building_category} — {room_type} ({length}م × {width}م × {height}م | المساحة: {area:.2f} م²)")
    
    for item, details in fixture_specs.items():
        st.markdown(f"- **{item}:** {details}")