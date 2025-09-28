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
    page_title="DataVision AI - Análise Inteligente de Dados",
    page_icon="🔮",
    layout="wide"
)

# Initialize services
data_service = DataService()
chart_service = ChartService()
file_service = FileService()

# Initialize the coordinator agent
coordinator = CoordinatorAgent()

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = DEFAULT_LANGUAGE
if 'data' not in st.session_state:
    st.session_state.data = None
if 'file_processed' not in st.session_state:
    st.session_state.file_processed = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'suggested_charts' not in st.session_state:
    st.session_state.suggested_charts = None

# Create a sidebar for settings
with st.sidebar:
    # Language selector
    selected_language = st.selectbox(
        "Idioma / Language",
        options=["Português (Brasil)", "English (US)"],
        index=0 if st.session_state.language == "pt_BR" else 1
    )
    
    # Handle language changes - reset chart suggestions when language changes
    if selected_language == "Português (Brasil)" and st.session_state.language != "pt_BR":
        st.session_state.language = "pt_BR"
        st.session_state.suggested_charts = None  # Reset charts for new language
    elif selected_language == "English (US)" and st.session_state.language != "en_US":
        st.session_state.language = "en_US"
        st.session_state.suggested_charts = None  # Reset charts for new language

# Get current language dictionary
lang = LANGUAGES[st.session_state.language]

# App title and description
st.title(lang["app_title"])
st.markdown(lang["app_description"])

# File uploader
uploaded_file = st.file_uploader(lang["file_uploader"], type=["csv"])

if uploaded_file is not None:
    # Only process the file if it hasn't been processed yet or if it's a new file
    file_needs_processing = False
    
    if not st.session_state.file_processed:
        file_needs_processing = True
    elif uploaded_file.name != st.session_state.get('current_file_name', ''):
        file_needs_processing = True
        
    if file_needs_processing:
        # Display file details
        file_details = {
            lang["filename"]: uploaded_file.name, 
            lang["filetype"]: uploaded_file.type, 
            lang["filesize"]: f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.write(lang["file_details"])
        st.write(file_details)
        
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
            
            # Generate AI-powered initial analysis using Insight Agent
            with st.spinner(lang.get("generating_analysis", "Generating initial analysis...")):
                from agents.insight_agent import InsightAgent
                insight_agent = InsightAgent()
                ai_analysis = insight_agent.process(data_preview, operation='initial_analysis', language=st.session_state.language)
                st.session_state.analysis_results = {'ai_insights': ai_analysis}
    
    # If file is processed successfully, display analysis and allow queries
    if st.session_state.file_processed and st.session_state.data is not None:
        # Display a preview of the data
        st.subheader(lang["data_preview"])
        st.dataframe(st.session_state.data.head())
        
        # Display AI-powered initial analysis
        if st.session_state.analysis_results:
            st.subheader(lang.get("initial_analysis", "Initial Analysis"))
            
            # Display AI-generated insights
            ai_insights = st.session_state.analysis_results.get('ai_insights', '')
            if ai_insights:
                st.write(ai_insights)
            else:
                st.info("No analysis available yet.")
        
        # Visualization section
        st.subheader(lang.get("visualization", "Visualization"))
        
        # Get AI-suggested charts (cache in session state to avoid re-fetching)
        if 'suggested_charts' not in st.session_state or st.session_state.suggested_charts is None:
            with st.spinner(lang.get("analyzing_data", "Analyzing data for chart suggestions...")):
                st.session_state.suggested_charts = chart_service.get_ai_suggested_charts(st.session_state.data, st.session_state.language)
        
        suggested_charts = st.session_state.suggested_charts
        
        if suggested_charts:
            selected_graph = st.selectbox(
                lang.get("select_graph", "Select a graph to display:"), 
                list(suggested_charts.keys()), 
                format_func=lambda x: suggested_charts[x]
            )
        else:
            # Fallback to default options if AI suggestions fail
            graph_options = {
                "fraud_distribution": lang.get("fraud_distribution", "Fraud vs Regular Distribution"),
                "amount_distribution": lang.get("amount_distribution", "Amount Distribution"),
                "time_series": lang.get("time_series", "Transactions Over Time")
            }
            selected_graph = st.selectbox(lang.get("select_graph", "Select a graph to display:"), 
                                         list(graph_options.keys()), 
                                         format_func=lambda x: graph_options[x])
        
        if st.button(lang.get("generate_graph", "Generate Graph")):
            with st.spinner(lang.get("generating_graph", "Generating graph...")):
                try:
                    graph_path = chart_service.generate_graph(st.session_state.data, selected_graph, st.session_state.language)
                    st.image(graph_path)
                except Exception as e:
                    st.error(f"Error generating graph: {str(e)}")
                    st.info(lang.get("graph_error_info", "Please try a different chart type or check your data format."))
        
        # User query section
        st.subheader(lang["ask_questions"])
        user_query = st.text_input(lang["enter_question"], placeholder="Ask a question about the data...")
        
        if user_query:
            # Check if query is related to the data
            if not is_data_analysis_question(user_query):
                st.warning(lang.get("related_questions_warning", "Please ask questions related to the imported CSV file and fraud detection."))
            else:
                with st.spinner(lang["processing_query"]):
                    response, insights = coordinator.process_query(user_query)
                
                # Display response
                st.subheader(lang["response"])
                st.write(response)
                
                # Display additional insights if available
                if insights:
                    st.subheader(lang["additional_insights"])
                    st.write(insights)
else:
    st.info(lang["upload_prompt"])

# Add footer
st.markdown("---")
st.markdown(lang["footer"])