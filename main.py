import streamlit as st
import base64
import hashlib
import pandas as pd
import os
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials



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



# # 🌐 ========== Google Sheets Setup ==========
# GSHEET_NAME = "kcet_users"
# GSCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# # # Load credentials from Streamlit secrets or JSON
# # if "gcp_service_account" in st.secrets:
# #     creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], GSCOPE)
# # else:
# #     creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", GSCOPE)

# # Local use only: Load from creds.json
# creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", GSCOPE)


# gc = gspread.authorize(creds)
# sheet = gc.open(GSHEET_NAME).sheet1

# # ──========= Helper Functions =========─
# def hash_password(pw):
#     return hashlib.sha256(pw.encode()).hexdigest()

# def load_users():
#     return pd.DataFrame(sheet.get_all_records())

# def add_user(username, password_hash):
#     sheet.append_row([username, password_hash, False])

# def activate_user(username, active=True):
#     users = load_users().to_dict("records")
#     for i, u in enumerate(users, start=2):
#         if u["username"] == username:
#             sheet.update_cell(i, 3, str(active))
#             break

# def validate_login(u, pw):
#     df = load_users()
#     row = df[df.username == u]
#     if row.empty: return False, "User not found."
#     if row.iloc[0]["password_hash"] != hash_password(pw): return False, "Incorrect password."
#     if not str(row.iloc[0]["active"]).lower() in ["true","1"]: return False, "Account not activated."
#     return True, "Login successful."

# def register_user(u, pw):
#     df = load_users()
#     if u in df.username.values: return False, "Username exists."
#     add_user(u, hash_password(pw))
#     return True, "Registered! Complete payment via QR."

# # ──========= UI Helpers =========─
# def get_base64(path):
#     return base64.b64encode(open(path,"rb").read()).decode()

# logo_base64 = get_base64("logo.png")
# qr_base64 = get_base64("upi_qr.png")

# st.set_page_config(page_icon="logo.png", layout="wide")
# st.markdown(f"""
# <style>
# .header {{ display:flex; align-items:center; }}
# .header img {{ width:50px; }}
# .header h1 {{ margin-left:10px; font-size:2rem; }}
# .footer{{position:fixed;bottom:10px;left:50%;transform:translateX(-50%);font-size:14px;color:gray;}}
# </style>
# <div class="header"><img src="data:image/png;base64,{logo_base64}" alt=""><h1>CET SELECT</h1></div>
# <div class="footer">© 2025 OptionGuru. All rights reserved.</div>
# """, unsafe_allow_html=True)

# # ──========= Authentication Flow =========─
# def login_register_ui():
#     st.title("🔐 User Portal")
#     tab1, tab2 = st.tabs(["🔑 Login","🆕 Register"])
#     with tab1:
#         u = st.text_input("Username", key="l_u")
#         pw = st.text_input("Password", type="password", key="l_pw")
#         if st.button("Login"):
#             ok, msg = validate_login(u, pw)
#             st.success(msg) if ok else st.error(msg)
#             if ok:
#                 st.session_state.user = u
#                 st.rerun()
#     with tab2:
#         u2 = st.text_input("Pick Username", key="r_u")
#         pw2 = st.text_input("Pick Password", type="password", key="r_pw")
#         if st.button("Register"):
#             ok, msg = register_user(u2, pw2)
#             st.success(msg) if ok else st.error(msg)
#             if ok:
#                 st.image(qr_base64, width=200, caption="Scan to pay")
#                 st.info("Email admin after payment for activation")

# # ──========= Admin Panel =========─
# ADMIN_USERNAME = "admin"
# ADMIN_PASSWORD = "supersecret"

# def admin_login_ui():
#     st.title("🛡️ Admin Access")
#     u = st.text_input("Admin Username")
#     pw = st.text_input("Admin Password", type="password")
#     if st.button("Login as Admin"):
#         if u == ADMIN_USERNAME and pw == ADMIN_PASSWORD:
#             st.session_state.admin = True
#             st.rerun()
#         else:
#             st.error("Invalid admin credentials")

# def admin_panel():
#     st.title("👥 Admin Dashboard")
#     df = load_users()
#     st.markdown(f"**Total Registered Users:** {len(df)}")
#     act = df[df.active.astype(str).str.lower()=="true"]
#     inact = df[df.active.astype(str).str.lower()!="true"]
#     st.markdown(f"**• Active:** {len(act)} • **Inactive:** {len(inact)}")
#     c1, c2 = st.columns(2)
#     with c1:
#         if st.button("Download Active"):
#             st.download_button("CSV", act.to_csv(index=False), "active_users.csv", "text/csv")
#     with c2:
#         if st.button("Download Inactive"):
#             st.download_button("CSV", inact.to_csv(index=False), "inactive_users.csv", "text/csv")
#     st.markdown("---")
#     st.subheader("Manage Account Status")
#     for i,r in df.iterrows():
#         cols = st.columns([3,1,1])
#         cols[0].write(r["username"])
#         cols[1].write("🟢" if str(r["active"]).lower()=="true" else "🔴")
#         if str(r["active"]).lower()!="true":
#             if cols[2].button("Activate", key=f"act_{r['username']}"):
#                 activate_user(r["username"], True)
#                 st.rerun()
#         else:
#             if cols[2].button("Deactivate", key=f"deact_{r['username']}"):
#                 activate_user(r["username"], False)
#                 st.rerun()
#     if st.button("Logout Admin"):
#         del st.session_state.admin
#         st.rerun()

# # ──========= Routing =========─
# if st.sidebar.button("Admin Login"):
#     st.session_state.show_admin_login = True

# if st.session_state.get("show_admin_login"):
#     admin_login_ui()
# elif st.session_state.get("admin"):
#     admin_panel()
# elif "user" not in st.session_state:
#     login_register_ui()
# else:
#     st.sidebar.success(f"Logged in: {st.session_state.user}")
#     if st.sidebar.button("Logout"):
#         del st.session_state.user
#         st.rerun()
    # st.header("🎓 KCET College Predictor")
    # st.write("Your secure prediction space here.")


st.title("🎓 Welcome to KCET College Predictor")
#st.write("✅ This is the secure area of your app, visible only to activated users.")


    
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


    # # ✅ Prepare pages dynamically
    # pages = {
    #     "Dashboards": [
    #         st.Page("pages/kcet_predictor.py", title="kcet_predictor"),
    #     ]
    # }


    # # ✅ Render pages
    # pg = st.navigation(pages)
    # pg.run()
