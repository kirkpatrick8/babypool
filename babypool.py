import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import random
import time
from datetime import datetime
from github import Github
from github import GithubException
import json
import io

# Page config
st.set_page_config(page_title="Belfast 12 Pubs of Christmas", page_icon="🍺", layout="wide")

# Custom CSS for modal and styling
st.markdown("""
    <style>
    .modal {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
        z-index: 1000;
    }
    .overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 999;
    }
    .stProgress .st-bo { background-color: #ff4b4b; }
    .stProgress .st-bp { background-color: #28a745; }
    .achievement {
        padding: 10px;
        margin: 5px;
        border-radius: 5px;
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# GitHub configuration
GITHUB_TOKEN = st.secrets["github"]["GITHUB_TOKEN"]
REPO_NAME = st.secrets["github"]["REPO_NAME"]
BRANCH_NAME = "main"
DATA_FILE = "pub_crawl_data.json"

# Initialize GitHub client
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# Constants
PUBS_DATA = {
    'name': [
        "Lavery's", "The Points", "Sweet Afton", "Kelly's Cellars",
        "Whites Tavern", "The Deer's Head", "The John Hewitt", "Duke of York",
        "The Harp Bar", "The Dirty Onion", "Thirsty Goat", "Ulster Sports Club"
    ],
    'latitude': [
        54.589539, 54.591556, 54.595067, 54.599553, 54.600033, 54.601439,
        54.601928, 54.601803, 54.602000, 54.601556, 54.601308, 54.600733
    ],
    'longitude': [
        -5.934469, -5.933333, -5.932894, -5.932236, -5.928497, -5.930294,
        -5.928617, -5.927442, -5.927058, -5.926673, -5.926417, -5.925219
    ],
    'rules': [
        "Christmas Jumpers Required", "Last Names Only", "No Swearing Challenge",
        "Power Hour (Down Drink in 2-3 Gulps)", "No Phones & Drink with Left Hand Only",
        "Must Speak in Different Accents", "Different Drink Type Required",
        "Must Bow Before Taking a Drink", "Double Parked",
        "The Arm Pub - Drink from Someone Else's Arm",
        "No First Names & Photo Challenge", "Buddy System - Final Challenge"
    ]
}

PUNISHMENTS = [
    "Buy Mark a Drink", "Irish dance for 30 seconds", "Tell an embarrassing story",
    "Down your drink", "Add a shot to your next drink", "Sing a Christmas carol",
    "Switch drinks with someone", "No phone for next 2 pubs", 
    "Wear your jumper inside out", "Give someone your drink",
    "Talk in an accent for 10 mins", "Do 10 jumping jacks"
]

ACHIEVEMENTS = {
    'first_pub': {'name': 'First Timer', 'desc': 'Complete your first pub', 'points': 100},
    'halfway': {'name': 'Halfway Hero', 'desc': 'Complete 6 pubs', 'points': 250},
    'finisher': {'name': 'Challenge Champion', 'desc': 'Complete all 12 pubs', 'points': 500},
    'rule_breaker': {'name': 'Rule Breaker', 'desc': 'Get punished 3 times', 'points': 150},
    'speed_demon': {'name': 'Speed Demon', 'desc': 'Complete 3 pubs in under 90 minutes', 'points': 300},
}

# Data management functions
@st.cache_data(ttl=60)
def load_data():
    """Load data from GitHub"""
    try:
        content = repo.get_contents(DATA_FILE, ref=BRANCH_NAME)
        return json.loads(content.decoded_content.decode())
    except Exception as e:
        st.sidebar.error(f"Error loading data: {e}")
        return {'participants': {}, 'punishments': [], 'achievements': {}}

def save_data(data):
    """Save data to GitHub"""
    try:
        content = repo.get_contents(DATA_FILE, ref=BRANCH_NAME)
        repo.update_file(
            DATA_FILE,
            f"Update data - {datetime.now()}",
            json.dumps(data, indent=2),
            content.sha,
            branch=BRANCH_NAME
        )
    except GithubException as e:
        if e.status == 404:
            repo.create_file(
                DATA_FILE,
                f"Create data file - {datetime.now()}",
                json.dumps(data, indent=2),
                branch=BRANCH_NAME
            )
        else:
            raise e

# Initialize or load session state
if 'data' not in st.session_state:
    st.session_state.data = load_data()

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

def name_entry_modal():
    """Display modal for name entry"""
    if st.session_state.current_user is None:
        st.markdown("""
            <div class="overlay"></div>
            <div class="modal">
                <h2>Welcome to the Belfast 12 Pubs of Christmas! 🎄</h2>
                <p>Enter your name to begin the challenge:</p>
            </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("Your Name", key="name_input")
        if name:
            if name not in st.session_state.data['participants']:
                st.session_state.data['participants'][name] = {
                    'start_time': datetime.now().isoformat(),
                    'current_pub': 0,
                    'completed_pubs': [],
                    'points': 0,
                    'rule_breaks': 0,
                    'achievements': []
                }
                save_data(st.session_state.data)
            st.session_state.current_user = name
            st.rerun()

def check_achievements(name):
    """Check and award achievements"""
    participant = st.session_state.data['participants'][name]
    achievements = participant.get('achievements', [])
    pubs_completed = len(participant['completed_pubs'])
    
    # First pub completion
    if pubs_completed == 1 and 'first_pub' not in achievements:
        award_achievement(name, 'first_pub')
        
    # Halfway achievement
    if pubs_completed >= 6 and 'halfway' not in achievements:
        award_achievement(name, 'halfway')
        
    # Completion achievement
    if pubs_completed == 12 and 'finisher' not in achievements:
        award_achievement(name, 'finisher')
        
    # Rule breaker achievement
    if participant['rule_breaks'] >= 3 and 'rule_breaker' not in achievements:
        award_achievement(name, 'rule_breaker')

def award_achievement(name, achievement_id):
    """Award an achievement to a participant"""
    achievement = ACHIEVEMENTS[achievement_id]
    participant = st.session_state.data['participants'][name]
    
    if 'achievements' not in participant:
        participant['achievements'] = []
        
    participant['achievements'].append(achievement_id)
    participant['points'] += achievement['points']
    
    save_data(st.session_state.data)
    
    st.balloons()
    st.success(f"🏆 Achievement Unlocked: {achievement['name']}! (+{achievement['points']} points)")

def show_achievements(name):
    """Display achievements for a participant"""
    participant = st.session_state.data['participants'][name]
    achievements = participant.get('achievements', [])
    
    st.subheader("🏆 Your Achievements")
    
    if achievements:
        for ach_id in achievements:
            ach = ACHIEVEMENTS[ach_id]
            st.markdown(f"""
                <div class="achievement">
                    <h3>{ach['name']}</h3>
                    <p>{ach['desc']}</p>
                    <small>+{ach['points']} points</small>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Complete challenges to earn achievements!")

def show_progress(name):
    """Show progress for current participant"""
    participant = st.session_state.data['participants'][name]
    
    st.header(f"Progress Tracker for {name}")
    
    # Progress bar and stats
    progress = len(participant['completed_pubs'])
    st.progress(progress/12)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pubs Completed", f"{progress}/12")
    with col2:
        st.metric("Points", participant['points'])
    with col3:
        st.metric("Rule Breaks", participant['rule_breaks'])
    
    if participant['current_pub'] < 12:
        current_pub = PUBS_DATA['name'][participant['current_pub']]
        current_rule = PUBS_DATA['rules'][participant['current_pub']]
        
        st.subheader(f"Current Pub: {current_pub}")
        st.info(f"Rule: {current_rule}")
        
        if st.button("Mark Current Pub as Complete", type="primary"):
            participant['completed_pubs'].append(current_pub)
            participant['current_pub'] += 1
            participant['points'] += 100
            save_data(st.session_state.data)
            check_achievements(name)
            st.rerun()
    else:
        st.success("🎉 Congratulations! You've completed the Belfast 12 Pubs of Christmas! 🎉")

def show_map():
    """Display interactive map"""
    st.header("Pub Route Map")
    
    m = folium.Map(
        location=[54.595733, -5.930294],
        zoom_start=15,
        tiles='CartoDB positron'
    )
    
    # Add markers and route
    for i, (name, lat, lon) in enumerate(zip(
        PUBS_DATA['name'],
        PUBS_DATA['latitude'],
        PUBS_DATA['longitude']
    )):
        # Determine marker color based on completion
        color = 'green' if name in st.session_state.data['participants'][st.session_state.current_user]['completed_pubs'] else 'red'
        
        popup_text = f"""
            <b>{i+1}. {name}</b><br>
            Rule: {PUBS_DATA['rules'][i]}
        """
        
        folium.Marker(
            [lat, lon],
            popup=popup_text,
            icon=folium.Icon(color=color)
        ).add_to(m)
        
        # Connect pubs with lines
        if i > 0:
            points = [
                [PUBS_DATA['latitude'][i-1], PUBS_DATA['longitude'][i-1]],
                [lat, lon]
            ]
            folium.PolyLine(
                points,
                weight=2,
                color='blue',
                opacity=0.8
            ).add_to(m)
    
    st_folium(m)

def add_punishment(name):
    """Record a punishment"""
    current_pub = PUBS_DATA['name'][st.session_state.data['participants'][name]['current_pub']]
    punishment = random.choice(PUNISHMENTS)
    
    st.session_state.data['punishments'].append({
        'time': datetime.now().isoformat(),
        'name': name,
        'pub': current_pub,
        'punishment': punishment
    })
    
    st.session_state.data['participants'][name]['rule_breaks'] += 1
    save_data(st.session_state.data)
    check_achievements(name)
    
    return punishment

def show_punishment_wheel():
    """Display punishment wheel"""
    st.header("Rule Breaker's Wheel of Punishment")
    
    if st.button("Spin the Wheel", type="primary"):
        with st.spinner("Spinning the wheel..."):
            time.sleep(1.5)
        punishment = add_punishment(st.session_state.current_user)
        st.snow()
        st.success(f"Your punishment is: {punishment}")

def show_leaderboard():
    """Display leaderboard"""
    st.header("🏆 Leaderboard")
    
    data = []
    for name, stats in st.session_state.data['participants'].items():
        data.append({
            'Name': name,
            'Pubs Completed': len(stats['completed_pubs']),
            'Points': stats['points'],
            'Achievements': len(stats.get('achievements', [])),
            'Rule Breaks': stats['rule_breaks']
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values(['Points', 'Pubs Completed'], ascending=[False, False])
    st.dataframe(df, use_container_width=True)

def main():
    st.title("🎄 Belfast 12 Pubs of Christmas 🍺")
    
    # Show name entry modal if no user selected
    name_entry_modal()
    
    if st.session_state.current_user:
        tabs = st.tabs([
            "📊 My Progress",
            "🏆 Achievements",
            "🗺️ Map",
            "👥 Leaderboard",
            "🎯 Punishment Wheel"
        ])
        
        with tabs[0]:
            show_progress(st.session_state.current_user)
        
        with tabs[1]:
            show_achievements(st.session_state.current_user)
        
        with tabs[2]:
            show_map()
        
        with tabs[3]:
            show_leaderboard()
        
        with tabs[4]:
            show_punishment_wheel()
        
        # Refresh button in sidebar
        if st.sidebar.button("Refresh Data"):
            st.cache_data.clear()
            st.session_state.data = load_data()
            st.rerun()

if __name__ == "__main__":
    main()
