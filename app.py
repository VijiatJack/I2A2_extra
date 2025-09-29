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
            
            # Reset conversation history for new file
            st.session_state.conversation_history = []
            
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
        
        # Chart generation options
        st.write(lang.get("chart_generation_options", "Chart Generation Options"))
        
        # Get AI-suggested charts (cache in session state to avoid re-fetching)
        if 'suggested_charts' not in st.session_state or st.session_state.suggested_charts is None:
            with st.spinner(lang.get("analyzing_data", "Analyzing data for chart suggestions...")):
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
                                             key="fallback_chart")
            
            # Generate and Download buttons
            col1, col2 = st.columns([3, 1])
            
            with col1:
                generate_clicked = st.button(lang.get("generate_graph", "Generate Graph"), key="generate_ai_chart")
            
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
                with st.spinner(lang.get("generating_graph", "Generating graph...")):
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
                placeholder=lang.get("manual_chart_placeholder", "Ex: histogram of Amount column, scatter plot between X and Y..."),
                height=100,
                key="manual_chart_input"
            )
            
            # Generate and Download buttons for custom charts
            col1, col2 = st.columns([3, 1])
            
            with col1:
                generate_custom_clicked = st.button(lang.get("generate_custom_graph", "Generate Custom Graph"), key="generate_custom_chart")
            
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
                    with st.spinner(lang.get("generating_graph", "Generating graph...")):
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
        
        # User query section
        st.subheader(lang["ask_questions"])
        user_query = st.text_input(lang["enter_question"], placeholder="Ask a question about the data...")
        
        if user_query:
            # Check if query is related to the data using current dataset context
            data_columns = list(st.session_state.data.columns) if st.session_state.data is not None else None
            if not is_data_analysis_question(user_query, data_columns):
                st.warning(lang.get("related_questions_warning", "Please ask questions related to the imported CSV file and its data."))
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