import os
import uuid
import json

import streamlit as st

from pages.helper.data_models import RegisteredCases
from pages.helper import db_queries
from pages.helper.utils import image_obj_to_numpy, detect_all_faces, draw_face_boxes

st.set_page_config(page_title="Register New Case")


if "login_status" not in st.session_state:
    st.write("You don't have access to this page")

elif st.session_state["login_status"]:
    user = st.session_state.user

    st.title("Register New Case")

    image_col, form_col = st.columns(2)
    save_flag = 0

    with image_col:
        image_obj = st.file_uploader(
            "Upload Photo", type=["jpg", "jpeg", "png"], key="new_case"
        )

        if image_obj:
            # Cache detection results in session state keyed by file identity
            file_key = f"{image_obj.name}_{image_obj.size}"

            if st.session_state.get("nc_file_key") != file_key:
                # New image uploaded — run detection and cache results
                unique_id = str(uuid.uuid4())
                uploaded_file_path = "./resources/" + unique_id + ".jpg"

                with open(uploaded_file_path, "wb") as f:
                    f.write(image_obj.read())
                image_obj.seek(0)

                with st.spinner("Detecting faces..."):
                    image_numpy = image_obj_to_numpy(image_obj)
                    faces = detect_all_faces(image_numpy, max_faces=5)

                if not faces:
                    # Clean up orphaned image
                    if os.path.exists(uploaded_file_path):
                        os.remove(uploaded_file_path)
                    st.session_state["nc_file_key"] = file_key
                    st.session_state["nc_faces"] = []
                    st.session_state["nc_image_numpy"] = None
                    st.session_state["nc_unique_id"] = None
                    st.session_state["nc_uploaded_path"] = None
                else:
                    st.session_state["nc_file_key"] = file_key
                    st.session_state["nc_faces"] = faces
                    st.session_state["nc_image_numpy"] = image_numpy
                    st.session_state["nc_unique_id"] = unique_id
                    st.session_state["nc_uploaded_path"] = uploaded_file_path

            # Read cached state
            faces = st.session_state.get("nc_faces", [])
            image_numpy = st.session_state.get("nc_image_numpy")
            unique_id = st.session_state.get("nc_unique_id")

            if not faces:
                st.error(
                    "❌ No face detected in this image.\n\n"
                    "**Tips:** use a well-lit, front-facing photo with one clear face visible."
                )
                selected_face_idx = None
            elif len(faces) == 1:
                # Single face — highlight and auto-select
                annotated = draw_face_boxes(image_numpy, faces, selected_idx=0)
                st.image(annotated, use_container_width=True)
                st.success("✅ 1 face detected.")
                selected_face_idx = 0
            else:
                # Multiple faces — let user pick
                st.warning(
                    f"⚠️ {len(faces)} faces detected. Select the person to register:"
                )
                options = [f"Face {i + 1}" for i in range(len(faces))]
                choice = st.radio(
                    "Select face", options, horizontal=True, key="nc_face_choice"
                )
                selected_face_idx = options.index(choice)
                annotated = draw_face_boxes(
                    image_numpy, faces, selected_idx=selected_face_idx
                )
                st.image(annotated, use_container_width=True)
                st.info(f"Using **Face {selected_face_idx + 1}** for registration.")
        else:
            # File uploader cleared — reset cached state
            for k in [
                "nc_file_key",
                "nc_faces",
                "nc_image_numpy",
                "nc_unique_id",
                "nc_uploaded_path",
            ]:
                st.session_state.pop(k, None)
            selected_face_idx = None
            unique_id = None
            faces = []

    # ── Registration form ─────────────────────────────────────────────────────
    face_ready = image_obj and faces and selected_face_idx is not None

    if face_ready:
        with form_col.form(key="new_case_form"):
            name = st.text_input("Name *")
            father_name = st.text_input("Father's Name")
            age = st.number_input("Age", min_value=1, max_value=120, value=10, step=1)
            mobile_number = st.text_input("Mobile Number (10 digits)")
            adhaar_card = st.text_input("Aadhaar Card (12 digits)")
            address = st.text_input("Address")
            city = st.text_input("City *")
            birthmarks = st.text_input("Birth Marks")
            last_seen = st.text_input("Last Seen *")
            description = st.text_area("Description (optional)")

            st.markdown("**Complainant Details**")
            complainant_name = st.text_input("Complainant Name *")
            complainant_phone = st.text_input("Complainant Phone * (10 digits)")
            complainant_email = st.text_input("Complainant Email")

            submit_bt = st.form_submit_button("Save Case")

            if submit_bt:
                errors = []
                if not name.strip():
                    errors.append("❌ Name is required.")
                if not last_seen.strip():
                    errors.append("❌ Last Seen location is required.")
                if not complainant_name.strip():
                    errors.append("❌ Complainant Name is required.")
                if not complainant_phone.strip():
                    errors.append("❌ Complainant Phone is required.")
                elif (
                    not complainant_phone.strip().isdigit()
                    or len(complainant_phone.strip()) != 10
                ):
                    errors.append("❌ Complainant Phone must be exactly 10 digits.")
                if mobile_number.strip() and (
                    not mobile_number.strip().isdigit()
                    or len(mobile_number.strip()) != 10
                ):
                    errors.append("❌ Mobile Number must be exactly 10 digits.")
                if adhaar_card.strip() and (
                    not adhaar_card.strip().isdigit() or len(adhaar_card.strip()) != 12
                ):
                    errors.append("❌ Aadhaar Card must be exactly 12 digits.")

                if errors:
                    for err in errors:
                        st.error(err)
                else:
                    selected_landmarks = faces[selected_face_idx]["landmarks"]
                    new_case_details = RegisteredCases(
                        id=unique_id,
                        submitted_by=user,
                        name=name.strip(),
                        father_name=father_name.strip(),
                        age=str(age),
                        complainant_mobile=complainant_phone.strip(),
                        complainant_name=complainant_name.strip(),
                        complainant_email=complainant_email.strip() or None,
                        face_mesh=json.dumps(selected_landmarks),
                        adhaar_card=adhaar_card.strip(),
                        birth_marks=birthmarks.strip(),
                        address=address.strip(),
                        city=city.strip() or None,
                        last_seen=last_seen.strip(),
                        description=description.strip() or None,
                        status="NF",
                        matched_with="",
                    )
                    db_queries.register_new_case(new_case_details)
                    save_flag = 1

        if save_flag:
            st.success("✅ Case registered successfully.")

else:
    st.write("You don't have access to this page")
