import streamlit as st
import base64
import hashlib
import pandas as pd
import os

def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# Set the page to full-screen mode
st.set_page_config(page_icon="logo.png", layout="wide")

# Load the image and convert to base64
image_path = "logo.png"
image_base64 = get_image_base64(image_path)

# Display the logo and title
st.markdown(
    f"""
        <style>
        .header {{
            display: flex;
            align-items: center;
        }}
        .header img {{
            width: 50px;
        }}
        .header h1 {{
            margin-left: 10px;
            font-size: 2rem;
        }}
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

#st.logo(image_path, size="large")

# Add copyright footer


# ------------------ Config ------------------
USER_DB_FILE = "users.csv"
QR_CODE_IMAGE = "static/upi_qr.png"  # Replace with your actual QR code image
ADMIN_EMAIL = "sachinvspatil@gmail.com"  # Replace with your support email

# ------------------ Auth Utils ------------------
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

def logout_user(username):
    set_user_active(username, False)

# ------------------ Login & Registration UI ------------------
def login_register_ui():
    st.title("🔐 User Access Portal")
    tab_login, tab_register = st.tabs(["🔑 Login", "🆕 Register"])

    # ---- Login Tab ----
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

    # ---- Register Tab ----
    with tab_register:
        st.subheader("Register")
        reg_user = st.text_input("Choose Username", key="reg_user")
        reg_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        if st.button("Register"):
            success, msg = register_user(reg_user, reg_pass)
            if success:
                st.success(msg)
                st.info("🎉 You are registered but not yet activated.")
                st.info("📲 Please complete your payment to activate your account.")
                st.image(QR_CODE_IMAGE, width=250)
                st.write(f"📧 After payment, email your username and transaction ID to **{ADMIN_EMAIL}**.")
            else:
                st.error(msg)
# ------------------ Auth Wrapper ------------------
# ------------------ MAIN ------------------
if "user" not in st.session_state:
    login_register_ui()
else:
    st.sidebar.success(f"✅ Logged in as: {st.session_state.user}")
    if st.sidebar.button("Logout"):
        logout_user(st.session_state.user)
        del st.session_state.user
        st.rerun()

    # Protected app content starts here
    st.title("🎓 Welcome to KCET College Predictor")
    st.write("✅ This is the secure area of your app, visible only to activated users.")

    st.markdown('<div class="copyright">© 2025 OptionGuru. All rights reserved.</div>', unsafe_allow_html=True)


    # ✅ Prepare pages dynamically
    pages = {
        "Dashboards": [
            st.Page("pages/kcet_predictor.py", title="kcet_predictor"),
        ]
    }


    # ✅ Render pages
    pg = st.navigation(pages)
    pg.run()
