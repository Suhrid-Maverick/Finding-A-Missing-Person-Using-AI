import streamlit as st

from pages.helper import db_queries

st.set_page_config(page_title="Cases Map")

if "login_status" not in st.session_state:
    st.write("You don't have access to this page")

elif st.session_state["login_status"]:
    st.title("Cases by City — India Map")

    try:
        import folium
        from streamlit_folium import st_folium
    except ImportError:
        st.error(
            "❌ Map dependencies not installed. Run: `pip install folium streamlit-folium`"
        )
        st.stop()

    # Approximate lat/lon for major Indian cities
    CITY_COORDS = {
        "Delhi": (28.6139, 77.2090),
        "New Delhi": (28.6139, 77.2090),
        "Mumbai": (19.0760, 72.8777),
        "Bengaluru": (12.9716, 77.5946),
        "Bangalore": (12.9716, 77.5946),
        "Hyderabad": (17.3850, 78.4867),
        "Chennai": (13.0827, 80.2707),
        "Kolkata": (22.5726, 88.3639),
        "Pune": (18.5204, 73.8567),
        "Ahmedabad": (23.0225, 72.5714),
        "Jaipur": (26.9124, 75.7873),
        "Lucknow": (26.8467, 80.9462),
        "Kanpur": (26.4499, 80.3319),
        "Nagpur": (21.1458, 79.0882),
        "Indore": (22.7196, 75.8577),
        "Thane": (19.2183, 72.9781),
        "Bhopal": (23.2599, 77.4126),
        "Visakhapatnam": (17.6868, 83.2185),
        "Patna": (25.5941, 85.1376),
        "Vadodara": (22.3072, 73.1812),
        "Surat": (21.1702, 72.8311),
        "Noida": (28.5355, 77.3910),
        "Gurgaon": (28.4595, 77.0266),
        "Gurugram": (28.4595, 77.0266),
        "Chandigarh": (30.7333, 76.7794),
        "Coimbatore": (11.0168, 76.9558),
        "Kochi": (9.9312, 76.2673),
        "Agra": (27.1767, 78.0081),
        "Varanasi": (25.3176, 82.9739),
        "Meerut": (28.9845, 77.7064),
        "Raipur": (21.2514, 81.6296),
        "Ranchi": (23.3441, 85.3096),
        "Guwahati": (26.1445, 91.7362),
        "Jodhpur": (26.2389, 73.0243),
        "Amritsar": (31.6340, 74.8723),
        "Jabalpur": (23.1815, 79.9864),
        "Haora": (22.5958, 88.2636),
        "Faridabad": (28.4089, 77.3178),
        "Unknown": (20.5937, 78.9629),
    }

    counts = db_queries.get_case_counts_by_city()

    if not counts:
        st.info(
            "No cases with city data registered yet. Add a city when registering cases."
        )
        st.stop()

    # Build map centered on India
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="CartoDB positron")

    placed = 0
    skipped = []
    for city, data in counts.items():
        total = data["found"] + data["not_found"]
        coords = CITY_COORDS.get(city)
        if coords is None:
            # Try case-insensitive lookup
            city_lower = city.lower()
            for key, val in CITY_COORDS.items():
                if key.lower() == city_lower:
                    coords = val
                    break
        if coords is None:
            skipped.append(city)
            continue

        radius = max(8, min(40, total * 5))
        color = "#e74c3c" if data["not_found"] > 0 else "#27ae60"
        tooltip = (
            f"<b>{city}</b><br>"
            f"Total: {total}<br>"
            f"Not Found: {data['not_found']}<br>"
            f"Found: {data['found']}"
        )
        folium.CircleMarker(
            location=coords,
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            tooltip=folium.Tooltip(tooltip),
        ).add_to(m)
        placed += 1

    st_folium(m, width=900, height=550)

    # Legend
    st.markdown(
        """
        <div style="font-size:0.85rem; color:#555; margin-top:8px;">
        <span style="color:#e74c3c;">●</span> Has unresolved cases &nbsp;&nbsp;
        <span style="color:#27ae60;">●</span> All cases resolved &nbsp;&nbsp;
        Circle size = number of cases
        </div>
        """,
        unsafe_allow_html=True,
    )

    if skipped:
        st.caption(f"Cities without map coordinates (not shown): {', '.join(skipped)}")

    # Summary table
    st.write("---")
    st.subheader("City Summary")
    rows = [
        {
            "City": city,
            "Total": d["found"] + d["not_found"],
            "Found": d["found"],
            "Not Found": d["not_found"],
        }
        for city, d in counts.items()
    ]
    import pandas as pd

    df = pd.DataFrame(rows).sort_values("Total", ascending=False).reset_index(drop=True)
    st.dataframe(df, use_container_width=True)

else:
    st.write("You don't have access to this page")
