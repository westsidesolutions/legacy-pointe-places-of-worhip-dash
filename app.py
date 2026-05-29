import html
from pathlib import Path

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

st.set_page_config(page_title="Prospect Atlas", layout="wide")
st.title("Prospect Atlas")

#CSV_PATH = Path(__file__).parent / "prospects.csv"
#CSV_PATH = Path(__file__).parent / "synagogues_property_size_full.csv"
#CSV_PATH = Path(__file__).parent / "Synagogue Place of Worship Prospects - Sheet3.csv"
#CSV_PATH = Path(__file__).parent / "Place of Worship Prospects - Sheet1.csv"
CSV_PATH = Path(__file__).parent / "Place of Worship Prospects - Delivery.csv"

DISPLAY_COLS = [
    "name", "address", "city", "zip_code", "primary_type",
    "phone", "website", "rating", "review_count",
    "AreaBuilding", "AreaLotSF", "AreaLotAcres",
    "Contact1_NameFirst", "Contact1_NameLast", "Contact1_Title", "Contact1_Email",
    "Contact2_NameFirst", "Contact2_NameLast", "Contact2_Title", "Contact2_Email",
]

if not CSV_PATH.exists():
    st.error(f"Data file missing: {CSV_PATH.name}")
    st.stop()

df = pd.read_csv(CSV_PATH)

with st.sidebar:
    st.header("Filters")

    verticals = sorted(df["vertical"].dropna().unique())
    selected_verticals = st.multiselect("Vertical", verticals)

    states = sorted(df["state"].dropna().unique())
    selected_states = st.multiselect("State", states)

    cities = sorted(df["city"].dropna().unique())
    selected_cities = st.multiselect("City", cities)

    zips = sorted(df["zip_code"].dropna().unique())
    selected_zips = st.multiselect("ZIP code", zips)

    primary_types = sorted(df["primary_type"].dropna().unique())
    selected_primary_types = st.multiselect("Primary type", primary_types)

filtered = df
if selected_verticals:
    filtered = filtered[filtered["vertical"].isin(selected_verticals)]
if selected_states:
    filtered = filtered[filtered["state"].isin(selected_states)]
if selected_cities:
    filtered = filtered[filtered["city"].isin(selected_cities)]
if selected_zips:
    filtered = filtered[filtered["zip_code"].isin(selected_zips)]
if selected_primary_types:
    filtered = filtered[filtered["primary_type"].isin(selected_primary_types)]

map_df = filtered.dropna(subset=["latitude", "longitude"])

if len(map_df) == 0:
    st.info("No prospects match your filters.")
else:
    center_lat = map_df["latitude"].mean()
    center_lon = map_df["longitude"].mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles="cartodbpositron")
    cluster = MarkerCluster().add_to(m)

    for _, row in map_df.iterrows():
        name = html.escape(str(row.get("name") or "Unknown"))
        addr = html.escape(str(row.get("address") or ""))
        phone = html.escape(str(row.get("phone") or ""))
        website = row.get("website") or ""
        rating = row.get("rating")
        reviews = row.get("review_count")

        popup_html = f"<b>{name}</b><br>{addr}"
        if phone:
            popup_html += f"<br>📞 <a href='tel:{phone}'>{phone}</a>"
        if website:
            safe_url = html.escape(str(website), quote=True)
            popup_html += f"<br>🌐 <a href='{safe_url}' target='_blank'>Website</a>"
        if rating is not None:
            popup_html += f"<br>⭐ {rating} ({reviews or 0} reviews)"

        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=name,
        ).add_to(cluster)

    bounds = [
        [map_df["latitude"].min(), map_df["longitude"].min()],
        [map_df["latitude"].max(), map_df["longitude"].max()],
    ]
    m.fit_bounds(bounds)

    st_folium(m, height=500, use_container_width=True, returned_objects=[])

st.write(f"**{len(filtered):,} of {len(df):,} prospects** match your filters")
#st.dataframe(filtered)
#display_df = filtered.drop(columns=["latitude", "longitude"], errors="ignore")
#st.dataframe(display_df)
display_df = filtered[[c for c in DISPLAY_COLS if c in filtered.columns]]
st.dataframe(display_df)
