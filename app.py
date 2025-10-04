import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import os

# ============= DATABASE FUNCTIONS =============
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Create the base users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        method TEXT NOT NULL,
        user_id TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Add profile columns if they don't exist (for existing databases)
    try:
        c.execute('ALTER TABLE users ADD COLUMN name TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE users ADD COLUMN username TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE users ADD COLUMN pronouns TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE users ADD COLUMN bio TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE users ADD COLUMN links TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE users ADD COLUMN avatar TEXT')
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(method, user_id, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed = hash_password(password)
    try:
        c.execute("INSERT INTO users (method, user_id, password) VALUES (?, ?, ?)", (method, user_id.strip(), hashed))
        conn.commit()
        st.success("Registration successful! You can now sign in.")
    except sqlite3.IntegrityError:
        st.error("Account already exists. Please log in or use a different email/phone.")
    conn.close()
    clean_null_users()

def login_user(method, user_id, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed = hash_password(password)
    c.execute("SELECT * FROM users WHERE method=? AND user_id=? AND password=?", (method, user_id.strip(), hashed))
    result = c.fetchone()
    conn.close()
    return result

def user_exists(method, user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE method=? AND user_id=?", (method, user_id.strip()))
    result = c.fetchone()
    conn.close()
    return result is not None

def update_password(method, user_id, new_password):
    hashed = hash_password(new_password)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE method=? AND user_id=?", (hashed, method, user_id.strip()))
    conn.commit()
    conn.close()

def fetch_profile(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('SELECT name, username, pronouns, bio, links, avatar FROM users WHERE user_id=?', (user_id,))
        profile = c.fetchone()
        conn.close()
        return profile
    except sqlite3.OperationalError:
        conn.close()
        return ("", "", "", "", "", "")

def update_profile(user_id, name, username, pronouns, bio, links, avatar):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('''
            UPDATE users
            SET name=?, username=?, pronouns=?, bio=?, links=?, avatar=?
            WHERE user_id=?
        ''', (name, username, pronouns, bio, links, avatar, user_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.OperationalError as e:
        conn.close()
        st.error(f"Database error: {e}")
        return False

def clean_null_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE user_id='' OR password='' OR user_id IS NULL OR password IS NULL")
    conn.commit()
    conn.close()

def list_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, method, user_id FROM users")
    users = c.fetchall()
    conn.close()
    return users

def delete_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE user_id=?", (user_id.strip(),))
    conn.commit()
    conn.close()

# ============= SESSION INIT =============
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = ""
if 'user_method' not in st.session_state:
    st.session_state['user_method'] = None
if 'nav' not in st.session_state:
    st.session_state['nav'] = "Home"
if "reset_show" not in st.session_state:
    st.session_state["reset_show"] = False
if "edit_profile_mode" not in st.session_state:
    st.session_state["edit_profile_mode"] = False
if "show_signup" not in st.session_state:
    st.session_state["show_signup"] = False

def logout():
    st.session_state['logged_in'] = False
    st.session_state['user'] = ""
    st.session_state['user_method'] = None
    st.session_state['edit_profile_mode'] = False
    st.session_state['show_signup'] = False
    st.info("You've been logged out. Please sign in again.")

# ============= UI HELPERS =============
def pretty_card(title, body, icon=None):
    st.markdown(
        f"""
        <div style='border-radius:12px; background:#f8fafc; padding:1.5em 1em; margin-bottom:1em; box-shadow:0 6px 18px #0001;'>
        <h3 style='margin-bottom:0.5em;'>{icon if icon else ''} {title}</h3>
        <div style='font-size:1.10em;'>{body}</div>
        </div>
        """, unsafe_allow_html=True
    )

def password_reset_modal():
    pretty_card(
        "🔑 Reset Password",
        "Enter your registered E-mail or Phone and a new password below."
    )
    reset_method = st.selectbox("Reset by", ["E-mail", "Phone Number"], key="reset_method_modal")
    reset_id = st.text_input("E-mail" if reset_method=="E-mail" else "Phone Number", key="reset_id_modal")
    new_pass = st.text_input("New Password", type="password", key="reset_pass_modal")
    reset_btn = st.button("Reset Password", key="resetpw_btn_modal")
    if reset_btn:
        kind = "email" if reset_method == "E-mail" else "phone"
        if not reset_id.strip() or not new_pass:
            st.warning("Please enter both your registered email/phone and a new password.")
        elif not user_exists(kind, reset_id):
            st.error("No such account found.")
        else:
            update_password(kind, reset_id, new_pass)
            st.success("Password updated! You can now sign in with your new password.")

# ============= LOGIN PAGE =============
def login_page():
    st.markdown("""
    <style>
    .main-card {
        # max-width: 00px;
        # margin: 0 auto 1.5em auto; /* Removed top space! */
        # border-radius:0px;
        # border: 1.5px solid #E0E0E0;
        # background:#f8fafc;
        # box-shadow: none; /* Remove all shadow */
        # padding:2.5em 2em 2em 2em;
    }
    .field-label {
        font-weight:600;
        margin-bottom: 0.4em;
        letter-spacing: 0.01em;
        color: #46506a;
        font-size: 1.1em;
    }
    .login-title { 
        font-size:2.4em;
        font-weight:700;
        margin-bottom:0.4em;
        color: #425ad7;
        text-align:center;
    }
    .login-caption {
        font-size:1.15em;
        color:#596085;
        margin-bottom:2.5em;
        margin-top:-0.8em;
        font-weight: 400;
        letter-spacing: 0.03em;
        text-align:center;
    }
    .signin-subtitle {
        font-size:1.8em;
        color:#2c3e50;
        margin-bottom:1.2em;
        font-weight:600;
        text-align:center;
    }
    .signup-link {
        text-align:center;
        margin-top:1.5em;
        font-size:1.1em;
        color:#666;
    }
    .signup-link a {
        color:#425ad7;
        text-decoration:none;
        font-weight:600;
    }
    .signup-link a:hover {
        text-decoration:underline;
    }
    </style>
    """, unsafe_allow_html=True)

    # App Title and Caption
    st.markdown("""
    <div style='text-align:center;margin-bottom:1.5em;'>
        <div class='login-title'>Welcome to Career Navigator Pro</div>
        <div class='login-caption'><b>where ambition meets opportunity. </b></div>
    </div>
    """, unsafe_allow_html=True)

    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.get("show_signup", False):
            st.markdown("<div class='main-card'>", unsafe_allow_html=True)
            st.markdown("<div class='signin-subtitle'>Sign In</div>", unsafe_allow_html=True)
            
            login_method = st.selectbox("Sign in with", ("E-mail", "Phone Number"), key="login_method_main")
            st.markdown("<div class='field-label'>%s</div>" % ("E-mail" if login_method == "E-mail" else "Phone Number"), unsafe_allow_html=True)
            login_id = st.text_input("", placeholder="e.g. user@email.com" if login_method=="E-mail" else "9876543210", key="login_id_main", label_visibility="collapsed")
            st.markdown("<div class='field-label'>Password</div>", unsafe_allow_html=True)
            login_pass = st.text_input("", type="password", placeholder="Your password", key="login_pass_main", label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            sign_in = st.button("🔑 Sign In", key="signin_btn_main", use_container_width=True, type="primary")
            forgot_btn = st.button("Forgot Password?", key="forgot_btn_main", use_container_width=True)
            
            if sign_in:
                kind = "email" if login_method == "E-mail" else "phone"
                result = login_user(kind, login_id, login_pass)
                if result:
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = login_id
                    st.session_state['user_method'] = kind
                    st.success(f"Welcome, {login_id}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
            
            if forgot_btn:
                st.session_state["reset_show"] = True
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class='signup-link'>
                New to Career Navigator? <a href='#' onclick='return false;'>Create Account</a>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Create Account", key="show_signup_btn", use_container_width=True):
                st.session_state["show_signup"] = True
                st.rerun()
        
        else:
            st.markdown("<div class='main-card'>", unsafe_allow_html=True)
            st.markdown("<div class='signin-subtitle'>Create Account</div>", unsafe_allow_html=True)
            
            reg_method = st.selectbox("Sign up with", ["E-mail", "Phone Number"], key="reg_method_main")
            st.markdown("<div class='field-label'>%s</div>" % ("E-mail" if reg_method == "E-mail" else "Phone Number"), unsafe_allow_html=True)
            reg_id = st.text_input("", key="reg_id_main", placeholder="e.g. user@email.com" if reg_method=="E-mail" else "9876543210", label_visibility="collapsed")
            st.markdown("<div class='field-label'>Create Password</div>", unsafe_allow_html=True)
            reg_pass = st.text_input("", type="password", key="reg_pass_main", placeholder="Your password", label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            sign_up = st.button("✨ Create Account", key="signup_btn_main", use_container_width=True, type="primary")
            
            if sign_up:
                kind = "email" if reg_method == "E-mail" else "phone"
                if not reg_id.strip() or not reg_pass:
                    st.warning("Please enter all details.")
                elif user_exists(kind, reg_id):
                    st.error("Account already exists. Try logging in.")
                else:
                    register_user(kind, reg_id, reg_pass)
                    if not st.session_state.get('error_occurred', False):  # If registration was successful
                        st.session_state["show_signup"] = False
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class='signup-link'>
                Already have an account? <a href='#' onclick='return false;'>Sign In</a>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Back to Sign In", key="back_signin_btn", use_container_width=True):
                st.session_state["show_signup"] = False
                st.rerun()
    if st.session_state.get("reset_show", False):
        st.markdown("---")
        password_reset_modal()
        st.session_state["reset_show"] = False

# ============ PROFILE PAGE ============
def user_profile_page():
    st.subheader("My Profile")
    profile = fetch_profile(st.session_state['user'])
    if profile:
        name, username, pronouns, bio, links, avatar = profile
    else:
        name, username, pronouns, bio, links, avatar = ("", "", "", "", "", "")
    st.markdown("""
    <style>
    .profile-header {
        text-align:center; margin-bottom:1.2em;
    }
    .avatar-img {
        display: block; margin-left:auto; margin-right:auto;
        border-radius:50%; width:120px; height:120px; object-fit:cover;
        box-shadow: 0 2px 8px #0002;
    }
    .pf-label {
        color:#6172c7; font-size:1.05em; font-weight:600;
        margin-bottom: 0.3em;
    }
    .pf-row {
        margin:0.3em 0 1em 0; font-size:1.18em;
        padding: 0.5em;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 3px solid #6172c7;
    }
    .pf-bio {
        font-size:1.09em; color:#445;
        margin-bottom:0.8em; margin-top:0.25em;
        padding: 0.5em;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 3px solid #6172c7;
    }
    </style>
    """, unsafe_allow_html=True)
    if not st.session_state.get("edit_profile_mode", False):
        st.markdown("<div class='profile-header'>", unsafe_allow_html=True)
        if avatar and os.path.exists(avatar):
            st.image(avatar, width=120)
        else:
            st.image('https://cdn-icons-png.flaticon.com/512/3177/3177440.png', width=120)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='pf-label'>Name</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='pf-row'>{name or 'Not provided'}</div>", unsafe_allow_html=True)
        st.markdown("<div class='pf-label'>Username</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='pf-row'>{username or 'Not provided'}</div>", unsafe_allow_html=True)
        st.markdown("<div class='pf-label'>Pronouns</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='pf-row'>{pronouns or 'Not provided'}</div>", unsafe_allow_html=True)
        st.markdown("<div class='pf-label'>Bio</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='pf-bio'>{bio or 'No bio provided yet.'}</div>", unsafe_allow_html=True)
        st.markdown("<div class='pf-label'>Links</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='pf-row'>{links or 'No links provided'}</div>", unsafe_allow_html=True)
        if st.button("Edit Profile", type="primary"):
            st.session_state["edit_profile_mode"] = True
            st.rerun()
    else:
        st.markdown("### Edit Profile")
        with st.form("profile_form"):
            name_new = st.text_input("Name", value=name or "", placeholder="Enter your full name")
            username_new = st.text_input("Username", value=username or "", placeholder="Choose a username")
            pronouns_new = st.text_input("Pronouns", value=pronouns or "", placeholder="e.g., he/him, she/her, they/them")
            bio_new = st.text_area("Bio", value=bio or "", placeholder="Tell us about yourself...", height=100)
            links_new = st.text_input("Links", value=links or "", placeholder="Your website, social media, etc.")
            st.markdown("**Profile Photo**")
            avatar_file = st.file_uploader("Upload new profile photo", type=['png', 'jpg', 'jpeg'])
            col1, col2 = st.columns(2)
            save_btn = col1.form_submit_button("💾 Save Changes", type="primary")
            cancel_btn = col2.form_submit_button("❌ Cancel")
        if save_btn:
            avatar_path = avatar or ""
            if avatar_file:
                os.makedirs("profile_avatars", exist_ok=True)
                avatar_path = f"profile_avatars/{st.session_state['user']}_{avatar_file.name}"
                try:
                    with open(avatar_path, "wb") as f:
                        f.write(avatar_file.read())
                except Exception as e:
                    st.error(f"Error saving image: {e}")
                    avatar_path = avatar or ""
            success = update_profile(
                st.session_state['user'], 
                name_new, 
                username_new, 
                pronouns_new, 
                bio_new, 
                links_new, 
                avatar_path
            )
            if success:
                st.session_state["edit_profile_mode"] = False
                st.success("✅ Profile updated successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to update profile. Please try again.")
        if cancel_btn:
            st.session_state["edit_profile_mode"] = False
            st.rerun()

# ============ ADMIN AND APP (unchanged) ============
def admin_page():
    st.subheader("🛠️ Admin: User Database & Cleaning")
    users = list_users()
    pretty_card(
        "All Users",
        "",
        icon="📋"
    )
    if users:
        df = pd.DataFrame(users, columns=["ID", "Method", "User ID"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No users found in database.")
    del_user = st.text_input("Delete a user (enter User ID):", value="", key="delete_user_admin")
    if st.button("Delete User", key="delete_user_btn"):
        if del_user.strip():
            delete_user(del_user)
            st.success("User deleted (if existed). Refresh the page to see updates.")
            st.rerun()
    st.markdown("---")
    if st.button("🧹 Clean Null/Empty Accounts", key="clean_db_btn"):
        clean_null_users()
        st.success("Cleaned empty/null users from DB.")
        st.rerun()

def professional_app():
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/190/190411.png", width=80)
    st.sidebar.title("Career Navigator Pro")
    st.sidebar.write(f"Signed in as: {st.session_state['user']}")
    nav = st.sidebar.radio(
        "Navigation",
        ["Home", "My Career Path", "Top Skills", "Resources", "Feedback", "Profile", "Admin"],
        key="main_nav"
    )
    st.sidebar.markdown("---")
    if st.sidebar.button("Log Out"):
        logout()
        st.rerun()
    if nav == "Home":
        st.markdown("""
            <div style='border-radius:8px;padding:1.2em 1em;background:linear-gradient(90deg,#667eea 0,#764ba2 100%);color:#fff;margin-bottom:10px;'>
            <h2 style='margin-bottom:10px;'>Career Navigator Pro</h2>
            <h5 style='margin-top:0;'>Shape Your Future. Bridge The Gap.</h5>
            <p style='margin-bottom:0.5em;font-size:1.15em;'>Empowering you with skills, resources, and confidence for tomorrow's careers!</p>
            </div>
            """, unsafe_allow_html=True)
        st.image("https://img.freepik.com/premium-vector/guidance-concept-career-hiking_118813-4269.jpg", width=340)
        st.header("Why Career Navigator?")
        st.markdown("""
        - *Tailored career journeys* based on your interests and strengths  
        - *Real-time skill gap and readiness assessment*  
        - *Top-class notes, tutorials, and job resources*  
        - *Spotlight: Trending skills & future tech*  
        """)
    elif nav == "My Career Path":
        st.markdown("### 1️⃣ Select your career interest/domain")
        domains = ["AI & ML", "Web Development", "Cybersecurity", "Data Science", "Cloud", "Blockchain",
                   "Digital Marketing", "UI/UX", "Finance", "Product", "Other"]
        domain = st.selectbox("What's your dream career area?", domains, key="career_select")
        st.markdown("### 2️⃣ Rate your confidence level")
        confidence = st.slider("How would you rate your current knowledge?", 0, 100, 50, key="confidence_slider")
        req = 70
        st.progress(confidence / 100)
        if confidence < req:
            st.error(f"Skill Gap: {req-confidence} points to reach job-ready level.")
        else:
            st.success("You're currently job-ready!")
        show_res_btn = st.button("Show learning resources", key="show_resources_btn")
        if show_res_btn:
            with st.spinner("Fetching best materials..."):
                res = [
                    {"name": "FreeCodeCamp", "link": "https://freecodecamp.org", "desc": "Interactive coding and learning"},
                    {"name": "Coursera Free", "link": "https://coursera.org/courses?price=free", "desc": "Free university-level courses"},
                    {"name": "YouTube Tutorials", "link": f"https://youtube.com/results?search_query={domain}+tutorial", "desc": "Video lessons"},
                    {"name": "GeeksforGeeks", "link": "https://geeksforgeeks.org", "desc": "Notes and practice problems"},
                    {"name": "MIT OpenCourseWare", "link": "https://ocw.mit.edu/", "desc": "World-class university tutorials"}
                ]
                st.markdown("#### *Recommended Resources*")
                for r in res:
                    st.info(f"[{r['name']}]({r['link']}) — {r['desc']}")
    elif nav == "Top Skills":
        st.markdown("### 🌟 Trending & Future Skills")
        col1, col2 = st.columns(2)
        now = ["AI & ML", "Data Science", "Cloud", "Web/Mobile Apps", "Cybersecurity", "Blockchain"]
        future = ["Quantum Computing", "Augmented Reality", "Robotics", "Edge AI", "IoT/Industry 4.0", "GreenTech"]
        with col1:
            st.subheader("Hot Right Now")
            for skill in now:
                st.success(skill)
        with col2:
            st.subheader("Shaping the Future")
            for skill in future:
                st.info(skill)
        st.caption("Based on global job market & tech industry analysis.")
    elif nav == "Resources":
        st.markdown("### 📚 Universal Resources")
        st.markdown("Find great notes, cheat sheets, and tutorials for every tech domain:")
        st.write("- [MIT OpenCourseWare](https://ocw.mit.edu/)")
        st.write("- [GitHub Trending](https://github.com/trending)")
        st.write("- [GeeksforGeeks](https://geeksforgeeks.org/)")
        st.write("- [Codecademy](https://www.codecademy.com/)")
    elif nav == "Feedback":
        st.markdown("### 💬 Share your feedback!")
        feedback = st.text_area("Tell us your thoughts, suggestions, or feature requests:")
        if st.button("Submit feedback", key="feedback_btn"):
            st.success("Thank you! We appreciate your input and will use it to improve.")
    elif nav == "Profile":
        user_profile_page()
    elif nav == "Admin":
        if st.session_state['user'] == 'admin':
            admin_page()
        else:
            st.error("Access denied (admin only).")

st.set_page_config(page_title="Career Navigator Pro", layout='wide', page_icon="🎓")

if st.session_state['logged_in']:
    professional_app()
else:
    login_page()
