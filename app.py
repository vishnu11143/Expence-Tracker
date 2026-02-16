import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.let_it_rain import rain

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Smart Expense Tracker", page_icon="💰", layout="wide")

# ---------- CUSTOM CSS (Gen Z look) ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
h1, h2, h3 { color: #00FFD1; }
div.stButton > button:first-child {
    background: linear-gradient(90deg,#00FFD1,#00A8FF);
    color:black;
    font-weight:bold;
    border-radius:12px;
    height:3em;
    width:100%;
}
</style>
""", unsafe_allow_html=True)

st.title("💸 Smart Expense Tracker")
st.caption("Track your daily expenses like a pro")

# ---------- DATABASE ----------
conn = sqlite3.connect("expenses.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    category TEXT,
    amount REAL,
    note TEXT
)
""")
conn.commit()

# ---------- INPUT FORM ----------
st.subheader("➕ Add Expense")

col1, col2, col3, col4 = st.columns(4)

with col1:
    exp_date = st.date_input("Date", date.today())

with col2:
    category = st.selectbox("Category", ["Food","Transport","Shopping","Bills","Entertainment","Other"])

with col3:
    amount = st.number_input("Amount", min_value=0.0, step=10.0)

with col4:
    note = st.text_input("Note")

if st.button("Add Expense 🚀"):
    c.execute("INSERT INTO expenses(date,category,amount,note) VALUES(?,?,?,?)",
              (str(exp_date),category,amount,note))
    conn.commit()

    st.success("Expense Added Successfully!")

    # Animation
    rain(
        emoji="💸",
        font_size=30,
        falling_speed=4,
        animation_length="short"
    )

# ---------- LOAD DATA ----------
df = pd.read_sql_query("SELECT * FROM expenses", conn)

# ---------- SUMMARY ----------
st.divider()
st.header("📊 Dashboard")

if df.empty:
    st.info("No expenses yet — add some to see magic ✨")
    st.stop()

df["date"] = pd.to_datetime(df["date"])

today_df = df[df["date"].dt.date == date.today()]
today_total = today_df["amount"].sum()
overall_total = df["amount"].sum()

colA, colB = st.columns(2)
colA.metric("Today's Spending", f"₹ {today_total}")
colB.metric("Total Spending", f"₹ {overall_total}")

# ---------- CATEGORY PIE (Neon Glow) ----------
st.subheader("Spending by Category")

pie = px.pie(df, names="category", values="amount",
             color_discrete_sequence=px.colors.sequential.Tealgrn)

pie.update_traces(textposition='inside', textinfo='percent+label')
pie.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  font_color='white')

st.plotly_chart(pie, use_container_width=True)

# ---------- DAILY TREND ----------
st.subheader("Daily Trend")

daily = df.groupby("date")["amount"].sum().reset_index()

line_color = "red" if daily["amount"].iloc[-1] > daily["amount"].mean() else "green"

trend = go.Figure()
trend.add_trace(go.Scatter(
    x=daily["date"],
    y=daily["amount"],
    mode="lines+markers",
    line=dict(color=line_color, width=4),
    marker=dict(size=8)
))

trend.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='white'
)

st.plotly_chart(trend, use_container_width=True)

# ---------- TODAY REPORT ----------
st.subheader("🧠 Smart Insight")

if today_total == 0:
    st.warning("You haven't spent anything today — saving mode activated 🧘")

elif today_total < 300:
    st.success("Great! Your spending today is under control 💚")

elif today_total < 800:
    st.info("Moderate spending today — keep balance ⚖️")

else:
    st.error("High spending today! Try to control tomorrow 🔴")

# ---------- TABLE ----------
st.subheader("📜 Expense History")
st.dataframe(df.sort_values(by="date", ascending=False), use_container_width=True)
