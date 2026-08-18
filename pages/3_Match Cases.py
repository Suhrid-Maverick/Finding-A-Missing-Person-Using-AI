import streamlit as st

from pages.helper import db_queries, match_algo, train_model
from pages.helper import emailer

# Distance threshold used in match_algo — keep in sync
DISTANCE_THRESHOLD = 3.0


def confidence_from_distance(distance: float) -> float:
    """Convert a KNN distance to a 0–100 confidence percentage."""
    return max(0.0, min(100.0, (1.0 - distance / DISTANCE_THRESHOLD) * 100))


def case_viewer(registered_case_id: str, public_case_id: str, confidence: float = None):
    try:
        case_details = db_queries.get_registered_case_detail(registered_case_id)[0]
        data_col, image_col = st.columns(2)

        # case_details: (name, complainant_mobile, complainant_email, age, last_seen, birth_marks)
        labels = ["Name", "Mobile", "Age", "Last Seen", "Birth Marks"]
        display_values = [
            case_details[0],  # name
            case_details[1],  # complainant_mobile
            case_details[3],  # age
            case_details[4],  # last_seen
            case_details[5],  # birth_marks
        ]
        for text, value in zip(labels, display_values):
            data_col.write(f"**{text}:** {value}")

        if confidence is not None:
            data_col.write("")
            data_col.markdown("**Match Confidence**")
            data_col.progress(
                confidence / 100,
                text=f"{confidence:.0f}% confidence",
            )

        db_queries.update_found_status(registered_case_id, public_case_id)
        st.success("✅ Status updated. Case is now marked as Found.")

        try:
            image_col.image(
                "./resources/" + registered_case_id + ".jpg",
                width=80,
                use_container_width=False,
            )
        except Exception as img_err:
            st.warning(f"Could not load image: {str(img_err)}")

        # Send email to complainant
        sent = emailer.send_match_notification(registered_case_id, case_details)
        if sent:
            st.info(f"📧 Notification sent to {case_details[2]}")

    except Exception as e:
        import traceback

        traceback.print_exc()
        st.error(f"❌ Something went wrong: {str(e)}. Please check logs.")


if "login_status" not in st.session_state:
    st.write("You don't have access to this page")

elif st.session_state["login_status"]:
    user = st.session_state.user

    is_admin = st.session_state.get("role", "").lower() == "admin"

    st.title("Check for Match")

    if not is_admin:
        st.info("🔒 Only Admins can trigger the matching process.")
    else:
        col1, col2 = st.columns(2)
        refresh_bt = col1.button("🔄 Refresh")
        st.write("---")

        if refresh_bt:
            with st.spinner("Fetching data and training model..."):
                result = train_model.train(user)
                matched_ids = match_algo.match()

                if matched_ids["status"]:
                    if not matched_ids["result"]:
                        st.info("No matches found.")
                    else:
                        for matched_id, submitted_cases in matched_ids[
                            "result"
                        ].items():
                            for submitted_case in submitted_cases:
                                if isinstance(submitted_case, tuple):
                                    submitted_case_id, distance = submitted_case
                                    conf = confidence_from_distance(distance)
                                else:
                                    submitted_case_id = submitted_case
                                    conf = None

                                case_viewer(matched_id, submitted_case_id, conf)
                                st.write("---")
                else:
                    st.info("No matches found.")

else:
    st.write("You don't have access to this page")
