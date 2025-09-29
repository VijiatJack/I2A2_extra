import streamlit as st
from agents.coordinator import CoordinatorAgent
import os
from dotenv import load_dotenv
from languages import LANGUAGES, DEFAULT_LANGUAGE

# Import new services and utilities
from config.settings import get_app_settings
from services.data_service import DataService
from services.chart_service import ChartService
from services.file_service import FileService
from utils.validation import is_data_analysis_question

# Load environment variables
load_dotenv()



# Check if API key is set
if not os.getenv("GEMINI_API_KEY"):
    st.error("Please set your GEMINI_API_KEY in a .env file")
    st.stop()

# Set page configuration
st.set_page_config(
    page_title="DataVision AI",  # Keep simple since language isn't determined yet
     page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling and sidebar toggle
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #06b6d4;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --card-shadow: 0 10px 25px rgba(0,0,0,0.1);
        --border-radius: 12px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Custom header styling */
    .custom-header {
        background: var(--background-gradient);
        padding: 2rem;
        border-radius: var(--border-radius);
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: var(--card-shadow);
    }
    
    .custom-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .custom-header p {
        margin: 1rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Card styling */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--card-shadow);
        margin-bottom: 1.5rem;
        border: 1px solid #e5e7eb;
    }
    
    /* File uploader styling */
    .stFileUploader > div > div {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 2px dashed var(--primary-color);
        border-radius: var(--border-radius);
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > div:hover {
        border-color: var(--secondary-color);
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        background: var(--secondary-color);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8fafc;
        padding: 0.5rem;
        border-radius: var(--border-radius);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary-color);
        color: white;
        border-color: var(--primary-color);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: var(--border-radius);
        border: 2px solid #e5e7eb;
        transition: border-color 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    /* Text input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: var(--border-radius);
        border: 2px solid #e5e7eb;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid var(--success-color);
        border-radius: var(--border-radius);
    }
    
    .stError {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid var(--error-color);
        border-radius: var(--border-radius);
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid var(--warning-color);
        border-radius: var(--border-radius);
    }
    
    .stInfo {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border: 1px solid var(--accent-color);
        border-radius: var(--border-radius);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Updated sidebar selectors for current Streamlit version */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: var(--border-radius);
        overflow: hidden;
        box-shadow: var(--card-shadow);
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: var(--primary-color) !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: var(--primary-color);
        border-radius: var(--border-radius);
    }
    
    /* Metric styling */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--card-shadow);
        text-align: center;
        border: 1px solid #e5e7eb;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* Animation for loading states */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading-pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        /* Dark mode color variables */
        :root {
            --primary-color: #818cf8;
            --secondary-color: #a78bfa;
            --accent-color: #22d3ee;
            --success-color: #34d399;
            --warning-color: #fbbf24;
            --error-color: #f87171;
            --background-gradient: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            --card-shadow: 0 10px 25px rgba(0,0,0,0.3);
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #334155;
            --border-color: #475569;
        }
        
        /* Main app background */
        .stApp {
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
        }
        
        /* Sidebar dark mode */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e293b 0%, #334155 100%) !important;
            color: var(--text-primary) !important;
        }
        
        section[data-testid="stSidebar"] * {
            color: var(--text-primary) !important;
        }
        
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] .stCheckbox label,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] div {
            color: var(--text-primary) !important;
        }
        
        /* Custom header dark mode */
        .custom-header {
            background: var(--background-gradient);
            color: var(--text-primary);
        }
        
        /* Card styling dark mode */
        .custom-card {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        .custom-card h3,
        .custom-card h4,
        .custom-card p,
        .custom-card div {
            color: var(--text-primary) !important;
        }
        
        /* AI Analysis response dark mode */
        div[style*="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)"] {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
            border-left: 4px solid var(--accent-color) !important;
            color: var(--text-primary) !important;
        }
        
        div[style*="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)"] {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
            border-left: 4px solid var(--success-color) !important;
            color: var(--text-primary) !important;
        }
        
        div[style*="background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%)"] {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
            border-left: 4px solid var(--warning-color) !important;
            color: var(--text-primary) !important;
        }
        
        /* Chart Generation Options headers dark mode */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--bg-secondary) !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--primary-color) !important;
            color: white !important;
        }
        
        /* Metric containers dark mode */
        .metric-container {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        .metric-label {
            color: var(--text-secondary) !important;
        }
        
        /* File uploader dark mode */
        .stFileUploader > div > div {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%) !important;
            border: 2px dashed var(--primary-color) !important;
            color: var(--text-primary) !important;
        }
        
        /* Input fields dark mode */
        .stSelectbox > div > div,
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: var(--bg-card) !important;
            border: 2px solid var(--border-color) !important;
            color: var(--text-primary) !important;
        }
        
        /* Welcome section dark mode */
        div[style*="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)"] {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%) !important;
            color: var(--text-primary) !important;
        }
        
        div[style*="background: white; padding: 1.5rem; border-radius: 8px"] {
            background: var(--bg-card) !important;
            color: var(--text-primary) !important;
        }
        
        /* General text color fixes */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: var(--text-primary) !important;
        }
        
        .stApp p, .stApp div, .stApp span {
            color: var(--text-primary) !important;
        }
        
        /* Dataframe dark mode */
        .stDataFrame {
            background: var(--bg-card) !important;
        }
        
        .stDataFrame table {
            background: var(--bg-card) !important;
            color: var(--text-primary) !important;
        }
        
        .stDataFrame th {
            background: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
        }
        
        .stDataFrame td {
            background: var(--bg-card) !important;
            color: var(--text-primary) !important;
        }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .custom-header h1 {
            font-size: 2rem;
        }
        
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
</style>



""", unsafe_allow_html=True)

# Initialize services
data_service = DataService()
chart_service = ChartService()
file_service = FileService()

# Initialize the coordinator agent
coordinator = CoordinatorAgent()

# Initialize session state first
if 'language' not in st.session_state:
    st.session_state.language = DEFAULT_LANGUAGE

# Get current language dictionary early
lang = LANGUAGES[st.session_state.language]

# Continue with other session state initialization
if 'data' not in st.session_state:
    st.session_state.data = None
if 'file_processed' not in st.session_state:
    st.session_state.file_processed = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'suggested_charts' not in st.session_state:
    st.session_state.suggested_charts = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'current_file_name' not in st.session_state:
    st.session_state.current_file_name = None
if 'generated_chart_path' not in st.session_state:
    st.session_state.generated_chart_path = None

# Create a sidebar for settings
with st.sidebar:
    # Language selector
    selected_language = st.selectbox(
        "🌐 Language / Idioma",
        options=["Português (Brasil)", "English (US)"],
        index=0 if st.session_state.language == "pt_BR" else 1
    )
    
    # Handle language changes - reset chart suggestions when language changes
    if selected_language == "Português (Brasil)" and st.session_state.language != "pt_BR":
        st.session_state.language = "pt_BR"
        st.session_state.suggested_charts = None  # Reset charts for new language
        st.rerun()  # Rerun to update lang variable
    elif selected_language == "English (US)" and st.session_state.language != "en_US":
        st.session_state.language = "en_US"
        st.session_state.suggested_charts = None  # Reset charts for new language
        st.rerun()  # Rerun to update lang variable

    # Update lang variable after potential language change
    lang = LANGUAGES[st.session_state.language]

    # Add settings header and help section
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; margin-bottom: 1rem;">
        <h2 style="color: #6366f1; margin: 0;">{lang['settings_title']}</h2>
        <p style="color: #6b7280; font-size: 0.9rem; margin: 0.5rem 0 0 0;">{lang['settings_subtitle']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Update language selector help text
    st.markdown(f"<small>{lang['language_help']}</small>", unsafe_allow_html=True)
    
    # Add help section in sidebar
    st.markdown("---")
    st.markdown(f"### {lang['help_section_title']}")
    st.markdown(f"""
    {lang['help_step_1']}
    
    {lang['help_step_2']}
    
    {lang['help_step_3']}
    
    {lang['help_step_4']}
    """)
    st.markdown("---")



# App title and description with custom styling
st.markdown(f"""
<div class="custom-header">
    <h1>{lang["app_title"]}</h1>
    <p>{lang["app_description"].replace('**DataVision AI**', 'DataVision AI').strip()}</p>
</div>
""", unsafe_allow_html=True)

# File uploader with enhanced styling
st.markdown(f"""
<div class="custom-card">
    <h3 style="color: #374151; margin-bottom: 1rem; display: flex; align-items: center;">
        {lang['upload_data_title']}
        <span style="margin-left: 0.5rem; font-size: 0.8rem; color: #6b7280; font-weight: normal;">
            {lang['upload_data_subtitle']}
        </span>
    </h3>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    lang["file_uploader"], 
    type=["csv"],
    help=lang['upload_help']
)

if uploaded_file is not None:
    # Only process the file if it hasn't been processed yet or if it's a new file
    file_needs_processing = False
    
    if not st.session_state.file_processed:
        file_needs_processing = True
    elif uploaded_file.name != st.session_state.get('current_file_name', ''):
        file_needs_processing = True
        
    if file_needs_processing:
        # Display file details in a styled card
        st.markdown(f"""
        <div class="custom-card">
            <h4 style="color: #374151; margin-bottom: 1rem; display: flex; align-items: center;">
                📋 {lang['file_info_title']}
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        file_details = {
            lang["filename"]: uploaded_file.name, 
            lang["filetype"]: uploaded_file.type, 
            lang["filesize"]: f"{uploaded_file.size / 1024:.2f} KB"
        }
        
        # Create columns for file details
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">📄</div>
                <div class="metric-label">{lang["filename"]}</div>
                <div style="font-weight: 600; color: #374151; margin-top: 0.5rem;">{uploaded_file.name}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">🗂️</div>
                <div class="metric-label">{lang["filetype"]}</div>
                <div style="font-weight: 600; color: #374151; margin-top: 0.5rem;">{uploaded_file.type}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">📏</div>
                <div class="metric-label">{lang["filesize"]}</div>
                <div style="font-weight: 600; color: #374151; margin-top: 0.5rem;">{uploaded_file.size / 1024:.2f} KB</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Process the file with a loading spinner
        with st.spinner(lang["processing"]):
            data_preview = file_service.process_uploaded_file(uploaded_file)
        
        # Check if data_preview is a string (error message)
        if isinstance(data_preview, str):
            st.error(data_preview)
            st.info(lang["error_invalid_file"])
            st.session_state.file_processed = False
            st.session_state.data = None
        else:
            st.success(lang["success_message"])
            
            # Store the processed data in session state
            st.session_state.data = data_preview
            st.session_state.file_processed = True
            st.session_state.current_file_name = uploaded_file.name
            
            # Reset chart suggestions for new file
            st.session_state.suggested_charts = None
            
            # Reset conversation history for new file
            st.session_state.conversation_history = []
            
            # Generate AI-powered initial analysis using Insight Agent
            with st.spinner("🧠 " + lang.get("generating_analysis", "Generating initial analysis...")):
                from agents.insight_agent import InsightAgent
                insight_agent = InsightAgent()
                ai_analysis = insight_agent.process(data_preview, operation='initial_analysis', language=st.session_state.language)
                st.session_state.analysis_results = {'ai_insights': ai_analysis}
    
    # If file is processed successfully, display analysis and allow queries
    if st.session_state.file_processed and st.session_state.data is not None:
        # Data preview section
        st.markdown(f"""
        <div class="custom-card">
            <h3 style="color: #374151; margin-bottom: 1rem; display: flex; align-items: center;">
                {lang['data_preview_title']}
                <span style="margin-left: 0.5rem; font-size: 0.8rem; color: #6b7280; font-weight: normal;">
                    {lang['data_preview_subtitle']}
                </span>
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(st.session_state.data.head(), use_container_width=True)
        
        # Analysis results section
        if st.session_state.analysis_results:
            st.markdown(f"""
            <div class="custom-card">
                <h3 style="color: #374151; margin-bottom: 1rem; display: flex; align-items: center;">
                    {lang['ai_analysis_title']}
                    <span style="margin-left: 0.5rem; font-size: 0.8rem; color: #6b7280; font-weight: normal;">
                        {lang['ai_analysis_subtitle']}
                    </span>
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            ai_insights = st.session_state.analysis_results.get('ai_insights', '')
            if ai_insights:
                st.markdown(f"""
                <div style="background: var(--background-gradient); 
                           padding: 1.5rem; border-radius: 12px; border-left: 4px solid #06b6d4; 
                           margin-bottom: 1rem;">
                    {ai_insights}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info(lang['info_box_message'])
        
        # Visualization section
        st.markdown(f"""
        <div class="custom-card">
            <h3 style="color: #374151; margin-bottom: 1rem; display: flex; align-items: center;">
                {lang['visualization_title']}
                <span style="margin-left: 0.5rem; font-size: 0.8rem; color: #6b7280; font-weight: normal;">
                    {lang['visualization_subtitle']}
                </span>
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Chart generation options
        st.write(lang.get("chart_generation_options", "Chart Generation Options"))
        
        # Get AI-suggested charts (cache in session state to avoid re-fetching)
        if 'suggested_charts' not in st.session_state or st.session_state.suggested_charts is None:
            with st.spinner("🤖 " + lang.get("analyzing_data", "Analyzing data for chart suggestions...")):
                st.session_state.suggested_charts = chart_service.get_ai_suggested_charts(st.session_state.data, st.session_state.language)
        
        suggested_charts = st.session_state.suggested_charts
        
        # Create tabs for different chart generation methods
        tab1, tab2 = st.tabs(["📊 " + lang.get("select_graph", "Select a graph"), "✏️ " + lang.get("manual_chart_option", "Manual Input")])
        
        with tab1:
            if suggested_charts:
                # Display chart suggestions with refresh button
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    selected_graph = st.selectbox(
                        lang.get("select_graph", "Select a graph to display:"), 
                        list(suggested_charts.keys()), 
                        format_func=lambda x: suggested_charts[x],
                        key="ai_suggested_chart"
                    )
                
                with col2:
                    if st.button("🔄", help=lang.get("refresh_suggestions", "Get new suggestions"), key="refresh_suggestions"):
                        # Force refresh of chart suggestions
                        with st.spinner(lang.get("getting_new_suggestions", "Getting new suggestions...")):
                            st.session_state.suggested_charts = chart_service.get_ai_suggested_charts(st.session_state.data, st.session_state.language)
                            st.rerun()
            else:
                # Fallback to default options if AI suggestions fail
                graph_options = {
                    "fraud_distribution": lang.get("fraud_distribution", "Fraud vs Regular Distribution"),
                    "amount_distribution": lang.get("amount_distribution", "Amount Distribution"),
                    "time_series": lang.get("time_series", "Transactions Over Time")
                }
                selected_graph = st.selectbox(lang.get("select_graph", "Select a graph to display:"), 
                                             list(graph_options.keys()), 
                                             format_func=lambda x: graph_options[x],
                                             key="fallback_chart",
                                             help=lang['fallback_chart_help'])
            
            # Generate and Download buttons
            col1, col2 = st.columns([3, 1])
            
            with col1:
                generate_clicked = st.button(
                    lang.get("generate_graph", "Generate Graph"), 
                    key="generate_ai_chart",
                    help=lang['generate_ai_help']
                )
            
            with col2:
                if st.session_state.generated_chart_path and os.path.exists(st.session_state.generated_chart_path):
                    with open(st.session_state.generated_chart_path, "rb") as file:
                        st.download_button(
                            label="📥",
                            data=file.read(),
                            file_name=f"chart_{selected_graph}.png",
                            mime="image/png",
                            help=lang.get("download_chart", "Download chart"),
                            key="download_ai_chart"
                        )
            
            if generate_clicked:
                with st.spinner("📊 " + lang.get("generating_graph", "Generating graph...")):
                    try:
                        graph_path = chart_service.generate_graph(st.session_state.data, selected_graph, st.session_state.language)
                        st.session_state.generated_chart_path = graph_path
                        st.image(graph_path)
                        
                        # Add to conversation history
                        if selected_graph in suggested_charts:
                            description = suggested_charts[selected_graph]
                        else:
                            description = selected_graph
                        st.session_state.conversation_history.append(f"Generated chart: {description}")
                        
                    except Exception as e:
                        st.error(f"Error generating graph: {str(e)}")
                        st.info(lang.get("graph_error_info", "Please try a different chart type or check your data format."))
        
        with tab2:
            manual_chart_input = st.text_area(
                lang.get("manual_chart_option", "Or manually enter the desired chart type:"),
                placeholder=lang.get("manual_chart_placeholder", "💡 Examples: histogram of Amount column, scatter plot between V1 and V2, correlation heatmap, box plot for outliers..."),
                height=100,
                key="manual_chart_input",
                help=lang['manual_chart_help']
            )
            
            # Generate and Download buttons for custom charts
            col1, col2 = st.columns([3, 1])
            
            with col1:
                generate_custom_clicked = st.button(
                    lang.get("generate_custom_graph", "Generate Custom Graph"), 
                    key="generate_custom_chart",
                    help=lang['generate_custom_help']
                )
            
            with col2:
                if st.session_state.generated_chart_path and os.path.exists(st.session_state.generated_chart_path):
                    with open(st.session_state.generated_chart_path, "rb") as file:
                        st.download_button(
                            label="📥",
                            data=file.read(),
                            file_name="custom_chart.png",
                            mime="image/png",
                            help=lang.get("download_chart", "Download chart"),
                            key="download_custom_chart"
                        )
            
            if generate_custom_clicked:
                if not manual_chart_input.strip():
                    st.error(lang.get("custom_chart_validation_error", "Please describe the type of chart you want to generate."))
                else:
                    with st.spinner("🎨 " + lang.get("generating_graph", "Generating graph...")):
                        try:
                            # Pass conversation history to custom chart generation
                            graph_path = chart_service.generate_custom_chart(
                                st.session_state.data, 
                                manual_chart_input, 
                                st.session_state.language,
                                st.session_state.conversation_history
                            )
                            st.session_state.generated_chart_path = graph_path
                            
                            # Display the chart in the custom tab (tab2)
                            st.image(graph_path)
                            
                            # Add to conversation history
                            st.session_state.conversation_history.append(f"Custom chart request: {manual_chart_input}")
                            
                            # Success message to confirm chart generation
                            st.success(lang.get("custom_chart_generated", "Custom chart generated successfully!"))
                            
                        except Exception as e:
                            st.error(f"Error generating custom graph: {str(e)}")
                            st.info(lang.get("graph_error_info", "Please try a different chart type or check your data format."))
        
        # Questions section
        st.markdown(f"""
        <div class="custom-card">
            <h3 style="color: #374151; margin-bottom: 1rem; display: flex; align-items: center;">
                {lang['questions_title']}
                <span style="margin-left: 0.5rem; font-size: 0.8rem; color: #6b7280; font-weight: normal;">
                    {lang['questions_subtitle']}
                </span>
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        user_query = st.text_input(
            lang["enter_question"], 
            placeholder=lang["question_placeholder"],
            help=lang['question_help']
        )
        
        if user_query:
            # Check if query is related to the data using current dataset context
            data_columns = list(st.session_state.data.columns) if st.session_state.data is not None else None
            if not is_data_analysis_question(user_query, data_columns):
                st.warning(lang.get("related_questions_warning", "Please ask questions related to the imported CSV file and its data."))
            else:
                with st.spinner("🔄 " + lang["processing_query"]):
                    response, insights = coordinator.process_query(user_query)
                
                # Display response in styled containers
                st.markdown(f"""
                <div style="background: var(--background-gradient); 
                           padding: 1.5rem; border-radius: 12px; border-left: 4px solid #10b981; 
                           margin: 1rem 0;">
                    <h4 style="color: #065f46; margin: 0 0 1rem 0; display: flex; align-items: center;">
                        {lang['ai_response_title']}
                    </h4>
                """, unsafe_allow_html=True)
                st.write(response)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Display additional insights if available
                if insights:
                    st.markdown(f"""
                    <div style="background: var(--background-gradient); 
                               padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f59e0b; 
                               margin: 1rem 0;">
                        <h4 style="color: #92400e; margin: 0 0 1rem 0; display: flex; align-items: center;">
                            {lang['additional_insights_title']}
                        </h4>
                    """, unsafe_allow_html=True)
                    st.write(insights)
                    st.markdown("</div>", unsafe_allow_html=True)
else:
    # Welcome screen for new users
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem 2rem; background: var(--background-gradient); 
                border-radius: 12px; margin: 2rem 0;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
        <h2 style="color: #374151; margin-bottom: 1rem;">{lang['welcome_title']}</h2>
        <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem; max-width: 600px; margin-left: auto; margin-right: auto;">
            {lang['welcome_description']}
        </p>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 2rem;">
            <div style="background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 200px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤖</div>
                <h4 style="color: #374151; margin: 0 0 0.5rem 0;">{lang['welcome_ai_title']}</h4>
                <p style="color: #6b7280; font-size: 0.9rem; margin: 0;">{lang['welcome_ai_description']}</p>
            </div>
            <div style="background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 200px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📈</div>
                <h4 style="color: #374151; margin: 0 0 0.5rem 0;">{lang['welcome_charts_title']}</h4>
                <p style="color: #6b7280; font-size: 0.9rem; margin: 0;">{lang['welcome_charts_description']}</p>
            </div>
            <div style="background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 200px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>
                <h4 style="color: #374151; margin: 0 0 0.5rem 0;">{lang['welcome_questions_title']}</h4>
                <p style="color: #6b7280; font-size: 0.9rem; margin: 0;">{lang['welcome_questions_description']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Add footer with enhanced styling
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 2rem 0; color: #6b7280; background: var(--background-gradient); 
           border-radius: 12px; margin-top: 2rem;">
    <p style="margin: 0; font-size: 0.9rem;">{lang["footer"]}</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.7;">
        {lang['footer_made_with']}
    </p>
</div>
""", unsafe_allow_html=True)