import streamlit as st
import json
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="OnePowership Canlı Gemi Takibi", layout="wide")

# Streamlit'in ekstra boşluklarını kaldırmak için stil ekle
st.markdown(
    """
    <style>
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100vw;
        }
        .stApp {
            padding: 0 !important;
            margin: 0 !important;
        }
        iframe {
            height: 98vh !important;
            width: 100vw !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Başlık
st.markdown('<h1 style="margin-bottom:0;">OnePowership Canlı Gemi Takibi</h1>', unsafe_allow_html=True)

# GeoJSON dosyasını oku
with open('.venv/package.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

# İlk feature'ı al
feature = geojson_data['features'][0]
props = feature['properties']
coords = feature['geometry']['coordinates']

lat = coords[1]
lng = coords[0]

coordination = [lat, lng]
my_map = folium.Map(location=coordination, zoom_start=4)

folium.GeoJson(
    geojson_data,
    name="Vessel",
    tooltip=folium.GeoJsonTooltip(fields=["vessel_name", "mmsi", "imo"]),
    popup=folium.GeoJsonPopup(fields=["vessel_name", "mmsi", "imo"])
).add_to(my_map)

# Folium haritasını tam ekran gösterirken yükleniyor animasyonu ekle
with st.spinner("Harita yükleniyor, lütfen bekleyin..."):
    st_folium(my_map, width=1920, height=980)

st.write("Vessel Name:", props.get("vessel_name"))
st.write("MMSI:", props.get("mmsi"))
st.write("IMO:", props.get("imo"))
st.write("Son güncelleme:", props.get("received"))

