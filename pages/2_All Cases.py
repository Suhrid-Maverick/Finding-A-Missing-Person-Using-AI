import streamlit as st
import pandas as pd

from pages.helper import db_queries, emailer

PAGE_SIZE = 10


def _reset_page(key: str):
    """Reset pagination when filters change."""
    st.session_state[key] = 0


# ── Case viewers ─────────────────────────────────────────────────────────────


def case_viewer(case, is_admin: bool = False):
    case = list(case)
    case_id = case.pop(0)  # index 0 → id

    matched_with_id = ""
    try:
        matched_with_id = case.pop(-1) or ""  # last item → matched_with
        matched_with_id = matched_with_id.replace("{", "").replace("}", "").strip()
    except Exception:
        matched_with_id = ""

    matched_with_details = None
    if matched_with_id:
        matched_with_details = db_queries.get_public_case_detail(matched_with_id)

    # remaining: [name, age, status, last_seen]
    data_col, image_col, matched_col = st.columns([3, 1, 2])

    status_value = None
    for label, value in zip(["Name", "Age", "Status", "Last Seen"], case):
        if value == "F":
            status_value = "F"
            value = "Found"
        elif value == "NF":
            value = "Not Found"
        data_col.write(f"**{label}:** {value}")

    try:
        image_col.image(
            "./resources/" + str(case_id) + ".jpg",
            width=120,
            use_container_width=False,
        )
    except Exception:
        image_col.caption("No image")

    if matched_with_details:
        matched_col.write(f"**Location:** {matched_with_details[0][0]}")
        matched_col.write(f"**Submitted By:** {matched_with_details[0][1]}")
        matched_col.write(f"**Mobile:** {matched_with_details[0][2]}")
        matched_col.write(f"**Birth Marks:** {matched_with_details[0][3]}")

    # Admin: resend notification email for Found cases
    if is_admin and status_value == "F":
        if st.button("📧 Send Notification Email", key=f"email_{case_id}"):
            case_detail_rows = db_queries.get_registered_case_detail(case_id)
            if case_detail_rows:
                sent = emailer.send_match_notification(case_id, case_detail_rows[0])
                if sent:
                    complainant_email = (
                        case_detail_rows[0][2] if len(case_detail_rows[0]) > 2 else None
                    )
                    st.success(
                        f"✅ Email sent to {complainant_email or 'configured address'}."
                    )
                else:
                    st.warning("⚠️ Email could not be sent. Check SMTP configuration.")

    # Admin: Edit / Delete
    if is_admin:
        with st.expander("✏️ Edit / Delete"):
            with st.form(key=f"edit_{case_id}"):
                new_name = st.text_input("Name", value=case[0] if case else "")
                new_last_seen = st.text_input(
                    "Last Seen", value=case[3] if len(case) > 3 else ""
                )
                save_btn = st.form_submit_button("💾 Save Changes")
                if save_btn:
                    db_queries.update_registered_case(
                        case_id, {"name": new_name, "last_seen": new_last_seen}
                    )
                    st.success("Updated!")
                    st.rerun()

            confirm = st.checkbox(
                "I confirm I want to permanently delete this case",
                key=f"del_confirm_{case_id}",
            )
            if st.button("🗑️ Delete Case", key=f"del_{case_id}", type="primary"):
                if confirm:
                    db_queries.delete_registered_case(case_id)
                    st.success("Case deleted!")
                    st.rerun()
                else:
                    st.warning("Please tick the confirmation box first.")

    st.write("---")


def public_case_viewer(case: list) -> None:
    case = list(case)
    case_id = str(case.pop(0))

    data_col, image_col, _ = st.columns(3)
    for label, value in zip(
        ["Status", "Location", "Mobile", "Birth Marks", "Submitted on", "Submitted by"],
        case,
    ):
        if label == "Status":
            value = "Found" if value == "F" else "Not Found"
        data_col.write(f"**{label}:** {value}")

    try:
        image_col.image(
            "./resources/" + case_id + ".jpg",
            width=120,
            use_container_width=False,
        )
    except Exception:
        image_col.caption("No image")

    st.write("---")


# ── Pagination helper ─────────────────────────────────────────────────────────


def paginate(items: list, page_key: str):
    """Return the current page slice and render Prev / Next controls."""
    total = len(items)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = st.session_state.get(page_key, 0)
    page = max(0, min(page, total_pages - 1))
    st.session_state[page_key] = page

    paginated = items[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]

    def render_controls():
        col_prev, col_info, col_next = st.columns([1, 3, 1])
        if col_prev.button("◀ Prev", disabled=page == 0, key=f"{page_key}_prev"):
            st.session_state[page_key] = page - 1
            st.rerun()
        col_info.markdown(
            f"<div style='text-align:center; padding-top:6px'>Page {page + 1} of {total_pages} &nbsp;·&nbsp; {total} record(s)</div>",
            unsafe_allow_html=True,
        )
        if col_next.button(
            "Next ▶", disabled=page >= total_pages - 1, key=f"{page_key}_next"
        ):
            st.session_state[page_key] = page + 1
            st.rerun()

    return paginated, render_controls


# ── Main page ─────────────────────────────────────────────────────────────────

if "login_status" not in st.session_state:
    st.write("You don't have access to this page")

elif st.session_state["login_status"]:
    user = st.session_state.user
    is_admin = st.session_state.get("role", "").lower() == "admin"

    st.title("View Submitted Cases")

    # ── Filters ──────────────────────────────────────────────────────────────
    filter_col, search_col, date_col = st.columns([2, 3, 2])

    status = filter_col.selectbox(
        "Filter by Status",
        options=["All", "Not Found", "Found", "Public Cases"],
        on_change=_reset_page,
        args=("page_reg",),
    )

    search_name = search_col.text_input(
        "🔍 Search by Name",
        placeholder="Type a name to filter…",
        on_change=_reset_page,
        args=("page_reg",),
    )

    date_filter = date_col.date_input("Filter by Date (on or after)", value=None)

    st.write("---")

    # ── Public Cases view ────────────────────────────────────────────────────
    if status == "Public Cases":
        cases_data = list(db_queries.fetch_public_cases(False, status))

        if search_name:
            cases_data = [
                c for c in cases_data if search_name.lower() in str(c).lower()
            ]

        if date_filter:
            # submitted_on is at index 5 (0-indexed) in public case tuples
            cases_data = [
                c for c in cases_data if c[5] and str(c[5])[:10] >= str(date_filter)
            ]

        if cases_data:
            df = pd.DataFrame(
                cases_data,
                columns=[
                    "ID",
                    "Status",
                    "Location",
                    "Mobile",
                    "Birth Marks",
                    "Submitted On",
                    "Submitted By",
                ],
            )
            df["Status"] = (
                df["Status"].map({"F": "Found", "NF": "Not Found"}).fillna(df["Status"])
            )
            st.download_button(
                "📥 Download as CSV",
                data=df.to_csv(index=False),
                file_name="public_cases.csv",
                mime="text/csv",
            )

        if not cases_data:
            st.info("No public cases found.")
        else:
            paginated, render_controls = paginate(cases_data, "page_pub")
            for case in paginated:
                public_case_viewer(case)
            render_controls()

    # ── Registered Cases view ─────────────────────────────────────────────────
    else:
        cases_data = list(db_queries.fetch_registered_cases(user, status))

        if search_name:
            cases_data = [
                c for c in cases_data if search_name.lower() in str(c[1]).lower()
            ]

        if date_filter:
            # Filter registered cases by submitted_on; requires a separate query
            # Use DB-level filtering: re-query with date constraint
            from sqlmodel import Session, select
            from pages.helper.db_queries import engine
            from pages.helper.data_models import RegisteredCases
            import datetime

            date_dt = datetime.datetime.combine(date_filter, datetime.time.min)
            with Session(engine) as session:
                q = (
                    select(
                        RegisteredCases.id,
                        RegisteredCases.name,
                        RegisteredCases.age,
                        RegisteredCases.status,
                        RegisteredCases.last_seen,
                        RegisteredCases.matched_with,
                    )
                    .where(RegisteredCases.submitted_by == user)
                    .where(RegisteredCases.submitted_on >= date_dt)
                )
                if status != "All":
                    status_filter = "F" if status == "Found" else "NF"
                    q = q.where(RegisteredCases.status == status_filter)
                cases_data = list(session.exec(q).all())

            if search_name:
                cases_data = [
                    c for c in cases_data if search_name.lower() in str(c[1]).lower()
                ]

        if cases_data:
            df = pd.DataFrame(
                cases_data,
                columns=["ID", "Name", "Age", "Status", "Last Seen", "Matched With"],
            )
            df["Status"] = (
                df["Status"].map({"F": "Found", "NF": "Not Found"}).fillna(df["Status"])
            )
            st.download_button(
                "📥 Download as CSV",
                data=df.to_csv(index=False),
                file_name="registered_cases.csv",
                mime="text/csv",
            )

        if not cases_data:
            st.info("No cases found.")
        else:
            paginated, render_controls = paginate(cases_data, "page_reg")
            for case in paginated:
                case_viewer(case, is_admin=is_admin)
            render_controls()

else:
    st.write("You don't have access to this page")
