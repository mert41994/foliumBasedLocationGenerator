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
        .main .block-container { padding: 0 !important; margin: 0 !important; max-width: 100vw; }
        .stApp { padding: 0 !important; margin: 0 !important; }
        iframe { height: 99vh !important; width: 100vw !important; }
        header {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stToolbar"] {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True
)

# Başlık
st.markdown('<h1 style="margin-bottom:0;">OnePowership Realtime Ship Tracking</h1><a href="http://192.168.3.122:51280">OnePowership</a>', unsafe_allow_html=True)

# JSON dosyasını oku ve GeoJSON formatına dönüştür
with open('.venv/datas.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

if "data" not in data or not isinstance(data["data"], list):
    st.error("JSON dosyasında 'data' anahtarı yok veya bir liste değil!")
else:
    vessels = data["data"]

    # Haritanın merkezini gemilerin ortalamasına göre ayarla
    if vessels:
        avg_lat = sum(v["lat"] for v in vessels) / len(vessels)
        avg_lng = sum(v["lng"] for v in vessels) / len(vessels)
        map_center = [avg_lat, avg_lng]
    else:
        map_center = [0.0, 0.0]

    my_map = folium.Map(
        location=map_center,
        zoom_start=3,
        tiles="Cartodb Positron",
        width="95%",
        height="100%"
    )

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
        fg = folium.FeatureGroup(name=f"Gemi Tipi {vtype}")
        for v_idx, vessel in enumerate(group_vessels):
            lat = vessel["lat"]
            lng = vessel["lng"]
            popup_html = (
                f"<b>Vessel Name:</b> {vessel.get('vessel_name')}<br>"
                f"<b>MMSI:</b> {vessel.get('mmsi')}<br>"
                f"<b>IMO:</b> {vessel.get('imo')}<br>"
                f"<b>Latitude:</b> {lat}<br>"
                f"<b>Longitude:</b> {lng}<br>"
                f"<b>Course:</b> {vessel.get('course', '')}<br>"
                f"<b>Speed:</b> {vessel.get('speed', '')} kn<br>"
                f"<b>Nav Status:</b> {vessel.get('nav_status', '')}<br>"
                f"<b>Last Update:</b> {time_ago(vessel.get('received'))}"
            )
            tooltip_html = (
                f"{vessel.get('vessel_name')}<br>"
                f"Lat: {lat}, Lng: {lng}<br>"
                f"Speed: {vessel.get('speed', '')} kn"
            )
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=tooltip_html,
                icon=folium.Icon(color=colors[(idx + v_idx) % len(colors)])
            ).add_to(fg)
        fg.add_to(my_map)

    folium.LayerControl().add_to(my_map)

    # Harita için responsive bir div ile padding ekle
    st.markdown(
        """
        <style>
        html, body, .stApp {
            overflow-x: hidden !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100vw !important;
        }
        .map-container {
            width: 100%;
            height: 80%;
            margin: 0 auto;
            padding-left: 10px;
            padding-right: 10px;
            box-sizing: border-box;
        }
        .map-container iframe {
            width: 100% !important;
            height: 100% !important;
            min-height: 400px;
            margin: 0 auto;
            box-sizing: border-box;
            display: block;
        }
        </style>
        <div class="map-container">
        """,
        unsafe_allow_html=True
    )

    with st.spinner("Harita yükleniyor, lütfen bekleyin..."):
        st_folium(my_map, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Tüm gemileri açılır kapanır şekilde listele
    with st.expander("Gemi Listesi", expanded=False):
        for vessel in vessels:
            st.markdown(
                f"""
                <div style="padding:8px 0; border-bottom:1px solid #eee;">
                    <b>Vessel Name:</b> {vessel.get('vessel_name')}<br>
                    <b>MMSI:</b> {vessel.get('mmsi')}<br>
                    <b>IMO:</b> {vessel.get('imo')}<br>
                    <b>Latitude:</b> {vessel.get('lat')}<br>
                    <b>Longitude:</b> {vessel.get('lng')}<br>
                    <b>Course:</b> {vessel.get('course', '')}<br>
                    <b>Speed:</b> {vessel.get('speed', '')} kn<br>
                    <b>Nav Status:</b> {vessel.get('nav_status', '')}<br>
                    <b>Last Update:</b> {time_ago(vessel.get('received'))}
                </div>
                """,
                unsafe_allow_html=True
            )

