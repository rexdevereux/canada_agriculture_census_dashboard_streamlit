import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
from pathlib import Path
import branca.colormap as cm

# ====================================================================
# Page Configuration
# ====================================================================
st.set_page_config(
    page_title="Canada Agricultural Atlas",
    page_icon="🍁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stMetric label {
        color: #31333F !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #0e1117 !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #31333F !important;
    }
    h1 {
        color: #d62728;
    }
    </style>
""", unsafe_allow_html=True)

# ====================================================================
# Product Dictionaries
# ====================================================================
HA_FIELD_CROPS = {
    "ALFALFA": "Alfalfa and alfalfa mixtures",
    "BARLEY": "Barley",
    "BUCWHT": "Buckwheat",
    "CANARY": "Canary seed",
    "CANOLA": "Canola (rapeseed)",
    "CHICPEA": "Chick peas",
    "CORNGR": "Corn for grain",
    "CORNSI": "Corn for silage",
    "DFPEAS": "Dry field peas",
    "FABABN": "Faba beans",
    "FLAXSD": "Flaxseed",
    "FORAGE": "Forage seed for seed",
    "GINSENG": "Ginseng",
    "HEMP": "Hemp",
    "LENTIL": "Lentils",
    "MUSTSD": "Mustard seed",
    "MXDGRN": "Mixed grains",
    "OATS": "Oats",
    "ODFBNS": "Other dry beans",
    "OFIELD": "Other field crops",
    "OTTAME": "All other tame hay and fodder crops",
    "POTATS": "Potatoes",
    "RYEFAL": "Fall rye",
    "RYESPG": "Spring rye",
    "SOYBNS": "Soybeans",
    "SUGARB": "Sugar beets",
    "SUNFLS": "Sunflowers",
    "TRITCL": "Triticale",
    "WHITBN": "Dry white beans",
    "WHTDUR": "Durum wheat",
    "WHTSPG": "Spring wheat (excluding durum)",
    "WHTWIN": "Winter wheat",
}

HA_VEGETABLES = {
    "ASPNPRD": "Asparagus non-producing",
    "ASPPROD": "Asparagus producing",
    "BEANS": "Beans",
    "BEETS": "Beets",
    "BROCLI": "Broccoli",
    "BRSPRT": "Brussels sprouts",
    "CABAGE": "Cabbage",
    "CARROT": "Carrots",
    "CELERY": "Celery",
    "CHINCABG": "Chinese cabbage",
    "CLFLWR": "Cauliflower",
    "CUCUMB": "Cucumbers",
    "GARLIC": "Garlic",
    "GRPEAS": "Green peas",
    "KALE": "Kale",
    "LETUCE": "Lettuce",
    "ONIONS": "Onions",
    "PEPPER": "Peppers",
    "PUMPKIN": "Pumpkins",
    "RADISH": "Radishes",
    "RHUBARB": "Rhubarb",
    "RTBAGA": "Rutabagas",
    "SHALOT": "Shallots",
    "SPNACH": "Spinach",
    "SQUAZUC": "Squash and zucchini",
    "SWCORN": "Sweet corn",
    "TOMATO": "Tomatoes",
}

HA_FRUITS_BERRIES = {
    "APCTTA": "Apricots",
    "APPLETA": "Apples",
    "BLUEBTA": "Blueberries",
    "CRANBTA": "Cranberries",
    "CURRANT": "Blackcurrants, redcurrants and whitecurrants",
    "GRAPETA": "Grapes",
    "HASKAPTA": "Haskaps",
    "HBLUEBTA": "Blueberries, highbush",
    "LBLUEBTA": "Blueberries, lowbush",
    "PEARTA": "Pears",
    "PECHTA": "Peaches",
    "PLUMTA": "Plums",
    "RASPBTA": "Raspberries",
    "SASKBTA": "Saskatoons",
    "SRCHTA": "Sour cherries",
    "STRWBTA": "Strawberries",
    "SWCHTA": "Sweet cherries",
    "OTFRTTA": "Other fruits, berries and nuts",
}

GREENHOUSE_PRODUCTS = {
    "GRNCUCUMB": "Greenhouse cucumbers",
    "GRNFLOWER": "Cut flowers",
    "GRNHERB": "Greenhouse herbs",
    "GRNOTHER": "Other greenhouse products",
    "GRNOTHVEG": "Other greenhouse fruits and vegetables",
    "GRNPEPPER": "Greenhouse peppers",
    "GRNPLANTS": "Potted plants, indoor or outdoor",
    "GRNTOMATO": "Greenhouse tomatoes",
}

LIVESTOCK_ANIMALS = {
    "BFCOWS": "Beef cows",
    "BFHEIF": "Heifers for beef herd replacement",
    "BISON": "Bison (buffalo)",
    "BOARS": "Boars",
    "BULLS": "Bulls, 1 year and over",
    "CALFU1": "Calves under 1 year",
    "DEER": "Deer",
    "DONKEYS": "Donkeys",
    "ELK": "Elk",
    "EWES": "Ewes",
    "FDHEIF": "Heifers for dairy herd replacement",
    "GOATS": "Goats",
    "GRWPIG": "Growing pigs",
    "HORSES": "Horses",
    "LAMAS": "Llamas and alpacas",
    "LAMBS": "Lambs",
    "MINK": "Mink",
    "MKTLAMBS": "Market lambs",
    "MLKCOW": "Milk cows",
    "MLKHEIF": "Milk heifers",
    "NRSPIG": "Nursing pigs",
    "RABBIT": "Rabbits",
    "RAMS": "Rams",
    "REPLAMBS": "Replacement lambs",
    "SOWS": "Sows and gilts for breeding",
    "STEERS": "Steers, 1 year and over",
    "WEANPIG": "Weaner pigs",
}

POULTRY = {
    "BREEDCHK": "Layer and broiler breeders",
    "BROILER": "Broilers, roasters and Cornish",
    "DUCK": "Ducks",
    "GEESE": "Geese",
    "HATCHNUM": "Chicks or other poultry hatched",
    "LAYHEN": "Laying hens, 19 weeks and over",
    "OTHPLT": "Other poultry",
    "PULETS": "Pullets under 19 weeks",
    "TURKEY": "Turkeys",
}

# Map categories to their product dictionaries
CATEGORY_PRODUCTS = {
    "🌾 Field Crops": HA_FIELD_CROPS,
    "🥬 Vegetables": HA_VEGETABLES,
    "🍓 Fruits & Berries": HA_FRUITS_BERRIES,
    "🏡 Greenhouse Products": GREENHOUSE_PRODUCTS,
    "🐄 Livestock": LIVESTOCK_ANIMALS,
    "🐔 Poultry": POULTRY,
}

# ====================================================================
# Data Loading
# ====================================================================
@st.cache_data
def load_data():
    """Load agricultural statistics data."""
    try:
        # Load ADM2 agricultural data
        adm2_path = Path("data/canada_adm2_agricultural_stats.geojson")
        if not adm2_path.exists():
            st.error(f"Data file not found at {adm2_path}")
            st.stop()
        
        adm2 = gpd.read_file(adm2_path)
        
        # Convert to WGS84 for web mapping
        if adm2.crs != "EPSG:4326":
            adm2 = adm2.to_crs("EPSG:4326")
        
        return adm2
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

adm2_data = load_data()

# ====================================================================
# Category Configuration
# ====================================================================
CATEGORIES = {
    "🌾 Field Crops": {
        "columns": ("top_field_crop", "top_field_crop_value"),
        "color": "YlOrRd",
        "description": "Major field crops including wheat, canola, barley, and more",
        "unit": "hectares"
    },
    "🥬 Vegetables": {
        "columns": ("top_vegetable", "top_vegetable_value"),
        "color": "Greens",
        "description": "Vegetable production including lettuce, carrots, tomatoes, and more",
        "unit": "hectares"
    },
    "🍓 Fruits & Berries": {
        "columns": ("top_fruit_berry", "top_fruit_berry_value"),
        "color": "RdPu",
        "description": "Fruit and berry production including apples, blueberries, strawberries",
        "unit": "hectares"
    },
    "🏡 Greenhouse Products": {
        "columns": ("top_greenhouse", "top_greenhouse_value"),
        "color": "Purples",
        "description": "Greenhouse production including tomatoes, cucumbers, peppers, flowers",
        "unit": "hectares"
    },
    "🐄 Livestock": {
        "columns": ("top_livestock", "top_livestock_value"),
        "color": "YlOrBr",
        "description": "Livestock including beef cattle, dairy cows, pigs, sheep, and more",
        "unit": "count"
    },
    "🐔 Poultry": {
        "columns": ("top_poultry", "top_poultry_value"),
        "color": "Oranges",
        "description": "Poultry production including chickens, turkeys, ducks, geese",
        "unit": "count"
    },
    "🌱 All Crops": {
        "columns": ("top_crop", "top_crop_value"),
        "color": "YlGn",
        "description": "Overall dominant crop across all categories",
        "unit": "hectares"
    },
    "🐮 All Animals": {
        "columns": ("top_animal", "top_animal_value"),
        "color": "BuPu",
        "description": "Overall dominant animal production (livestock + poultry)",
        "unit": "count"
    },
}

# ====================================================================
# Sidebar
# ====================================================================
st.sidebar.image("https://em-content.zobj.net/source/twitter/376/maple-leaf_1f341.png", width=100)
st.sidebar.title("Agricultural Atlas")
st.sidebar.markdown("**Canada**")
st.sidebar.markdown("---")

# Category selector
selected_category = st.sidebar.selectbox(
    "Select Product Category",
    options=list(CATEGORIES.keys()),
    help="Choose which agricultural category to visualize"
)

category_info = CATEGORIES[selected_category]
col_name, col_value = category_info["columns"]
unit = category_info["unit"]

st.sidebar.markdown(f"*{category_info['description']}*")
st.sidebar.markdown("---")

# ====================================================================
# Analysis Mode & Product Selection
# ====================================================================
st.sidebar.markdown("🔎 Analysis Mode")

analysis_mode = st.sidebar.radio(
    "Choose visualization type",
    ["Top Product per Region", "Specific Product Distribution"],
    help="View dominant products or distribution of a specific product"
)

selected_product = None
selected_product_col = None
selected_product_label = None

if analysis_mode == "Specific Product Distribution":
    # Get products for the selected category
    if selected_category in CATEGORY_PRODUCTS:
        available_products = CATEGORY_PRODUCTS[selected_category]
        
        # Create reverse mapping (label -> code)
        product_options = {v: k for k, v in available_products.items()}
        
        selected_product_label = st.sidebar.selectbox(
            "Select Product",
            options=sorted(product_options.keys()),
            help="Choose a specific product to visualize its distribution"
        )
        
        selected_product = product_options[selected_product_label]
        
        # Handle _HA suffix for greenhouse products
        if selected_category == "🏡 Greenhouse Products":
            selected_product_col = f"{selected_product}_HA"
        else:
            selected_product_col = selected_product
        
        st.sidebar.success(f"🔎 Showing: **{selected_product_label}**")
    elif selected_category in ["🌱 All Crops", "🐮 All Animals"]:
        st.sidebar.info("💡 Select a specific category (Field Crops, Vegetables, etc.) to view individual products")
        analysis_mode = "Top Product per Region"  # Force back to top product mode

st.sidebar.markdown("---")

# ====================================================================
# Province filter
# ====================================================================
st.sidebar.markdown("### 🗺️ Region Filter")

# Get unique provinces from ADM2 data
if 'Province' in adm2_data.columns:
    available_provinces = sorted(adm2_data['Province'].dropna().unique().tolist())
    available_provinces.insert(0, "All Canada")
    
    selected_provinces = st.sidebar.multiselect(
        "Select Province(s)",
        options=available_provinces,
        default=["All Canada"],
        help="Select one or more provinces to filter the map"
    )
    
    # Filter data
    if "All Canada" in selected_provinces or len(selected_provinces) == 0:
        map_data = adm2_data.copy()
    else:
        map_data = adm2_data[adm2_data['Province'].isin(selected_provinces)].copy()
        st.sidebar.info(f"Showing {len(map_data)} regions")
else:
    st.sidebar.error("Province field not found in data.")
    selected_provinces = ["All Canada"]
    map_data = adm2_data.copy()

# Filter out regions with no data for selected category/product
if analysis_mode == "Top Product per Region":
    map_data = map_data[map_data[col_value] > 0].copy()
    display_col = col_name
    value_col = col_value
else:
    # For specific product, filter by that column
    if selected_product_col and selected_product_col in map_data.columns:
        map_data[selected_product_col] = pd.to_numeric(map_data[selected_product_col], errors='coerce').fillna(0)
        map_data = map_data[map_data[selected_product_col] > 0].copy()
        display_col = selected_product_col
        value_col = selected_product_col
    else:
        st.error(f"Product column '{selected_product_col}' not found in data")
        st.stop()

# Display options
st.sidebar.markdown("---")
st.sidebar.markdown("### Display Options")
show_values = st.sidebar.checkbox("Show values on hover", value=True)
show_boundaries = st.sidebar.checkbox("Show province boundaries", value=True)

# ====================================================================
# Main Header
# ====================================================================
region_text = "All Canada" if "All Canada" in selected_provinces or len(selected_provinces) == 0 else ", ".join(selected_provinces)

if analysis_mode == "Top Product per Region":
    st.title(f"{selected_category.split()[1] if len(selected_category.split()) > 1 else selected_category} Distribution")
else:
    st.title(f"{selected_product_label} Distribution")

st.markdown(f"**Region:** {region_text}")

# Key metrics row
if len(map_data) > 0:
    if analysis_mode == "Top Product per Region":
        # Top region for category
        top_region_row = map_data.nlargest(1, col_value).iloc[0]
        top_region_name = top_region_row['shapeName']
        top_region_product = top_region_row[col_name]
        top_region_value = top_region_row[col_value]
        top_region_province = top_region_row.get('Province', 'N/A')
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            st.metric(
                "Top Region", 
                top_region_name,
                help=f"Region with highest production in {selected_category}"
            )
        
        with col_m2:
            st.metric(
                "Top Product", 
                top_region_product,
                help=f"Dominant product in {top_region_name}"
            )
        
        with col_m3:
            st.metric(
                f"Top Value ({unit})", 
                f"{top_region_value:,.0f}",
                help=f"Production value in {top_region_name}"
            )
        
        st.caption(f"📍 {top_region_name}, {top_region_province} produces {top_region_value:,.0f} {unit} of {top_region_product}")
    
    else:
        # For specific product distribution
        top_region_row = map_data.nlargest(1, value_col).iloc[0]
        top_region_name = top_region_row['shapeName']
        top_region_value = top_region_row[value_col]
        top_region_province = top_region_row.get('Province', 'N/A')
        
        total_production = map_data[value_col].sum()
        num_regions = len(map_data)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            st.metric(
                f"Total Production", 
                f"{total_production:,.0f} {unit}",
                help=f"Total {selected_product_label} production across all regions"
            )
        
        with col_m2:
            st.metric(
                "Top Region", 
                top_region_name,
                help=f"Region with highest {selected_product_label} production"
            )
        
        with col_m3:
            st.metric(
                f"Top Value", 
                f"{top_region_value:,.0f} {unit}",
                help=f"Production in {top_region_name}"
            )
        
        st.caption(f"{top_region_name}, {top_region_province} leads with {top_region_value:,.0f} {unit} of {selected_product_label} • {num_regions} regions producing")
    
    st.markdown("---")
else:
    if analysis_mode == "Top Product per Region":
        st.warning(f"⚠️ No data available for {selected_category} in the selected region(s).")
    else:
        st.warning(f"⚠️ No data available for {selected_product_label} in the selected region(s).")
    st.stop()

# ====================================================================
# Map and Legend Layout
# ====================================================================
col_map, col_legend = st.columns([3, 1])

# ====================================================================
# Map Column
# ====================================================================
with col_map:
    st.subheader("Interactive Map")
    
    # Calculate map center and zoom
    if len(selected_provinces) > 0 and "All Canada" not in selected_provinces:
        center_lat = map_data.geometry.centroid.y.mean()
        center_lon = map_data.geometry.centroid.x.mean()
        zoom_start = 6
    else:
        center_lat = 56.1304
        center_lon = -106.3468
        zoom_start = 4
    
    # Create folium map with dark basemap
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        control_scale=True
    )
    
    # Add province boundaries (if enabled)
    if show_boundaries and 'Province' in map_data.columns:
        province_boundaries = map_data.dissolve(by='Province', as_index=False)
        
        folium.GeoJson(
            province_boundaries,
            name="Province Boundaries",
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': '#ffffff',
                'weight': 2,
                'fillOpacity': 0,
                'opacity': 0.6
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['Province'],
                aliases=['Province:'],
                localize=True
            )
        ).add_to(m)
    
    if analysis_mode == "Top Product per Region":
        # CATEGORICAL COLOR MAP
        unique_products = map_data[col_name].dropna().unique()
        
        if len(unique_products) <= 10:
            colors = [
                '#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b',
                '#e6f598', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2'
            ]
        else:
            import matplotlib.cm as cm_mpl
            import matplotlib.colors as mcolors
            cmap = cm_mpl.get_cmap('tab20', len(unique_products))
            colors = [mcolors.rgb2hex(cmap(i)) for i in range(len(unique_products))]
        
        product_colors = dict(zip(unique_products, colors[:len(unique_products)]))
        
        def style_function(feature):
            product = feature['properties'].get(col_name)
            color = product_colors.get(product, '#888888')
            return {
                'fillColor': color,
                'fillOpacity': 0.6,
                'color': color,
                'weight': 1.5,
                'opacity': 0.9
            }
        
        def highlight_function(feature):
            product = feature['properties'].get(col_name)
            color = product_colors.get(product, '#888888')
            return {
                'fillColor': color,
                'fillOpacity': 0.85,
                'weight': 3,
                'color': '#ffffff',
                'opacity': 1
            }
        
        tooltip_fields = ["shapeName", col_name, col_value]
        tooltip_aliases = ["Region:", "Product:", f"Value ({unit}):"]
        
        if "Province" in map_data.columns:
            tooltip_fields.insert(1, "Province")
            tooltip_aliases.insert(1, "Province:")
    
    else:
        # CONTINUOUS COLOR SCALE
        vmin = map_data[value_col].min()
        vmax = map_data[value_col].max()
        
        # Category-specific color scales
        continuous_color_scales = {
            "🌾 Field Crops": ['#ffffe5', '#fff7bc', '#fee391', '#fec44f', '#fe9929', '#ec7014', '#cc4c02', '#993404', '#662506'],
            "🥬 Vegetables": ['#f7fcf5', '#e5f5e0', '#c7e9c0', '#a1d99b', '#74c476', '#41ab5d', '#238b45', '#006d2c', '#00441b'],
            "🍓 Fruits & Berries": ['#fff5f0', '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a', '#ef3b2c', '#cb181d', '#a50f15', '#67000d'],
            "🏡 Greenhouse Products": ['#fcfbfd', '#efedf5', '#dadaeb', '#bcbddc', '#9e9ac8', '#807dba', '#6a51a3', '#54278f', '#3f007d'],
            "🐄 Livestock": ['#ffffe5', '#fff7bc', '#fee391', '#fec44f', '#fe9929', '#ec7014', '#cc4c02', '#993404', '#662506'],
            "🐔 Poultry": ['#fff5eb', '#fee6ce', '#fdd0a2', '#fdae6b', '#fd8d3c', '#f16913', '#d94801', '#a63603', '#7f2704'],
        }
        
        colors = continuous_color_scales.get(selected_category, ['#ffffe5', '#fff7bc', '#fee391', '#fec44f', '#fe9929', '#ec7014', '#cc4c02', '#993404', '#662506'])
        
        colormap = cm.LinearColormap(
            colors=colors,
            vmin=vmin,
            vmax=vmax
        )
        
        def style_function(feature):
            value = feature['properties'].get(value_col, 0)
            return {
                'fillColor': colormap(value) if value > 0 else '#cccccc',
                'fillOpacity': 0.7,
                'color': '#666666',
                'weight': 1,
                'opacity': 0.8
            }
        
        def highlight_function(feature):
            return {
                'fillOpacity': 0.9,
                'weight': 3,
                'color': '#ffffff'
            }
        
        tooltip_fields = ["shapeName", value_col]
        tooltip_aliases = ["Region:", f"{selected_product_label} ({unit}):"]
        
        if "Province" in map_data.columns:
            tooltip_fields.insert(1, "Province")
            tooltip_aliases.insert(1, "Province:")
    
    # Add GeoJson layer
    folium.GeoJson(
        map_data,
        name="Agricultural Products",
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: rgba(255, 255, 255, 0.95);
                color: #333;
                border: 2px solid #333;
                border-radius: 5px;
                padding: 8px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            """,
        ) if show_values else None
    ).add_to(m)
    
    folium.LayerControl().add_to(m)
    st_folium(m, width=None, height=600, returned_objects=[])

# ====================================================================
# Legend Column
# ====================================================================
with col_legend:
    if analysis_mode == "Top Product per Region":
        st.subheader("Legend")
        
        for product, color in product_colors.items():
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown(
                    f'<div style="width: 20px; height: 20px; background-color: {color}; '
                    f'border: 1px solid #333; border-radius: 3px;"></div>',
                    unsafe_allow_html=True
                )
            with col2:
                st.markdown(f"**{product}**")
        
        st.caption(f"{len(product_colors)} unique products")
    
    else:
        st.subheader("Color Scale")
        st.markdown(f"**{selected_product_label}**")
        st.markdown(f"Range: {map_data[value_col].min():,.0f} - {map_data[value_col].max():,.0f} {unit}")
        
        # Get the color scale for this category
        continuous_color_scales = {
            "🌾 Field Crops": ['#ffffe5', '#fff7bc', '#fee391', '#fec44f', '#fe9929', '#ec7014', '#cc4c02', '#993404', '#662506'],
            "🥬 Vegetables": ['#f7fcf5', '#e5f5e0', '#c7e9c0', '#a1d99b', '#74c476', '#41ab5d', '#238b45', '#006d2c', '#00441b'],
            "🍓 Fruits & Berries": ['#fff5f0', '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a', '#ef3b2c', '#cb181d', '#a50f15', '#67000d'],
            "🏡 Greenhouse Products": ['#fcfbfd', '#efedf5', '#dadaeb', '#bcbddc', '#9e9ac8', '#807dba', '#6a51a3', '#54278f', '#3f007d'],
            "🐄 Livestock": ['#ffffe5', '#fff7bc', '#fee391', '#fec44f', '#fe9929', '#ec7014', '#cc4c02', '#993404', '#662506'],
            "🐔 Poultry": ['#fff5eb', '#fee6ce', '#fdd0a2', '#fdae6b', '#fd8d3c', '#f16913', '#d94801', '#a63603', '#7f2704'],
        }
        
        colors = continuous_color_scales.get(selected_category, ['#ffffe5', '#fff7bc', '#fee391', '#fec44f', '#fe9929', '#ec7014', '#cc4c02', '#993404', '#662506'])
        gradient_str = ', '.join(colors)
        
        st.markdown(f"""
        <div style="background: linear-gradient(to right, {gradient_str}); 
                    height: 30px; border-radius: 5px; border: 1px solid #333; margin: 10px 0;"></div>
        <div style="display: flex; justify-content: space-between; font-size: 11px;">
            <span>Low</span>
            <span>Medium</span>
            <span>High</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption(f"{len(map_data)} regions")

# ====================================================================
# Additional Visualizations
# ====================================================================
st.markdown("---")
st.subheader("Production Analysis")

viz_col1, viz_col2 = st.columns(2)

with viz_col1:
    # Bar chart
    if analysis_mode == "Top Product per Region":
        product_summary = map_data.groupby(col_name)[col_value].sum().sort_values(ascending=False).head(10)
        chart_title = f"Top 10 Products by Total Value ({unit})"
    else:
        product_summary = map_data.nlargest(10, value_col)[[value_col, 'shapeName']].set_index('shapeName')[value_col]
        chart_title = f"Top 10 Regions - {selected_product_label} ({unit})"
    
    fig_bar = px.bar(
        x=product_summary.values,
        y=product_summary.index,
        orientation='h',
        labels={'x': f'Total Value ({unit})', 'y': 'Region' if analysis_mode != "Top Product per Region" else 'Product'},
        title=chart_title,
        color=product_summary.values,
        color_continuous_scale=category_info["color"]
    )
    fig_bar.update_layout(
        showlegend=False,
        height=450,
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

#### Bubble 
with viz_col2:
    # Bubble Chart - Province Statistics
    
    # Calculate statistics per province
    province_stats = map_data.groupby('Province').agg({
        value_col: ['sum', 'mean', 'count']
    }).reset_index()
    province_stats.columns = ['Province', 'Total_Production', 'Avg_Per_Region', 'Num_Regions']
    
    # Sort by total production and get top 10
    province_stats = province_stats.nlargest(10, 'Total_Production')
    
    fig_bubble = px.scatter(
        province_stats,
        x='Num_Regions',
        y='Total_Production',
        size='Avg_Per_Region',
        color='Province',
        hover_name='Province',
        hover_data={
            'Num_Regions': ':,',
            'Total_Production': ':,.0f',
            'Avg_Per_Region': ':,.0f',
            'Province': False
        },
        labels={
            'Num_Regions': 'Number of Producing Regions',
            'Total_Production': f'Total Production ({unit})',
            'Avg_Per_Region': f'Avg per Region ({unit})'
        },
        title=f"Provincial Overview: Scale vs Intensity",
        size_max=60
    )
    
    fig_bubble.update_layout(
        showlegend=True,
        height=450,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=9)
        ),
        xaxis=dict(gridcolor='lightgray'),
        yaxis=dict(gridcolor='lightgray')
    )
    
    st.plotly_chart(fig_bubble, use_container_width=True)
    st.caption("💡 **Bubble size** = Average production per region | **X-axis** = Number of regions | **Y-axis** = Total production")

# ====================================================================
# Sankey Diagram - Full Width
# ====================================================================
if 'Province' in map_data.columns and len(map_data) > 5:
    st.markdown("---")
    
    if analysis_mode == "Top Product per Region":
        # Get top province-product combinations
        sankey_data = map_data.groupby(['Province', col_name])[col_value].sum().reset_index()
        sankey_data = sankey_data.nlargest(25, col_value)  # Increased to 25 for more detail
        
        # Create source and target lists
        provinces = sankey_data['Province'].unique().tolist()
        products = sankey_data[col_name].unique().tolist()
        
        # Create node labels (provinces first, then products)
        labels = provinces + products
        
        # Create source, target, and value lists
        source = [provinces.index(p) for p in sankey_data['Province']]
        target = [len(provinces) + products.index(p) for p in sankey_data[col_name]]
        values = sankey_data[col_value].tolist()
        
        # Color nodes by type
        node_colors = ['#3498db'] * len(provinces) + ['#e74c3c'] * len(products)
        
        fig_sankey = {
            'data': [{
                'type': 'sankey',
                'node': {
                    'pad': 20,
                    'thickness': 25,
                    'line': {'color': 'white', 'width': 1},
                    'label': labels,
                    'color': node_colors,
                    'customdata': [f'{unit}' for _ in labels],
                    'hovertemplate': '%{label}<br>%{value:,.0f} ' + unit + '<extra></extra>'
                },
                'link': {
                    'source': source,
                    'target': target,
                    'value': values,
                    'color': 'rgba(255,255,255,0.3)',  # White with transparency
                    'hovertemplate': '%{source.label} → %{target.label}<br>%{value:,.0f} ' + unit + '<extra></extra>'
                }
            }],
            'layout': {
                'title': {
                    'text': f'Province to Product Flow (Top 25 Combinations)',
                    'font': {'size': 18}
                },
                'height': 600,
                'font': {'size': 11},
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)'
            }
        }
        
        st.plotly_chart(fig_sankey, use_container_width=True)
        
        st.caption("💡 **How to read:** Flow thickness represents production volume. Blue nodes are provinces, red nodes are products. Hover for details.")
        
    else:
        # For specific product, show province -> region sankey
        sankey_data = map_data.nlargest(25, value_col)[['Province', 'shapeName', value_col]].copy()
        
        provinces = sankey_data['Province'].unique().tolist()
        regions = sankey_data['shapeName'].unique().tolist()
        
        labels = provinces + regions
        
        source = [provinces.index(p) for p in sankey_data['Province']]
        target = [len(provinces) + regions.index(r) for r in sankey_data['shapeName']]
        values = sankey_data[value_col].tolist()
        
        node_colors = ['#3498db'] * len(provinces) + ['#2ecc71'] * len(regions)
        
        fig_sankey = {
            'data': [{
                'type': 'sankey',
                'node': {
                    'pad': 20,
                    'thickness': 25,
                    'line': {'color': 'white', 'width': 1},
                    'label': labels,
                    'color': node_colors,
                    'hovertemplate': '%{label}<br>%{value:,.0f} ' + unit + '<extra></extra>'
                },
                'link': {
                    'source': source,
                    'target': target,
                    'value': values,
                    'color': 'rgba(255,255,255,0.3)',  # White with transparency
                    'hovertemplate': '%{source.label} → %{target.label}<br>%{value:,.0f} ' + unit + '<extra></extra>'
                }
            }],
            'layout': {
                'title': {
                    'text': f'{selected_product_label} Production: Province to Region Flow (Top 25)',
                    'font': {'size': 18}
                },
                'height': 600,
                'font': {'size': 11},
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)'
            }
        }
        
        st.plotly_chart(fig_sankey, use_container_width=True)
        
        st.caption("💡 **How to read:** Flow thickness represents production volume. Blue nodes are provinces, green nodes are regions. Hover for details.")

# ====================================================================
# Province Comparison
# ====================================================================
if 'Province' in map_data.columns and (len(selected_provinces) > 1 or "All Canada" in selected_provinces):
    st.markdown("---")
    st.subheader("Provincial Comparison")
    
    province_summary = map_data.groupby('Province').agg({
        value_col: 'sum',
        'ADM2_KEY': 'count'
    }).rename(columns={
        value_col: 'Total Production',
        'ADM2_KEY': 'Number of Regions'
    }).sort_values('Total Production', ascending=False)
    
    province_color_map = {
        'Ontario': '#1f77b4',
        'Quebec / Québec': '#3498db',
        'British Columbia / Colombie-Britannique': '#2ecc71',
        'Alberta': '#e74c3c',
        'Manitoba': '#f39c12',
        'Saskatchewan': '#f1c40f',
        'Nova Scotia / Nouvelle-Écosse': '#9b59b6',
        'New Brunswick / Nouveau-Brunswick': '#e67e22',
        'Newfoundland and Labrador / Terre-Neuve-et-Labrador': '#16a085',
        'Prince Edward Island / Île-du-Prince-Édouard': '#e91e63',
        'Northwest Territories / Territoires du Nord-Ouest': '#34495e',
        'Nunavut': '#95a5a6',
        'Yukon': '#d35400',
    }
    
    fig_province = px.bar(
        province_summary.head(10),
        y=province_summary.head(10).index,
        x='Total Production',
        orientation='h',
        title=f"Top 10 Provinces by Total Production ({unit})",
        labels={'y': 'Province', 'Total Production': f'Total Value ({unit})'},
        text='Total Production',
        color=province_summary.head(10).index,
        color_discrete_map=province_color_map
    )
    fig_province.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig_province.update_layout(
        height=500,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    st.plotly_chart(fig_province, use_container_width=True)

# ====================================================================
# Data Table
# ====================================================================
with st.expander("📋 View Full Data Table"):
    if analysis_mode == "Top Product per Region":
        display_columns = ["shapeName", "Province", col_name, col_value]
    else:
        display_columns = ["shapeName", "Province", value_col]
    
    display_columns = [c for c in display_columns if c in map_data.columns]
    table_data = map_data[display_columns].sort_values(display_columns[-1], ascending=False).reset_index(drop=True)
    
    st.dataframe(table_data, use_container_width=True, height=400)
    
    csv = table_data.to_csv(index=False)
    region_suffix = "_".join([p.lower().replace(" ", "_") for p in selected_provinces]) if "All Canada" not in selected_provinces else "canada"
    filename = f"{region_suffix}_{selected_product_label.lower().replace(' ', '_')}.csv" if analysis_mode != "Top Product per Region" else f"{region_suffix}_{selected_category.lower().replace(' ', '_')}.csv"
    
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )

# ====================================================================
# Footer
# ====================================================================
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("**📊 Data Source**")
    st.markdown("Statistics Canada Agricultural Census")

with footer_col2:
    st.markdown("**Analysis & Development**")
    st.markdown("Rex Devereux")

with footer_col3:
    st.markdown("**🔗 Links**")
    st.markdown("[GitHub](https://github.com/rexdevereux) | [LinkedIn](https://www.linkedin.com/in/rex-devereux/)")

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 About")
st.sidebar.info(
    """
    This interactive atlas visualizes agricultural production patterns across 
    Canada at the ADM2 (Census Division) level.
    
    Data is allocated to regions using area-weighted proportional assignment 
    for farms that cross administrative boundaries.
    """
)

st.sidebar.markdown("### 💡 How to Use")
st.sidebar.markdown("""
1. Select a product category
2. Choose analysis mode:
   - **Top Product per Region**: See dominant products
   - **Specific Product**: See distribution
3. Filter by province (optional)
4. Toggle province boundaries
5. Hover over regions for details
6. Download data as needed
""")

st.sidebar.markdown("---")
st.sidebar.caption("🍁 Powered by Streamlit | Data: Statistics Canada")