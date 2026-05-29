import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from classes import Concert

# ────────────────────────────────────────────────────────────────────────────
# session_state init
# ────────────────────────────────────────────────────────────────────────────
if "concert" not in st.session_state:
    st.session_state.concert = None

# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────
def fmt(seconds):
    return str(timedelta(seconds=int(seconds)))

def build_df(concert):
    rows = []
    for rec in concert.record:
        end = rec["exitTime"] or datetime.now()
        dur = (end - rec["entryTime"]).total_seconds() if rec["entryTime"] else 0
        rows.append({
            "Ticket":    rec["ticketID"],
            "Name":      rec["name"],
            "Entry":     rec["entryTime"].strftime("%H:%M:%S") if rec["entryTime"] else "N/A",
            "Exit":      rec["exitTime"].strftime("%H:%M:%S") if rec["exitTime"] else "Still inside",
            "Duration":  fmt(dur),
            "Status":    "Inside" if rec["exitTime"] is None else "Exited",
            "_dur_sec":  dur,
            "_exit_dt":  rec["exitTime"],
            "_entry_dt": rec["entryTime"],
        })
    return pd.DataFrame(rows)

# ────────────────────────────────────────────────────────────────────────────
# SCREEN 1 — Concert Setup
# ────────────────────────────────────────────────────────────────────────────
if st.session_state.concert is None:
    st.title("🎵 Concert Attendance System")
    st.subheader("Set up a new concert")

    c1, c2, c3 = st.columns(3)
    h = c1.number_input("Hours",   min_value=0, max_value=23, value=2)
    m = c2.number_input("Minutes", min_value=0, max_value=59, value=30)
    s = c3.number_input("Seconds", min_value=0, max_value=59, value=0)

    if st.button("Create Concert Entry", use_container_width=True):
        st.session_state.concert = Concert(hours=int(h), mins=int(m), secs=int(s))
        st.rerun()

    st.stop()

# ────────────────────────────────────────────────────────────────────────────
# SCREEN 2 — Main App
# ────────────────────────────────────────────────────────────────────────────
concert = st.session_state.concert

st.title("Concert Attendance System")
st.caption(f"Concert duration: {concert.duration}")

if st.button("New Concert"):
    st.session_state.concert = None
    st.rerun()

st.divider()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Manage Attendees")
    st.divider()

    # Push
    st.subheader("Push Attendee")
    name_input = st.text_input("Name", placeholder="Enter attendee name", label_visibility="collapsed")
    if st.button("Push", use_container_width=True):
        if name_input.strip():
            existing_ids = [a.get("ticketID", 0) for a in concert.record]
            next_ticket  = max(existing_ids) + 1 if existing_ids else 1
            attendee = {
                "ticketID":  next_ticket,
                "name":      name_input.strip(),
                "entryTime": datetime.now(),
                "exitTime":  None,
            }
            concert.attendees.append(attendee)
            concert.record.append(attendee)
            st.success(f"{name_input.strip()} entered. Ticket #{next_ticket}")
            st.rerun()
        else:
            st.error("Name cannot be empty.")

    st.divider()

    # Pop
    st.subheader("Pop Attendee")
    if st.button("Pop Last", use_container_width=True):
        if not concert.attendees:
            st.error("No attendees inside the venue.")
        else:
            attendee = concert.attendees.pop()
            attendee["exitTime"] = datetime.now()
            st.success(f"{attendee['name']} exited. Ticket #{attendee['ticketID']}")
            st.rerun()

    st.divider()

    # Peek
    st.subheader("Peek Last Attendee")
    if st.button("Peek", use_container_width=True):
        if not concert.attendees:
            st.error("No attendees inside.")
        else:
            a = concert.attendees[-1]
            entry = a["entryTime"].strftime("%H:%M:%S") if a["entryTime"] else "N/A"
            st.info(f"**{a['name']}** | Ticket #{a['ticketID']} | Entry: {entry}")

    st.divider()
    st.metric("Currently Inside", len(concert.attendees))
    st.metric("Total on Record",  len(concert.record))

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Attendees",
    "⏱ Durations",
    "⚠️ Violations",
    "📊 Report",
])

# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — Attendees
# ────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("All Attendees")

    if not concert.record:
        st.info("No attendees yet. Push some from the sidebar.")
    else:
        df = build_df(concert)
        st.dataframe(df[["Ticket", "Name", "Entry", "Exit", "Status"]], use_container_width=True, hide_index=True)

        st.subheader("Currently Inside (Stack)")
        if not concert.attendees:
            st.caption("Venue is empty.")
        else:
            stack_data = [
                {
                    "Ticket": a["ticketID"],
                    "Name":   a["name"],
                    "Entry":  a["entryTime"].strftime("%H:%M:%S") if a["entryTime"] else "N/A"
                }
                for a in reversed(concert.attendees)
            ]
            st.dataframe(pd.DataFrame(stack_data), use_container_width=True, hide_index=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — Durations
# ────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Attendance Duration")

    if not concert.record:
        st.info("No data yet.")
    else:
        df    = build_df(concert)
        valid = df[df["_dur_sec"] > 0]

        if valid.empty:
            st.info("No duration data yet.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Average Stay",  fmt(valid["_dur_sec"].mean()))
            col2.metric("Longest Stay",  fmt(valid["_dur_sec"].max()))
            col3.metric("Shortest Stay", fmt(valid["_dur_sec"].min()))

            fig, ax = plt.subplots(figsize=(9, max(3, len(valid) * 0.5)))
            ax.barh(valid["Name"], valid["_dur_sec"] / 60, height=0.5)
            ax.axvline(
                concert.duration.total_seconds() / 60,
                color="red", linestyle="--", linewidth=1, label="Concert Duration"
            )
            ax.set_xlabel("Minutes")
            ax.set_title("Stay Duration per Attendee")
            ax.legend(fontsize=8)
            ax.grid(axis="x", linestyle=":")
            st.pyplot(fig)
            plt.close(fig)

            st.dataframe(df[["Ticket", "Name", "Duration"]], use_container_width=True, hide_index=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — Violations
# ────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Rule Violations")

    if not concert.record:
        st.info("No data yet.")
    else:
        violations = []
        for rec in concert.record:
            if rec["entryTime"] is None:
                continue
            end      = rec["exitTime"] or datetime.now()
            attended = end - rec["entryTime"]
            if attended > concert.duration:
                violations.append({"Ticket": rec["ticketID"], "Name": rec["name"], "Violation": "Overstay"})
            elif rec["exitTime"] and attended < concert.duration:
                violations.append({"Ticket": rec["ticketID"], "Name": rec["name"], "Violation": "Early Exit"})

        if not violations:
            st.success("No violations detected!")
        else:
            st.dataframe(pd.DataFrame(violations), use_container_width=True, hide_index=True)

# ────────────────────────────────────────────────────────────────────────────
# TAB 4 — Report
# ────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Attendance Report")

    if not concert.record:
        st.info("No data yet.")
    else:
        df = build_df(concert)

        total    = len(df)
        still_in = (df["Status"] == "Inside").sum()
        exited   = (df["Status"] == "Exited").sum()

        v_count = 0
        for rec in concert.record:
            if rec["entryTime"] is None:
                continue
            end      = rec["exitTime"] or datetime.now()
            attended = end - rec["entryTime"]
            if attended > concert.duration or (rec["exitTime"] and attended < concert.duration):
                v_count += 1

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Registered", total)
        col2.metric("Still Inside",     still_in)
        col3.metric("Exited",           exited)
        col4.metric("Violations",       v_count)

        st.divider()
        st.write("**Entry & Exit Summary**")
        st.dataframe(df[["Ticket", "Name", "Entry", "Exit", "Status"]], use_container_width=True, hide_index=True)

        valid = df[df["_dur_sec"] > 0]
        if not valid.empty:
            st.divider()
            st.write("**Duration Statistics**")
            s1, s2, s3 = st.columns(3)
            s1.metric("Average Stay",  fmt(valid["_dur_sec"].mean()))
            s2.metric("Longest Stay",  fmt(valid["_dur_sec"].max()))
            s3.metric("Shortest Stay", fmt(valid["_dur_sec"].min()))

            fig2, ax2 = plt.subplots(figsize=(8, 3))
            ax2.hist(valid["_dur_sec"] / 60, bins=8)
            ax2.axvline(
                concert.duration.total_seconds() / 60,
                color="red", linestyle="--", linewidth=1, label="Concert Duration"
            )
            ax2.set_xlabel("Minutes")
            ax2.set_ylabel("Attendees")
            ax2.set_title("Distribution of Stay Durations")
            ax2.legend(fontsize=8)
            ax2.grid(axis="y", linestyle=":")
            st.pyplot(fig2)
            plt.close(fig2)

        st.divider()
        csv = df[["Ticket", "Name", "Entry", "Exit", "Duration", "Status"]].to_csv(index=False).encode()
        st.download_button(
            "Download Report CSV",
            data=csv,
            file_name=f"attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )