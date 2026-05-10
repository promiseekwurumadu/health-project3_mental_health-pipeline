# dashboard.py
# This builds a live interactive web dashboard
# using only Python — no HTML or JavaScript needed
# Run it with: streamlit run dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3

# ── PAGE CONFIGURATION ────────────────────────────────────────────
# This must be the very first streamlit command in the file
st.set_page_config(
    page_title = "Mental Health Services Dashboard",
    page_icon  = "🧠",
    layout     = "wide"   # use full screen width
)

# ── LOAD DATA FROM DATABASE ───────────────────────────────────────
@st.cache_data  # cache means: only load from database once
                # then store in memory for speed
                # like keeping a book on your desk instead of
                # going to the library every time you need it
def load_data():
    conn = sqlite3.connect('health.db')

    # Join facilities and capacity tables into one dataframe
    df = pd.read_sql("""
        SELECT
            f.facility_id,
            f.state,
            f.facility_type,
            f.urban_rural,
            f.accepts_insurance,
            f.operating_months,
            f.year,
            c.patients_served,
            c.staff_count,
            c.bed_count,
            c.patients_per_staff,
            c.num_services,
            c.is_overburdened
        FROM facilities f
        JOIN capacity c
          ON f.facility_id = c.facility_id
         AND f.year        = c.year
    """, conn)

    conn.close()
    return df

def load_services():
    conn = sqlite3.connect('health.db')
    df   = pd.read_sql("SELECT * FROM services", conn)
    conn.close()
    return df

# ── HEADER ────────────────────────────────────────────────────────
st.title("🧠 Mental Health Services Dashboard")
st.markdown("**US Mental Health Facilities | 2020–2022 | N-MHSS Survey Data**")
st.markdown("---")

# ── LOAD DATA ─────────────────────────────────────────────────────
df       = load_data()
services = load_services()

# ── SIDEBAR FILTERS ───────────────────────────────────────────────
# The sidebar is the panel on the left side of the screen
# Everything here controls what the charts show
st.sidebar.header("🔧 Filters")
st.sidebar.markdown("Use these to explore the data")

# Year filter
selected_years = st.sidebar.multiselect(
    "Select Year(s)",
    options = sorted(df['year'].unique()),
    default = sorted(df['year'].unique())  # all years selected by default
)

# State filter
selected_states = st.sidebar.multiselect(
    "Select State(s)",
    options = sorted(df['state'].unique()),
    default = sorted(df['state'].unique())
)

# Facility type filter
selected_types = st.sidebar.multiselect(
    "Select Facility Type(s)",
    options = sorted(df['facility_type'].unique()),
    default = sorted(df['facility_type'].unique())
)

# Urban/Rural filter
selected_urban = st.sidebar.multiselect(
    "Urban / Rural",
    options = sorted(df['urban_rural'].unique()),
    default = sorted(df['urban_rural'].unique())
)

# ── APPLY FILTERS ─────────────────────────────────────────────────
# Filter the dataframe based on what the user selected
filtered = df[
    (df['year'].isin(selected_years))         &
    (df['state'].isin(selected_states))       &
    (df['facility_type'].isin(selected_types))&
    (df['urban_rural'].isin(selected_urban))
]

# ── WARNING IF NO DATA ────────────────────────────────────────────
if filtered.empty:
    st.warning("No data matches your filters. Please adjust the selections.")
    st.stop()

# ── TOP METRICS BAR ───────────────────────────────────────────────
# These are the big numbers at the top — like a scoreboard
st.subheader("📊 Summary Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Facilities",
    f"{len(filtered):,}"
)
col2.metric(
    "Total Patients Served",
    f"{filtered['patients_served'].sum():,.0f}"
)
col3.metric(
    "Avg Patients per Facility",
    f"{filtered['patients_served'].mean():,.0f}"
)
col4.metric(
    "Overburdened Facilities",
    f"{filtered['is_overburdened'].sum():,.0f}"
)
col5.metric(
    "States Covered",
    f"{filtered['state'].nunique()}"
)

st.markdown("---")

# ── TABS ──────────────────────────────────────────────────────────
# Tabs are like different pages within the same dashboard
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ By State",
    "🏥 By Facility Type",
    "📈 Trends Over Time",
    "⚠️ Overburdened Facilities"
])

# ════════════════════════════════════════════════════════════════
# TAB 1 — BY STATE
# ════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Mental Health Services by State")

    col1, col2 = st.columns(2)

    with col1:
        # Bar chart — facilities per state (top 15)
        state_counts = (
            filtered.groupby('state')['facility_id']
            .count()
            .reset_index()
            .rename(columns={'facility_id': 'facility_count'})
            .sort_values('facility_count', ascending=False)
            .head(15)
        )

        fig = px.bar(
            state_counts,
            x     = 'state',
            y     = 'facility_count',
            title = 'Top 15 States by Number of Facilities',
            color = 'facility_count',
            color_continuous_scale = 'Blues'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Bar chart — average patients per state (top 15)
        state_patients = (
            filtered.groupby('state')['patients_served']
            .mean()
            .reset_index()
            .rename(columns={'patients_served': 'avg_patients'})
            .sort_values('avg_patients', ascending=False)
            .head(15)
        )

        fig2 = px.bar(
            state_patients,
            x     = 'state',
            y     = 'avg_patients',
            title = 'Top 15 States by Average Patients Served',
            color = 'avg_patients',
            color_continuous_scale = 'Greens'
        )
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Insurance acceptance by state
    state_insurance = (
        filtered.groupby('state')['accepts_insurance']
        .mean()
        .mul(100)
        .reset_index()
        .rename(columns={'accepts_insurance': 'pct_accepts_insurance'})
        .sort_values('pct_accepts_insurance', ascending=False)
    )

    fig3 = px.bar(
        state_insurance,
        x     = 'state',
        y     = 'pct_accepts_insurance',
        title = 'Percentage of Facilities Accepting Insurance by State',
        color = 'pct_accepts_insurance',
        color_continuous_scale = 'RdYlGn'
    )
    fig3.add_hline(
        y          = state_insurance['pct_accepts_insurance'].mean(),
        line_dash  = "dash",
        line_color = "red",
        annotation_text = "National Average"
    )
    st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 2 — BY FACILITY TYPE
# ════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Analysis by Facility Type")

    col1, col2 = st.columns(2)

    with col1:
        # Pie chart — facility type distribution
        type_counts = (
            filtered.groupby('facility_type')['facility_id']
            .count()
            .reset_index()
            .rename(columns={'facility_id': 'count'})
        )

        fig4 = px.pie(
            type_counts,
            names  = 'facility_type',
            values = 'count',
            title  = 'Distribution of Facility Types'
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        # Box plot — patient distribution per facility type
        fig5 = px.box(
            filtered,
            x     = 'facility_type',
            y     = 'patients_served',
            title = 'Patient Volume Distribution by Facility Type',
            color = 'facility_type'
        )
        fig5.update_layout(
            showlegend  = False,
            xaxis_tickangle = -30
        )
        st.plotly_chart(fig5, use_container_width=True)

    # Average services offered per facility type
    type_services = (
        filtered.groupby('facility_type')['num_services']
        .mean()
        .reset_index()
        .rename(columns={'num_services': 'avg_services'})
        .sort_values('avg_services', ascending=True)
    )

    fig6 = px.bar(
        type_services,
        x           = 'avg_services',
        y           = 'facility_type',
        orientation = 'h',
        title       = 'Average Number of Services Offered by Facility Type',
        color       = 'avg_services',
        color_continuous_scale = 'Purples'
    )
    st.plotly_chart(fig6, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 3 — TRENDS OVER TIME
# ════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("How Has Mental Health Provision Changed Over Time?")

    # Average patients per year
    yearly = (
        filtered.groupby('year')
        .agg(
            avg_patients    = ('patients_served', 'mean'),
            total_facilities= ('facility_id', 'count'),
            avg_staff       = ('staff_count', 'mean'),
            avg_beds        = ('bed_count', 'mean')
        )
        .reset_index()
    )

    col1, col2 = st.columns(2)

    with col1:
        fig7 = px.line(
            yearly,
            x      = 'year',
            y      = 'avg_patients',
            title  = 'Average Patients Served Per Facility Over Time',
            markers= True
        )
        fig7.update_traces(line_color='#1f77b4', line_width=3)
        st.plotly_chart(fig7, use_container_width=True)

    with col2:
        fig8 = px.line(
            yearly,
            x      = 'year',
            y      = 'avg_staff',
            title  = 'Average Staff Count Per Facility Over Time',
            markers= True
        )
        fig8.update_traces(line_color='#2ca02c', line_width=3)
        st.plotly_chart(fig8, use_container_width=True)

    # Urban vs Rural trend
    urban_trend = (
        filtered.groupby(['year', 'urban_rural'])['patients_served']
        .mean()
        .reset_index()
    )

    fig9 = px.line(
        urban_trend,
        x      = 'year',
        y      = 'patients_served',
        color  = 'urban_rural',
        title  = 'Average Patients Served: Urban vs Rural vs Suburban Over Time',
        markers= True
    )
    fig9.update_traces(line_width=2)
    st.plotly_chart(fig9, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 4 — OVERBURDENED FACILITIES
# ════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("⚠️ Overburdened Facilities Analysis")
    st.markdown(
        "Facilities are flagged as **overburdened** when they serve "
        "more than **50 patients per staff member**. "
        "This is a key indicator of service quality risk."
    )

    col1, col2 = st.columns(2)

    with col1:
        # Overburdened by state
        overburden_state = (
            filtered.groupby('state')['is_overburdened']
            .sum()
            .reset_index()
            .rename(columns={'is_overburdened': 'overburdened_count'})
            .sort_values('overburdened_count', ascending=False)
            .head(15)
        )

        fig10 = px.bar(
            overburden_state,
            x     = 'state',
            y     = 'overburdened_count',
            title = 'Top 15 States with Most Overburdened Facilities',
            color = 'overburdened_count',
            color_continuous_scale = 'Reds'
        )
        st.plotly_chart(fig10, use_container_width=True)

    with col2:
        # Overburdened by facility type
        overburden_type = (
            filtered.groupby('facility_type')['is_overburdened']
            .mean()
            .mul(100)
            .reset_index()
            .rename(columns={'is_overburdened': 'pct_overburdened'})
            .sort_values('pct_overburdened', ascending=False)
        )

        fig11 = px.bar(
            overburden_type,
            x     = 'facility_type',
            y     = 'pct_overburdened',
            title = 'Percentage Overburdened by Facility Type',
            color = 'pct_overburdened',
            color_continuous_scale = 'OrRd'
        )
        fig11.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig11, use_container_width=True)

    # Raw table of overburdened facilities
    st.subheader("Overburdened Facility Detail")
    overburden_detail = (
        filtered[filtered['is_overburdened'] == True][[
            'facility_id', 'state', 'facility_type',
            'patients_served', 'staff_count',
            'patients_per_staff', 'year'
        ]]
        .sort_values('patients_per_staff', ascending=False)
        .head(50)
    )

    st.dataframe(
        overburden_detail.style.background_gradient(
            subset = ['patients_per_staff'],
            cmap   = 'Reds'
        ),
        use_container_width=True
    )

# ── FOOTER ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "Built with Python · Streamlit · Plotly · SQLite | "
    "Portfolio Project 3 of 3 | Data Engineering"
)