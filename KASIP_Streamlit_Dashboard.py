import json
import folium
from streamlit_folium import st_folium

fmap = folium.Map(location=[6.02, 102.22], zoom_start=9, tiles="CartoDB dark_matter")

# 1. Add Kelantan District Boundary Polygons (if kelantan_districts.geojson is in your repo)
try:
    with open("kelantan_districts.geojson", "r", encoding="utf-8") as f:
        kelantan_gj = json.load(f)

    # Detect the first property field name for hover tooltip
    sample_props = kelantan_gj["features"][0].get("properties", {}) if kelantan_gj.get("features") else {}
    label_field = next(
        (k for k in sample_props.keys() if "name" in k.lower() or "district" in k.lower() or "adm2" in k.lower()),
        next(iter(sample_props.keys()), None),
    )

    def zone_style(feature):
        props_text = str(feature.get("properties", {})).upper()
        fill_col = "#3987e8"
        for dist_key, meta in DISTRICT_META.items():
            if dist_key in props_text:
                fill_col = meta["hex"]
                break
        return {
            "fillColor": fill_col,
            "color": "#cbd6e8",
            "weight": 1.5,
            "fillOpacity": 0.32,
        }

    geojson_kwargs = {
        "data": kelantan_gj,
        "name": "Kelantan Districts",
        "style_function": zone_style,
    }
    if label_field:
        geojson_kwargs["tooltip"] = folium.GeoJsonTooltip(fields=[label_field], aliases=["District:"])

    folium.GeoJson(**geojson_kwargs).add_to(fmap)
except Exception:
    pass

# 2. Keep the Interactive Circle Markers & Pop-Ups on Top
for d_name, meta in DISTRICT_META.items():
    stu_n = int(counts_by_dist.get(d_name, 0))
    pop_txt = (
        f"<b>{d_name}</b><br>"
        f"Zone: <b>{meta['zone']}</b> ({meta['access']})<br>"
        f"Students: <b>{stu_n}</b> | Centres: <b>{meta['centres']}</b><br>"
        f"Centre: {meta['recommended_centre']}"
    )
    folium.CircleMarker(
        location=[meta["lat"], meta["lon"]],
        radius=13,
        color="#ffffff",
        weight=2,
        fill=True,
        fill_color=meta["hex"],
        fill_opacity=0.9,
        tooltip=d_name,
        popup=folium.Popup(pop_txt, max_width=260),
    ).add_to(fmap)
