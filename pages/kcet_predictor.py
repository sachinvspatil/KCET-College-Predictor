import streamlit as st
import pandas as pd

# ------------------ Config ------------------
#st.set_page_config(page_title="KCET College Predictor 2025", page_icon="🎓", layout="centered")
#st.title("🎓 KCET 2024 College Predictor")

@st.cache_data
def load_cutoff_data():
    df = pd.read_csv("cutoff_data.csv")
    df.columns = df.columns.str.strip()  # Strip whitespace from column names
    df["Cutoff Rank"] = pd.to_numeric(df["Cutoff Rank"], errors="coerce")
    return df

df = load_cutoff_data()

# ------------------ Category Map ------------------
category_map = {
    "GM": "General Merit (Unreserved)", "GMK": "General Merit - Kannada Medium", "GMR": "General Merit - Rural",
    "1G": "Category 1 - General", "1K": "Category 1 - Kannada Medium", "1R": "Category 1 - Rural",
    "2AG": "Category 2A - General", "2AK": "Category 2A - Kannada Medium", "2AR": "Category 2A - Rural",
    "2BG": "Category 2B - General", "2BK": "Category 2B - Kannada Medium", "2BR": "Category 2B - Rural",
    "3AG": "Category 3A - General", "3AK": "Category 3A - Kannada Medium", "3AR": "Category 3A - Rural",
    "3BG": "Category 3B - General", "3BK": "Category 3B - Kannada Medium", "3BR": "Category 3B - Rural",
    "SCG": "SC - General", "SCK": "SC - Kannada Medium", "SCR": "SC - Rural",
    "STG": "ST - General", "STK": "ST - Kannada Medium", "STR": "ST - Rural",
}
category_display = [f"{k} – {v}" for k, v in category_map.items()]

# ------------------ Dropdown Options ------------------
college_options = sorted(
    df[['College Code', 'College Name']].drop_duplicates().apply(
        lambda row: f"{row['College Code']} – {row['College Name']}", axis=1
    ).tolist()
)

branch_options = sorted(
    df[['Branch Code', 'Branch Name']].drop_duplicates().apply(
        lambda row: f"{row['Branch Code']} – {row['Branch Name']}", axis=1
    ).tolist()
)

location_options = sorted(df['Location'].dropna().unique().tolist())

# ------------------ Tabs ------------------
tab1, tab2 = st.tabs(["🎯 Rank-Based Prediction", "🏫 College & Branch Explorer"])

# ------------------ TAB 1: Rank-Based ------------------
with tab1:
    with st.form("branch_form"):
        st.markdown("### 🏫 Explore Colleges, Branches, Locations, Categories")

        selected_branch = st.selectbox("💡 Optional: Filter by Branch", ["-- Any --"] + branch_options)
        selected_college = st.selectbox("🏛️ Optional: Filter by College", ["-- Any --"] + college_options)
        selected_category_display = st.selectbox("🎯 Optional: Filter by Category", ["-- Any --"] + sorted(category_display))
        selected_location = st.selectbox("📍 Optional: Filter by Location", ["-- Any --"] + location_options)

        branch_submit = st.form_submit_button("🔍 Show Results")

    if branch_submit:
        filtered_df = df.copy()

        if selected_branch != "-- Any --":
            branch_code = selected_branch.split(" – ")[0]
            filtered_df = filtered_df[filtered_df["Branch Code"] == branch_code]

        if selected_college != "-- Any --":
            college_code = selected_college.split(" – ")[0]
            filtered_df = filtered_df[filtered_df["College Code"] == college_code]

        if selected_category_display != "-- Any --":
            category_code = selected_category_display.split(" – ")[0]
            filtered_df = filtered_df[filtered_df["Category"] == category_code]

        if selected_location != "-- Any --":
            filtered_df = filtered_df[filtered_df["Location"] == selected_location]

        result_df = filtered_df[[
            'College Code', 'College Name', 'Location',
            'Branch Code', 'Branch Name',
            'Category', 'Cutoff Rank'
        ]].dropna().sort_values(by=["College Code", "Branch Code", "Cutoff Rank"])

        st.subheader("📋 Available Branches and Cutoffs")
        if not result_df.empty:
            st.success(f"Found {len(result_df)} matching record(s).")
            st.dataframe(result_df.reset_index(drop=True))
        else:
            st.warning("❌ No matching records found.")

# ------------------ TAB 2: College & Branch Explorer ------------------
with tab2:
    with st.form("rank_form"):
        st.markdown("### 🔍 Search by Rank + Category")

        col1, col2 = st.columns(2)
        with col1:
            rank = st.number_input("📈 Enter your KCET Rank", min_value=1, step=1)
            selected_college = st.selectbox("🏛️ Optional: Filter by College", ["-- Any --"] + college_options)
            selected_location = st.selectbox("📍 Optional: Filter by Location", ["-- Any --"] + location_options)
        with col2:
            selected_category_display = st.selectbox("🎯 Select your Category", sorted(category_display))
            selected_branch = st.selectbox("💡 Optional: Filter by Branch", ["-- Any --"] + branch_options)

        submit = st.form_submit_button("🔍 Find Colleges")

    if submit:
        filtered_df = df.copy()
        category = selected_category_display.split(" – ")[0]

        if selected_college != "-- Any --":
            college_code = selected_college.split(" – ")[0]
            filtered_df = filtered_df[filtered_df["College Code"] == college_code]

        if selected_branch != "-- Any --":
            branch_code = selected_branch.split(" – ")[0]
            filtered_df = filtered_df[filtered_df["Branch Code"] == branch_code]

        if selected_location != "-- Any --":
            filtered_df = filtered_df[filtered_df["Location"] == selected_location]

        tolerance = max(int(rank * 0.15), 500)
        min_rank = max(rank - tolerance, 1)
        max_rank = rank + tolerance

        filtered_df = filtered_df[
            (filtered_df["Category"] == category) &
            (filtered_df["Cutoff Rank"].between(min_rank, max_rank))
        ]

        st.subheader("🎓 Eligible Colleges and Branches")
        if not filtered_df.empty:
            st.success(f"Found {len(filtered_df)} option(s) within ±{tolerance} ranks.")
            st.dataframe(filtered_df.sort_values(by="Cutoff Rank").reset_index(drop=True))
        else:
            st.warning("❌ No eligible colleges found. Try adjusting your filters.")
