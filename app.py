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
    page_title="CSV AI Parser",
    page_icon="📊",
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

# Create a sidebar for settings
with st.sidebar:
    # Language selector
    selected_language = st.selectbox(
        "Idioma / Language",
        options=["Português (Brasil)", "English (US)"],
        index=0 if st.session_state.language == "pt_BR" else 1
    )
    
    # Update language in session state
    if selected_language == "Português (Brasil)" and st.session_state.language != "pt_BR":
        st.session_state.language = "pt_BR"
    elif selected_language == "English (US)" and st.session_state.language != "en_US":
        st.session_state.language = "en_US"

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
            
            # Generate initial analysis
            with st.spinner(lang.get("generating_analysis", "Generating initial analysis...")):
                analysis_results = data_service.analyze_data(data_preview)
                st.session_state.analysis_results = analysis_results
    
    # If file is processed successfully, display analysis and allow queries
    if st.session_state.file_processed and st.session_state.data is not None:
        # Display a preview of the data
        st.subheader(lang["data_preview"])
        st.dataframe(st.session_state.data.head())
        
        # Display initial analysis
        if st.session_state.analysis_results:
            analysis = st.session_state.analysis_results
            
            st.subheader(lang.get("initial_analysis", "Initial Analysis"))
            
            # Records analysis
            st.write(f"### {lang.get('records_analysis', 'Records Analysis')}")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(lang.get("total_records", "Total Records"), f"{analysis['records']['total']:,}")
            with col2:
                st.metric(lang.get("regular_transactions", "Regular Transactions"), 
                            f"{analysis['records']['regular']:,} ({analysis['records']['regular_percentage']:.2f}%)")
            with col3:
                st.metric(lang.get("fraudulent_transactions", "Fraudulent Transactions"), 
                            f"{analysis['records']['fraudulent']:,} ({analysis['records']['fraud_percentage']:.2f}%)")
            
            # Time analysis
            st.write(f"### {lang.get('time_analysis', 'Time Analysis')}")
            st.metric(lang.get("total_time_period", "Total Time Period"), 
                        f"{analysis['time']['total_days']:.2f} days ({analysis['time']['total_hours']:.2f} hours)")
            
            # Amount analysis
            st.write(f"### {lang.get('amount_analysis', 'Amount Analysis')}")
            
            # Regular transactions
            st.write(f"#### {lang.get('regular_transactions_heading', 'Regular Transactions')}")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(lang.get("min_amount", "Minimum Amount"), f"${analysis['amounts']['regular_min']:.2f}")
            with col2:
                st.metric(lang.get("max_amount", "Maximum Amount"), f"${analysis['amounts']['regular_max']:.2f}")
            with col3:
                st.metric(lang.get("avg_amount", "Average Amount"), f"${analysis['amounts']['regular_avg']:.2f}")
            
            # Fraudulent transactions
            st.write(f"#### {lang.get('fraudulent_transactions_heading', 'Fraudulent Transactions')}")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(lang.get("min_amount", "Minimum Amount"), f"${analysis['amounts']['fraud_min']:.2f}")
            with col2:
                st.metric(lang.get("max_amount", "Maximum Amount"), f"${analysis['amounts']['fraud_max']:.2f}")
            with col3:
                st.metric(lang.get("avg_amount", "Average Amount"), f"${analysis['amounts']['fraud_avg']:.2f}")
            
            # Total amounts
            st.write(f"#### {lang.get('total_amounts', 'Total Amounts')}")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(lang.get("regular_total", "Regular Total"), 
                            f"${analysis['amounts']['regular_total']:.2f} ({analysis['amounts']['regular_percentage']:.2f}%)")
            with col2:
                st.metric(lang.get("fraudulent_total", "Fraudulent Total"), 
                            f"${analysis['amounts']['fraud_total']:.2f} ({analysis['amounts']['fraud_percentage']:.2f}%)")
        
        # Graph options
        st.subheader(lang.get("visualization", "Visualization"))
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
                graph_path = chart_service.generate_graph(st.session_state.data, selected_graph)
                st.image(graph_path)
        
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