import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="centered")

st.title("💰 Smart Expense Tracker")
st.subheader("Track your daily expenses easily")

# Database
conn = sqlite3.connect("expenses.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT,
    note TEXT,
    date TEXT
)
""")
conn.commit()

# Add expense
st.header("Add Expense")

amount = st.number_input("Amount", min_value=0.0, step=1.0)
category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Other"])
note = st.text_input("Note")
selected_date = st.date_input("Date", date.today())

if st.button("Add"):
    c.execute("INSERT INTO expenses(amount,category,note,date) VALUES(?,?,?,?)",
              (amount, category, note, str(selected_date)))
    conn.commit()
    st.success("Expense Added!")

# Show expenses
st.header("All Expenses")

df = pd.read_sql_query("SELECT * FROM expenses", conn)

if not df.empty:
    st.dataframe(df)
    st.write("Total Spent:", df["amount"].sum())
else:
    st.info("No expenses yet")


import plotly.express as px

st.header("Analytics")

if not df.empty:

    # Category pie chart
    pie = px.pie(df, names="category", values="amount", title="Spending by Category")
    st.plotly_chart(pie, use_container_width=True)

    # Daily spending chart
    df["date"] = pd.to_datetime(df["date"])
    daily = df.groupby("date")["amount"].sum().reset_index()

    line = px.line(daily, x="date", y="amount", title="Daily Spending Trend", markers=True)
    st.plotly_chart(line, use_container_width=True)


