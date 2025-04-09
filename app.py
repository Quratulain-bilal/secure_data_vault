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
    
    /* Sidebar with same background image */
    .stSidebar {{
        background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), url('{BACKGROUND_IMAGE}') no-repeat center center fixed !important;
        background-size: cover !important;
    }}

    /* White headings */
    h1, h2, h3, h4, h5, h6 {{
        color: white !important;
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
    
    /* Gradient Titles */
    .gradient-title {{
        background: linear-gradient(135deg, #1db954, #0a5c36);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 20px;
    }}
    
    /* Responsive Design */
    @media (max-width: 768px) {{
        .gradient-title {{
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

# --- Fun Facts About Encryption ---
ENCRYPTION_FACTS = [
    "The Caesar Cipher is one of the earliest known encryption techniques.",
    "Modern encryption uses algorithms that are nearly impossible to crack without the key.",
    "Quantum computers could potentially break current encryption methods.",
    "AES (Advanced Encryption Standard) is widely used for secure data encryption.",
    "Encryption protects over 80% of online transactions worldwide."
]

def display_random_fact():
    fact = random.choice(ENCRYPTION_FACTS)
    st.info(f"💡 **Did You Know?** {fact}")

# --- Interactive Game: Decode Challenge ---
def decode_challenge():
    st.subheader("🎮 Decode Challenge")
    challenge_text = "HELLOSECURE"
    encrypted_challenge = encrypt_data(challenge_text)
    
    st.write("Can you decode this encrypted message?")
    st.code(encrypted_challenge, language="text")
    
    user_input = st.text_input("Enter the decrypted text:")
    
    if st.button("Check Answer"):
        if user_input.strip().upper() == challenge_text:
            st.success("🎉 Correct! You decoded the message!")
        else:
            st.error("❌ Incorrect. Try again!")

# --- Dashboard Page ---
def dashboard_page():
    """Dashboard/Home Page"""
    st.markdown('<h1 class="gradient-title">📊 Secure Data Vault</h1>', unsafe_allow_html=True)
    
    # Display Random Fact
    display_random_fact()
    
    # Welcome Message
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("""
        Welcome to the **Secure Data Vault**! This application allows you to securely store and retrieve encrypted data.
        Use the sidebar to navigate between different features:
        - **Store Data**: Encrypt and save your sensitive information.
        - **Retrieve Data**: Decrypt and access your stored data.
        - **Logout**: Securely log out of your account.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Game
    decode_challenge()

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