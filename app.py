import streamlit as st
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
from hashlib import pbkdf2_hmac
import json
import os
import random

# --- Constants ---
DATA_FILE = "data_store.json"
MAX_FAILED_ATTEMPTS = 3
DEFAULT_SALT = "studifinity_salt"
BACKGROUND_IMAGE = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80"

# --- UI Styling ---
st.markdown(
    f"""
    <style>
    /* Main app background with your image */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('{BACKGROUND_IMAGE}') no-repeat center center fixed;
        background-size: cover;
        color: white;
    }}
    
    /* Sidebar - Black Glassmorphism with White Text */
    .stSidebar {{
        background: rgba(10, 10, 10, 0.85) !important;
      
    }}
    
    .stSidebar .stMarkdown h1,
    .stSidebar .stMarkdown h2,
    .stSidebar .stMarkdown h3,
    .stSidebar .stMarkdown h4,
    .stSidebar .stMarkdown h5,
    .stSidebar .stMarkdown h6 {{
        color: white !important;
    }}
    
    /* Force white text for all headings */
    h1, h2, h3, h4, h5, h6 {{
        color: white !important;
        background-image: none !important;
        -webkit-text-fill-color: white !important;
    }}
    
    /* Dashboard title specific styling */
    .dashboard-title {{
        color: white !important;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
        background: none !important;
        -webkit-text-fill-color: white !important;
        text-shadow: none !important;
    }}
    
    /* Input fields - white background with black text */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {{
        background-color: white !important;
        color: black !important;
        border-radius: 8px !important;
    }}
    
    /* Placeholder text - dark gray */
    .stTextInput>div>div>input::placeholder,
    .stTextArea>div>div>textarea::placeholder {{
        color: #333 !important;
        opacity: 0.8 !important;
    }}
    
    /* Buttons - dark green gradient */
    .stButton>button {{
        background: linear-gradient(135deg, #0a5c36, #1db954) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(10, 92, 54, 0.4) !important;
    }}
    
    /* Cards - glassmorphism effect */
    .card {{
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }}
    
    /* Success messages */
    .stAlert-success {{
        background: rgba(10, 92, 54, 0.2) !important;
        border-left: 4px solid #1db954 !important;
    }}
    
    /* Responsive Design */
    @media (max-width: 768px) {{
        .dashboard-title {{
            font-size: 2rem;
        }}
        
        .card {{
            padding: 15px !important;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Key Management ---
@st.cache_resource
def load_cipher():
    key = Fernet.generate_key()
    return Fernet(key)

cipher = load_cipher()

# --- Data Handling ---
def load_data():
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Security Functions ---
def hash_passkey(passkey, salt=DEFAULT_SALT):
    key = pbkdf2_hmac('sha256', passkey.encode(), salt.encode(), 100000)
    return urlsafe_b64encode(key).decode()

def encrypt_data(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(encrypted_text):
    return cipher.decrypt(encrypted_text.encode()).decode()

# --- Session Management ---
if "data_store" not in st.session_state:
    st.session_state.data_store = load_data()

if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

if "authorized" not in st.session_state:
    st.session_state.authorized = False

if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# --- Dashboard Page ---
def dashboard_page():
    """Dashboard/Home Page"""
    st.markdown('<h1 class="dashboard-title">📊 Secure Data Vault</h1>', unsafe_allow_html=True)
    
    # Stats Cards Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <h3>🔢</h3>
            <h2>{len(st.session_state.data_store[st.session_state.current_user]["entries"])}</h2>
            <p>Total Secrets</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <h3>🛡️</h3>
            <h2>256-bit</h2>
            <p>Encryption</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <h3>⚡</h3>
            <h2>100%</h2>
            <p>Secure</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Security Tips
    st.subheader("🔒 Security Tips")
    tips = [
        "Change passwords every 3 months",
        "Never share encryption keys",
        "Use complex passphrases",
        "Enable 2FA where possible",
        "Beware of phishing attempts"
    ]
    
    for tip in tips:
        st.markdown(f"""
        <div class="card" style="padding: 12px 15px; margin-bottom: 8px;">
            <p>✓ {tip}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("🔒 Encrypt New Data", use_container_width=True):
            st.session_state.page = "store"
            st.rerun()
    with action_col2:
        if st.button("🔓 Decrypt Data", use_container_width=True):
            st.session_state.page = "retrieve"
            st.rerun()

# --- Login/Register Page ---
def login_page():
    """Login/Registration Page"""
    st.title("🔐 Secure Login")
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        if st.button("Login / Register"):
            if not username or not password:
                st.error("Please enter both fields")
                return
                
            hashed_pass = hash_passkey(password)
            users = st.session_state.data_store
            
            if username not in users:
                users[username] = {"password": hashed_pass, "entries": {}}
                st.success("Account created! Logged in.")
            elif users[username]["password"] != hashed_pass:
                st.session_state.failed_attempts += 1
                st.error(f"Wrong password. {MAX_FAILED_ATTEMPTS - st.session_state.failed_attempts} attempts left")
                return
            else:
                st.success("Login successful!")
                
            st.session_state.current_user = username
            st.session_state.authorized = True
            save_data(users)
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

# --- Store Data Page ---
def store_data_page():
    """Data Encryption Page"""
    st.title("🔒 Store Data")
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        data = st.text_area("Your Data", placeholder="Enter text to encrypt", height=150)
        passkey = st.text_input("Encryption Key", type="password", placeholder="Set a passkey")
        
        if st.button("Encrypt & Save"):
            if not data or not passkey:
                st.error("All fields required")
                return
                
            encrypted = encrypt_data(data)
            hashed_key = hash_passkey(passkey)
            
            st.session_state.data_store[st.session_state.current_user]["entries"][encrypted] = hashed_key
            save_data(st.session_state.data_store)
            
            st.success("Data encrypted and saved!")
            st.code(encrypted)
            
        st.markdown('</div>', unsafe_allow_html=True)

# --- Retrieve Data Page ---
def retrieve_data_page():
    """Data Decryption Page"""
    st.title("🔓 Retrieve Data")
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        encrypted = st.text_area("Encrypted Data", placeholder="Paste encrypted data", height=100)
        passkey = st.text_input("Decryption Key", type="password", placeholder="Enter passkey")
        
        if st.button("Decrypt"):
            if not encrypted or not passkey:
                st.error("All fields required")
                return
                
            entries = st.session_state.data_store[st.session_state.current_user]["entries"]
            hashed_input = hash_passkey(passkey)
            
            if encrypted in entries and entries[encrypted] == hashed_input:
                decrypted = decrypt_data(encrypted)
                st.success("Decrypted successfully!")
                st.text_area("Decrypted Data", decrypted, height=150)
            else:
                st.error("Invalid passkey or data")
                
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main App ---
if st.session_state.authorized:
    st.sidebar.title(f"Welcome, {st.session_state.current_user}!")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🏠 Dashboard"):
        st.session_state.page = "home"
    if st.sidebar.button("💾 Store Data"):
        st.session_state.page = "store"
    if st.sidebar.button("📂 Retrieve Data"):
        st.session_state.page = "retrieve"
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authorized = False
        st.session_state.current_user = ""
        st.rerun()

if not st.session_state.authorized:
    login_page()
else:
    if "page" not in st.session_state:
        st.session_state.page = "home"
        
    if st.session_state.page == "home":
        dashboard_page()
    elif st.session_state.page == "store":
        store_data_page()
    elif st.session_state.page == "retrieve":
        retrieve_data_page()
