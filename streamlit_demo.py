"""
CulturalOS API Demo - Streamlit Testing Interface
Created for judge testing and project viability demonstration
Author: Ugandan Student leveraging unlimited possibilities
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
st.set_page_config(
    page_title="CulturalOS API Demo",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .api-status {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .status-healthy {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    
    .status-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .json-display {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        max-height: 400px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if the API is running and healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"API returned status {response.status_code}"}
    except Exception as e:
        return False, {"error": str(e)}

def make_request(endpoint, method="GET", data=None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return False, {"error": str(e)}

def display_json_response(data, title="API Response"):
    """Display JSON response in a formatted way"""
    st.subheader(title)
    with st.expander("View Raw JSON", expanded=False):
        st.markdown(f'<div class="json-display">{json.dumps(data, indent=2)}</div>', unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🌍 CulturalOS API Demo</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h3>🚀 Judge Testing Interface - Demonstrating Unlimited Possibilities</h3>
        <p><em>Built by a Ugandan student showcasing world-class API development</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🎯 Demo Navigation")
    st.sidebar.markdown("---")
    
    # API Health Check
    st.sidebar.subheader("📊 API Status")
    is_healthy, health_data = check_api_health()
    
    if is_healthy:
        st.sidebar.markdown('<div class="api-status status-healthy">✅ API is Online</div>', unsafe_allow_html=True)
        st.sidebar.json(health_data)
    else:
        st.sidebar.markdown('<div class="api-status status-error">❌ API is Offline</div>', unsafe_allow_html=True)
        st.sidebar.error(f"Error: {health_data.get('error', 'Unknown error')}")
        st.error("⚠️ Please ensure the API server is running at http://localhost:8000")
        st.code("cd backend && python main.py")
        return
    
    # Demo Sections
    demo_sections = [
        "🏠 Overview",
        "👥 User Management", 
        "🧠 Cultural Intelligence",
        "🏢 Enterprise Analytics",
        "🎵 Music Analysis",
        "📊 Performance Metrics",
        "📚 API Documentation"
    ]
    
    selected_section = st.sidebar.selectbox("Choose Demo Section:", demo_sections)
    
    # Main Content
    if selected_section == "🏠 Overview":
        show_overview()
    elif selected_section == "👥 User Management":
        show_user_management()
    elif selected_section == "🧠 Cultural Intelligence":
        show_cultural_intelligence()
    elif selected_section == "🏢 Enterprise Analytics":
        show_enterprise_analytics()
    elif selected_section == "🎵 Music Analysis":
        show_music_analysis()
    elif selected_section == "📊 Performance Metrics":
        show_performance_metrics()
    elif selected_section == "📚 API Documentation":
        show_api_documentation()

def show_overview():
    st.header("🚀 Project Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🤖 AI-Powered</h3>
            <p>Google Gemini Integration</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🌍 Global Ready</h3>
            <p>Enterprise Scalable</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Production Ready</h3>
            <p>Professional API</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("🎯 What This Demo Proves")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 💡 Technical Excellence
        - **FastAPI Backend**: Modern async Python framework
        - **Google Gemini AI**: Real-time AI explanations
        - **PostgreSQL Database**: Enterprise-grade data storage
        - **Docker Ready**: Containerized deployment
        - **Interactive Docs**: Auto-generated API documentation
        """)
    
    with col2:
        st.markdown("""
        ### 🌍 Unlimited Possibilities
        - **Ugandan Innovation**: Built from the Pearl of Africa
        - **Global Standards**: Competing with international APIs  
        - **Cultural Intelligence**: AI that understands diversity
        - **Scalable Architecture**: Ready for millions of users
        - **Professional Quality**: Enterprise-ready solution
        """)
    
    st.markdown("---")
    
    st.subheader("🔧 Live API Testing")
    st.info("👆 Use the sidebar to navigate through different API endpoints and see live responses!")

def show_user_management():
    st.header("👥 User Management System")
    
    st.markdown("""
    This section demonstrates the user management capabilities of our API.
    Real users are stored in the SQLite database and can be created via the API.
    """)
    
    # User creation form
    st.subheader("➕ Create New User")
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_email = st.text_input("Email", placeholder="user@example.com")
            new_username = st.text_input("Username", placeholder="johndoe")
        with col2:
            new_full_name = st.text_input("Full Name", placeholder="John Doe")
            new_password = st.text_input("Password", type="password", placeholder="password123")
        
        if st.form_submit_button("🚀 Create User", type="primary"):
            if new_email and new_username and new_full_name and new_password:
                user_data = {
                    "email": new_email,
                    "username": new_username,
                    "full_name": new_full_name,
                    "password": new_password
                }
                
                with st.spinner("Creating user..."):
                    success, response = make_request("/api/auth/users", method="POST", data=user_data)
                
                if success:
                    st.success(f"✅ User created successfully! ID: {response.get('id')}")
                else:
                    st.error(f"❌ Failed to create user: {response.get('error', 'Unknown error')}")
            else:
                st.error("❌ Please fill in all fields")
    
    st.markdown("---")
    
    if st.button("🔄 Fetch All Users", type="primary"):
        with st.spinner("Fetching users from API..."):
            success, data = make_request("/api/auth/users")
            
        if success:
            st.success("✅ Users retrieved successfully!")
            
            users_list = data.get('users', [])
            if users_list:
                # Display users in cards
                for user in users_list:
                    with st.expander(f"👤 {user['full_name']} ({user['username']})", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("User ID", user['id'])
                            st.metric("Role", user['role'].title())
                        
                        with col2:
                            st.metric("Subscription", user['subscription'].title())
                            st.metric("Created", user['created_at'][:10])
                        
                        with col3:
                            st.metric("Email", user['email'])
                            st.metric("Username", user['username'])
                
                # Display as DataFrame
                st.subheader("📊 Users Table")
                df = pd.DataFrame(users_list)
                st.dataframe(df, use_container_width=True)
                
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Users", data.get('total', 0))
                with col2:
                    premium_users = len([u for u in users_list if u.get('subscription') == 'premium'])
                    st.metric("Premium Users", premium_users)
                with col3:
                    free_users = len([u for u in users_list if u.get('subscription') == 'free'])
                    st.metric("Free Users", free_users)
            else:
                st.info("No users found in the database")
            
            display_json_response(data, "Raw API Response")
        else:
            st.error(f"❌ Failed to fetch users: {data.get('error', 'Unknown error')}")

def show_cultural_intelligence():
    st.header("🧠 Cultural Intelligence Analysis")
    
    st.markdown("""
    **🤖 This is the heart of our AI integration!**  
    Every analysis includes real-time explanations generated by Google Gemini AI.
    """)
    
    # User selection
    users = {
        "1": "Alex Chen (San Francisco) - K-pop, Electronic, Jazz",
        "2": "Maria Rodriguez (Mexico City) - Reggaeton, Latin",
        "3": "Kenji Tanaka (Tokyo) - J-pop, City Pop", 
        "4": "Emma Thompson (London) - Indie, World Music"
    }
    
    selected_user = st.selectbox("Select User for Analysis:", options=list(users.keys()), format_func=lambda x: users[x])
    
    if st.button("🔮 Analyze Cultural Intelligence", type="primary"):
        with st.spinner("🤖 Generating AI-powered cultural analysis..."):
            # Use the actual cultural analysis endpoint
            analysis_data = {
                "include_social_media": True,
                "analysis_depth": "comprehensive"
            }
            success, data = make_request("/api/cultural/analyze", method="POST", data=analysis_data)
        
        if success:
            st.success("✅ Cultural analysis completed with AI explanations!")
            
            # Key Metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                overall_score = data.get('results', {}).get('overall_score', 0.8)
                st.metric("Overall Score", f"{int(overall_score * 100)}/100", delta="High")
            
            with col2:
                cultural_awareness = data.get('results', {}).get('cultural_awareness', 0.75)
                st.metric("Cultural Awareness", f"{int(cultural_awareness * 100)}/100", delta="Good")
            
            with col3:
                global_mindset = data.get('results', {}).get('global_mindset', 0.85)
                st.metric("Global Mindset", f"{int(global_mindset * 100)}/100", delta="Excellent")
            
            st.markdown("---")
            
            # AI-Powered Predictions
            st.subheader("🔮 AI-Powered Trend Predictions")
            for prediction in data['predictions']:
                with st.expander(f"📈 {prediction['nextTrend']} ({prediction['probability']}% confidence)", expanded=True):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**🤖 AI Explanation:**")
                        st.info(prediction['ai_explanation'])
                        st.markdown(f"**📊 Analysis:** {prediction['reasoning']}")
                    
                    with col2:
                        st.metric("Probability", f"{prediction['probability']}%")
                        st.metric("Timeframe", prediction['timeframe'])
                        st.metric("Category", prediction['category'].title())
            
            # Cultural Insights with AI
            st.subheader("💡 Cultural Insights (AI-Enhanced)")
            for insight in data['insights']:
                with st.expander(f"🧠 {insight['category']}", expanded=True):
                    st.markdown(f"**Finding:** {insight['finding']}")
                    st.markdown(f"**🤖 AI Explanation:**")
                    st.success(insight['ai_explanation'])
                    st.progress(insight['confidence'] / 100)
                    st.caption(f"Confidence: {insight['confidence']}%")
            
            # Recommendations with AI
            st.subheader("🎯 AI-Powered Recommendations")
            for rec in data['recommendations']:
                with st.expander(f"✨ {rec['title']}", expanded=True):
                    st.markdown(f"**Description:** {rec['description']}")
                    st.markdown(f"**🤖 AI Explanation:**")
                    st.info(rec['ai_explanation'])
                    
                    if 'examples' in rec:
                        st.markdown("**Examples:**")
                        for example in rec['examples']:
                            st.markdown(f"- {example}")
                    
                    st.metric("Cultural Impact", f"{rec['cultural_impact']}%")
            
            display_json_response(data, "Complete Cultural Analysis Response")
        else:
            st.error(f"❌ Analysis failed: {data.get('error', 'Unknown error')}")

def show_enterprise_analytics():
    st.header("🏢 Enterprise Analytics Dashboard")
    
    st.markdown("""
    Demonstrating enterprise-grade analytics capabilities for organizations managing diverse teams.
    """)
    
    if st.button("📊 Load Team Analytics", type="primary"):
        with st.spinner("Loading enterprise analytics..."):
            success, data = make_request("/api/enterprise/dashboard")
        
        if success:
            st.success("✅ Enterprise analytics loaded successfully!")
            
            # Organization Summary
            summary = data.get('organization_overview', {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Employees", summary.get('total_employees', 0))
            
            with col2:
                st.metric("Global Offices", summary.get('global_offices', 0))
            
            with col3:
                diversity_index = summary.get('cultural_diversity_index', 0.8)
                st.metric("Diversity Index", f"{int(diversity_index * 100)}/100")
            
            with col4:
                cross_teams = summary.get('cross_cultural_teams', 0)
                st.metric("Cross-Cultural Teams", cross_teams)
            
            st.markdown("---")
            
            # Performance Metrics Visualization
            st.subheader("📈 Performance Metrics")
            
            # Use performance metrics from the actual API response
            metrics = data.get('performance_metrics', {})
            
            # Create a DataFrame for visualization
            metrics_data = {
                'Metric': ['Cultural Competency', 'Team Collaboration', 'Employee Satisfaction', 'Retention Rate'],
                'Score': [
                    metrics.get('cultural_competency_score', 0.8) * 100,
                    metrics.get('team_collaboration_score', 0.85) * 100,
                    metrics.get('employee_satisfaction', 0.75) * 100,
                    metrics.get('retention_rate', 0.9) * 100
                ]
            }
            teams_df = pd.DataFrame(metrics_data)
            
            # Cultural Score Chart
            fig_scores = px.bar(
                teams_df, 
                x='team_name', 
                y='cultural_score',
                title="Cultural Scores by Team",
                color='cultural_score',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig_scores, use_container_width=True)
            
            # Diversity vs Cultural Score Scatter
            fig_scatter = px.scatter(
                teams_df,
                x='diversity_index',
                y='cultural_score', 
                size='members_count',
                color='team_name',
                title="Diversity Index vs Cultural Score",
                hover_data=['engagement_rate']
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Team Details
            st.subheader("👥 Team Details")
            for team in data['team_performance']:
                with st.expander(f"🏗️ {team['team_name']} ({team['members_count']} members)", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Cultural Score", f"{team['cultural_score']}/100")
                        st.metric("Diversity Index", f"{team['diversity_index']}/100")
                    
                    with col2:
                        st.metric("Monthly Growth", f"{team['monthly_growth']:.1f}%")
                        st.metric("Engagement Rate", f"{team['engagement_rate']:.1%}")
                    
                    with col3:
                        st.metric("Active Campaigns", team['active_campaigns'])
                        st.metric("Cross-Cultural Projects", team['cross_cultural_projects'])
                    
                    st.markdown("**Top Cultural Insights:**")
                    for insight in team['top_cultural_insights']:
                        st.markdown(f"- {insight}")
            
            # Cultural Trends
            st.subheader("📊 Cultural Trends Adoption")
            trends_df = pd.DataFrame(data['cultural_trends'])
            
            fig_trends = px.bar(
                trends_df,
                x='trend',
                y='adoption_rate',
                title="Cultural Trends Adoption Rates",
                color='impact_score',
                color_continuous_scale='plasma'
            )
            st.plotly_chart(fig_trends, use_container_width=True)
            
            display_json_response(data, "Enterprise Analytics Response")
        else:
            st.error(f"❌ Failed to load analytics: {data.get('error', 'Unknown error')}")

def show_music_analysis():
    st.header("🎵 Music Listening Analysis")
    
    st.markdown("""
    Analyze user music patterns to generate cultural insights and personalized recommendations.
    """)
    
    # User selection
    users = {
        "1": "Alex Chen - K-pop & Electronic",
        "2": "Maria Rodriguez - Reggaeton & Latin", 
        "3": "Kenji Tanaka - J-pop & City Pop",
        "4": "Emma Thompson - Indie & World Music"
    }
    
    selected_user = st.selectbox("Select User:", options=list(users.keys()), format_func=lambda x: users[x])
    days = st.slider("Analysis Period (days):", min_value=7, max_value=90, value=30)
    
    if st.button("🎧 Analyze Music History", type="primary"):
        with st.spinner("Analyzing music listening patterns..."):
            # Use the actual music analysis endpoint
            music_data = {
                "track_name": "Blinding Lights",
                "artist": "The Weeknd", 
                "genre": "Pop"
            }
            success, data = make_request("/api/cultural/music-analysis", method="POST", data=music_data)
        
        if success:
            st.success("✅ Music analysis completed!")
            
            # Key Metrics
            col1, col2, col3 = st.columns(3)
            
            track_info = data.get('track_info', {})
            
            with col1:
                cultural_impact = data.get('cultural_impact_score', 0.7)
                st.metric("Cultural Impact", f"{int(cultural_impact * 100)}/100")
            
            with col2:
                cross_appeal = data.get('cross_cultural_appeal', 0.8)
                st.metric("Cross-Cultural Appeal", f"{int(cross_appeal * 100)}/100")
            
            with col3:
                st.metric("Track Analyzed", track_info.get('name', 'N/A'))
            
            # Genre Distribution
            st.subheader("🎼 Genre Distribution")
            genres = {}
            for song in data['listening_history'][:100]:  # Analyze first 100 songs
                genre = song['genre']
                genres[genre] = genres.get(genre, 0) + 1
            
            if genres:
                genre_df = pd.DataFrame(list(genres.items()), columns=['Genre', 'Count'])
                fig_pie = px.pie(genre_df, values='Count', names='Genre', title="Music Genres Distribution")
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Recent Listening History
            st.subheader("🎵 Recent Tracks")
            tracks_df = pd.DataFrame(data['listening_history'][:20])  # Show last 20 tracks
            
            if not tracks_df.empty:
                st.dataframe(
                    tracks_df[['title', 'artist', 'album', 'genre', 'duration_ms']],
                    use_container_width=True
                )
            
            # Analysis Summary
            st.subheader("📊 Cultural Analysis Summary")
            summary = data['analysis_summary']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Top Genres:**")
                for genre in summary['top_genres']:
                    st.markdown(f"- {genre}")
            
            with col2:
                st.markdown("**Cultural Indicators:**")
                for indicator in summary['cultural_indicators']:
                    st.markdown(f"- {indicator}")
            
            display_json_response(data, "Music Analysis Response")
        else:
            st.error(f"❌ Analysis failed: {data.get('error', 'Unknown error')}")

def show_performance_metrics():
    st.header("📊 API Performance Metrics")
    
    st.markdown("""
    Real-time performance testing of API endpoints to demonstrate system reliability.
    """)
    
    if st.button("🚀 Run Performance Tests", type="primary"):
        st.subheader("⏱️ Response Time Testing")
        
        endpoints_to_test = [
            ("/health", "Health Check"),
            ("/api/auth/users", "User Management"),
            ("/api/cultural/profile", "Cultural Intelligence Profile"),
            ("/api/enterprise/dashboard", "Enterprise Analytics"),
            ("/api/analytics/overview", "Analytics Overview")
        ]
        
        results = []
        
        for endpoint, name in endpoints_to_test:
            with st.spinner(f"Testing {name}..."):
                start_time = time.time()
                success, data = make_request(endpoint)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                results.append({
                    "Endpoint": name,
                    "Status": "✅ Success" if success else "❌ Failed",
                    "Response Time (ms)": f"{response_time:.2f}",
                    "Data Size": len(str(data)) if success else 0
                })
                
                # Display real-time results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(f"{name} Status", "✅ OK" if success else "❌ ERROR")
                with col2:
                    st.metric("Response Time", f"{response_time:.2f}ms")
                with col3:
                    st.metric("Data Size", f"{len(str(data))} chars" if success else "0")
        
        # Results Summary
        st.subheader("📈 Performance Summary")
        results_df = pd.DataFrame(results)
        st.dataframe(results_df, use_container_width=True)
        
        # Response Time Chart
        success_results = [r for r in results if "Success" in r["Status"]]
        if success_results:
            chart_df = pd.DataFrame(success_results)
            chart_df["Response Time (ms)"] = pd.to_numeric(chart_df["Response Time (ms)"])
            
            fig = px.bar(
                chart_df,
                x="Endpoint",
                y="Response Time (ms)",
                title="API Response Times",
                color="Response Time (ms)",
                color_continuous_scale="viridis"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance Analysis
        st.subheader("🎯 Performance Analysis")
        avg_response_time = sum(float(r["Response Time (ms)"]) for r in success_results) / len(success_results) if success_results else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average Response Time", f"{avg_response_time:.2f}ms")
        
        with col2:
            success_rate = len(success_results) / len(results) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        with col3:
            total_endpoints = len(results)
            st.metric("Endpoints Tested", total_endpoints)

def show_api_documentation():
    st.header("📚 API Documentation")
    
    st.markdown("""
    Interactive API documentation and testing interface.
    """)
    
    st.subheader("🔗 Documentation Links")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📖 Interactive Docs
        **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
        
        Features:
        - Try out all endpoints interactively
        - View request/response schemas
        - Authentication testing
        - Real-time API exploration
        """)
    
    with col2:
        st.markdown("""
        ### 📋 Alternative Docs  
        **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
        
        Features:
        - Clean, readable documentation
        - Detailed schema descriptions
        - Code examples
        - Comprehensive API reference
        """)
    
    st.markdown("---")
    
    st.subheader("🎯 Key API Endpoints")
    
    endpoints_info = [
        {
            "Method": "GET",
            "Endpoint": "/health",
            "Description": "System health check",
            "AI Integration": "No"
        },
        {
            "Method": "GET", 
            "Endpoint": "/api/auth/users",
            "Description": "Retrieve all users from database",
            "AI Integration": "No"
        },
        {
            "Method": "POST",
            "Endpoint": "/api/cultural/analyze",
            "Description": "Complete cultural intelligence analysis", 
            "AI Integration": "✅ Gemini AI"
        },
        {
            "Method": "GET",
            "Endpoint": "/api/cultural/profile",
            "Description": "Get cultural intelligence profile",
            "AI Integration": "✅ Gemini AI"
        },
        {
            "Method": "GET",
            "Endpoint": "/api/enterprise/dashboard", 
            "Description": "Enterprise dashboard overview",
            "AI Integration": "✅ Gemini AI"
        },
        {
            "Method": "POST",
            "Endpoint": "/api/cultural/music-analysis",
            "Description": "Music listening analysis",
            "AI Integration": "No"
        }
    ]
    
    endpoints_df = pd.DataFrame(endpoints_info)
    st.dataframe(endpoints_df, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("🤖 AI Integration Highlights")
    
    st.success("""
    **Google Gemini AI Powers:**
    - Cultural trend predictions with personalized explanations
    - Music recommendation reasoning
    - Cultural insight analysis
    - Personalized todo generation with cultural context
    
    **Every AI response is unique and tailored to the user's cultural profile!**
    """)
    
    st.info("""
    **For Judges:** 
    1. Visit http://localhost:8000/docs for interactive testing
    2. Try the cultural analysis endpoints to see real AI responses
    3. Each API call to AI-powered endpoints generates unique explanations
    4. All responses include both structured data and human-readable AI insights
    """)

if __name__ == "__main__":
    main()