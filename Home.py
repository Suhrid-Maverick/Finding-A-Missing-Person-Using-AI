import yaml
import base64
import streamlit as st
from yaml import SafeLoader
import streamlit_authenticator as stauth

from pages.helper import db_queries

# Initialise DB once at startup
db_queries.create_db()

if "login_status" not in st.session_state:
    st.session_state["login_status"] = False

try:
    with open("login_config.yml") as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Configuration file 'login_config.yml' not found")
    st.stop()

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# ── Custom login page styling ─────────────────────────────────────────────────
if not st.session_state.get("authentication_status"):
    st.markdown(
        """
        <style>
        /* Hide default Streamlit header on login page */
        [data-testid="stHeader"] { background: transparent; }

        /* Login card wrapper */
        .login-card {
            max-width: 420px;
            margin: 0 auto;
            padding: 2.5rem 2rem;
            border-radius: 16px;
            background: #ffffff;
            box-shadow: 0 4px 24px rgba(0,0,0,0.10);
        }

        /* Banner */
        .login-banner {
            text-align: center;
            padding: 2rem 0 1.5rem 0;
        }
        .login-banner h1 {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1a237e;
            margin-bottom: 0.25rem;
        }
        .login-banner .tagline {
            font-size: 0.95rem;
            color: #546e7a;
            margin-top: 0;
        }
        .login-banner .badge {
            display: inline-block;
            background: #e3f2fd;
            color: #1565c0;
            border-radius: 20px;
            padding: 4px 14px;
            font-size: 0.78rem;
            font-weight: 600;
            margin-top: 0.5rem;
            letter-spacing: 0.5px;
        }

        /* Style all text inputs inside the form */
        div[data-testid="stTextInput"] input {
            border-radius: 8px !important;
            border: 1.5px solid #cfd8dc !important;
            padding: 10px 14px !important;
            font-size: 0.97rem !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #1565c0 !important;
            box-shadow: 0 0 0 2px rgba(21,101,192,0.15) !important;
        }

        /* Style the submit button */
        div[data-testid="stForm"] button[kind="primaryFormSubmit"],
        div[data-testid="stForm"] button[type="submit"] {
            background-color: #1565c0 !important;
            color: white !important;
            border-radius: 8px !important;
            width: 100% !important;
            padding: 0.6rem !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            border: none !important;
        }
        div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
        div[data-testid="stForm"] button[type="submit"]:hover {
            background-color: #0d47a1 !important;
        }
        </style>

        <div class="login-banner">
            <h1>Missing Person Identification System</h1>
            <p class="tagline">Officer &amp; Admin Portal — Secure Login</p>
            <span class="badge">AI-Powered Facial Recognition</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Perform login — updates session state authentication_status
authenticator.login(location="main")

# ── Post-login dashboard ──────────────────────────────────────────────────────
if st.session_state.get("authentication_status"):
    authenticator.logout("Logout", "sidebar")

    st.session_state["login_status"] = True
    user_info = config["credentials"]["usernames"][st.session_state["username"]]
    st.session_state["user"] = st.session_state["username"]

    role = user_info.get("role", "Officer")
    st.session_state["role"] = role

    role_colour = "#e74c3c" if role.lower() == "admin" else "#27ae60"
    role_badge = (
        f'<span style="background:{role_colour}; color:white; padding:3px 10px; '
        f'border-radius:12px; font-size:13px; font-weight:600">{role}</span>'
    )

    st.write(
        f'<p style="color:grey; text-align:left; font-size:45px">{user_info["name"]}</p>',
        unsafe_allow_html=True,
    )

    st.write(
        f'<p style="color:grey; text-align:left; font-size:20px">'
        f'{user_info["area"]}, {user_info["city"]}&nbsp;&nbsp;{role_badge}</p>',
        unsafe_allow_html=True,
    )

    st.write("---")

    found_cases = db_queries.get_registered_cases_count(st.session_state["user"], "F")
    non_found_cases = db_queries.get_registered_cases_count(st.session_state["user"], "NF")

    found_col, not_found_col = st.columns(2)
    found_col.metric("Found Cases Count", value=len(found_cases))
    not_found_col.metric("Not Found Cases Count", value=len(non_found_cases))

    st.write("---")

    # ── Cases map ─────────────────────────────────────────────────────────────
    st.subheader("Cases by City")

    try:
        import folium
        from streamlit_folium import st_folium

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
            "Faridabad": (28.4089, 77.3178),
            "Allahabad": (25.4358, 81.8463),
            "Prayagraj": (25.4358, 81.8463),
            "Mathura": (27.4924, 77.6737),
            "Bareilly": (28.3670, 79.4304),
            "Aligarh": (27.8974, 78.0880),
            "Moradabad": (28.8386, 78.7733),
            "Saharanpur": (29.9680, 77.5460),
            "Gorakhpur": (26.7606, 83.3732),
            "Firozabad": (27.1591, 78.3957),
            "Jhansi": (25.4484, 78.5685),
            "Ghaziabad": (28.6692, 77.4538),
            "Ludhiana": (30.9010, 75.8573),
            "Jalandhar": (31.3260, 75.5762),
            "Dehradun": (30.3165, 78.0322),
            "Haridwar": (29.9457, 78.1642),
            "Rishikesh": (30.0869, 78.2676),
            "Shimla": (31.1048, 77.1734),
            "Bathinda": (30.2110, 74.9455),
            "Unknown": (20.5937, 78.9629),
        }

        counts = db_queries.get_case_counts_by_city()

        if not counts:
            st.info("No cases with city data yet. Add a city when registering cases.")
        else:
            m = folium.Map(
                location=[20.5937, 78.9629], zoom_start=5, tiles="CartoDB positron"
            )

            for city, data in counts.items():
                total = data["found"] + data["not_found"]
                coords = CITY_COORDS.get(city)
                if coords is None:
                    for key, val in CITY_COORDS.items():
                        if key.lower() == city.lower():
                            coords = val
                            break
                if coords is None:
                    continue

                color = "#e74c3c" if data["not_found"] > 0 else "#27ae60"
                tooltip = (
                    f"<b>{city}</b><br>"
                    f"Total: {total} &nbsp;|&nbsp; "
                    f"Not Found: {data['not_found']} &nbsp;|&nbsp; "
                    f"Found: {data['found']}"
                )
                folium.CircleMarker(
                    location=coords,
                    radius=max(8, min(40, total * 5)),
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.6,
                    tooltip=folium.Tooltip(tooltip),
                ).add_to(m)

            st_folium(m, width="100%", height=420, returned_objects=[])

            st.markdown(
                '<span style="color:#e74c3c;">●</span> Has unresolved cases &nbsp;&nbsp;'
                '<span style="color:#27ae60;">●</span> All resolved &nbsp;&nbsp;'
                "Circle size = number of cases",
                unsafe_allow_html=True,
            )

    except ImportError:
        st.info("Install `folium` and `streamlit-folium` to enable the map.")

elif st.session_state.get("authentication_status") == False:
    st.error("❌ Username or password is incorrect. Please try again.")
elif st.session_state.get("authentication_status") is None:
    st.session_state["login_status"] = False
