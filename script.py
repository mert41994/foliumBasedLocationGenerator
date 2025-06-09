import streamlit as st
import json
import folium
from streamlit_folium import st_folium
from datetime import datetime, timezone

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

# JSON dosyasını oku ve GeoJSON formatına dönüştür
with open('.venv/package.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

if "data" not in data or not isinstance(data["data"], list):
    st.error("JSON dosyasında 'data' anahtarı yok veya bir liste değil!")
else:
    vessels = data["data"]
    features = []
    for vessel in vessels:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [vessel["lng"], vessel["lat"]]
            },
            "properties": {
                "vessel_name": vessel.get("vessel_name"),
                "mmsi": vessel.get("mmsi"),
                "imo": vessel.get("imo"),
                "received": vessel.get("received")
            }
        })

    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    # Haritanın merkezini ilk geminin koordinatlarına ayarla
    first_coords = features[0]["geometry"]["coordinates"]
    my_map = folium.Map(location=[first_coords[1], first_coords[0]], zoom_start=4)

    # Renk listesi (gemi sayısı kadar döner)
    colors = ["red", "blue", "green", "purple", "orange", "darkred", "lightred", 
              "beige", "darkblue", "darkgreen", "cadetblue", "darkpurple", "white", 
              "pink", "lightblue", "lightgreen", "gray", "black", "lightgray"]

    def time_ago(received_str):
        try:
            received_time = datetime.strptime(received_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            diff = now - received_time
            seconds = int(diff.total_seconds())
            if seconds < 60:
                return f"{seconds} saniye önce"
            elif seconds < 3600:
                minutes = seconds // 60
                return f"{minutes} dakika önce"
            elif seconds < 86400:
                hours = seconds // 3600
                return f"{hours} saat önce"
            else:
                days = seconds // 86400
                return f"{days} gün önce"
        except Exception:
            return received_str

    # Grupları vtype'a göre ayır
    groups = {}
    for vessel in vessels:
        vtype = vessel.get("vtype", "Diğer")
        if vtype not in groups:
            groups[vtype] = []
        groups[vtype].append(vessel)

    # Her grup için ayrı FeatureGroup ve markerlar ekle
    for idx, (vtype, group_vessels) in enumerate(groups.items()):
        fg = folium.FeatureGroup(name=f"Vessel Type {vtype}")
        for v_idx, vessel in enumerate(group_vessels):
            folium.Marker(
                location=[vessel["lat"], vessel["lng"]],
                popup=folium.Popup(
                    f"Vessel Name: {vessel.get('vessel_name')}<br>"
                    f"MMSI: {vessel.get('mmsi')}<br>"
                    f"IMO: {vessel.get('imo')}<br>"
                    f"Son güncelleme: {time_ago(vessel.get('received'))}",
                    max_width=300
                ),
                tooltip=vessel.get("vessel_name"),
                icon=folium.Icon(color=colors[(idx + v_idx) % len(colors)])
            ).add_to(fg)
        fg.add_to(my_map)

    folium.LayerControl().add_to(my_map)

    with st.spinner("Harita yükleniyor, lütfen bekleyin..."):
        st_folium(my_map, width=1720, height=980)

    # Tüm gemileri listele
    for vessel in vessels:
        st.write("Vessel Name:", vessel.get("vessel_name"))
        st.write("MMSI:", vessel.get("mmsi"))
        st.write("IMO:", vessel.get("imo"))
        st.write("Son güncelleme:", time_ago(vessel.get("received")))
        st.markdown("---")

