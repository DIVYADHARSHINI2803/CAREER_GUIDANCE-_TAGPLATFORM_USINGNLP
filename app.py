
"""
TAG - Together Achieve Growth
Enhanced Version with Real-time Updates & NLP Features
"""

import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import hashlib
import os
import re
import json

# ==================== NLP FUNCTIONS (Lightweight, no heavy dependencies) ====================

# Career keywords for auto-detection
CAREER_KEYWORDS = {
    'Engineering': ['engineer', 'coding', 'programming', 'software', 'it', 'computer', 'tech', 'robotics', 'ai', 'machine learning', 'web development', 'app development', 'btech', 'be'],
    'Medical': ['doctor', 'medical', 'mbbs', 'nurse', 'healthcare', 'hospital', 'dentist', 'pharmacy', 'bds', 'bhms', 'bams', 'veterinary', 'physician', 'surgeon'],
    'Arts': ['arts', 'design', 'creative', 'painting', 'music', 'dance', 'theatre', 'journalism', 'mass communication', 'literature', 'fine arts', 'animation', 'graphic design'],
    'Government Jobs': ['government', 'civil service', 'upsc', 'ssc', 'bank', 'railway', 'defence', 'police', 'ias', 'ips', 'irs', 'government exam', 'ssc cgl', 'banking'],
    'Other': ['business', 'entrepreneur', 'sports', 'law', 'research', 'teaching', 'management', 'hotel management', 'event management', 'digital marketing']
}

# Sentiment keywords
SENTIMENT_KEYWORDS = {
    'confused': ['confused', 'not sure', 'dilemma', 'unclear', 'uncertain', 'which one', 'what to do', 'help me decide', 'can\'t decide'],
    'anxious': ['worried', 'anxious', 'stressed', 'pressure', 'tension', 'nervous', 'scared', 'fear', 'anxiety', 'overwhelmed'],
    'excited': ['excited', 'passionate', 'interested', 'love', 'enjoy', 'fascinated', 'dream', 'aspire', 'motivated', 'enthusiastic'],
    'urgent': ['urgent', 'immediate', 'soon', 'deadline', 'fast', 'quickly', 'asap', 'emergency', 'time sensitive']
}

def simple_nlp_analysis(message):
    """Lightweight NLP analysis using keyword matching"""
    message_lower = message.lower()
    
    # 1. Auto-detect career type
    detected_career = "Other"
    career_confidence = 0
    
    for career, keywords in CAREER_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                detected_career = career
                career_confidence += 1
                break
        if career_confidence > 0:
            break
    
    # 2. Sentiment detection
    sentiment = "neutral"
    sentiment_reason = ""
    
    for sent_type, keywords in SENTIMENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                if sent_type == 'confused':
                    sentiment = "confused"
                    sentiment_reason = "Student appears confused about career path"
                elif sent_type == 'anxious':
                    sentiment = "anxious"
                    sentiment_reason = "Student shows signs of anxiety/stress"
                elif sent_type == 'excited':
                    sentiment = "excited"
                    sentiment_reason = "Student is excited and motivated"
                elif sent_type == 'urgent':
                    sentiment = "urgent"
                    sentiment_reason = "Query marked as urgent"
                break
        if sentiment != "neutral":
            break
    
    # 3. Extract key skills/interests
    skills = []
    skill_keywords = {
        'Technical': ['coding', 'programming', 'math', 'science', 'computer', 'technical', 'engineering'],
        'Creative': ['drawing', 'painting', 'writing', 'music', 'design', 'creative', 'artistic'],
        'Analytical': ['problem solving', 'logic', 'analysis', 'research', 'analytical', 'critical thinking'],
        'Social': ['teaching', 'helping', 'communication', 'leadership', 'social', 'people', 'team']
    }
    
    for skill, keywords in skill_keywords.items():
        for keyword in keywords:
            if keyword in message_lower:
                skills.append(skill)
                break
    
    # 4. Calculate urgency score (1-5)
    urgency_score = 1
    if sentiment == "urgent":
        urgency_score = 5
    elif any(word in message_lower for word in ['help', 'guidance', 'advice']):
        urgency_score = 3
    elif any(word in message_lower for word in ['interested', 'curious', 'want to know']):
        urgency_score = 2
    
    # 5. Extract key phrases (simple)
    key_phrases = []
    words = message_lower.split()
    for i in range(len(words)-1):
        phrase = f"{words[i]} {words[i+1]}"
        if phrase in ['career path', 'which field', 'what subject', 'how to become', 'scope of', 'future of']:
            key_phrases.append(phrase)
    
    return {
        'detected_career': detected_career,
        'career_confidence': min(career_confidence, 3),
        'sentiment': sentiment,
        'sentiment_reason': sentiment_reason,
        'detected_skills': list(set(skills)),
        'urgency_score': urgency_score,
        'key_phrases': key_phrases[:3]
    }

def generate_smart_response(query, nlp_result):
    """Generate intelligent response suggestion based on NLP analysis"""
    responses = []
    
    # Based on sentiment
    if nlp_result['sentiment'] == 'anxious':
        responses.append("🌟 Don't worry! Many students have similar questions. Let me help you clarify your career path.")
    elif nlp_result['sentiment'] == 'confused':
        responses.append("💡 It's completely normal to be confused about career choices. Let's break this down step by step.")
    elif nlp_result['sentiment'] == 'excited':
        responses.append("🎉 That's great enthusiasm! Let's channel this energy into finding the perfect career path for you.")
    
    # Based on detected career
    if nlp_result['detected_career'] != 'Other':
        responses.append(f"📚 Regarding {nlp_result['detected_career']}, here are some key points to consider...")
    
    # Based on skills
    if nlp_result['detected_skills']:
        skills_str = ', '.join(nlp_result['detected_skills'])
        responses.append(f"🔧 Based on your interest in {skills_str}, here are some career options...")
    
    # General helpful response
    if not responses:
        responses.append("Thank you for your query! Here's some guidance to help you make an informed decision.")
    
    return " ".join(responses)

def get_career_insights(career_type):
    """Provide career-specific insights"""
    insights = {
        'Engineering': {
            'scope': 'High demand in software, hardware, AI, robotics, and core engineering sectors',
            'exams': 'JEE Main, JEE Advanced, BITSAT, VITEEE, State engineering exams',
            'colleges': 'IITs, NITs, BITS, IIITs, State Engineering Colleges',
            'salary_range': '₹3-20 LPA (fresher), increases with experience',
            'skills': 'Problem-solving, Mathematics, Programming, Logical thinking'
        },
        'Medical': {
            'scope': 'Growing demand in healthcare, research, and specialized medicine',
            'exams': 'NEET-UG, AIIMS MBBS, JIPMER, State medical exams',
            'colleges': 'AIIMS, JIPMER, CMC Vellore, AFMC, State Medical Colleges',
            'salary_range': '₹6-15 LPA (fresher), higher for specialists',
            'skills': 'Empathy, Attention to detail, Memory, Scientific aptitude'
        },
        'Arts': {
            'scope': 'Diverse opportunities in media, design, education, and creative industries',
            'exams': 'DUET, BHU UET, JNUEE, CUET, University-specific exams',
            'colleges': 'DU, JNU, BHU, Jamia Millia Islamia, Lady Shri Ram College',
            'salary_range': '₹2-10 LPA, varies by specialization',
            'skills': 'Creativity, Communication, Critical thinking, Adaptability'
        },
        'Government Jobs': {
            'scope': 'Stable careers with job security and benefits across various departments',
            'exams': 'UPSC CSE, SSC CGL, Banking exams (IBPS, SBI), RRB, State PSCs',
            'colleges': 'Any recognized university (eligibility based on exam)',
            'salary_range': '₹5-15 LPA + allowances (7th Pay Commission)',
            'skills': 'General awareness, Aptitude, Reasoning, Communication'
        },
        'Other': {
            'scope': 'Many emerging fields including business, sports, law, research, and more',
            'exams': 'Varies by field (CLAT for Law, CAT for MBA, etc.)',
            'colleges': 'Field-specific top institutions',
            'salary_range': 'Varies widely by industry and role',
            'skills': 'Field-specific skills and continuous learning'
        }
    }
    return insights.get(career_type, insights['Other'])

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="TAG - Career Guidance with AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI (same as before)
def load_css():
    st.markdown("""
        <style>
        /* Main container styling */
        .main { padding: 0rem 1rem; }
        
        /* Card styling */
        .css-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 1rem;
        }
        
        /* Statistic cards */
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }
        .stat-card:hover { transform: translateY(-5px); }
        
        /* NLP Insight Card */
        .nlp-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 1rem;
            border-radius: 15px;
            color: white;
            margin-bottom: 1rem;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.5rem 2rem;
            border-radius: 25px;
            font-weight: bold;
            transition: all 0.3s;
        }
        .stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        /* Badge styling */
        .badge {
            display: inline-block;
            padding: 0.25rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-right: 0.5rem;
        }
        .badge-engineering { background: #ff6b6b; color: white; }
        .badge-medical { background: #4ecdc4; color: white; }
        .badge-arts { background: #ffd93d; color: black; }
        .badge-government { background: #6c5ce7; color: white; }
        .badge-other { background: #a8a8a8; color: white; }
        
        /* Sentiment badges */
        .sentiment-confused { background: #ffa502; color: white; }
        .sentiment-anxious { background: #ff4757; color: white; }
        .sentiment-excited { background: #26de81; color: white; }
        .sentiment-neutral { background: #747d8c; color: white; }
        .sentiment-urgent { background: #e84118; color: white; }
        
        /* Typography */
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ==================== DATABASE SETUP (Same as before with NLP columns) ====================
def init_database():
    """Initialize SQLite database with required tables including NLP columns"""
    conn = sqlite3.connect('database.db', check_same_thread=False)
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create queries table with NLP columns
    c.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            student_email TEXT NOT NULL,
            career_type TEXT NOT NULL,
            phone TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            admin_response TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            detected_career TEXT,
            sentiment TEXT,
            urgency_score INTEGER DEFAULT 1,
            detected_skills TEXT,
            nlp_insights TEXT
        )
    ''')
    
    # Create notifications table
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Check if admin exists
    c.execute("SELECT * FROM users WHERE role='admin'")
    if not c.fetchone():
        admin_password = hash_password("admin123")
        c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                 ("Admin", "admin@tag.com", admin_password, "admin"))
    
    conn.commit()
    conn.close()

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(name, email, password):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        if c.fetchone():
            return False, "Email already registered!"
        
        hashed = hash_password(password)
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                 (name, email, hashed))
        user_id = c.lastrowid
        
        c.execute("INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
                 (user_id, "Welcome to TAG! Start exploring career options.", "success"))
        
        conn.commit()
        return True, "Registration successful!"
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def authenticate_user(email, password):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        
        if user and verify_password(password, user[3]):
            return True, {"id": user[0], "name": user[1], "email": user[2], "role": user[4]}
        return False, "Invalid email or password!"
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def save_query(student_name, student_email, career_type, phone, message):
    """Save student query with NLP analysis"""
    try:
        # Perform NLP analysis
        nlp_result = simple_nlp_analysis(message)
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Use AI-detected career if available and confidence is good
        final_career = career_type
        if nlp_result['detected_career'] != 'Other' and nlp_result['career_confidence'] >= 2:
            final_career = nlp_result['detected_career']
        
        c.execute('''
            INSERT INTO queries (student_name, student_email, career_type, phone, message, 
                               detected_career, sentiment, urgency_score, detected_skills, nlp_insights)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (student_name, student_email, final_career, phone, message,
              nlp_result['detected_career'], nlp_result['sentiment'], 
              nlp_result['urgency_score'], json.dumps(nlp_result['detected_skills']),
              json.dumps(nlp_result)))
        
        # Get admin users for notification with priority
        c.execute("SELECT id FROM users WHERE role='admin'")
        admins = c.fetchall()
        
        # Add priority indicator in notification for urgent queries
        priority_msg = f"New query from {student_name} regarding {final_career}"
        if nlp_result['urgency_score'] >= 4:
            priority_msg = f"🔴 URGENT: {priority_msg}"
        elif nlp_result['sentiment'] == 'anxious':
            priority_msg = f"🟡 ANXIOUS: {priority_msg}"
        
        for admin in admins:
            c.execute('''
                INSERT INTO notifications (user_id, message, type) 
                VALUES (?, ?, ?)
            ''', (admin[0], priority_msg, "info"))
        
        conn.commit()
        return True, "Query submitted successfully! AI has analyzed your query."
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def get_all_queries():
    try:
        conn = sqlite3.connect('database.db')
        df = pd.read_sql_query("SELECT * FROM queries ORDER BY date DESC", conn)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        conn.close()

def get_student_queries(email):
    try:
        conn = sqlite3.connect('database.db')
        df = pd.read_sql_query("SELECT * FROM queries WHERE student_email=? ORDER BY date DESC", conn, params=(email,))
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        conn.close()

def delete_query(query_id):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("DELETE FROM queries WHERE id=?", (query_id,))
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        conn.close()

def update_query_status(query_id, status, response=""):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            UPDATE queries 
            SET status=?, admin_response=? 
            WHERE id=?
        ''', (status, response, query_id))
        
        c.execute("SELECT student_email FROM queries WHERE id=?", (query_id,))
        student_email = c.fetchone()[0]
        c.execute("SELECT id FROM users WHERE email=?", (student_email,))
        student_id = c.fetchone()[0]
        
        c.execute('''
            INSERT INTO notifications (user_id, message, type) 
            VALUES (?, ?, ?)
        ''', (student_id, f"Your query #{query_id} has been {status}", "success"))
        
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        conn.close()

def get_unread_notifications(user_id):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            SELECT * FROM notifications 
            WHERE user_id=? AND is_read=0 
            ORDER BY created_at DESC
        ''', (user_id,))
        notifications = c.fetchall()
        return notifications
    except Exception as e:
        return []
    finally:
        conn.close()

def mark_notifications_read(user_id):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('UPDATE notifications SET is_read=1 WHERE user_id=?', (user_id,))
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        conn.close()

# ==================== SESSION MANAGEMENT ====================
def init_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = 'Home'
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.page = 'Home'
    st.session_state.notifications = []
    st.rerun()

def notification_badge():
    if st.session_state.logged_in:
        notifications = get_unread_notifications(st.session_state.user['id'])
        if notifications:
            st.sidebar.markdown(f"""
                <div style="background-color: #ff4757; color: white; padding: 5px 10px; 
                            border-radius: 20px; text-align: center; margin: 10px 0;">
                    🔔 {len(notifications)} New Notification(s)
                </div>
            """, unsafe_allow_html=True)
            
            if st.sidebar.button("📩 View Notifications"):
                st.session_state.page = 'Notifications'
                st.rerun()

def get_badge_class(career_type):
    badges = {
        'Engineering': 'badge-engineering',
        'Medical': 'badge-medical',
        'Arts': 'badge-arts',
        'Government Jobs': 'badge-government',
        'Other': 'badge-other'
    }
    return badges.get(career_type, 'badge-other')

def get_sentiment_class(sentiment):
    sentiments = {
        'confused': 'sentiment-confused',
        'anxious': 'sentiment-anxious',
        'excited': 'sentiment-excited',
        'neutral': 'sentiment-neutral',
        'urgent': 'sentiment-urgent'
    }
    return sentiments.get(sentiment, 'sentiment-neutral')

# ==================== UI PAGES ====================
def home_page():
    load_css()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
            <div style="padding: 2rem 0;">
                <h1 style="font-size: 4rem; margin-bottom: 0;">TAG</h1>
                <h2 style="color: #666; margin-top: 0;">Together Achieve Growth</h2>
                <p style="font-size: 1.2rem; color: #444; margin: 2rem 0;">
                    AI-powered career guidance platform for government school students. 
                    Get personalized career recommendations and expert advice.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.logged_in:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🚀 Get Started", use_container_width=True):
                    st.session_state.page = 'Sign Up'
                    st.rerun()
            with col2:
                if st.button("🔐 Login", use_container_width=True):
                    st.session_state.page = 'Login'
                    st.rerun()
    
    with col2:
        st.markdown("""
            <div class="css-card">
                <h3 style="color: white;">🤖 AI-Powered Features</h3>
                <p>✨ Smart career detection</p>
                <p>💭 Sentiment analysis</p>
                <p>🎯 Skill extraction</p>
                <p>⚡ Priority scoring</p>
                <p>📊 Career insights</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="stat-card">
                <h3 style="color: #667eea;">🎯 Our Mission</h3>
                <p style="color: #666;">To provide AI-powered career guidance to government school students.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stat-card">
                <h3 style="color: #667eea;">👁️ Our Vision</h3>
                <p style="color: #666;">Every student deserves quality career guidance powered by AI.</p>
            </div>
        """, unsafe_allow_html=True)

def signup_page():
    load_css()
    st.markdown("<h1 style='text-align: center;'>Join TAG Community</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
        """, unsafe_allow_html=True)
        
        with st.form("signup_form"):
            name = st.text_input("👤 Full Name *", placeholder="Enter your full name")
            email = st.text_input("📧 Email *", placeholder="Enter your email")
            password = st.text_input("🔒 Password *", type="password", placeholder="Min 6 characters")
            confirm_password = st.text_input("🔒 Confirm Password *", type="password", placeholder="Re-enter password")
            
            submitted = st.form_submit_button("🚀 Create Account", use_container_width=True)
            
            if submitted:
                if not all([name, email, password, confirm_password]):
                    st.error("❌ Please fill all fields!")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match!")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters long!")
                else:
                    with st.spinner("Creating your account..."):
                        time.sleep(1)
                        success, message = create_user(name, email, password)
                        if success:
                            st.success("✅ Account created successfully!")
                            st.balloons()
                            st.info("Please login to continue")
                            time.sleep(2)
                            st.session_state.page = 'Login'
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        
        st.markdown("</div>", unsafe_allow_html=True)

def login_page():
    load_css()
    st.markdown("<h1 style='text-align: center;'>Welcome Back!</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("📧 Email *", placeholder="Enter your email")
            password = st.text_input("🔒 Password *", type="password", placeholder="Enter your password")
            
            submitted = st.form_submit_button("🔐 Login", use_container_width=True)
            
            if submitted:
                if not all([email, password]):
                    st.error("❌ Please fill all fields!")
                else:
                    with st.spinner("Authenticating..."):
                        time.sleep(1)
                        success, result = authenticate_user(email, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user = result
                            
                            if result['role'] == 'admin':
                                st.session_state.page = 'Admin'
                            else:
                                st.session_state.page = 'Dashboard'
                            
                            st.success(f"✨ Welcome back, {result['name']}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {result}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("🔑 Demo Credentials"):
            st.markdown("""
                **Admin Access:**  
                - Email: `admin@tag.com`  
                - Password: `admin123`  
                
                **Student Access:**  
                - Create your own account
            """)

def student_dashboard():
    load_css()
    
    count = st_autorefresh(interval=10000, key="student_refresh")
    
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h1>👋 Welcome, {st.session_state.user['name']}!</h1>
        </div>
    """, unsafe_allow_html=True)
    
    queries_df = get_student_queries(st.session_state.user['email'])
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="stat-card"><h3>📊 Total Queries</h3><h2 style="color:#667eea;">{len(queries_df)}</h2></div>""", unsafe_allow_html=True)
    with col2:
        pending = len(queries_df[queries_df['status'] == 'pending']) if not queries_df.empty else 0
        st.markdown(f"""<div class="stat-card"><h3>⏳ Pending</h3><h2 style="color:#ffa502;">{pending}</h2></div>""", unsafe_allow_html=True)
    with col3:
        answered = len(queries_df[queries_df['status'] == 'answered']) if not queries_df.empty else 0
        st.markdown(f"""<div class="stat-card"><h3>✅ Answered</h3><h2 style="color:#26de81;">{answered}</h2></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="stat-card"><h3>📅 Joined</h3><h2 style="color:#778ca3;">{datetime.now().strftime('%b %Y')}</h2></div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # AI-Powered Query Assistant Section
    st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem;">
            <h3 style="color: white;">🤖 AI-Powered Query Assistant</h3>
            <p style="color: white;">Type your query below and watch AI analyze it in real-time!</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Live NLP Analysis Preview
    preview_message = st.text_area("✏️ Type your query here for AI analysis...", height=100, key="preview", 
                                    placeholder="Example: I'm confused between Engineering and Medical. I like computers but also want to help people. What should I choose?")
    
    if preview_message and len(preview_message) > 10:
        nlp_preview = simple_nlp_analysis(preview_message)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            sentiment_class = get_sentiment_class(nlp_preview['sentiment'])
            st.markdown(f"""
                <div class="stat-card">
                    <h4>💭 Sentiment</h4>
                    <span class="badge {sentiment_class}">{nlp_preview['sentiment'].upper()}</span>
                    <p style="font-size:0.8rem; margin-top:0.5rem;">{nlp_preview['sentiment_reason'] or 'Neutral'}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="stat-card">
                    <h4>🎯 Detected Career</h4>
                    <span class="badge {get_badge_class(nlp_preview['detected_career'])}">{nlp_preview['detected_career']}</span>
                    <p style="font-size:0.8rem;">Confidence: {'⭐' * nlp_preview['career_confidence']}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="stat-card">
                    <h4>🔧 Skills Detected</h4>
                    <p style="font-size:0.9rem;">{', '.join(nlp_preview['detected_skills']) if nlp_preview['detected_skills'] else 'None detected'}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            urgency_color = "#e84118" if nlp_preview['urgency_score'] >= 4 else "#ffa502" if nlp_preview['urgency_score'] >= 3 else "#26de81"
            st.markdown(f"""
                <div class="stat-card">
                    <h4>⚡ Urgency Score</h4>
                    <h2 style="color:{urgency_color};">{nlp_preview['urgency_score']}/5</h2>
                </div>
            """, unsafe_allow_html=True)
        
        # Show AI Suggestion
        if nlp_preview['detected_career'] != 'Other':
            insights = get_career_insights(nlp_preview['detected_career'])
            with st.expander("💡 AI Career Insights", expanded=True):
                st.markdown(f"""
                    <div style="background: #f0f2f6; padding: 1rem; border-radius: 10px;">
                        <p><strong>📚 Scope:</strong> {insights['scope']}</p>
                        <p><strong>📝 Key Exams:</strong> {insights['exams']}</p>
                        <p><strong>🏛️ Top Colleges:</strong> {insights['colleges']}</p>
                        <p><strong>💰 Salary Range:</strong> {insights['salary_range']}</p>
                        <p><strong>🔧 Key Skills:</strong> {insights['skills']}</p>
                    </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Submit query form
    with st.expander("📝 Submit New Career Query", expanded=True):
        with st.form("query_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                student_name = st.text_input("👤 Your Name *", value=st.session_state.user['name'])
                career_type = st.selectbox(
                    "🎯 Career Type *",
                    ["Engineering", "Medical", "Arts", "Government Jobs", "Other"]
                )
            
            with col2:
                phone = st.text_input("📞 Phone Number *", placeholder="10-digit mobile number")
            
            message = st.text_area("💬 Your Query *", placeholder="Describe your career query in detail...", height=150)
            
            submitted = st.form_submit_button("🚀 Submit Query with AI Analysis", use_container_width=True)
            
            if submitted:
                if not all([student_name, career_type, phone, message]):
                    st.error("❌ Please fill all required fields!")
                elif len(phone) != 10 or not phone.isdigit():
                    st.error("❌ Please enter a valid 10-digit phone number!")
                else:
                    with st.spinner("AI is analyzing your query..."):
                        success, msg = save_query(student_name, st.session_state.user['email'], career_type, phone, message)
                        if success:
                            st.success("✅ " + msg)
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ " + msg)
    
    # Query history with NLP insights
    st.markdown("## 📋 Your Query History")
    
    if queries_df.empty:
        st.info("🌟 You haven't submitted any queries yet. Use the AI assistant above!")
    else:
        for _, row in queries_df.iterrows():
            status_color = {'pending': '#ffa502', 'answered': '#26de81', 'resolved': '#20bf6b'}.get(row['status'], '#778ca3')
            badge_class = get_badge_class(row['career_type'])
            sentiment_class = get_sentiment_class(row.get('sentiment', 'neutral'))
            
            st.markdown(f"""
                <div class="query-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span class="badge {badge_class}">{row['career_type']}</span>
                            <span class="badge" style="background-color: {status_color};">{row['status'].upper()}</span>
                            <span class="badge {sentiment_class}">🧠 {row.get('sentiment', 'neutral').upper()}</span>
                        </div>
                        <small style="color: #999;">{row['date'][:10]}</small>
                    </div>
                    <p style="margin: 1rem 0; font-size: 1.1rem;">{row['message']}</p>
                    <div style="display: flex; justify-content: space-between;">
                        <small>📞 {row['phone']}</small>
                        <small>🆔 #{row['id']}</small>
                    </div>
            """, unsafe_allow_html=True)
            
            # Show NLP insights if available
            if row.get('urgency_score') and row['urgency_score'] >= 3:
                st.warning(f"⚡ This query was marked as priority (Urgency: {row['urgency_score']}/5)")
            
            if row['admin_response']:
                st.markdown(f"""
                    <div style="background-color: #e8f4fd; padding: 1rem; border-radius: 10px; margin-top: 1rem;">
                        <strong>👨‍🏫 Admin Response:</strong>
                        <p style="margin-top: 0.5rem;">{row['admin_response']}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

def admin_panel():
    load_css()
    
    count = st_autorefresh(interval=5000, key="admin_refresh")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h1>👑 AI-Powered Admin Dashboard</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style="background: #f0f2f6; padding: 0.5rem; border-radius: 10px; text-align: center;">
                <small>🔄 Auto-refresh: {datetime.now().strftime('%H:%M:%S')}</small>
            </div>
        """, unsafe_allow_html=True)
    
    queries_df = get_all_queries()
    
    # Statistics with NLP insights
    st.markdown("## 📊 AI-Powered Analytics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""<div class="stat-card"><h3>📝 Total</h3><h2>{len(queries_df)}</h2></div>""", unsafe_allow_html=True)
    with col2:
        pending = len(queries_df[queries_df['status'] == 'pending']) if not queries_df.empty else 0
        st.markdown(f"""<div class="stat-card"><h3>⏳ Pending</h3><h2>{pending}</h2></div>""", unsafe_allow_html=True)
    with col3:
        urgent = len(queries_df[queries_df['urgency_score'] >= 4]) if not queries_df.empty and 'urgency_score' in queries_df.columns else 0
        st.markdown(f"""<div class="stat-card"><h3>🔴 Urgent</h3><h2 style="color:#e84118;">{urgent}</h2></div>""", unsafe_allow_html=True)
    with col4:
        anxious = len(queries_df[queries_df['sentiment'] == 'anxious']) if not queries_df.empty and 'sentiment' in queries_df.columns else 0
        st.markdown(f"""<div class="stat-card"><h3>😟 Anxious</h3><h2 style="color:#ff4757;">{anxious}</h2></div>""", unsafe_allow_html=True)
    with col5:
        unique = queries_df['student_email'].nunique() if not queries_df.empty else 0
        st.markdown(f"""<div class="stat-card"><h3>👥 Students</h3><h2>{unique}</h2></div>""", unsafe_allow_html=True)
    
    # Charts
    if not queries_df.empty:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            career_counts = queries_df['career_type'].value_counts().reset_index()
            career_counts.columns = ['Career Type', 'Count']
            fig = px.pie(career_counts, values='Count', names='Career Type', title='Career Distribution')
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'sentiment' in queries_df.columns:
                sentiment_counts = queries_df['sentiment'].value_counts().reset_index()
                sentiment_counts.columns = ['Sentiment', 'Count']
                fig = px.bar(sentiment_counts, x='Sentiment', y='Count', title='Student Sentiment Analysis', color='Sentiment')
                st.plotly_chart(fig, use_container_width=True)
    
    # Queries feed
    st.markdown("---")
    st.markdown("## 📋 Live Queries Feed with AI Insights")
    
    if queries_df.empty:
        st.info("📭 No queries yet")
    else:
        # Sort by urgency
        if 'urgency_score' in queries_df.columns:
            queries_df = queries_df.sort_values('urgency_score', ascending=False)
        
        for _, row in queries_df.iterrows():
            urgency_badge = "🔴 URGENT" if row.get('urgency_score', 0) >= 4 else "🟡 HIGH" if row.get('urgency_score', 0) >= 3 else "🟢 NORMAL"
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                        <div style="background: white; padding: 1rem; border-radius: 10px; 
                                    border-left: 5px solid #667eea; margin-bottom: 1rem;">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>👤 {row['student_name']}</strong>
                                <small>{urgency_badge} | 🕐 {row['date']}</small>
                            </div>
                            <p><strong>📧 Email:</strong> {row['student_email']}</p>
                            <p><strong>🎯 Career:</strong> {row['career_type']}</p>
                            <p><strong>💬 Message:</strong> {row['message']}</p>
                    """, unsafe_allow_html=True)
                    
                    # Show NLP insights
                    if row.get('sentiment'):
                        sentiment_class = get_sentiment_class(row['sentiment'])
                        st.markdown(f"""
                            <div style="background: #f8f9fa; padding: 0.5rem; border-radius: 5px; margin-top: 0.5rem;">
                                <small>🧠 AI Analysis: <span class="badge {sentiment_class}">{row['sentiment'].upper()}</span>
                                | Urgency: {row.get('urgency_score', 1)}/5 
                                | Skills: {row.get('detected_skills', '[]')}</small>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    if row['admin_response']:
                        st.markdown(f"""
                            <div style="background: #e8f4fd; padding: 0.5rem; border-radius: 5px; margin-top: 0.5rem;">
                                <strong>✅ Response:</strong> {row['admin_response']}
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    # AI response suggestion
                    if st.button("🤖 AI Suggest", key=f"ai_suggest_{row['id']}", use_container_width=True):
                        nlp_result = simple_nlp_analysis(row['message'])
                        suggestion = generate_smart_response(row['message'], nlp_result)
                        st.info(f"💡 AI Suggestion: {suggestion}")
                    
                    current_status = row['status']
                    new_status = st.selectbox(
                        "Status",
                        ['pending', 'answered', 'resolved'],
                        index=['pending', 'answered', 'resolved'].index(current_status) if current_status in ['pending', 'answered', 'resolved'] else 0,
                        key=f"status_{row['id']}"
                    )
                    
                    response = st.text_area("Response", value=row['admin_response'] if row['admin_response'] else "", key=f"resp_{row['id']}", height=80)
                    
                    if st.button("📤 Update", key=f"update_{row['id']}", use_container_width=True):
                        if update_query_status(row['id'], new_status, response):
                            st.success("✅ Updated!")
                            st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"del_{row['id']}", use_container_width=True):
                        if delete_query(row['id']):
                            st.success("✅ Deleted!")
                            st.rerun()
                
                st.markdown("---")

def notifications_page():
    load_css()
    st.markdown("<h1>🔔 Notifications</h1>", unsafe_allow_html=True)
    
    notifications = get_unread_notifications(st.session_state.user['id'])
    
    if not notifications:
        st.info("📭 No new notifications")
    else:
        for notif in notifications:
            st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 10px; 
                            margin-bottom: 1rem; border-left: 5px solid #667eea;">
                    <div style="display: flex; justify-content: space-between;">
                        <span>{notif[3]}</span>
                        <small>{notif[6] if len(notif) > 6 else 'Just now'}</small>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        if st.button("Mark all as read", use_container_width=True):
            mark_notifications_read(st.session_state.user['id'])
            st.success("✅ Notifications marked as read")
            st.rerun()

def about_page():
    load_css()
    st.markdown("<h1>ℹ️ About TAG with AI</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="stat-card">
                <h3>🤖 AI-Powered Features</h3>
                <ul>
                    <li>Smart career path detection</li>
                    <li>Sentiment analysis for student queries</li>
                    <li>Urgency scoring system</li>
                    <li>Skill extraction from text</li>
                    <li>AI-generated response suggestions</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stat-card">
                <h3>🎯 Our Mission</h3>
                <p>Using AI to make career guidance accessible, personalized, and efficient for every government school student.</p>
            </div>
        """, unsafe_allow_html=True)

# ==================== MAIN APP ====================
def main():
    init_database()
    init_session()
    
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h1 style="color: white; margin: 0;">🎯 TAG</h1>
                <p style="color: rgba(255,255,255,0.8);">AI-Powered Career Guidance</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        menu_options = ['Home', 'About']
        
        if not st.session_state.logged_in:
            menu_options.extend(['Login', 'Sign Up'])
        else:
            if st.session_state.user['role'] == 'admin':
                menu_options.extend(['Admin', 'Notifications'])
            else:
                menu_options.extend(['Dashboard', 'Notifications'])
        
        page_icons = {'Home': '🏠', 'About': 'ℹ️', 'Login': '🔐', 'Sign Up': '📝', 'Dashboard': '📊', 'Admin': '👑', 'Notifications': '🔔'}
        
        for option in menu_options:
            icon = page_icons.get(option, '📌')
            if st.sidebar.button(f"{icon} {option}", key=f"nav_{option}", use_container_width=True):
                st.session_state.page = option
                st.rerun()
        
        if st.session_state.logged_in:
            st.markdown("---")
            notification_badge()
            
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
                    <p style="color: white; margin: 0;">👤 Logged in as:</p>
                    <p style="color: white; font-weight: bold; margin: 0;">{st.session_state.user['name']}</p>
                    <p style="color: rgba(255,255,255,0.8); font-size: 0.8rem;">{st.session_state.user['role'].title()}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.sidebar.button("🚪 Logout", use_container_width=True):
                logout()
    
    # Page routing
    if st.session_state.page == 'Home':
        home_page()
    elif st.session_state.page == 'About':
        about_page()
    elif st.session_state.page == 'Login':
        if not st.session_state.logged_in:
            login_page()
        else:
            st.session_state.page = 'Dashboard' if st.session_state.user['role'] != 'admin' else 'Admin'
            st.rerun()
    elif st.session_state.page == 'Sign Up':
        if not st.session_state.logged_in:
            signup_page()
        else:
            st.session_state.page = 'Dashboard'
            st.rerun()
    elif st.session_state.page == 'Dashboard':
        if st.session_state.logged_in and st.session_state.user['role'] == 'student':
            student_dashboard()
        else:
            st.warning("Please login as student")
            st.session_state.page = 'Login'
            st.rerun()
    elif st.session_state.page == 'Admin':
        if st.session_state.logged_in and st.session_state.user['role'] == 'admin':
            admin_panel()
        else:
            st.warning("Unauthorized access")
            st.session_state.page = 'Login'
            st.rerun()
    elif st.session_state.page == 'Notifications':
        if st.session_state.logged_in:
            notifications_page()
        else:
            st.session_state.page = 'Login'
            st.rerun()

if __name__ == "__main__":
    main()