Career Navigator Pro
Career Navigator Pro is a professional web application for career guidance and planning. It offers user sign-in, user profile editing (including avatar/photo), password reset, resource recommendations, and a clean admin dashboard. The app is built using Streamlit and uses SQLite for persistent user storage.

Setup Instructions
1. Clone the repository
bash
git clone <https://github.com/Suprajacheekatla/Streamlit_career_app>
cd <YOUR_PROJECT_FOLDER>
2. Install dependencies
bash
pip install streamlit pandas
Python 3.8+ is recommended

sqlite3 and hashlib are part of Python standard library.

3. Run the application
bash
streamlit run app.py
Usage Guide
Sign In: Use your registered email or phone and password.

Create Account: Click "Create Account" on the sign-in page. Fill in required details. After registration, log in with your new credentials.

Forgot Password: Click "Forgot Password?" to reset your password with your registered email/phone.

Profile: After logging in, navigate to "Profile" in the sidebar. Here you can view and edit your name, username, pronouns, bio, links, and upload a profile photo.

Admin Tools: Log in as the user "admin" for access to user management tools.

Navigation: Use sidebar to explore career tools, resources, feedback, and more.

Dependencies
streamlit

pandas

sqlite3 (Python built-in)

hashlib (Python built-in)

os (Python built-in)

File & Folder Structure
app.py — Main Streamlit application (your complete code).

users.db — SQLite database (auto-generated).

/profile_avatars/ — Folder for uploaded profile images (auto-created).

README.md — This documentation file.
Troubleshooting
If login or registration fails, make sure your Python version is 3.8 or higher and dependencies are installed.

To reset for clean start, delete the users.db file and restart the app.

Profile images are stored in profile_avatars/. Make sure your system has appropriate write permissions.

About
This project is designed for academic/learning purposes and streamlines the development cycle for feature-rich Streamlit web applications. For any further improvements or issues, please open a Pull Request or Issue in the repository.

⚠️ Note: The app is hosted on Render's free tier.  
If it seems offline, please wait ~1 minute while it restarts.

