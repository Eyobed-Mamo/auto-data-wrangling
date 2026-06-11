import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="Auto Data Wrangling", layout="wide")

# ── Load & clean data (same logic as your original script) ───
@st.cache_data
def load_data():
    url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DA0101EN-SkillsNetwork/labs/Data%20files/auto.csv"
    headers = [
        "symboling","normalized-losses","make","fuel-type","aspiration",
        "num-of-doors","body-style","drive-wheels","engine-location",
        "wheel-base","length","width","height","curb-weight","engine-type",
        "num-of-cylinders","engine-size","fuel-system","bore","stroke",
        "compression-ratio","horsepower","peak-rpm","city-mpg","highway-mpg","price"
    ]
    raw = pd.read_csv(url, names=headers)
    df = raw.copy()

    # Replace ? with NaN
    df.replace("?", np.nan, inplace=True)

    # Fill missing numeric columns with mean
    for col in ["normalized-losses", "bore", "stroke", "horsepower", "peak-rpm"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col].fillna(df[col].mean(), inplace=True)

    # Fill num-of-doors with most frequent
    df["num-of-doors"].fillna("four", inplace=True)

    # Drop rows with no price
    df.dropna(subset=["price"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Fix data types
    df["price"]      = df["price"].astype(float)
    df["horsepower"] = df["horsepower"].astype(float)
    df["peak-rpm"]   = df["peak-rpm"].astype(float)

    # Unit conversions
    df["city-L/100km"]    = 235 / df["city-mpg"].astype(float)
    df["highway-L/100km"] = 235 / df["highway-mpg"].astype(float)

    # Normalize
    for col in ["length", "width", "height"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col] / df[col].max()

    # Binning horsepower
    bins = np.linspace(df["horsepower"].min(), df["horsepower"].max(), 4)
    df["horsepower-binned"] = pd.cut(
        df["horsepower"], bins,
        labels=["Low", "Medium", "High"],
        include_lowest=True
    )

    # Dummy variables
    df["fuel-type-gas"]      = (df["fuel-type"] == "gas").astype(int)
    df["fuel-type-diesel"]   = (df["fuel-type"] == "diesel").astype(int)
    df["aspiration-std"]     = (df["aspiration"] == "std").astype(int)
    df["aspiration-turbo"]   = (df["aspiration"] == "turbo").astype(int)

    return raw, df

raw_df, clean_df = load_data()

# ── Sidebar filters ───────────────────────────────────────────
st.sidebar.title("🔧 Filters")

fuel_options = clean_df["fuel-type"].dropna().unique().tolist()
selected_fuel = st.sidebar.multiselect("Fuel Type", fuel_options, default=fuel_options)

body_options = clean_df["body-style"].dropna().unique().tolist()
selected_body = st.sidebar.multiselect("Body Style", body_options, default=body_options)

drive_options = clean_df["drive-wheels"].dropna().unique().tolist()
selected_drive = st.sidebar.multiselect("Drive Wheels", drive_options, default=drive_options)

filtered = clean_df[
    clean_df["fuel-type"].isin(selected_fuel) &
    clean_df["body-style"].isin(selected_body) &
    clean_df["drive-wheels"].isin(selected_drive)
]

# ── Header ────────────────────────────────────────────────────
st.title("🚗 Auto Dataset — Data Wrangling Portfolio Project")
st.markdown(
    "An end-to-end data cleaning and exploration project using the "
    "[UCI Auto Dataset](https://archive.ics.uci.edu/ml/machine-learning-databases/autos/imports-85.data). "
    "Use the sidebar to filter the data."
)

# ── Metrics row ───────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Cars", len(filtered))
col2.metric("Avg Price", f"${filtered['price'].mean():,.0f}")
col3.metric("Avg Horsepower", f"{filtered['horsepower'].mean():.0f} hp")
col4.metric("Fuel Types", filtered["fuel-type"].nunique())

st.divider()

# ── Tab layout ────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Charts", "🧹 Data Cleaning", "📋 Raw vs Clean", "🔢 Full Dataset"])

# ── Tab 1: Charts ─────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Price by Body Style")
        fig1 = px.box(filtered, x="body-style", y="price", color="body-style",
                      labels={"price": "Price (USD)", "body-style": "Body Style"})
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("Horsepower Distribution")
        fig2 = px.histogram(filtered, x="horsepower", color="horsepower-binned",
                            nbins=30, category_orders={"horsepower-binned": ["Low","Medium","High"]},
                            labels={"horsepower": "Horsepower", "horsepower-binned": "Category"})
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Price vs Engine Size")
        fig3 = px.scatter(filtered, x="engine-size", y="price", color="fuel-type",
                          hover_data=["make", "body-style"],
                          labels={"engine-size": "Engine Size", "price": "Price (USD)"})
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.subheader("City Fuel Efficiency (L/100km)")
        fig4 = px.bar(
            filtered.groupby("body-style")["city-L/100km"].mean().reset_index(),
            x="body-style", y="city-L/100km", color="body-style",
            labels={"city-L/100km": "Avg L/100km", "body-style": "Body Style"}
        )
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

# ── Tab 2: Data Cleaning Steps ────────────────────────────────
with tab2:
    st.subheader("What Was Done to Clean This Data")

    steps = {
        "1. Replaced '?' with NaN": (
            "The raw dataset used '?' as a placeholder for missing values. "
            "These were replaced with NaN so pandas can detect and handle them properly."
        ),
        "2. Filled missing numeric values with column mean": (
            "Columns like normalized-losses, bore, stroke, horsepower, and peak-rpm "
            "had missing entries filled with each column's average — a common imputation strategy."
        ),
        "3. Filled missing 'num-of-doors' with most frequent value": (
            "84% of sedans have four doors, so missing values were filled with 'four'."
        ),
        "4. Dropped rows with no price": (
            "Price is the target variable for prediction. Rows without a price are useless "
            "for modeling, so they were removed entirely."
        ),
        "5. Fixed data types": (
            "Columns like price, horsepower, and peak-rpm were stored as text (object). "
            "They were converted to float so math operations work correctly."
        ),
        "6. Converted mpg → L/100km": (
            "Fuel consumption was converted from miles per gallon to liters per 100km "
            "using the formula: L/100km = 235 / mpg."
        ),
        "7. Normalized length, width, height": (
            "Each dimension was divided by its max value, scaling all values to a 0–1 range. "
            "This prevents large-scale columns from dominating models."
        ),
        "8. Binned horsepower into Low / Medium / High": (
            "Continuous horsepower values were grouped into 3 equal-width bins for "
            "easier categorical analysis."
        ),
        "9. Created dummy variables for fuel-type and aspiration": (
            "Text categories like 'gas'/'diesel' were converted to 0/1 columns so "
            "they can be used in machine learning models."
        ),
    }

    for title, explanation in steps.items():
        with st.expander(title):
            st.write(explanation)

    st.subheader("Missing Values — Before Cleaning")
    raw_copy = raw_df.replace("?", np.nan)
    missing = raw_copy.isnull().sum()
    missing = missing[missing > 0].reset_index()
    missing.columns = ["Column", "Missing Count"]
    missing["% Missing"] = (missing["Missing Count"] / len(raw_copy) * 100).round(1)
    st.dataframe(missing, use_container_width=True)

# ── Tab 3: Raw vs Clean ───────────────────────────────────────
with tab3:
    st.subheader("Raw Data (first 10 rows)")
    st.dataframe(raw_df.head(10), use_container_width=True)

    st.subheader("Cleaned Data (first 10 rows)")
    st.dataframe(clean_df.head(10), use_container_width=True)

# ── Tab 4: Full Dataset ───────────────────────────────────────
with tab4:
    st.subheader(f"Filtered Dataset — {len(filtered)} rows")
    st.dataframe(filtered, use_container_width=True)
    st.download_button("⬇ Download Filtered CSV", filtered.to_csv(index=False),
                       file_name="filtered_auto_data.csv", mime="text/csv")