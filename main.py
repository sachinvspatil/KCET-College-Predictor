import streamlit as st
import base64
import hashlib
import pandas as pd
import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://draktjzrxhplnrriumkq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRyYWt0anpyeGhwbG5ycml1bWtxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0NzkzMjAsImV4cCI6MjA2NzA1NTMyMH0.tNR5qQZlvGSjlCS9c6nJGwUwmr4gVuysZd15Sn6DjDw"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------ Simple User Store ------------------
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def save_user(email, password_hash, active=False):
    # Store email in lowercase for case-insensitive matching
    email = email.lower()
    supabase.table("users").insert({
        "email": email,
        "password_hash": password_hash,
        "active": active
    }).execute()

def user_exists(email):
    # Case-insensitive check for email
    email = email.lower()
    res = supabase.table("users").select("id").eq("email", email).execute()
    return len(res.data) > 0

def validate_login(email, password):
    import hashlib
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    email = email.lower()
    res = supabase.table("users").select("password_hash,active").eq("email", email).execute()
    if not res.data:
        return False, "User not found. Please register."
    user = res.data[0]
    if user["password_hash"] != pw_hash:
        return False, "Incorrect password."
    if not user["active"]:
        return False, "Account not activated. Please contact admin."
    return True, "Login successful."

def activate_user(email, active=True):
    email = email.lower()
    supabase.table("users").update({"active": active}).eq("email", email).execute()

def load_users():
    res = supabase.table("users").select("email,active").execute()
    import pandas as pd
    return pd.DataFrame(res.data)

# ------------------ Utility ------------------
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ------------------ UI Config ------------------
st.set_page_config(page_icon="logo.png", layout="wide")

image_path = "logo.png"
image_base64 = get_image_base64(image_path)

st.markdown(
    f"""
    <style>
    .header {{ display: flex; align-items: center; }}
    .header img {{ width: 50px; }}
    .header h1 {{ margin-left: 10px; font-size: 2rem; }}
    .copyright {{
        position: fixed;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 14px;
        color: gray;
        text-align: center;
    }}
    </style>
    <div class="header">
        <img src="data:image/png;base64,{image_base64}" alt="Logo">
        <h1>CET SELECT</h1>
    </div>
    <div class="copyright">© 2025 OptionGuru. All rights reserved.</div>
    """,
    unsafe_allow_html=True,
)

# ------------------ Login/Register UI ------------------
def is_valid_email(email):
    import re
    # Simple regex for email validation
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

def login_register_ui():
    st.title("🔐 User Login / Register")
    tab1, tab2, tab3 = st.tabs(["🔑 Login", "🆕 Register", "🛡️ Admin Login"])
    with tab1:
        username = st.text_input("Email", key="login_user")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            ok, msg = validate_login(username, password)
            if ok:
                st.session_state.user = username
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    with tab2:
        new_email = st.text_input("Email", key="reg_user")
        new_password = st.text_input("Choose Password", type="password", key="reg_pw")
        if st.button("Register"):
            if not is_valid_email(new_email):
                st.error("Please enter a valid email address.")
            elif user_exists(new_email):
                st.error("Email already registered.")
            elif not new_email or not new_password:
                st.error("Email and password required.")
            else:
                save_user(new_email, hash_password(new_password), active=False)
                st.success("Registration successful! Please contact admin sachinvspatil@gmail.com throgh your registerd email id for activation.")
    with tab3:
        if st.session_state.get("admin"):
            admin_panel()
        else:
            admin_login_ui()

# ------------------ Admin Panel ------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "supersecret"

def admin_login_ui():
    st.title("🛡️ Admin Access")
    u = st.text_input("Admin Username")
    pw = st.text_input("Admin Password", type="password")
    if st.button("Login as Admin"):
        if u == ADMIN_USERNAME and pw == ADMIN_PASSWORD:
            st.session_state.admin = True
            st.session_state.show_admin_login = False
            st.rerun()
        else:
            st.error("Invalid admin credentials")

def admin_panel():
    st.title("👥 Admin Dashboard")
    df = load_users()
    st.markdown(f"**Total Registered Users:** {len(df)}")
    act = df[df.active.astype(str).str.lower()=="true"]
    inact = df[df.active.astype(str).str.lower()!="true"]
    st.markdown(f"**• Active:** {len(act)} • **Inactive:** {len(inact)}")
    st.markdown("---")
    st.subheader("Manage Account Status")
    for i, r in df.iterrows():
        cols = st.columns([3,1,1])
        cols[0].write(r["email"])
        cols[1].write("🟢" if str(r["active"]).lower()=="true" else "🔴")
        if str(r["active"]).lower()!="true":
            if cols[2].button("Activate", key=f"act_{r['email']}"):
                activate_user(r["email"], True)
                st.rerun()
        else:
            if cols[2].button("Deactivate", key=f"deact_{r['email']}"):
                activate_user(r["email"], False)
                st.rerun()
    if st.button("Logout Admin"):
        del st.session_state.admin
        st.rerun()

# ------------------ Main App Routing ------------------
if st.session_state.get("show_admin_login"):
    admin_login_ui()
    st.stop()

if st.session_state.get("admin"):
    admin_panel()
    st.stop()

if "user" not in st.session_state:
    login_register_ui()
    st.stop()

st.sidebar.success(f"Logged in: {st.session_state.user}")
if st.sidebar.button("Logout"):
    del st.session_state.user
    st.rerun()

# Add Admin Login button to sidebar
if st.sidebar.button("Admin Login"):
    st.session_state.show_admin_login = True

st.title("🎓 Welcome to KCET College Predictor")

@st.cache_data
def load_cutoff_data():
    df = pd.read_csv("cleaned_cutoff_data_latest_cs.csv")
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
tab1, tab2 = st.tabs(["🏫 College & Branch Explorer", "🎯 Rank-Based Prediction"])

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
            selected_category_display = st.selectbox("🎯 Select your Category", ["-- Any --"] + sorted(category_display))
            selected_branch = st.selectbox("💡 Optional: Filter by Branch", ["-- Any --"] + branch_options)

        submit = st.form_submit_button("🔍 Find Colleges")

    if submit:
        filtered_df = df.copy()
        if selected_category_display != "-- Any --":
            category = selected_category_display.split(" – ")[0]
            filtered_df = filtered_df[filtered_df["Category"] == category]

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
            filtered_df["Cutoff Rank"].between(min_rank, max_rank)
        ]

        st.subheader("🎓 Eligible Colleges and Branches")
        if not filtered_df.empty:
            st.success(f"Found {len(filtered_df)} option(s) within ±{tolerance} ranks.")
            st.dataframe(filtered_df.sort_values(by="Cutoff Rank").reset_index(drop=True))
        else:
            st.warning("❌ No eligible colleges found. Try adjusting your filters.")
