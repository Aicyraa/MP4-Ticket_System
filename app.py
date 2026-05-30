import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from utils import fmt, build_df, metric_card, metric_row, box_title, empty_state
from datetime import datetime, timedelta
import sys
import os


sys.path.insert(0, os.path.dirname(__file__))
from classes import Concert

st.set_page_config(
    page_title="Concert Attendance",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

  html, body,
  [data-testid="stAppViewContainer"],
  [data-testid="stApp"],
  [data-testid="stMain"],
  .main, .block-container {
    background-color: #F7F7F8 !important;
    color: #1A1A2E !important;
    font-family: 'DM Sans', sans-serif !important;
  }

  #MainMenu, footer, header { visibility: hidden; }
  section[data-testid="stSidebar"] { display: none; }
  .block-container { padding: 2rem 3rem 4rem 3rem !important; max-width: 1200px; }

  [data-testid="stTextInput"] input,
  [data-testid="stNumberInput"] input {
    background-color: #FFFFFF !important;
    color: #1A1A2E !important;
    border: 1px solid #E8E8EE !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
  }

  .stTabs [data-baseweb="tab-list"] {
    gap: 0.25rem; background: #EDEDF0 !important;
    border-radius: 12px; padding: 4px; margin-bottom: 1.5rem;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 9px; font-size: 0.85rem; font-weight: 500;
    padding: 0.45rem 1.1rem; color: #888 !important; background: transparent !important;
  }
  .stTabs [aria-selected="true"] {
    background: #FFFFFF !important; color: #1A1A2E !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }
  .stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding: 0 !important; }
  .stTabs [data-baseweb="tab-border"] { display: none !important; }

  .stButton > button {
    font-family: 'DM Sans', sans-serif !important; font-size: 0.85rem !important;
    font-weight: 500 !important; border-radius: 10px !important;
    padding: 0.45rem 1.1rem !important; border: 1px solid #E8E8EE !important;
    background: #FFFFFF !important; color: #1A1A2E !important;
    transition: all 0.15s ease !important;
  }
  .stButton > button:hover {
    border-color: #1A1A2E !important; background: #1A1A2E !important; color: #FFFFFF !important;
  }

  .metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
  .metric-card {
    flex: 1; background: #FFFFFF; border: 1px solid #E8E8EE;
    border-radius: 14px; padding: 1.2rem 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }
  .metric-card .label {
    font-size: 0.73rem; font-weight: 500; text-transform: uppercase;
    letter-spacing: 0.8px; color: #999; margin-bottom: 0.4rem;
  }
  .metric-card .value { font-size: 2rem; font-weight: 600; color: #1A1A2E; line-height: 1; }
  .metric-card .value.green { color: #2D9E6B; }
  .metric-card .value.amber { color: #E07B1A; }
  .metric-card .value.red   { color: #D94F4F; }
  .metric-card .value.blue  { color: #2E6EE0; }

  .page-header {
    background: #FFFFFF; border: 1px solid #E8E8EE; border-radius: 16px;
    padding: 1.25rem 1.75rem; margin-bottom: 1.75rem; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  }
  .page-header h1 { font-size: 1.4rem; font-weight: 600; margin: 0 0 2px 0; color: #1A1A2E; }
  .page-header p  { font-size: 0.8rem; color: #999; margin: 0; font-family: 'DM Mono', monospace; }

  .box-title {
    font-size: 0.73rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.9px; color: #AAA; margin-bottom: 0.5rem;
  }

  .peek-card { background: #F7F7F8; border-radius: 12px; padding: 1rem 1.25rem; }
  .peek-row { display: flex; justify-content: space-between; align-items: center; padding: 0.55rem 0; border-bottom: 1px solid #E8E8EE; }
  .peek-row:last-child { border-bottom: none; }
  .peek-label { font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; color: #999; }
  .peek-value { font-weight: 500; color: #1A1A2E; font-family: 'DM Mono', monospace; font-size: 0.9rem; }

  .setup-wrapper { text-align: center; padding: 4rem 0 2rem 0; }
  .setup-icon    { font-size: 3rem; margin-bottom: 0.5rem; }
  .setup-title   { font-size: 1.8rem; font-weight: 600; color: #1A1A2E; margin-bottom: 0.25rem; }
  .setup-sub     { font-size: 0.9rem; color: #888; }

  .empty-state { text-align: center; padding: 3rem 1rem; color: #BBBBCC; }
  .empty-icon  { font-size: 2.5rem; margin-bottom: 0.5rem; }
  .empty-text  { font-size: 0.9rem; margin: 0; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Session state ─────────────────────────────────────────────────────────────
if "concert" not in st.session_state:
    st.session_state.concert = None
if "action_msg" not in st.session_state:
    st.session_state.action_msg = None
if "action_type" not in st.session_state:
    st.session_state.action_type = None


# ════════════════════════════════════════════════════════════════════════════
# SCREEN 1 — Setup
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.concert is None:
    st.markdown(
        '<div class="setup-wrapper">'
        '<div class="setup-icon">🎵</div>'
        '<div class="setup-title">Concert Attendance</div>'
        '<div class="setup-sub">Set the concert duration to get started</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("**Concert Duration**")
        c1, c2, c3 = st.columns(3)
        h = c1.number_input("Hours", min_value=0, max_value=23, value=2)
        m = c2.number_input("Minutes", min_value=0, max_value=59, value=0)
        s = c3.number_input("Seconds", min_value=0, max_value=59, value=0)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Create Concert →", width='stretch'):
            if h == 0 and m == 0 and s == 0:
                st.error("Duration must be greater than zero.")
            else:
                st.session_state.concert = Concert(
                    hours=int(h), mins=int(m), secs=int(s)
                )
                st.rerun()
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# SCREEN 2 — Main
# ════════════════════════════════════════════════════════════════════════════
concert = st.session_state.concert

# ── Page header ───────────────────────────────────────────────────────────────
h_left, h_right = st.columns([1, 0.16])
with h_left:
    st.markdown(
        f'<div class="page-header">'
        f"<h1>🎵 Concert Attendance System</h1>"
        f'<p>Duration: {concert.duration} &nbsp;·&nbsp; {datetime.now().strftime("%A, %d %B %Y")}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )
with h_right:
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    if st.button("+ New Concert", width='stretch'):
        st.session_state.concert = None
        st.session_state.action_msg = None
        st.rerun()


# ── Peek dialog ───────────────────────────────────────────────────────────────
@st.dialog("Last Attendee Inside")
def peek_modal():
    if not concert.attendees:
        st.warning("No attendees currently inside.")
        return
    a = concert.attendees[-1]
    entry = a["entryTime"].strftime("%H:%M:%S") if a["entryTime"] else "N/A"
    elapsed = (
        str(timedelta(seconds=int((datetime.now() - a["entryTime"]).total_seconds())))
        if a["entryTime"]
        else "N/A"
    )
    st.markdown(
        f'<div class="peek-card">'
        f'<div class="peek-row"><span class="peek-label">Name</span><span class="peek-value">{a["name"]}</span></div>'
        f'<div class="peek-row"><span class="peek-label">Ticket ID</span><span class="peek-value">#{a["ticketID"]}</span></div>'
        f'<div class="peek-row"><span class="peek-label">Entry Time</span><span class="peek-value">{entry}</span></div>'
        f'<div class="peek-row"><span class="peek-label">Time Elapsed</span><span class="peek-value">{elapsed}</span></div>'
        f"</div>",
        unsafe_allow_html=True,
    )


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🎟  Attendees",
        "⏱  Durations",
        "⚠️  Violations",
        "📊  Report",
    ]
)

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Attendees
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    inside = len(concert.attendees)
    total = len(concert.record)
    exited = total - inside
    metric_row(
        metric_card("Currently Inside", inside, "green"),
        metric_card("Total on Record", total, "blue"),
        metric_card("Already Exited", exited),
    )

    box_title("Manage Attendees")
    nc, pc, oc, kc = st.columns([3, 0.7, 0.7, 0.7])
    with nc:
        name_input = st.text_input(
            "n",
            placeholder="Enter attendee name...",
            label_visibility="collapsed",
            key="name_input",
        )
    with pc:
        push_clicked = st.button("Push", width='stretch')
    with oc:
        pop_clicked = st.button("Pop", width='stretch')
    with kc:
        peek_clicked = st.button("Peek", width='stretch')

    if push_clicked:
        stripped = name_input.strip()
        if stripped:
            result = concert.pushAttendee(name=stripped)
            if result:
                st.session_state.action_msg = (
                    f"✓ {result['name']} entered — Ticket #{result['ticketID']}"
                )
                st.session_state.action_type = "success"
        else:
            st.session_state.action_msg = "Name cannot be empty."
            st.session_state.action_type = "error"
        st.rerun()

    if pop_clicked:
        if not concert.attendees:
            st.session_state.action_msg = "No attendees inside the venue."
            st.session_state.action_type = "error"
        else:
            result = concert.popAttendee()
            if result:
                exit_str = result["exitTime"].strftime("%H:%M:%S")
                st.session_state.action_msg = f"✓ {result['name']} exited — Ticket #{result['ticketID']} · {exit_str}"
                st.session_state.action_type = "success"
        st.rerun()

    if peek_clicked:
        if not concert.attendees:
            st.session_state.action_msg = "No attendees currently inside."
            st.session_state.action_type = "error"
            st.rerun()
        else:
            peek_modal()

    if st.session_state.action_msg:
        if st.session_state.action_type == "success":
            st.success(st.session_state.action_msg)
        else:
            st.error(st.session_state.action_msg)
        st.session_state.action_msg = None
        st.session_state.action_type = None

    st.divider()

    lc, rc = st.columns([1.4, 1])
    with lc:
        box_title("All Attendees (Record)")
        if not concert.record:
            empty_state("📋", "No attendees on record yet.")
        else:
            df = build_df(concert)
            st.dataframe(
                df[["Ticket", "Name", "Entry", "Exit", "Status"]],
                width='stretch',
                hide_index=True,
            )
    with rc:
        box_title("Currently Inside (Stack — LIFO)")
        if not concert.attendees:
            empty_state("🏟️", "Venue is empty.")
        else:
            stack_data = [
                {
                    "Ticket": a["ticketID"],
                    "Name": a["name"],
                    "Entry": (
                        a["entryTime"].strftime("%H:%M:%S") if a["entryTime"] else "N/A"
                    ),
                }
                for a in reversed(concert.attendees)
            ]
            st.dataframe(
                pd.DataFrame(stack_data), width='stretch', hide_index=True
            )


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Durations
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    if not concert.record:
        empty_state("⏱", "No data yet. Add some attendees first.")
    else:
        durations = concert.getAttendanceDuration()
        if not durations:
            empty_state("⏱", "No valid duration data available.")
        else:
            dur_secs = []
            for rec in concert.record:
                if rec["entryTime"] is None:
                    continue
                end = rec["exitTime"] or datetime.now()
                dur_secs.append((end - rec["entryTime"]).total_seconds())

            avg = sum(dur_secs) / len(dur_secs)
            mx = max(dur_secs)
            mn = min(dur_secs)
            metric_row(
                metric_card("Average Stay", fmt(avg), "blue"),
                metric_card("Longest Stay", fmt(mx), "amber"),
                metric_card("Shortest Stay", fmt(mn), "green"),
            )

            box_title("Stay Duration per Attendee")
            df = build_df(concert)
            valid = df[df["_dur_sec"] > 0]
            concert_limit = concert.duration.total_seconds() / 60

            fig, ax = plt.subplots(figsize=(9, max(3, len(valid) * 0.55)))
            fig.patch.set_facecolor("#FFFFFF")
            ax.set_facecolor("#F7F7F8")
            colors = [
                "#D94F4F" if (s / 60) > concert_limit else "#2E6EE0"
                for s in valid["_dur_sec"]
            ]
            ax.barh(
                valid["Name"],
                valid["_dur_sec"] / 60,
                color=colors,
                height=0.5,
                zorder=3,
            )
            ax.axvline(
                concert_limit, color="#E07B1A", linestyle="--", linewidth=1.5, zorder=4
            )
            ax.set_xlabel("Minutes", fontsize=9, color="#888")
            ax.tick_params(colors="#555", labelsize=8)
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.spines["bottom"].set_color("#E8E8EE")
            ax.grid(axis="x", linestyle=":", color="#E8E8EE", zorder=0)
            ax.legend(
                handles=[
                    mpatches.Patch(color="#2E6EE0", label="Normal"),
                    mpatches.Patch(color="#D94F4F", label="Overstay"),
                    mpatches.Patch(
                        color="#E07B1A",
                        label=f"Concert Duration ({fmt(concert.duration.total_seconds())})",
                    ),
                ],
                fontsize=8,
                frameon=False,
            )
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            st.divider()
            box_title("Duration Breakdown")
            st.dataframe(
                df[["Ticket", "Name", "Entry", "Exit", "Duration"]],
                width='stretch',
                hide_index=True,
            )


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Violations
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    if not concert.record:
        empty_state("⚠️", "No data yet. Add some attendees first.")
    else:
        violations = concert.detectRuleViolations()
        overstay_count = sum(1 for _, _, v in violations if v == "overstay")
        early_count = sum(1 for _, _, v in violations if v == "early exit")
        clean_count = len(concert.record) - len(violations)
        metric_row(
            metric_card("Overstays", overstay_count, "red"),
            metric_card("Early Exits", early_count, "amber"),
            metric_card("No Violation", clean_count, "green"),
        )

        box_title("Violation Log")
        if not violations:
            st.success(
                "✓ No violations detected. Everyone is within the concert duration."
            )
        else:
            vdf = pd.DataFrame(
                [
                    {"Ticket": tid, "Name": name, "Violation": v.title()}
                    for tid, name, v in violations
                ]
            )
            st.dataframe(vdf, width='stretch', hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — Report
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    if not concert.record:
        empty_state("📊", "No data yet. Add some attendees first.")
    else:
        report = concert.generateAttendanceReport()
        df = build_df(concert)
        total = report["total"]
        still_in = report["still_inside"]
        exited = report["exited"]
        v_count = len(report["violations"])
        dur_secs = report["durations"]

        metric_row(
            metric_card("Total Registered", total, "blue"),
            metric_card("Still Inside", still_in, "green"),
            metric_card("Exited", exited),
            metric_card("Violations", v_count, "red" if v_count else ""),
        )

        box_title("Entry & Exit Summary")
        st.dataframe(
            df[["Ticket", "Name", "Entry", "Exit", "Duration", "Status"]],
            width='stretch',
            hide_index=True,
        )

        if dur_secs:
            avg = sum(dur_secs) / len(dur_secs)
            mx = max(dur_secs)
            mn = min(dur_secs)
            st.divider()
            metric_row(
                metric_card("Average Stay", fmt(avg), "blue"),
                metric_card("Longest Stay", fmt(mx), "amber"),
                metric_card("Shortest Stay", fmt(mn), "green"),
            )

            box_title("Distribution of Stay Durations")
            valid = df[df["_dur_sec"] > 0]
            fig2, ax2 = plt.subplots(figsize=(9, 3.5))
            fig2.patch.set_facecolor("#FFFFFF")
            ax2.set_facecolor("#F7F7F8")
            ax2.hist(
                valid["_dur_sec"] / 60,
                bins=max(4, len(valid) // 2),
                color="#2E6EE0",
                edgecolor="#FFFFFF",
                linewidth=0.8,
                zorder=3,
            )
            ax2.axvline(
                concert.duration.total_seconds() / 60,
                color="#E07B1A",
                linestyle="--",
                linewidth=1.5,
                label=f"Concert Duration ({fmt(concert.duration.total_seconds())})",
                zorder=4,
            )
            ax2.set_xlabel("Minutes", fontsize=9, color="#888")
            ax2.set_ylabel("Attendees", fontsize=9, color="#888")
            ax2.tick_params(colors="#555", labelsize=8)
            ax2.spines[["top", "right"]].set_visible(False)
            ax2.spines[["left", "bottom"]].set_color("#E8E8EE")
            ax2.grid(axis="y", linestyle=":", color="#E8E8EE", zorder=0)
            ax2.legend(fontsize=8, frameon=False)
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

        st.divider()
        box_title("Export")
        csv = (
            df[["Ticket", "Name", "Entry", "Exit", "Duration", "Status"]]
            .to_csv(index=False)
            .encode()
        )
        st.download_button(
            label="⬇  Download Report as CSV",
            data=csv,
            file_name=f"attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            width='stretch',
        )
