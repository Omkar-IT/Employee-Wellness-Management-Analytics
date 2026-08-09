import os, re, io, calendar
from datetime import date, datetime
import requests, streamlit as st
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from db import (init_db, save_mood_log, save_manual_mood, MOOD_LABELS, MOOD_EMOJI,
                 get_mood_logs_for_month, get_user_mood_history,
                 get_all_employee_mood_logs, get_latest_mood_per_employee)
from recommendations import get_period_recommendation
from auth import (make_token, read_token, get_user, username_taken, create_user,
                   verify_user, set_password, check_pw, new_otp, save_otp, check_otp)
from email_utils import send_otp

st.set_page_config(page_title="MoodMentor", layout="wide")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

BRAND_GREEN = "#1DBF73"
BRAND_GREEN_DARK = "#159c5e"
INK = "#1f2937"
MUTED = "#6b7280"
BG = "#f5f7f6"

MOOD_STYLE = {
    "Happy":   {"emoji": MOOD_EMOJI["Happy"],   "color": "#2ecc71"},
    "Neutral": {"emoji": MOOD_EMOJI["Neutral"], "color": "#3498db"},
    "Sad":     {"emoji": MOOD_EMOJI["Sad"],     "color": "#e67e22"},
    "Stress":  {"emoji": MOOD_EMOJI["Stress"],  "color": "#f1c40f"},
    "Angry":   {"emoji": MOOD_EMOJI["Angry"],   "color": "#e74c3c"},
    "Fear":    {"emoji": MOOD_EMOJI["Fear"],    "color": "#9b59b6"},
}
def style_for(label):
    return MOOD_STYLE.get(label, {"emoji": "", "color": "#bdbdbd"})

MOOD_TO_NUM = {"Happy": 2, "Neutral": 0, "Sad": -1, "Stress": -1, "Angry": -2, "Fear": -2}

def inject_css():
    st.markdown(f"""
    <style>
        .stApp {{ background: {BG}; }}
        #MainMenu, footer {{visibility: hidden;}}

        /* ---- Sidebar as a green-accented nav panel ---- */
        section[data-testid="stSidebar"] {{
            background: #ffffff;
            border-right: 1px solid #e5e7eb;
        }}
        section[data-testid="stSidebar"] .stRadio > label {{
            font-weight: 600; color: {INK};
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] label {{
            padding: 10px 14px; border-radius: 10px; margin-bottom: 4px;
        }}
        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
            background: #f0fdf6;
        }}

        /* ---- Generic card ---- */

        .mm-card h4 {{ margin-top: 0; }}

        /* ---- Metric tiles (Home page) ---- */
        .mm-metric {{
            background: #ffffff; border-radius: 16px; padding: 16px 18px;
            border: 1px solid #eef0ef; text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        .mm-metric .mm-label {{ color: {MUTED}; font-size: 12.5px; font-weight: 600; }}
        .mm-metric .mm-value {{ font-size: 26px; font-weight: 700; color: {INK}; margin-top: 4px; }}
        .mm-metric .mm-sub {{ font-size: 12px; color: {BRAND_GREEN}; font-weight: 600; margin-top: 2px; }}

        /* ---- Badges ---- */
        .mm-badge-positive {{
            display:inline-block; background:#e7faf1; color:{BRAND_GREEN_DARK};
            padding:3px 10px; border-radius:20px; font-size:12.5px; font-weight:700;
        }}

        /* ---- Top header bar ---- */
        .mm-header {{
            display:flex; justify-content:space-between; align-items:center;
            padding-bottom: 6px; margin-bottom: 10px;
        }}
        .mm-header h2 {{ margin: 0; color:{INK}; }}
        .mm-header p {{ margin: 0; color:{MUTED}; font-size: 13px; }}

        /* ---- Buttons ---- */
        div.stButton > button, .stFormSubmitButton > button {{
            border-radius: 10px; font-weight: 600;
        }}
        div.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
            background: {BRAND_GREEN}; border-color: {BRAND_GREEN};
        }}
        div.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {{
            background: {BRAND_GREEN_DARK}; border-color: {BRAND_GREEN_DARK};
        }}

        /* ---- Welcome / auth split screen ---- */
        .welcome-box {{
            background: linear-gradient(180deg, {BRAND_GREEN} 0%, {BRAND_GREEN_DARK} 100%);
            padding: 48px 32px; border-radius: 16px; color: white; height: 100%;
        }}
        .auth-card {{
            background: #ffffff; border-radius: 16px; padding: 28px 30px;
            border: 1px solid #eef0ef; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
    </style>
    """, unsafe_allow_html=True)

def donut_chart(counts: dict, size=2.6):
    labels, values, colors = [], [], []
    for k, v in counts.items():
        if v > 0:
            labels.append(k); values.append(v)
            colors.append(style_for(k)["color"])
    if not values:
        return None
    fig, ax = plt.subplots(figsize=(size, size))
    ax.pie(values, colors=colors, startangle=90, wedgeprops=dict(width=0.38, edgecolor="white"))
    ax.set(aspect="equal")
    fig.patch.set_alpha(0.0)
    return fig

def metric_tile(label, value, sub=None):
    sub_html = f"<div class='mm-sub'>{sub}</div>" if sub else ""
    st.markdown(
        f"<div class='mm-metric'><div class='mm-label'>{label}</div>"
        f"<div class='mm-value'>{value}</div>{sub_html}</div>",
        unsafe_allow_html=True,
    )

def build_pdf_report(username, start_d, end_d, entries, recommendation_text):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=48, bottomMargin=48)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("MoodMentor Wellness Report", styles["Title"]))
    story.append(Paragraph(f"{username} &nbsp;|&nbsp; {start_d} to {end_d}", styles["Normal"]))
    story.append(Spacer(1, 16))

    counts = {}
    for h in entries:
        counts[h["sentiment"]] = counts.get(h["sentiment"], 0) + 1
    summary_line = ", ".join(f"{k}: {v}" for k, v in counts.items())
    story.append(Paragraph("Mood summary", styles["Heading2"]))
    story.append(Paragraph(f"{len(entries)} entries logged. {summary_line}.", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Recommendation", styles["Heading2"]))
    story.append(Paragraph(recommendation_text, styles["Normal"]))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Entries", styles["Heading2"]))
    table_data = [["Date", "Time", "Mood", "Emotion", "Confidence", "Source"]]
    for h in sorted(entries, key=lambda r: r["created_at"], reverse=True):
        table_data.append([
            str(h["mood_date"]),
            h["created_at"].strftime("%H:%M"),
            h["sentiment"] or "\u2014",
            h.get("emotion") or "\u2014",
            f"{h['confidence']:.0%}" if h.get("confidence") is not None else "\u2014",
            h["source"],
        ])
    tbl = Table(table_data, repeatRows=1, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1DBF73")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7f6")]),
    ]))
    story.append(tbl)

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


inject_css()

@st.cache_resource
def setup(): init_db()
setup()

if "page" not in st.session_state: st.session_state.page = "welcome"
if "show_auth_panel" not in st.session_state: st.session_state.show_auth_panel = False
if "auth_mode" not in st.session_state: st.session_state.auth_mode = "login"
if "token" not in st.session_state: st.session_state.token = None
if "email" not in st.session_state: st.session_state.email = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "cal_year" not in st.session_state: st.session_state.cal_year = date.today().year
if "cal_month" not in st.session_state: st.session_state.cal_month = date.today().month
if "today_mood_saved" not in st.session_state: st.session_state.today_mood_saved = False
if "nav" not in st.session_state: st.session_state.nav = "Home"

def goto_auth(mode): st.session_state.auth_mode = mode; st.rerun()

def valid_pw(pw):
    return len(pw) >= 8 and re.search(r"[A-Za-z]", pw) and re.search(r"[0-9]", pw)


if st.session_state.token:
    user = read_token(st.session_state.token)
    if user:
        role = user.get("role", "employee")
        headers = {"Authorization": f"Bearer {st.session_state.token}"}

        with st.sidebar:
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:8px;padding:6px 4px 18px 4px'>"
                f"<span style='font-size:18px;font-weight:800;color:{INK}'>Mood Mentor</span></span>"
                f"</div>", unsafe_allow_html=True,
            )
            if role == "employee":
                nav_options = ["Home", "Journal", "Wellness Chat", "Dashboard"]
            else:
                nav_options = ["Reports"]
            st.session_state.nav = st.radio(
                "Navigate", nav_options,
                index=nav_options.index(st.session_state.nav) if st.session_state.nav in nav_options else 0,
                label_visibility="collapsed",
            )
            st.divider()
            st.caption(f"Signed in as **{user['username']}**")
            st.caption(f"{user['email']} · {role.capitalize()}")
            if st.button("Log out", use_container_width=True):
                st.session_state.token = None
                st.session_state.page = "welcome"
                st.session_state.show_auth_panel = False
                st.rerun()

        greeting = "Good Morning" if datetime.now().hour < 12 else (
            "Good Afternoon" if datetime.now().hour < 18 else "Good Evening")
        st.markdown(
            f"<div class='mm-header'><div><h2>{greeting}, {user['username']}!</h2>"
            f"<p>Here's your emotional wellness overview.</p></div></div>",
            unsafe_allow_html=True,
        )

        if role == "employee":
            section = st.session_state.nav

            if section == "Home":
                history_all = get_user_mood_history(user["id"], limit=500)
                latest = history_all[0] if history_all else None
                today_count = sum(1 for h in history_all if h["mood_date"] == date.today())
                streak = 0
                day_ptr = date.today()
                day_set = {h["mood_date"] for h in history_all}
                while day_ptr in day_set:
                    streak += 1
                    day_ptr = date.fromordinal(day_ptr.toordinal() - 1)

                positive_count = sum(1 for h in history_all if h["sentiment"] == "Happy")
                overall_score = int(100 * positive_count / len(history_all)) if history_all else 0

                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    if latest:
                        s = style_for(latest["sentiment"])
                        metric_tile("Current Mood", f"{s['emoji']} {latest['sentiment']}")
                    else:
                        metric_tile("Current Mood", "—")
                with m2:
                    metric_tile("Overall Score", f"{overall_score}%", "Positive" if overall_score >= 50 else "Needs care")
                with m3:
                    metric_tile("Entries Today", today_count)
                with m4:
                    metric_tile("Current Streak", f"{streak} Days")

                st.write("")
                st.subheader("How Do You Feel?")
                now = datetime.now()
                st.caption(f"{now.strftime('%Y-%m-%d')}  {now.strftime('%H:%M')}")

                cols = st.columns(len(MOOD_LABELS))
                picked = st.session_state.get("picked_mood")
                for col, label in zip(cols, MOOD_LABELS):
                    s = style_for(label)
                    with col:
                        st.markdown(
                            f"<div style='text-align:center;font-size:36px'>{s['emoji']}</div>"
                            f"<div style='text-align:center;color:{s['color']};font-weight:600'>{label}</div>",
                            unsafe_allow_html=True,
                        )
                        if st.button("Select", key=f"pick_{label}", use_container_width=True):
                            st.session_state.picked_mood = label

                st.write("")
                confirm_col = st.columns([3, 1, 3])[1]
                with confirm_col:
                    disabled = picked is None
                    if st.button("Save mood", type="primary", disabled=disabled,
                                 use_container_width=True):
                        save_manual_mood(user["id"], st.session_state.picked_mood)
                        st.session_state.today_mood_saved = True
                        st.session_state.picked_mood = None
                        st.rerun()

                if st.session_state.today_mood_saved:
                    st.success("Today's mood saved!")
                    st.session_state.today_mood_saved = False
                st.markdown("</div>", unsafe_allow_html=True)

                st.subheader("Your Mood Calendar")

                nav_l, nav_mid, nav_r = st.columns([1, 3, 1])
                if nav_l.button("← Prev"):
                    m, y = st.session_state.cal_month - 1, st.session_state.cal_year
                    if m == 0: m, y = 12, y - 1
                    st.session_state.cal_month, st.session_state.cal_year = m, y
                    st.rerun()
                if nav_r.button("Next →"):
                    m, y = st.session_state.cal_month + 1, st.session_state.cal_year
                    if m == 13: m, y = 1, y + 1
                    st.session_state.cal_month, st.session_state.cal_year = m, y
                    st.rerun()
                nav_mid.markdown(
                    f"<h4 style='text-align:center'>{calendar.month_name[st.session_state.cal_month]} "
                    f"{st.session_state.cal_year}</h4>", unsafe_allow_html=True,
                )

                logs = get_mood_logs_for_month(user["id"], st.session_state.cal_year,
                                                st.session_state.cal_month)
                by_day = {row["mood_date"].day: row for row in logs}

                weeks = calendar.Calendar(firstweekday=6).monthdayscalendar(
                    st.session_state.cal_year, st.session_state.cal_month
                )
                day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
                header_cols = st.columns(7)
                for c, name in zip(header_cols, day_names):
                    c.markdown(f"**{name}**")

                for week in weeks:
                    cols = st.columns(7)
                    for col, day_num in zip(cols, week):
                        if day_num == 0:
                            col.write("")
                            continue
                        entry = by_day.get(day_num)
                        s = style_for(entry["sentiment"] if entry else None)
                        time_label = entry["created_at"].strftime("%H:%M") if entry else ""
                        col.markdown(
                            f"<div title='{time_label}' style='text-align:center;padding:6px;border-radius:8px;"
                            f"background:{s['color']}22;border:1px solid {s['color']}'>"
                            f"<div style='font-size:11px'>{day_num}</div>"
                            f"<div style='font-size:20px'>{s['emoji']}</div>"
                            f"<div style='font-size:9px;color:#888'>{time_label}</div></div>",
                            unsafe_allow_html=True,
                        )

                legend = " · ".join(l for l in MOOD_LABELS)
                st.caption(f"{legend} · No entry logged  (hover/see time under each day)")
                st.markdown("</div>", unsafe_allow_html=True)

            elif section == "Journal":
                st.subheader(" Journal")
                journal_text = st.text_area(
                    "Write about how you're feeling today", height=150,
                    placeholder="Your note here...",
                )
                if st.button("Analyze my mood"):
                    if not journal_text.strip():
                        st.warning("Write something first.")
                    else:
                        with st.spinner("Running NLP analysis…"):
                            try:
                                resp = requests.post(
                                    f"{BACKEND_URL}/analyze-text",
                                    json={"text": journal_text},
                                    headers=headers, timeout=120,
                                )
                            except requests.exceptions.RequestException as e:
                                st.error(f"Could not reach backend: {e}"); resp = None
                        if resp is not None:
                            if resp.status_code != 200:
                                st.error("Analysis failed.")
                            else:
                                r = resp.json()
                                confidence = r.get("emotion_confidence")
                                save_mood_log(
                                    user["id"], r["final_sentiment"], r["final_emotion"],
                                    r["sentiment_scores"]["compound"], journal_text,
                                    confidence=confidence,
                                )
                                conf_str = f", Confidence: **{confidence:.0%}**" if confidence is not None else ""
                                st.success(f"Saved! Sentiment: **{r['final_sentiment']}**, "
                                           f"Emotion: **{r['final_emotion']}**{conf_str}")
                                st.bar_chart(r["emotion_scores"])
                                if r.get("recommendation"):
                                    st.info(f"**Recommendation:** {r['recommendation']}")
                st.markdown("</div>", unsafe_allow_html=True)

                st.subheader("Or upload a file")
                uploaded = st.file_uploader("Choose a CSV or TXT file", type=["csv", "txt"])
                if uploaded is not None and st.button("Run NLP Analysis on file"):
                    files = {"file": (uploaded.name, uploaded.getvalue())}
                    with st.spinner("Running multilingual NLP pipeline…"):
                        try:
                            resp = requests.post(f"{BACKEND_URL}/analyze", files=files,
                                                  headers=headers, timeout=120)
                        except requests.exceptions.RequestException as e:
                            st.error(f"Could not reach backend: {e}"); resp = None
                    if resp is not None:
                        if resp.status_code != 200:
                            st.error("Analysis failed.")
                        else:
                            r = resp.json()
                            confidence = r.get("emotion_confidence")
                            save_mood_log(
                                user["id"], r["final_sentiment"], r["final_emotion"],
                                r["sentiment_scores"]["compound"], r.get("cleaned_text", ""),
                                confidence=confidence,
                            )
                            conf_str = f", Confidence: **{confidence:.0%}**" if confidence is not None else ""
                            st.success(f"Saved! Sentiment: **{r['final_sentiment']}**, "
                                       f"Emotion: **{r['final_emotion']}**{conf_str}")
                            st.bar_chart(r["emotion_scores"])
                            if r.get("recommendation"):
                                st.info(f"**Recommendation:** {r['recommendation']}")
                st.markdown("</div>", unsafe_allow_html=True)

                st.subheader(" Past entries")
                history = [h for h in get_user_mood_history(user["id"], limit=20)
                           if h["journal_text"]]
                if not history:
                    st.caption("No journal entries yet.")
                for h in history:
                    s = style_for(h["sentiment"])
                    conf_str = f" · Confidence: {h['confidence']:.0%}" if h.get("confidence") is not None else ""
                    with st.expander(
                        f"{s['emoji']} {h['sentiment']} — {h['created_at'].strftime('%Y-%m-%d %H:%M')}{conf_str}"
                    ):
                        st.write(h["journal_text"])
                st.markdown("</div>", unsafe_allow_html=True)

            elif section == "Wellness Chat":
                st.subheader(" Wellness Chat")
                st.caption("A supportive space to talk about how you're feeling. "
                           "Not a substitute for professional care.")
                chat_box = st.container(height=450)
                with chat_box:
                    for turn in st.session_state.chat_history:
                        with st.chat_message(turn["role"]):
                            st.write(turn["content"])

                user_msg = st.chat_input("How are you feeling today?")
                if user_msg:
                    st.session_state.chat_history.append({"role": "user", "content": user_msg})
                    recent_history = st.session_state.chat_history[-10:-1]
                    try:
                        resp = requests.post(
                            f"{BACKEND_URL}/chat",
                            json={"message": user_msg, "history": recent_history},
                            headers=headers, timeout=60,
                        )
                        reply = resp.json()["reply"] if resp.status_code == 200 else \
                            "Sorry, I couldn't reach the wellness assistant right now."
                    except requests.exceptions.RequestException:
                        reply = "Sorry, I couldn't reach the wellness assistant right now."
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    st.rerun()

                if st.session_state.chat_history and st.button("Clear chat"):
                    st.session_state.chat_history = []
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            elif section == "Dashboard":
                history = get_user_mood_history(user["id"], limit=200)
                if not history:
                    st.info("No entries yet — pick a mood on Home or write a journal entry to see your dashboard.")
                else:
                    counts = {label: 0 for label in MOOD_LABELS}
                    for h in history:
                        if h["sentiment"] in counts:
                            counts[h["sentiment"]] += 1

                    c1, c2 = st.columns(2)
                    with c1:
                        st.write("**Mood distribution**")
                        fig = donut_chart(counts)
                        if fig: st.pyplot(fig, use_container_width=False)
                        else: st.bar_chart(counts)
                        st.markdown("</div>", unsafe_allow_html=True)
                    with c2:
                        st.write("**Mood trend over time**")
                        by_date = {}
                        for h in history:
                            d = h["mood_date"]
                            by_date.setdefault(d, []).append(MOOD_TO_NUM.get(h["sentiment"], 0))
                        trend = {str(d): sum(v) / len(v) for d, v in sorted(by_date.items())}
                        st.line_chart(trend)
                        st.markdown("</div>", unsafe_allow_html=True)

                    st.write("**Emotions detected from journal entries**")
                    emo_counts = {}
                    for h in history:
                        if h["source"] == "nlp" and h["emotion"]:
                            emo_counts[h["emotion"]] = emo_counts.get(h["emotion"], 0) + 1
                    if emo_counts:
                        st.bar_chart(emo_counts)
                    else:
                        st.caption("No journal-based emotion data yet.")
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.write("**Recent activity**")
                    table_rows = [{
                        "Date": h["mood_date"], "Time": h["created_at"].strftime("%H:%M"),
                        "Mood": f"{style_for(h['sentiment'])['emoji']} {h['sentiment']}",
                        "Confidence": f"{h['confidence']:.0%}" if h.get("confidence") is not None else "—",
                        "Source": h["source"],
                    } for h in history[:15]]
                    st.dataframe(table_rows, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.write("**Export report**")
                    oldest_date = history[-1]["mood_date"]
                    today = date.today()
                    date_range = st.date_input(
                        "Select date range", value=(oldest_date, today),
                        min_value=oldest_date, max_value=today,
                        key="dashboard_export_range",
                    )
                    if st.button("Export PDF"):
                        if isinstance(date_range, tuple) and len(date_range) == 2:
                            start_d, end_d = date_range
                        else:
                            start_d = end_d = date_range
                        filtered = [h for h in history if start_d <= h["mood_date"] <= end_d]
                        if not filtered:
                            st.warning("No entries in that date range.")
                        else:
                            recommendation_text = get_period_recommendation(filtered)
                            pdf_bytes = build_pdf_report(
                                user["username"], start_d, end_d, filtered, recommendation_text,
                            )
                            st.success(recommendation_text)
                            st.download_button(
                                "Download PDF", data=pdf_bytes,
                                file_name=f"moodmentor_report_{start_d}_{end_d}.pdf",
                                mime="application/pdf",
                            )
                    st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.subheader("Employee Wellness Report")

            latest = get_latest_mood_per_employee()
            if not latest:
                st.info("No employee entries yet.")
            else:
                st.write("**Latest mood per employee**")
                table_rows = [{
                    "Employee": row["username"],
                    "Email": row["email"],
                    "Date": row["mood_date"],
                    "Time": row["created_at"].strftime("%H:%M"),
                    "Mood": f"{style_for(row['sentiment'])['emoji']} {row['sentiment']}",
                    "Emotion": row["emotion"],
                } for row in latest]
                st.dataframe(table_rows, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.write("**Team mood trend (last 30 days)**")
            history = get_all_employee_mood_logs(limit_days=30)
            if not history:
                st.info("Not enough data yet to draw a trend chart.")
            else:
                by_date = {}
                for row in history:
                    d = row["mood_date"]
                    by_date.setdefault(d, []).append(MOOD_TO_NUM.get(row["sentiment"], 0))
                trend = {str(d): sum(v) / len(v) for d, v in sorted(by_date.items())}
                st.line_chart(trend)
                st.caption("Average mood score per day across all employees "
                           "(2 = Happy, 0 = Neutral, -1 = Sad/Stress, -2 = Angry/Fear)")
            st.markdown("</div>", unsafe_allow_html=True)

        st.stop()
    st.session_state.token = None


if st.session_state.page == "welcome":

    if not st.session_state.show_auth_panel:
        st.markdown('<div class="welcome-box">', unsafe_allow_html=True)
        st.markdown("## Mood<span style='color:#eafff4'>Mentor</span>", unsafe_allow_html=True)
        st.markdown("#### AI-Powered Emotional Wellness Assistant")
        st.write(
            "Understand your emotions. Improve your well-being. Live your best life. "
            "Journey into your inner world through emojis, text, voice recordings, "
            "and notes — and watch your emotional landscape unfold through beautiful "
            "charts and insights."
        )
        st.markdown(
            "<div style='text-align:center;font-size:36px;padding:24px 0'>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")
        if st.button("Get Started →", type="primary", use_container_width=True):
            st.session_state.show_auth_panel = True
            st.rerun()
        st.stop()

    left, right = st.columns([3, 2])

    with left:
        st.markdown('<div class="welcome-box">', unsafe_allow_html=True)
        st.markdown("## Mood<span style='color:#eafff4'>Mentor</span>", unsafe_allow_html=True)
        st.markdown("#### AI-Powered Emotional Wellness Assistant")
        st.write(
            "Understand your emotions. Improve your well-being. Live your best life. "
            "Journey into your inner world through emojis, text, voice recordings, "
            "and notes — and watch your emotional landscape unfold through beautiful "
            "charts and insights."
        )
        st.markdown(
            "<div style='text-align:center;font-size:36px;padding:24px 0'>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        mode = st.session_state.auth_mode

        if mode == "login":
            st.markdown("### Welcome Back!")
            st.caption("Login to your account")
            with st.form("login"):
                email = st.text_input("Email", placeholder="Enter your email")
                pw = st.text_input("Password", type="password", placeholder="Enter your password")
                go = st.form_submit_button("Login", type="primary", use_container_width=True)
            if go:
                u = get_user(email.strip().lower())
                if not u or not check_pw(pw, u["password_hash"]):
                    st.error("Invalid email or password.")
                elif not u["is_verified"]:
                    st.warning("Verify your email first.")
                    st.session_state.email = u["email"]; goto_auth("verify")
                else:
                    st.session_state.token = make_token(u)
                    st.rerun()
            c1, c2 = st.columns(2)
            if c1.button("Sign up", use_container_width=True): goto_auth("signup")
            if c2.button("Forgot password?", use_container_width=True): goto_auth("forgot")

        elif mode == "signup":
            st.markdown("### Create Account")
            st.caption("Let's get you started")
            with st.form("signup"):
                username = st.text_input("Full Name", placeholder="Enter your full name")
                email = st.text_input("Email", placeholder="Enter your email")
                pw = st.text_input("Password", type="password", placeholder="Create password")
                role_label = st.radio("I am signing up as a:", ["Employee", "Manager"], horizontal=True)
                go = st.form_submit_button("Send OTP", type="primary", use_container_width=True)
            if go:
                email = email.strip().lower()
                role = "manager" if role_label == "Manager" else "employee"
                if len(username) < 3:
                    st.error("Username too short.")
                elif not valid_pw(pw):
                    st.error("Password needs 8+ chars, letters and numbers.")
                elif username_taken(username) or get_user(email):
                    st.error("Username or email already in use.")
                else:
                    create_user(username, email, pw, role=role)
                    code = new_otp(); save_otp(email, code, "signup")
                    ok, msg = send_otp(email, code, "signup")
                    if ok:
                        st.session_state.email = email
                        st.success("Check your email for the code.")
                        goto_auth("verify")
                    else:
                        st.error(f"Email failed: {msg}")
            if st.button("Already have an account? Login"): goto_auth("login")

        elif mode == "verify":
            email = st.session_state.email
            st.markdown("### Verify OTP")
            st.caption(f"We have sent a 6-digit code to {email}")
            with st.form("verify"):
                code = st.text_input("Code", max_chars=6, placeholder="Enter 6-digit code")
                go = st.form_submit_button("Verify OTP", type="primary", use_container_width=True)
            if go:
                if check_otp(email, code.strip(), "signup"):
                    verify_user(email)
                    st.success("Verified! Please log in.")
                    goto_auth("login")
                else:
                    st.error("Invalid or expired code.")
            if st.button("← Back to login"): goto_auth("login")

        elif mode == "forgot":
            st.markdown("### Forgot password")
            with st.form("forgot"):
                email = st.text_input("Your account email")
                go = st.form_submit_button("Send reset code", type="primary", use_container_width=True)
            if go:
                email = email.strip().lower()
                if get_user(email):
                    code = new_otp(); save_otp(email, code, "password_reset")
                    send_otp(email, code, "password_reset")
                st.session_state.email = email
                st.info("If that email exists, a code was sent.")
                goto_auth("reset")
            if st.button("← Back to login"): goto_auth("login")

        elif mode == "reset":
            email = st.session_state.email
            st.markdown("### Reset password")
            with st.form("reset"):
                code = st.text_input("Reset code", max_chars=6)
                pw = st.text_input("New password", type="password")
                go = st.form_submit_button("Reset", type="primary", use_container_width=True)
            if go:
                if not valid_pw(pw):
                    st.error("Password needs 8+ chars, letters and numbers.")
                elif not check_otp(email, code.strip(), "password_reset"):
                    st.error("Invalid or expired code.")
                else:
                    set_password(email, pw)
                    st.success("Password reset. Please log in.")
                    goto_auth("login")
            if st.button("← Back to login"): goto_auth("login")

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

