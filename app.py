import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ── Brand ────────────────────────────────────────────────────
APP_NAME = "DataForge"
APP_ICON = "⚙️"
ACCENT = "#22c55e"      # green
ACCENT_DARK = "#16a34a"
MAX_FILE_SIZE_MB = 50
MAX_UNIQUE_FOR_MULTISELECT = 50

st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout="wide")

# ── Theme toggle (light/dark) ────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dark_css = f"""
<style>
.stApp {{ background-color: #0e1117; color: #fafafa; }}
section[data-testid="stSidebar"] {{ background-color: #161a23; }}
section[data-testid="stSidebar"] * {{ color: #fafafa !important; }}
h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {{ color: #fafafa; }}
div[data-testid="stMetricValue"] {{ color: {ACCENT}; }}
div[data-testid="stDataFrame"] {{ background-color: #161a23; }}
.stTabs [data-baseweb="tab"] {{ color: #c9c9c9; }}
.stTabs [aria-selected="true"] {{ color: {ACCENT} !important; border-bottom-color: {ACCENT} !important; }}
.stButton button, .stDownloadButton button {{
    background-color: {ACCENT}; color: #0e1117; border: none;
}}
.stButton button:hover, .stDownloadButton button:hover {{ background-color: {ACCENT_DARK}; color: #fff; }}
input, textarea, select {{ background-color: #1c212c !important; color: #fafafa !important; }}
</style>
"""

light_css = f"""
<style>
div[data-testid="stMetricValue"] {{ color: {ACCENT_DARK}; }}
.stTabs [aria-selected="true"] {{ color: {ACCENT_DARK} !important; border-bottom-color: {ACCENT_DARK} !important; }}
.stButton button, .stDownloadButton button {{
    background-color: {ACCENT}; color: #ffffff; border: none;
}}
.stButton button:hover, .stDownloadButton button:hover {{ background-color: {ACCENT_DARK}; color: #fff; }}
</style>
"""

st.markdown(dark_css if st.session_state.dark_mode else light_css, unsafe_allow_html=True)


# ── Built-in sample dataset (movies) ────────────────────────
def build_sample_movies_df():
    data = [
        {"title": "Inception", "genre": "Sci-Fi", "director": "Christopher Nolan", "release_year": 2010, "runtime_min": 148, "budget_musd": 160, "revenue_musd": 836.8, "rating": 8.8, "votes": 2400000},
        {"title": "The Dark Knight", "genre": "Action", "director": "Christopher Nolan", "release_year": 2008, "runtime_min": 152, "budget_musd": 185, "revenue_musd": 1006.0, "rating": 9.0, "votes": 2700000},
        {"title": "Parasite", "genre": "Thriller", "director": "Bong Joon-ho", "release_year": 2019, "runtime_min": 132, "budget_musd": 11, "revenue_musd": 263.1, "rating": 8.5, "votes": 850000},
        {"title": "Get Out", "genre": "Horror", "director": "Jordan Peele", "release_year": 2017, "runtime_min": 104, "budget_musd": 4.5, "revenue_musd": 255.4, "rating": 7.7, "votes": 560000},
        {"title": "La La Land", "genre": "Musical", "director": "Damien Chazelle", "release_year": 2016, "runtime_min": 128, "budget_musd": 30, "revenue_musd": 446.0, "rating": 8.0, "votes": 510000},
        {"title": "Interstellar", "genre": "Sci-Fi", "director": "Christopher Nolan", "release_year": 2014, "runtime_min": 169, "budget_musd": 165, "revenue_musd": 701.7, "rating": 8.7, "votes": 1900000},
        {"title": "Whiplash", "genre": "Drama", "director": "Damien Chazelle", "release_year": 2014, "runtime_min": 106, "budget_musd": 3.3, "revenue_musd": 49.0, "rating": 8.5, "votes": 850000},
        {"title": "Mad Max: Fury Road", "genre": "Action", "director": "George Miller", "release_year": 2015, "runtime_min": 120, "budget_musd": 150, "revenue_musd": 378.9, "rating": 8.1, "votes": 1100000},
        {"title": "Spirited Away", "genre": "Animation", "director": "Hayao Miyazaki", "release_year": 2001, "runtime_min": 125, "budget_musd": 19, "revenue_musd": 395.6, "rating": 8.6, "votes": 780000},
        {"title": "Coco", "genre": "Animation", "director": "Lee Unkrich", "release_year": 2017, "runtime_min": 105, "budget_musd": 175, "revenue_musd": 807.1, "rating": 8.4, "votes": 470000},
        {"title": "Joker", "genre": "Drama", "director": "Todd Phillips", "release_year": 2019, "runtime_min": 122, "budget_musd": 55, "revenue_musd": 1074.0, "rating": 8.4, "votes": 1500000},
        {"title": "Knives Out", "genre": "Mystery", "director": "Rian Johnson", "release_year": 2019, "runtime_min": 130, "budget_musd": 40, "revenue_musd": 311.4, "rating": 7.9, "votes": 600000},
        {"title": "Dune", "genre": "Sci-Fi", "director": "Denis Villeneuve", "release_year": 2021, "runtime_min": 155, "budget_musd": 165, "revenue_musd": 402.0, "rating": 8.0, "votes": 750000},
        {"title": "Everything Everywhere All at Once", "genre": "Sci-Fi", "director": None, "release_year": 2022, "runtime_min": 140, "budget_musd": 25, "revenue_musd": 141.3, "rating": 7.9, "votes": 420000},
        {"title": "The Grand Budapest Hotel", "genre": "Comedy", "director": "Wes Anderson", "release_year": 2014, "runtime_min": 99, "budget_musd": 25, "revenue_musd": 174.8, "rating": 8.1, "votes": 730000},
        {"title": "Moonlight", "genre": "Drama", "director": "Barry Jenkins", "release_year": 2016, "runtime_min": 111, "budget_musd": 1.5, "revenue_musd": 65.3, "rating": 7.4, "votes": 240000},
        {"title": "Soul", "genre": "Animation", "director": "Pete Docter", "release_year": 2020, "runtime_min": 100, "budget_musd": 150, "revenue_musd": None, "rating": 8.0, "votes": 280000},
        {"title": "Arrival", "genre": "Sci-Fi", "director": "Denis Villeneuve", "release_year": 2016, "runtime_min": 116, "budget_musd": 47, "revenue_musd": 203.4, "rating": 7.9, "votes": 760000},
        {"title": "Her", "genre": "Drama", "director": "Spike Jonze", "release_year": 2013, "runtime_min": 126, "budget_musd": 23, "revenue_musd": 48.3, "rating": 8.0, "votes": 470000},
        {"title": "Birdman", "genre": "Comedy", "director": "Alejandro G. Iñárritu", "release_year": 2014, "runtime_min": 119, "budget_musd": 18, "revenue_musd": 103.2, "rating": 7.7, "votes": 470000},
        # Intentional duplicate row for the "remove duplicates" demo
        {"title": "Inception", "genre": "Sci-Fi", "director": "Christopher Nolan", "release_year": 2010, "runtime_min": 148, "budget_musd": 160, "revenue_musd": 836.8, "rating": 8.8, "votes": 2400000},
    ]
    return pd.DataFrame(data)


# ── File I/O helpers ─────────────────────────────────────────
def load_file(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    if name.endswith(".json"):
        return pd.read_json(uploaded_file)
    raise ValueError("Unsupported file type. Please upload a .csv, .xlsx, or .json file.")


def to_csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8")


def to_excel_bytes(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="data")
    return buf.getvalue()


def to_json_bytes(df):
    return df.to_json(orient="records", indent=2).encode("utf-8")


def numeric_cols(df):
    return df.select_dtypes(include=np.number).columns.tolist()


def categorical_cols(df):
    return df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()


def datetime_cols(df):
    return df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns.tolist()


def load_into_session(new_df, file_id, file_name):
    st.session_state.file_id = file_id
    st.session_state.file_name = file_name
    st.session_state.original_df = new_df.copy()
    st.session_state.df = new_df.copy()
    st.session_state.filtered_df = None


# ── Sidebar: branding + theme toggle ────────────────────────
st.sidebar.markdown(f"## {APP_ICON} {APP_NAME}")
st.session_state.dark_mode = st.sidebar.toggle("🌙 Dark mode", value=st.session_state.dark_mode)

st.sidebar.divider()
st.sidebar.title("📁 Upload Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload a CSV, Excel, or JSON file", type=["csv", "xlsx", "xls", "json"]
)
st.sidebar.caption(f"Max file size: {MAX_FILE_SIZE_MB} MB")

if uploaded_file is not None:
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        st.sidebar.error(
            f"That file's {size_mb:.1f} MB — a bit over my {MAX_FILE_SIZE_MB} MB limit. "
            "Try a smaller one?"
        )
    else:
        file_id = f"{uploaded_file.name}-{uploaded_file.size}"
        if st.session_state.get("file_id") != file_id:
            try:
                new_df = load_file(uploaded_file)
            except Exception as e:
                st.sidebar.error(f"Couldn't read this file: {e}")
                st.stop()
            load_into_session(new_df, file_id, uploaded_file.name)

st.sidebar.divider()
with st.sidebar.expander("🎬 Try the example dataset"):
    st.caption("A small movies dataset with a few missing values and one duplicate thrown in, so you've got something to clean.")
    if st.button("Load example movie data", key="sidebar_sample"):
        load_into_session(build_sample_movies_df(), "example-movies", "example_movies.csv (built-in)")
        st.rerun()

st.sidebar.divider()
with st.sidebar.expander("ℹ️ About"):
    st.markdown(
        """
**Built by Eyobed Mamo**

<!-- TODO(Eyobed): replace this line with your own "why I built this" note —
it'll show up right here in the app. -->
*Write a line or two here about why you made this.*

[GitHub](https://github.com/Eyobed-Mamo)
        """
    )

# ── Empty state ──────────────────────────────────────────────
if "df" not in st.session_state:
    st.title(f"{APP_ICON} {APP_NAME}")
    st.markdown(
        "Drop a CSV, Excel, or JSON file in the sidebar and I'll help you clean it up, "
        "dig through it, and get it ready for whatever's next."
    )

    if st.button("🎬 Try with example movie data", type="primary"):
        load_into_session(build_sample_movies_df(), "example-movies", "example_movies.csv (built-in)")
        st.rerun()

    st.markdown(
        f"""
Once your data's loaded, here's what you can do with it:

- 🔍 Spot missing values and decide how to handle them
- 🗑️ Find and clear out duplicate rows
- 🔀 Fix data types that came in wrong (text that should be a number, etc.)
- 🎛️ Filter down to what you care about, then sort it
- 📊 Throw together charts to see what's going on
- 🔢 Pull quick summary stats without writing a line of code
- ⬇️ Export the cleaned version as CSV, Excel, or JSON when you're done

Handles files up to **{MAX_FILE_SIZE_MB} MB**. Everything happens in your browser session — nothing gets saved on a server anywhere.
        """
    )
    st.stop()

df = st.session_state.df

# ── Sidebar: dataset info / reset ───────────────────────────
st.sidebar.divider()
st.sidebar.caption(f"📄 **{st.session_state.file_name}**")
st.sidebar.caption(f"{df.shape[0]:,} rows × {df.shape[1]} columns")
if st.sidebar.button("↩️ Reset to original upload"):
    st.session_state.df = st.session_state.original_df.copy()
    st.session_state.filtered_df = None
    st.rerun()

# ── Header & top metrics ─────────────────────────────────────
st.title(f"{APP_ICON} {APP_NAME}")
st.caption("Drop in a file, clean it up, poke around, and export when you're happy with it.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Rows", f"{df.shape[0]:,}")
m2.metric("Columns", df.shape[1])
m3.metric("Missing values", int(df.isna().sum().sum()))
m4.metric("Duplicate rows", int(df.duplicated().sum()))

st.divider()

tab_table, tab_clean, tab_filter, tab_viz, tab_stats, tab_export = st.tabs(
    ["📋 Table", "🧹 Clean", "🎛️ Filter & Sort", "📊 Visualize", "🔢 Statistics", "⬇️ Export"]
)

# ── Tab: Table ───────────────────────────────────────────────
with tab_table:
    st.subheader("Data Preview")
    show_cols = st.multiselect(
        "Columns to display", df.columns.tolist(), default=df.columns.tolist()
    )
    n_rows = st.slider("Rows to show", 5, min(1000, max(5, len(df))), min(50, len(df)) or 5)
    st.dataframe(df[show_cols].head(n_rows) if show_cols else df.head(n_rows), use_container_width=True)
    st.caption(f"Showing {min(n_rows, len(df))} of {len(df):,} rows.")

# ── Tab: Clean ───────────────────────────────────────────────
with tab_clean:
    st.subheader("Missing Values")
    missing = df.isna().sum()
    missing = missing[missing > 0]
    if missing.empty:
        st.success("No missing values found. 🎉")
    else:
        miss_table = pd.DataFrame(
            {
                "Column": missing.index,
                "Missing Count": missing.values,
                "% Missing": (missing.values / len(df) * 100).round(1),
                "Dtype": [str(df[c].dtype) for c in missing.index],
            }
        )
        st.dataframe(miss_table, use_container_width=True, hide_index=True)

        st.markdown("##### Fix missing values in a column")
        col_to_fix = st.selectbox("Column", missing.index.tolist(), key="fix_col")
        is_numeric = pd.api.types.is_numeric_dtype(df[col_to_fix])
        method_options = ["Drop rows with missing value"]
        if is_numeric:
            method_options += ["Fill with mean", "Fill with median"]
        method_options += ["Fill with most frequent value", "Fill with custom value", "Forward fill", "Backward fill"]
        method = st.selectbox("Method", method_options, key="fix_method")
        custom_val = None
        if method == "Fill with custom value":
            custom_val = st.text_input("Custom value", key="fix_custom_val")

        if st.button("Apply fix", key="apply_fix"):
            new_df = df.copy()
            try:
                if method == "Drop rows with missing value":
                    new_df = new_df.dropna(subset=[col_to_fix])
                elif method == "Fill with mean":
                    new_df[col_to_fix] = new_df[col_to_fix].fillna(new_df[col_to_fix].mean())
                elif method == "Fill with median":
                    new_df[col_to_fix] = new_df[col_to_fix].fillna(new_df[col_to_fix].median())
                elif method == "Fill with most frequent value":
                    mode = new_df[col_to_fix].mode(dropna=True)
                    if len(mode):
                        new_df[col_to_fix] = new_df[col_to_fix].fillna(mode.iloc[0])
                elif method == "Fill with custom value":
                    new_df[col_to_fix] = new_df[col_to_fix].fillna(custom_val)
                elif method == "Forward fill":
                    new_df[col_to_fix] = new_df[col_to_fix].ffill()
                elif method == "Backward fill":
                    new_df[col_to_fix] = new_df[col_to_fix].bfill()
                new_df = new_df.reset_index(drop=True)
                st.session_state.df = new_df
                st.success(f"Applied: {method} → '{col_to_fix}'")
                st.rerun()
            except Exception as e:
                st.error(f"Couldn't apply that fix: {e}")

    st.divider()
    st.subheader("Duplicate Rows")
    dup_count = int(df.duplicated().sum())
    st.write(f"Found **{dup_count}** duplicate row(s).")
    dup_subset = st.multiselect(
        "Check duplicates based on specific columns (leave empty to check full rows)",
        df.columns.tolist(),
        key="dup_subset",
    )
    keep_option = st.radio("Keep which copy?", ["first", "last"], horizontal=True, key="dup_keep")
    if st.button("🗑️ Remove duplicate rows", disabled=dup_count == 0 and not dup_subset):
        subset = dup_subset if dup_subset else None
        new_df = df.drop_duplicates(subset=subset, keep=keep_option).reset_index(drop=True)
        removed = len(df) - len(new_df)
        st.session_state.df = new_df
        st.success(f"Removed {removed} duplicate row(s).")
        st.rerun()

    st.divider()
    st.subheader("Convert Data Types")
    c1, c2 = st.columns(2)
    with c1:
        col_to_convert = st.selectbox("Column", df.columns.tolist(), key="conv_col")
        st.caption(f"Current dtype: `{df[col_to_convert].dtype}`")
    with c2:
        target_type = st.selectbox(
            "Convert to",
            ["String / Text", "Integer", "Float", "Datetime", "Category", "Boolean"],
            key="conv_target",
        )
    if st.button("🔀 Convert", key="apply_convert"):
        new_df = df.copy()
        try:
            if target_type == "String / Text":
                new_df[col_to_convert] = new_df[col_to_convert].astype(str)
            elif target_type == "Integer":
                new_df[col_to_convert] = pd.to_numeric(new_df[col_to_convert], errors="coerce")
                if new_df[col_to_convert].isna().any():
                    st.warning("Some values couldn't be converted and were set to missing.")
                new_df[col_to_convert] = new_df[col_to_convert].astype("Int64")
            elif target_type == "Float":
                new_df[col_to_convert] = pd.to_numeric(new_df[col_to_convert], errors="coerce")
            elif target_type == "Datetime":
                new_df[col_to_convert] = pd.to_datetime(new_df[col_to_convert], errors="coerce")
            elif target_type == "Category":
                new_df[col_to_convert] = new_df[col_to_convert].astype("category")
            elif target_type == "Boolean":
                new_df[col_to_convert] = (
                    new_df[col_to_convert]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .map({"true": True, "1": True, "yes": True, "false": False, "0": False, "no": False})
                )
            st.session_state.df = new_df
            st.success(f"Converted '{col_to_convert}' to {target_type}.")
            st.rerun()
        except Exception as e:
            st.error(f"Conversion failed: {e}")

# ── Tab: Filter & Sort ───────────────────────────────────────
with tab_filter:
    st.subheader("Filter Rows")
    filter_cols = st.multiselect("Filter by column(s)", df.columns.tolist(), key="filter_cols")

    working = df.copy()
    with st.form("filter_form"):
        for col in filter_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                lo, hi = float(df[col].min()), float(df[col].max())
                if lo == hi:
                    st.caption(f"'{col}' has a single value ({lo}); no range to filter.")
                    continue
                sel = st.slider(f"{col} range", lo, hi, (lo, hi), key=f"f_{col}")
                working = working[(working[col] >= sel[0]) & (working[col] <= sel[1])]
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                min_d, max_d = df[col].min(), df[col].max()
                sel = st.date_input(f"{col} range", (min_d, max_d), key=f"f_{col}")
                if isinstance(sel, tuple) and len(sel) == 2:
                    working = working[(working[col] >= pd.Timestamp(sel[0])) & (working[col] <= pd.Timestamp(sel[1]))]
            else:
                uniques = df[col].dropna().unique().tolist()
                if len(uniques) <= MAX_UNIQUE_FOR_MULTISELECT:
                    sel = st.multiselect(f"{col} values", uniques, default=uniques, key=f"f_{col}")
                    working = working[working[col].isin(sel)]
                else:
                    sel = st.text_input(f"{col} contains", key=f"f_{col}")
                    if sel:
                        working = working[working[col].astype(str).str.contains(sel, case=False, na=False)]
        apply_filter = st.form_submit_button("Apply filters")

    if apply_filter or filter_cols:
        st.session_state.filtered_df = working
        st.caption(f"Filtered: {len(working):,} of {len(df):,} rows match.")
    else:
        st.session_state.filtered_df = df

    st.divider()
    st.subheader("Sort")
    sort_cols = st.multiselect("Sort by column(s) (priority order)", df.columns.tolist(), key="sort_cols")
    sort_dir = st.radio("Direction", ["Ascending", "Descending"], horizontal=True, key="sort_dir")
    base = st.session_state.filtered_df if st.session_state.filtered_df is not None else df
    if sort_cols:
        base = base.sort_values(by=sort_cols, ascending=(sort_dir == "Ascending"))
        st.session_state.filtered_df = base

    st.markdown("##### Result")
    st.dataframe(base, use_container_width=True)
    st.caption(f"{len(base):,} rows in this view.")

    cc1, cc2 = st.columns(2)
    with cc1:
        if st.button("✅ Keep only this view as my working data"):
            st.session_state.df = base.reset_index(drop=True)
            st.session_state.filtered_df = None
            st.success("Working data updated.")
            st.rerun()
    with cc2:
        st.download_button(
            "⬇ Download this view as CSV",
            to_csv_bytes(base),
            file_name="filtered_data.csv",
            mime="text/csv",
        )

# ── Tab: Visualize ───────────────────────────────────────────
with tab_viz:
    st.subheader("Charts")
    num_cols = numeric_cols(df)
    cat_cols = categorical_cols(df)
    green_scale = ["#d9f7e3", ACCENT, ACCENT_DARK]

    chart_type = st.selectbox(
        "Chart type",
        ["Histogram", "Bar (category counts)", "Scatter", "Box", "Line", "Pie", "Correlation Heatmap"],
    )

    try:
        if chart_type == "Histogram":
            if not num_cols:
                st.info("No numeric columns available for a histogram.")
            else:
                x = st.selectbox("Column", num_cols, key="hist_x")
                color = st.selectbox("Color by (optional)", [None] + cat_cols, key="hist_color")
                fig = px.histogram(df, x=x, color=color, color_discrete_sequence=px.colors.sequential.Greens[2:])
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Bar (category counts)":
            if not cat_cols:
                st.info("No categorical columns available.")
            else:
                x = st.selectbox("Column", cat_cols, key="bar_x")
                counts = df[x].value_counts().reset_index()
                counts.columns = [x, "count"]
                fig = px.bar(counts, x=x, y="count", color_discrete_sequence=[ACCENT])
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Scatter":
            if len(num_cols) < 2:
                st.info("Need at least 2 numeric columns for a scatter plot.")
            else:
                x = st.selectbox("X axis", num_cols, key="sc_x")
                y = st.selectbox("Y axis", [c for c in num_cols if c != x] or num_cols, key="sc_y")
                color = st.selectbox("Color by (optional)", [None] + cat_cols, key="sc_color")
                fig = px.scatter(df, x=x, y=y, color=color, color_discrete_sequence=px.colors.sequential.Greens[2:])
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Box":
            if not num_cols:
                st.info("No numeric columns available.")
            else:
                y = st.selectbox("Numeric column", num_cols, key="box_y")
                x = st.selectbox("Group by (optional)", [None] + cat_cols, key="box_x")
                fig = px.box(df, x=x, y=y, color_discrete_sequence=[ACCENT])
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Line":
            if not num_cols:
                st.info("No numeric columns available.")
            else:
                y = st.selectbox("Y axis", num_cols, key="line_y")
                x_options = datetime_cols(df) + num_cols
                x = st.selectbox("X axis", x_options, key="line_x")
                fig = px.line(df.sort_values(by=x), x=x, y=y, color_discrete_sequence=[ACCENT_DARK])
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Pie":
            if not cat_cols:
                st.info("No categorical columns available.")
            else:
                x = st.selectbox("Column", cat_cols, key="pie_x")
                counts = df[x].value_counts().reset_index()
                counts.columns = [x, "count"]
                fig = px.pie(counts, names=x, values="count", color_discrete_sequence=px.colors.sequential.Greens[::-1])
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Correlation Heatmap":
            if len(num_cols) < 2:
                st.info("Need at least 2 numeric columns for a correlation heatmap.")
            else:
                corr = df[num_cols].corr()
                fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="Greens", zmin=-1, zmax=1)
                st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Couldn't render that chart: {e}")

# ── Tab: Statistics ──────────────────────────────────────────
with tab_stats:
    st.subheader("Summary Statistics")
    num_cols = numeric_cols(df)
    if num_cols:
        st.markdown("##### Numeric columns")
        st.dataframe(df[num_cols].describe().T, use_container_width=True)
    else:
        st.info("No numeric columns to summarize.")

    cat_cols = categorical_cols(df)
    if cat_cols:
        st.markdown("##### Categorical columns")
        col = st.selectbox("Column", cat_cols, key="stats_cat_col")
        vc = df[col].value_counts(dropna=False).reset_index()
        vc.columns = [col, "count"]
        vc["%"] = (vc["count"] / len(df) * 100).round(1)
        st.dataframe(vc, use_container_width=True, hide_index=True)

# ── Tab: Export ──────────────────────────────────────────────
with tab_export:
    st.subheader("Export Your Cleaned Data")
    st.write(f"Current working dataset: **{df.shape[0]:,} rows × {df.shape[1]} columns**")
    e1, e2, e3 = st.columns(3)
    with e1:
        st.download_button("⬇ Download CSV", to_csv_bytes(df), file_name="cleaned_data.csv", mime="text/csv")
    with e2:
        st.download_button(
            "⬇ Download Excel",
            to_excel_bytes(df),
            file_name="cleaned_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with e3:
        st.download_button(
            "⬇ Download JSON", to_json_bytes(df), file_name="cleaned_data.json", mime="application/json"
        )

st.divider()
st.caption("Made by Eyobed Mamo · [GitHub](https://github.com/Eyobed-Mamo)")
