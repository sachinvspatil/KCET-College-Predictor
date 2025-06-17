import streamlit as st
import base64
import hashlib
import pandas as pd
import os

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

# ------------------ Auth Config ------------------
USER_DB_FILE = "users.csv"
QR_CODE_IMAGE = "upi_qr.png"
ADMIN_EMAIL = "sachinvspatil@gmail.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "supersecret"  # Change this securely!

# ------------------ Auth Functions ------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_user_db():
    if os.path.exists(USER_DB_FILE):
        return pd.read_csv(USER_DB_FILE)
    return pd.DataFrame(columns=["username", "password_hash", "active"])

def save_user_db(df):
    df.to_csv(USER_DB_FILE, index=False)

def validate_login(username, password):
    df = load_user_db()
    user = df[df.username == username]
    if not user.empty:
        if user.iloc[0]["password_hash"] == hash_password(password):
            if not user.iloc[0]["active"]:
                return False, "⛔ Your account is not activated. Please complete payment and contact admin."
            return True, "Login successful."
        return False, "Incorrect password."
    return False, "User not found."

def register_user(username, password):
    df = load_user_db()
    if username in df.username.values:
        return False, "Username already exists."
    new_user = pd.DataFrame({
        "username": [username],
        "password_hash": [hash_password(password)],
        "active": [False]
    })
    df = pd.concat([df, new_user], ignore_index=True)
    save_user_db(df)
    return True, "Registration successful. Please complete the next step."

def set_user_active(username, active=True):
    df = load_user_db()
    df.loc[df.username == username, "active"] = active
    save_user_db(df)

def deactivate_user(username):
    set_user_active(username, False)

def logout_user(username):
    set_user_active(username, False)

# ------------------ Login/Register UI ------------------
def login_register_ui():
    st.title("🔐 User Access Portal")
    tab_login, tab_register = st.tabs(["🔑 Login", "🆕 Register"])

    with tab_login:
        st.subheader("Login")
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            success, msg = validate_login(login_user, login_pass)
            if success:
                st.session_state.user = login_user
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    with tab_register:
        st.subheader("Register")
        reg_user = st.text_input("Choose Username", key="reg_user")
        reg_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        if st.button("Register"):
            success, msg = register_user(reg_user, reg_pass)
            if success:
                st.success(msg)
                st.info("🎉 You are registered but not yet activated.")
                st.image(QR_CODE_IMAGE, width=250)
                st.write(f"📧 After payment, email your username and transaction ID to **{ADMIN_EMAIL}**.")
            else:
                st.error(msg)

# ------------------ Admin UI ------------------
def admin_panel():
    st.sidebar.success("🛡️ Logged in as Admin")
    st.title("🛡️ Admin User Management Panel")
    df = load_user_db()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Download Active Users"):
            active = df[df["active"] == True]
            st.download_button("Download Active", active.to_csv(index=False), "active_users.csv", "text/csv")
    with col2:
        if st.button("📥 Download Inactive Users"):
            inactive = df[df["active"] != True]
            st.download_button("Download Inactive", inactive.to_csv(index=False), "inactive_users.csv", "text/csv")

    st.markdown("---")
    st.subheader("👥 Manage Users")
    for i, row in df.iterrows():
        col1, col2, col3 = st.columns([4, 2, 2])
        with col1:
            st.markdown(f"**{row['username']}**")
        with col2:
            status = "🟢 Active" if row["active"] else "🔴 Inactive"
            st.markdown(status)
        with col3:
            if not row["active"]:
                if st.button(f"✅ Activate", key=f"act_{row['username']}"):
                    set_user_active(row["username"], True)
                    st.rerun()
            else:
                if st.button(f"⛔ Deactivate", key=f"deact_{row['username']}"):
                    deactivate_user(row["username"])
                    st.rerun()

    if st.sidebar.button("Logout Admin"):
        del st.session_state.admin
        st.rerun()

# ------------------ Routing Logic ------------------
if st.sidebar.button("Admin Login"):
    st.session_state.show_admin_login = True

if st.session_state.get("show_admin_login"):
    st.title("🛡️ Admin Login")
    admin_user = st.text_input("Admin Username")
    admin_pass = st.text_input("Admin Password", type="password")
    if st.button("Login as Admin"):
        if admin_user == ADMIN_USERNAME and admin_pass == ADMIN_PASSWORD:
            st.session_state.admin = True
            del st.session_state.show_admin_login
            st.rerun()
        else:
            st.error("Invalid admin credentials.")

elif "admin" in st.session_state:
    admin_panel()

elif "user" not in st.session_state:
    login_register_ui()

else:
    st.sidebar.success(f"✅ Logged in as: {st.session_state.user}")
    if st.sidebar.button("Logout"):
        logout_user(st.session_state.user)
        del st.session_state.user
        st.rerun()

    st.title("🎓 Welcome to KCET College Predictor")
    st.write("✅ This is the secure area of your app, visible only to activated users.")


        
    @st.cache_data
    def load_cutoff_data():
        df = pd.read_csv("cleaned_cutoff_data_latest.csv")
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


    # # ✅ Prepare pages dynamically
    # pages = {
    #     "Dashboards": [
    #         st.Page("pages/kcet_predictor.py", title="kcet_predictor"),
    #     ]
    # }


    # # ✅ Render pages
    # pg = st.navigation(pages)
    # pg.run()
