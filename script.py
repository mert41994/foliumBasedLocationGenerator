import json
import os
import folium
from folium.plugins import MarkerCluster  # type: ignore
import pandas as pd
import numpy as np

with open('.venv/package.json', 'r', encoding='utf-8') as file:
    package_data = json.load(file)
    vessel_data = package_data.get("data", {})  # JSON içindeki "data" alanını çekiyoruz

# JSON içindeki gemi bilgilerini alıyoruz
lat = vessel_data.get("lat", 0)
lng = vessel_data.get("lng", 0)
vessel_name = vessel_data.get("vessel_name", "Bilinmiyor")
mmsi = vessel_data.get("mmsi", "Bilinmiyor")
imo = vessel_data.get("imo", "Bilinmiyor")

# Haritanın başlangıç koordinatını, geminin konumunu baz alarak ayarlayabilir veya sabit belirleyebilirsiniz.
coordination = [lat, lng]
my_map = folium.Map(location=coordination, zoom_start=4)

# Gemi konumuna marker ekliyoruz
vessel_coord = [lat, lng]
folium.Marker(
    vessel_coord,
    popup=f'{vessel_name}\nMMSI: {mmsi}\nIMO: {imo}',
    tooltip=vessel_name,
    icon=folium.Icon(color="green")
).add_to(my_map)

# Gemi konumunu gösterecek küçük bir çember ekliyoruz
folium.Circle(vessel_coord, radius=10).add_to(my_map)

my_map.save('map.html')
print("Harita başarıyla oluşturuldu ve 'map.html' olarak kaydedildi.")