import streamlit as st
import pandas as pd
import plotly.express as px

# cd "C:\Users\A.MohamedArkam\OneDrive - ams OSRAM\amoa\DropBox III\Desktop\EongsRequest\ploty_Dashboard\Weeklydashboard"
# streamlit run weekly_dashboard.py

# --- Load Data Automatically ---
@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()  # remove extra spaces
    df = df[['WorkWeek', 'Type', 'Material Description', 'Cost (USD)']]
    df = df.dropna(subset=['WorkWeek', 'Type', 'Material Description', 'Cost (USD)'])
    return df

# ✅ Automatically load the file from the same folder
df = load_data("Weekly Expenditure.xlsx")

# --- App Title ---
st.title("📊 Weekly Inventory Expenditure Dashboard")
st.markdown("Using default file: **Weekly Expenditure.xlsx**")

# --- Sidebar Filters ---
st.sidebar.header("🔎 Filter")
weeks = sorted(df['WorkWeek'].unique())
types = sorted(df['Type'].unique())

selected_weeks = st.sidebar.multiselect("Select Week(s)", options=weeks, default=weeks)
selected_types = st.sidebar.multiselect("Select Type(s)", options=types, default=types)

filtered_df = df[
    df['WorkWeek'].isin(selected_weeks) &
    df['Type'].isin(selected_types)
]

# --- Metrics ---
total = filtered_df['Cost (USD)'].sum()
sap = filtered_df[filtered_df['Type'] == 'SAP']['Cost (USD)'].sum()
expense = filtered_df[filtered_df['Type'] == 'Expense']['Cost (USD)'].sum()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Spend", f"${total:,.2f}")
col2.metric("📄 SAP Spend", f"${sap:,.2f}")
col3.metric("🛠 Expense Spend", f"${expense:,.2f}")

# --- Bar Chart Weekly Spend ---
summary = (
    filtered_df.groupby(['WorkWeek', 'Type'])['Cost (USD)']
    .sum()
    .reset_index()
)

fig = px.bar(
    summary,
    x='WorkWeek',
    y='Cost (USD)',
    color='Type',
    barmode='group',
    text_auto=True,
    title="Weekly Spend Summary by Type"
)
fig.update_traces(textfont_size=14)
fig.update_layout(
    title={
        'text': "Weekly Spend Summary by Type",
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis_title="Week",
    yaxis_title="Spend ($USD)",
    title_font=dict(size=18),
    title_font_family="Arial"
)

st.plotly_chart(fig, use_container_width=True)

# --- Drill Down ---
st.subheader("🔍 Drill Down by Week")
drill_week = st.selectbox("Select Week:", options=sorted(df['WorkWeek'].unique()))
drill_types = df[df['WorkWeek'] == drill_week]['Type'].unique().tolist()
selected_drill_type = st.selectbox("Select Type:", options=drill_types)

drill_df = df[
    (df['WorkWeek'] == drill_week) &
    (df['Type'] == selected_drill_type)
]

drill_summary = (
    drill_df.groupby('Material Description')['Cost (USD)']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

st.write(f"Top 10 items for **{drill_week}** ({selected_drill_type}):")
st.dataframe(drill_summary.head(10))

drill_fig = px.bar(
    drill_summary.head(10),
    x='Material Description',
    y='Cost (USD)',
    text_auto=True,
    title=f"Top 10 Items in {drill_week} ({selected_drill_type})"
)
drill_fig.update_layout(
    xaxis_title="Material Description",
    yaxis_title="Spend ($USD)",
    title_x=0.5
)
st.plotly_chart(drill_fig, use_container_width=True)

st.download_button(
    label="📥 Download Drilldown CSV",
    data=drill_summary.to_csv(index=False),
    file_name=f"Top_Items_{drill_week}_{selected_drill_type}.csv",
    mime='text/csv'
)

# --- Full Table ---
st.subheader("📋 Filtered Table")
st.dataframe(filtered_df.reset_index(drop=True))
