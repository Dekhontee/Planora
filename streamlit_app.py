
import streamlit as st
import requests
from datetime import datetime
import json

st.set_page_config(page_title="Planora — Study Plan Generator", layout="wide")
st.title("📚 Planora — AI Study Plan Generator")

st.markdown("Upload a syllabus (PDF) or paste the syllabus text, choose your exam date, hours per day, and plan length.")

# --- Simple account UI ---
if 'user' not in st.session_state:
    st.session_state['user'] = None
    st.session_state['user_id'] = None

with st.expander("Account (register / login)"):
    colu1, colu2, colu3 = st.columns([2,2,1])
    with colu1:
        form_username = st.text_input("Username", key="ui_username")
    with colu2:
        form_password = st.text_input("Password", type="password", key="ui_password")
    with colu3:
        if st.button("Register"):
            if not form_username or not form_password:
                st.warning("Enter username and password to register")
            else:
                try:
                    url = "http://localhost:8000/register"
                    r = requests.post(url, data={"username": form_username, "password": form_password}, timeout=5)
                    # Retry with trailing slash if 404
                    if r.status_code == 404:
                        url = "http://localhost:8000/register/"
                        r = requests.post(url, data={"username": form_username, "password": form_password}, timeout=5)
                    r.raise_for_status()
                    j = r.json()
                    if j.get('error'):
                        st.error(j.get('error'))
                    else:
                        st.success(f"Registered user id {j.get('user_id')}")
                except requests.exceptions.HTTPError as he:
                    status = getattr(he.response, 'status_code', 'N/A')
                    st.error(f"Register failed: HTTP {status} - {he}")
                except Exception as e:
                    st.error(f"Register failed: {e}")
        if st.button("Login"):
            if not form_username or not form_password:
                st.warning("Enter username and password to login")
            else:
                try:
                    url = "http://localhost:8000/login"
                    r = requests.post(url, data={"username": form_username, "password": form_password}, timeout=5)
                    if r.status_code == 404:
                        url = "http://localhost:8000/login/"
                        r = requests.post(url, data={"username": form_username, "password": form_password}, timeout=5)
                    r.raise_for_status()
                    j = r.json()
                    if j.get('error'):
                        st.error(j.get('error'))
                    else:
                        st.session_state['user'] = form_username
                        st.session_state['user_id'] = j.get('user_id')
                        st.success(f"Logged in as {form_username} (id {j.get('user_id')})")
                except requests.exceptions.HTTPError as he:
                    status = getattr(he.response, 'status_code', 'N/A')
                    st.error(f"Login failed: HTTP {status} - {he}")
                except Exception as e:
                    st.error(f"Login failed: {e}")

    # Admin: key rotation (only visible to user_id == 1)
    if st.session_state.get('user_id') == 1:
        with st.expander("Admin: Key Rotation (Dangerous)"):
            st.markdown("**Rotate encryption keys for stored refresh tokens.** Provide a new Fernet key (base64).")
            new_key = st.text_input("New Fernet Key (base64)")
            backup = st.checkbox("Backup existing ciphertexts before rotation", value=True)
            if st.button("Rotate Keys"):
                if not new_key:
                    st.warning("Enter the new key")
                else:
                    try:
                        r = requests.post("http://localhost:8000/rotate_keys", data={"new_key": new_key, "backup": str(bool(backup))}, timeout=30)
                        r.raise_for_status()
                        st.success("Rotation completed")
                        st.json(r.json())
                    except Exception as e:
                        st.error(f"Key rotation failed: {e}")


with st.form("plan_form"):
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Syllabus PDF (optional)")
    with col2:
        syllabus_text = st.text_area("Or paste syllabus text (optional)", height=120)

    # Extra input options: exam type, manual topics, or image with topics
    exam_type = st.radio("Exam type", options=["final", "regular_test"], index=0, help="Choose 'regular_test' for a single midterm/quiz or 'final' for cumulative final exams")
    manual_topics = st.text_area("Or enter topics manually (one per line)", height=100)
    topics_image = st.file_uploader("Upload image with topics (optional)", type=["png","jpg","jpeg"])
    
    col3, col4, col5, col6 = st.columns(4)
    with col3:
        exam_date = st.date_input("Exam date", value=datetime.today())
    with col4:
        hours_per_day = st.number_input("Hours available per day", min_value=0.5, max_value=12.0, value=2.0, step=0.5)
    with col5:
        plan_length = st.number_input("Plan length (days)", min_value=1, max_value=365, value=14, step=1)
    with col6:
        course_type = st.text_input("Course type (e.g., Chemistry, Calculus)", value="General")
    # OCR GPU option
    use_ocr_gpu = st.checkbox("Use OCR GPU (EasyOCR) if available", value=False)
    # Review-day fraction slider (percent)
    default_frac = 8 if exam_type == "final" else 4
    review_frac_pct = st.slider("Review days (% of total days)", min_value=0, max_value=30, value=default_frac, step=1, help="Fraction of total days to reserve as review days (0-30%).")
    
    submit = st.form_submit_button("🚀 Generate Plan", use_container_width=True)

if submit:
    with st.spinner("Generating your personalized study plan..."):
        url = "http://localhost:8000/plan"
        files = {}
        data = {
            "exam_date": str(exam_date),
                "use_ocr_gpu": str(use_ocr_gpu),
            "exam_type": exam_type,
            "hours_per_day": hours_per_day,
            "plan_length": plan_length,
            "course_type": course_type,
            "syllabus_text": syllabus_text,
            "topics_text": manual_topics,
        }
        # send review fraction as decimal (0.0-0.3)
        try:
            data['review_day_fraction'] = float(review_frac_pct) / 100.0
        except Exception:
            pass
        if uploaded_file is not None:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data.pop("syllabus_text", None)
        if topics_image is not None:
            # attach image as separate file field
            files["image"] = (topics_image.name, topics_image.getvalue(), topics_image.type)
            data.pop("topics_text", None)
        try:
            r = requests.post(url, data=data, files=files, timeout=30)
            r.raise_for_status()
            plan = r.json()
        except Exception as e:
            st.error(f"Error contacting backend: {e}")
            plan = None

    # Show OCR availability notice
    try:
        status = requests.get("http://localhost:8000/ocr_status", timeout=2).json()
        if not status.get('tesseract_binary') and not status.get('easyocr_installed'):
            st.warning("OCR is not available: install the Tesseract binary or EasyOCR for image uploads. See README for instructions.")
        elif not status.get('tesseract_binary') and status.get('easyocr_installed'):
            st.info("Tesseract binary missing; EasyOCR is available as fallback. You can enable EasyOCR GPU in the form (if supported).")
    except Exception:
        # ignore failures to contact backend ocr_status
        pass

    if plan:
        if plan.get("error"):
            st.error(f"❌ {plan.get('error')}")
        else:
            st.success(f"✅ Plan generated — {plan.get('plan_length')} days, {plan.get('hours_per_day')} hrs/day, {plan.get('topics_count')} topics")
            
            # Display summary stats
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Total Days", plan.get('plan_length'))
            with col2:
                st.metric("Hours/Day", plan.get('hours_per_day'))
            with col3:
                st.metric("Topics", plan.get('topics_count'))
            with col4:
                review_days = sum(1 for d in plan.get("plan", []) if d.get("is_review"))
                st.metric("Review Days", review_days)
            with col5:
                st.metric("Review %", f"{int(review_frac_pct)}%")
            
            # Persist active plan in session state token for checkbox keys
            import uuid, time
            token = str(uuid.uuid4())
            st.session_state['active_plan_token'] = token
            st.session_state['active_plan'] = plan

            # Helper to reset topic-done keys when a new plan is loaded/generated
            def _init_topic_keys(plan_obj, token_key):
                for day in plan_obj.get('plan', []):
                    for i, t in enumerate(day.get('topics', []), 1):
                        key = f"done_{token_key}_{day['day']}_{i}"
                        if key not in st.session_state:
                            st.session_state[key] = False

            _init_topic_keys(plan, token)

            # Display plan
            st.markdown("---")
            st.markdown("## 📅 Your Day-by-Day Plan")
            
            for day in plan.get("plan", []):
                day_num = day['day']
                is_review = day.get('is_review', False)
                
                if is_review:
                    st.markdown(f"### 🔄 Day {day_num} — Review Day")
                    st.info("**Review day**: Revisit previous topics and do practice questions.")
                else:
                    st.markdown(f"### 📖 Day {day_num}")
                
                def fmt(minutes: int) -> str:
                    h = minutes // 60
                    m = minutes % 60
                    if h > 0:
                        return f"{h}h {m}m"
                    return f"{m}m"

                st.write(f"**⏱️ Study time**: {hours_per_day} hours")
                st.write(f"**📝 {day.get('daily_summary')}")
                
                if day.get("topics"):
                    st.markdown("**Topics:**")
                    for i, t in enumerate(day.get("topics", []), 1):
                        est_min = t['estimated_minutes']
                        # Checkbox for marking topic as done
                        key = f"done_{st.session_state.get('active_plan_token','')}_{day_num}_{i}"
                        done = st.checkbox(f"{i}. {t['title']} — {fmt(est_min)}", value=st.session_state.get(key, False), key=key)
                
                st.markdown("")  # spacing
            
            # Save / Load / Reschedule options
            st.markdown("---")
            st.markdown("## 💾 Save & Reschedule")
            col_s1, col_s2, col_s3 = st.columns([1,1,2])
            with col_s1:
                if st.button("💾 Save Plan to Server"):
                    try:
                        plan_to_save = st.session_state['active_plan'].copy()
                        plan_to_save['review_day_fraction'] = float(review_frac_pct) / 100.0
                        payload = {"plan": json.dumps(plan_to_save), "course_type": course_type, "exam_date": str(exam_date)}
                        if st.session_state.get('user_id'):
                            payload['user_id'] = st.session_state.get('user_id')
                        resp = requests.post("http://localhost:8000/save_plan", data=payload, timeout=10)
                        resp.raise_for_status()
                        pid = resp.json().get('id')
                        st.success(f"Plan saved with id: {pid}")
                        st.session_state['last_saved_plan_id'] = pid
                    except Exception as e:
                        st.error(f"Failed to save plan: {e}")
                # Auto-save toggle
                auto = st.checkbox("Auto-save progress when marking topics done", value=st.session_state.get('auto_save', False))
                st.session_state['auto_save'] = auto
            with col_s2:
                load_id = st.text_input("Load plan id", value="", key="load_plan_id_input")
                if st.button("📂 Load Plan"):
                    try:
                        if not load_id:
                            st.warning("Enter a numeric plan id to load")
                        else:
                            r = requests.get(f"http://localhost:8000/get_plan?id={int(load_id)}", timeout=10)
                            r.raise_for_status()
                            loaded = r.json()
                            if loaded.get('error'):
                                st.error(f"Load failed: {loaded.get('error')}")
                            else:
                                st.session_state['active_plan'] = loaded
                                # Set exam_date if present
                                try:
                                    # store exam_date for reschedule calculations
                                    st.session_state['loaded_exam_date'] = loaded.get('exam_date')
                                    # Restore review_day_fraction if present in loaded plan
                                    if 'review_day_fraction' in loaded:
                                        st.session_state['loaded_review_frac_pct'] = int(loaded['review_day_fraction'] * 100)
                                except Exception:
                                    pass
                                st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Failed to load plan: {e}")
                    # List saved plans helper
                    if st.button("List saved plans"):
                        try:
                            params = {}
                            if st.session_state.get('user_id'):
                                params['user_id'] = st.session_state.get('user_id')
                            r = requests.get("http://localhost:8000/list_plans", params=params or None, timeout=5)
                            r.raise_for_status()
                            items = r.json().get('plans', [])
                            if not items:
                                st.info("No saved plans found")
                            else:
                                options = {str(p['id']): f"{p['id']} — {p.get('course_type','')} ({p.get('created_at')})" for p in items}
                                sel = st.selectbox("Select a plan to load", options=list(options.keys()))
                                if st.button("Load selected plan"):
                                    try:
                                        sid = int(sel)
                                        r2 = requests.get(f"http://localhost:8000/get_plan?id={sid}", timeout=10)
                                        r2.raise_for_status()
                                        loaded = r2.json()
                                        if loaded.get('error'):
                                            st.error(f"Load failed: {loaded.get('error')}")
                                        else:
                                            st.session_state['active_plan'] = loaded
                                            st.session_state['loaded_exam_date'] = loaded.get('exam_date')
                                            if 'review_day_fraction' in loaded:
                                                st.session_state['loaded_review_frac_pct'] = int(loaded['review_day_fraction'] * 100)
                                            st.experimental_rerun()
                                    except Exception as e:
                                        st.error(f"Failed to load selected plan: {e}")
                        except Exception as e:
                            st.error(f"Failed to list plans: {e}")
            with col_s3:
                if st.button("🔁 Reschedule For Days Left"):
                    # Build list of remaining (not-done) topics
                    active = st.session_state.get('active_plan')
                    if not active:
                        st.warning("No active plan to reschedule")
                    else:
                        remaining = []
                        for day in active.get('plan', []):
                            for i, t in enumerate(day.get('topics', []), 1):
                                key = f"done_{st.session_state.get('active_plan_token','')}_{day['day']}_{i}"
                                if not st.session_state.get(key, False):
                                    remaining.append(t['title'])
                        if not remaining:
                            st.info("All topics are marked done — nothing to reschedule")
                        else:
                            # compute days left until exam
                            try:
                                # prefer exam_date from the form, else from loaded plan
                                ed = None
                                if isinstance(exam_date, (str,)):
                                    ed = datetime.fromisoformat(exam_date).date()
                                else:
                                    ed = exam_date
                                # override if loaded plan has exam_date
                                if st.session_state.get('loaded_exam_date'):
                                    try:
                                        ed = datetime.fromisoformat(st.session_state['loaded_exam_date']).date()
                                    except Exception:
                                        pass
                                today = datetime.today().date()
                                days_left = (ed - today).days
                            except Exception:
                                days_left = 7
                            if days_left < 1:
                                days_left = 1
                            # call backend plan endpoint with remaining topics and new plan_length
                            try:
                                payload = {
                                    "topics_text": "\n".join(remaining),
                                    "plan_length": days_left,
                                    "hours_per_day": hours_per_day,
                                    "exam_type": exam_type,
                                    "course_type": course_type,
                                    "exam_date": str(exam_date),
                                }
                                # include review fraction in reschedule
                                try:
                                    payload['review_day_fraction'] = float(review_frac_pct) / 100.0
                                except Exception:
                                    pass
                                r = requests.post("http://localhost:8000/plan", data=payload, timeout=20)
                                r.raise_for_status()
                                new_plan = r.json()
                                st.session_state['active_plan'] = new_plan
                                # re-init topic keys for the new plan
                                new_token = str(uuid.uuid4())
                                st.session_state['active_plan_token'] = new_token
                                _init_topic_keys(new_plan, new_token)
                                st.success(f"Rescheduled remaining {len(remaining)} topics across {days_left} days")
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Reschedule failed: {e}")
            # If auto-save enabled, persist progress to server (non-blocking)
            if st.session_state.get('auto_save') and st.session_state.get('last_saved_plan_id'):
                try:
                    active_plan = st.session_state.get('active_plan')
                    # annotate plan topics with done flags
                    for day in active_plan.get('plan', []):
                        for i, t in enumerate(day.get('topics', []), 1):
                            key = f"done_{st.session_state.get('active_plan_token','')}_{day['day']}_{i}"
                            t['done'] = bool(st.session_state.get(key, False))
                    requests.post("http://localhost:8000/update_plan", data={"id": st.session_state.get('last_saved_plan_id'), "plan": json.dumps(active_plan)}, timeout=5)
                except Exception:
                    pass

            # Google Calendar quick actions (post-submit area)
            st.markdown("---")
            st.markdown("## 📅 Google Calendar")
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                if st.button("🔗 Connect Google Calendar"):
                    # require a saved plan id to attach tokens to
                    pid = st.session_state.get('last_saved_plan_id')
                    uid = st.session_state.get('user_id')
                    try:
                        params = {}
                        if pid:
                            params['plan_id'] = pid
                        if uid:
                            params['user_id'] = uid
                        r = requests.get("http://localhost:8000/gcal_auth_start", params=params or None, timeout=5)
                        r.raise_for_status()
                        auth = r.json()
                        if auth.get('error'):
                            st.error(f"OAuth start error: {auth.get('error')}")
                        else:
                            url = auth.get('auth_url')
                            st.markdown(f"<a href=\"{url}\" target=\"_blank\">Open Google consent screen</a>", unsafe_allow_html=True)
                            st.info("After granting access, return here — the server stores the refresh token.")
                    except Exception as e:
                        st.error(f"Failed to start OAuth flow: {e}")
            with col_g2:
                if st.button("📤 Push Plan To Google Calendar"):
                    pid = st.session_state.get('last_saved_plan_id')
                    if not pid:
                        st.warning("Save the plan first before pushing to Google Calendar")
                    else:
                        # build events payload
                        events = []
                        from datetime import datetime, timedelta
                        today = datetime.utcnow().date()
                        active = st.session_state.get('active_plan')
                        for d in active.get('plan', []):
                            day_index = d['day'] - 1
                            ev_date = (today + timedelta(days=day_index)).strftime('%Y-%m-%d')
                            events.append({"summary": d.get('daily_summary',''), "start_date": ev_date, "end_date": ev_date})
                        try:
                            r = requests.post("http://localhost:8000/gcal_create", data={"events": json.dumps(events), "access_token": f"plan:{pid}"}, timeout=10)
                            r.raise_for_status()
                            res = r.json()
                            st.success("Calendar events created (see response)")
                            st.json(res)
                        except Exception as e:
                            st.error(f"Failed to push to Google Calendar: {e}")
                # Revoke button
                if st.button("❌ Revoke Google Access"):
                    pid = st.session_state.get('last_saved_plan_id')
                    uid = st.session_state.get('user_id')
                    if not pid and not uid:
                        st.warning("No saved plan or user logged in to revoke tokens for")
                    else:
                        try:
                            data = {}
                            if pid:
                                data['plan_id'] = pid
                            elif uid:
                                data['user_id'] = uid
                            r = requests.post("http://localhost:8000/gcal_revoke", data=data, timeout=10)
                            r.raise_for_status()
                            st.success("Revocation attempted — see details below")
                            st.json(r.json())
                        except Exception as e:
                            st.error(f"Failed to revoke tokens: {e}")
            st.markdown("---")
            st.markdown("## 💾 Export Options")
            col1, col2 = st.columns(2)
            
            with col1:
                json_str = json.dumps(plan, indent=2)
                st.download_button(
                    label="📥 Download Plan (JSON)",
                    data=json_str,
                    file_name=f"planora_plan_{plan_length}days.json",
                    mime="application/json"
                )
            
            with col2:
                # Create a simple text export
                text_lines = [
                    f"Planora Study Plan — {plan_length} Days",
                    f"Course: {course_type}",
                    f"Exam Date: {exam_date}",
                    f"Hours/Day: {hours_per_day}",
                    "",
                    "=" * 50,
                    ""
                ]
                for day in plan.get("plan", []):
                    text_lines.append(f"Day {day['day']}" + (" (REVIEW)" if day.get("is_review") else ""))
                    text_lines.append(f"  Time: {day.get('total_minutes',0)} minutes")
                    text_lines.append(f"  Summary: {day.get('daily_summary')}")
                    for t in day.get("topics", []):
                        text_lines.append(f"    - {t['title']} ({t['estimated_minutes']} min)")
                    text_lines.append("")
                
                text_str = "\n".join(text_lines)
                st.download_button(
                    label="📄 Download Plan (Text)",
                    data=text_str,
                    file_name=f"planora_plan_{plan_length}days.txt",
                    mime="text/plain"
                )

                # Calendar export (ICS)
                def make_ics(plan_obj, start_date_str=None):
                    from datetime import datetime, timedelta
                    # start_date_str not used; we treat day 1 as today
                    now = datetime.utcnow()
                    lines = [
                        "BEGIN:VCALENDAR",
                        "VERSION:2.0",
                        "PRODID:-//Planora//Study Plan//EN",
                    ]
                    for d in plan_obj.get('plan', []):
                        day_index = d['day'] - 1
                        # event start = today + day_index
                        ev_date = (datetime.utcnow().date() + timedelta(days=day_index))
                        # make a simple all-day event
                        uid = f"planora-{plan_obj.get('course_type','')}-{d['day']}"
                        summary = d.get('daily_summary', f"Day {d['day']}")
                        lines += [
                            "BEGIN:VEVENT",
                            f"UID:{uid}",
                            f"DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}",
                            f"DTSTART;VALUE=DATE:{ev_date.strftime('%Y%m%d')}",
                            f"DTEND;VALUE=DATE:{(ev_date + timedelta(days=1)).strftime('%Y%m%d')}",
                            f"SUMMARY:{summary}",
                            "END:VEVENT",
                        ]
                    lines.append("END:VCALENDAR")
                    return "\r\n".join(lines)

                ics_str = make_ics(plan)
                st.download_button(label="📆 Download Calendar (ICS)", data=ics_str, file_name=f"planora_{plan_length}days.ics", mime="text/calendar")

                # PDF export via backend
                try:
                    r2 = requests.post("http://localhost:8000/export_pdf", data={"plan": json.dumps(plan)}, timeout=30)
                    if r2.status_code == 200:
                        st.download_button(label="📚 Download Plan (PDF)", data=r2.content, file_name=f"planora_plan_{plan_length}days.pdf", mime="application/pdf")
                    else:
                        st.warning("PDF export failed on backend.")
                except Exception:
                    st.warning("PDF export failed (backend may not be running or lacks reportlab).")

                # If a plan was loaded or saved earlier, display it even when the form isn't just submitted
                if not submit and st.session_state.get('active_plan'):
                    plan = st.session_state.get('active_plan')
                    # ensure we have a token and topic keys
                    if 'active_plan_token' not in st.session_state:
                        import uuid
                        st.session_state['active_plan_token'] = str(uuid.uuid4())

                    def _init_topic_keys(plan_obj, token_key):
                        for day in plan_obj.get('plan', []):
                            for i, t in enumerate(day.get('topics', []), 1):
                                key = f"done_{token_key}_{day['day']}_{i}"
                                if key not in st.session_state:
                                    st.session_state[key] = False

                    _init_topic_keys(plan, st.session_state['active_plan_token'])

                    st.markdown("---")
                    st.markdown("## 📅 Your Day-by-Day Plan")
                    def fmt(minutes: int) -> str:
                        h = minutes // 60
                        m = minutes % 60
                        if h > 0:
                            return f"{h}h {m}m"
                        return f"{m}m"

                    for day in plan.get("plan", []):
                        day_num = day['day']
                        is_review = day.get('is_review', False)
                        if is_review:
                            st.markdown(f"### 🔄 Day {day_num} — Review Day")
                            st.info("**Review day**: Revisit previous topics and do practice questions.")
                        else:
                            st.markdown(f"### 📖 Day {day_num}")

                        st.write(f"**⏱️ Study time**: {plan.get('hours_per_day')} hours")
                        st.write(f"**📝 {day.get('daily_summary')}")

                        if day.get("topics"):
                            st.markdown("**Topics:**")
                            for i, t in enumerate(day.get("topics", []), 1):
                                est_min = t['estimated_minutes']
                                key = f"done_{st.session_state.get('active_plan_token','')}_{day_num}_{i}"
                                done = st.checkbox(f"{i}. {t['title']} — {fmt(est_min)}", value=st.session_state.get(key, False), key=key)

                    # Auto-save for active plan (if enabled and saved previously)
                    if st.session_state.get('auto_save') and st.session_state.get('last_saved_plan_id'):
                        try:
                            active_plan = st.session_state.get('active_plan')
                            for day in active_plan.get('plan', []):
                                for i, t in enumerate(day.get('topics', []), 1):
                                    key = f"done_{st.session_state.get('active_plan_token','')}_{day['day']}_{i}"
                                    t['done'] = bool(st.session_state.get(key, False))
                            requests.post("http://localhost:8000/update_plan", data={"id": st.session_state.get('last_saved_plan_id'), "plan": json.dumps(active_plan)}, timeout=5)
                        except Exception:
                            pass

                    # simple save/load area when plan is active
                    st.markdown("---")
                    st.markdown("## 💾 Save & Reschedule")
                    col_s1, col_s2, col_s3 = st.columns([1,1,2])
                    with col_s1:
                        if st.button("💾 Save Plan to Server", key="save_active"):
                            try:
                                plan_to_save = st.session_state['active_plan'].copy()
                                frac_to_use = st.session_state.get('loaded_review_frac_pct', default_frac) if not submit else review_frac_pct
                                plan_to_save['review_day_fraction'] = float(frac_to_use) / 100.0
                                resp = requests.post("http://localhost:8000/save_plan", data={"plan": json.dumps(plan_to_save), "course_type": course_type, "exam_date": str(exam_date)}, timeout=10)
                                resp.raise_for_status()
                                pid = resp.json().get('id')
                                st.success(f"Plan saved with id: {pid}")
                                st.session_state['last_saved_plan_id'] = pid
                            except Exception as e:
                                st.error(f"Failed to save plan: {e}")
                    with col_s2:
                        load_id = st.text_input("Load plan id", value="", key="load_plan_id_input_2")
                        if st.button("📂 Load Plan", key="load_active"):
                            try:
                                if not load_id:
                                    st.warning("Enter a numeric plan id to load")
                                else:
                                    r = requests.get(f"http://localhost:8000/get_plan?id={int(load_id)}", timeout=10)
                                    r.raise_for_status()
                                    loaded = r.json()
                                    if loaded.get('error'):
                                        st.error(f"Load failed: {loaded.get('error')}")
                                    else:
                                        st.session_state['active_plan'] = loaded
                                        st.session_state['loaded_exam_date'] = loaded.get('exam_date')
                                        st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Failed to load plan: {e}")
                    with col_s3:
                        if st.button("🔁 Reschedule For Days Left", key="resched_active"):
                            active = st.session_state.get('active_plan')
                            if not active:
                                st.warning("No active plan to reschedule")
                            else:
                                remaining = []
                                for day in active.get('plan', []):
                                    for i, t in enumerate(day.get('topics', []), 1):
                                        key = f"done_{st.session_state.get('active_plan_token','')}_{day['day']}_{i}"
                                        if not st.session_state.get(key, False):
                                            remaining.append(t['title'])
                                if not remaining:
                                    st.info("All topics are marked done — nothing to reschedule")
                                else:
                                    try:
                                        ed = None
                                        if isinstance(exam_date, (str,)):
                                            ed = datetime.fromisoformat(exam_date).date()
                                        else:
                                            ed = exam_date
                                        if st.session_state.get('loaded_exam_date'):
                                            try:
                                                ed = datetime.fromisoformat(st.session_state['loaded_exam_date']).date()
                                            except Exception:
                                                pass
                                        today = datetime.today().date()
                                        days_left = (ed - today).days
                                    except Exception:
                                        days_left = 7
                                    if days_left < 1:
                                        days_left = 1
                                    try:
                                        payload = {
                                            "topics_text": "\n".join(remaining),
                                            "plan_length": days_left,
                                            "hours_per_day": hours_per_day,
                                            "exam_type": exam_type,
                                            "course_type": course_type,
                                            "exam_date": str(exam_date),
                                        }
                                        # include review fraction in reschedule
                                        try:
                                            payload['review_day_fraction'] = float(review_frac_pct) / 100.0
                                        except Exception:
                                            pass
                                        r = requests.post("http://localhost:8000/plan", data=payload, timeout=20)
                                        r.raise_for_status()
                                        new_plan = r.json()
                                        new_plan = r.json()
                                        st.session_state['active_plan'] = new_plan
                                        new_token = str(uuid.uuid4())
                                        st.session_state['active_plan_token'] = new_token
                                        _init_topic_keys(new_plan, new_token)
                                        st.success(f"Rescheduled remaining {len(remaining)} topics across {days_left} days")
                                        st.experimental_rerun()
                                    except Exception as e:
                                        st.error(f"Reschedule failed: {e}")
