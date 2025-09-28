import streamlit as st
from agents.coordinator import CoordinatorAgent
import os
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from languages import LANGUAGES, DEFAULT_LANGUAGE

# Load environment variables
load_dotenv()

def is_data_analysis_question(query):
    """
    Check if the query is related to data analysis using contextual validation.
    Supports both Portuguese and English questions.
    """
    query_lower = query.lower()
    
    # Data analysis contexts in Portuguese and English
    data_contexts = {
        # Data description contexts
        'data_description': [
            # Portuguese
            'tipos de dados', 'dados numéricos', 'dados categóricos', 'distribuição', 'variável', 
            'histograma', 'intervalo', 'mínimo', 'máximo', 'média', 'mediana', 'tendência central',
            'variabilidade', 'desvio padrão', 'variância', 'estatística', 'resumo',
            # English
            'data types', 'numeric data', 'categorical data', 'distribution', 'variable',
            'histogram', 'range', 'minimum', 'maximum', 'mean', 'median', 'central tendency',
            'variability', 'standard deviation', 'variance', 'statistics', 'summary'
        ],
        
        # Pattern and trend contexts
        'patterns_trends': [
            # Portuguese
            'padrões', 'tendências', 'temporal', 'frequente', 'agrupamento', 'cluster',
            'comportamento', 'evolução', 'série temporal', 'sazonalidade',
            # English
            'patterns', 'trends', 'temporal', 'frequent', 'clustering', 'cluster',
            'behavior', 'evolution', 'time series', 'seasonality'
        ],
        
        # Anomaly detection contexts
        'anomalies': [
            # Portuguese
            'anomalias', 'outliers', 'valores atípicos', 'discrepantes', 'anômalos',
            'irregulares', 'suspeitos', 'incomuns',
            # English
            'anomalies', 'outliers', 'atypical values', 'discrepant', 'anomalous',
            'irregular', 'suspicious', 'unusual'
        ],
        
        # Variable relationships contexts
        'relationships': [
            # Portuguese
            'relação', 'correlação', 'associação', 'dependência', 'influência',
            'dispersão', 'tabela cruzada', 'conexão', 'vínculo',
            # English
            'relationship', 'correlation', 'association', 'dependency', 'influence',
            'scatter', 'cross table', 'connection', 'link'
        ],
        
        # Fraud detection specific contexts
        'fraud_detection': [
            # Portuguese
            'fraude', 'fraudulento', 'transação', 'pagamento', 'suspeita', 'irregular',
            'detecção', 'classificação', 'normal', 'regular', 'legítimo',
            # English
            'fraud', 'fraudulent', 'transaction', 'payment', 'suspicious', 'irregular',
            'detection', 'classification', 'normal', 'regular', 'legitimate'
        ],
        
        # General data analysis contexts
        'general_analysis': [
            # Portuguese
            'dados', 'arquivo', 'csv', 'análise', 'exploração', 'investigação',
            'interpretação', 'insights', 'conclusões', 'resultados', 'descobertas',
            'opinião', 'avaliação', 'qualidade', 'estrutura',
            # English
            'data', 'file', 'csv', 'analysis', 'exploration', 'investigation',
            'interpretation', 'insights', 'conclusions', 'results', 'findings',
            'opinion', 'evaluation', 'quality', 'structure'
        ]
    }
    
    # Check if query contains any relevant context terms
    for context_category, terms in data_contexts.items():
        if any(term in query_lower for term in terms):
            return True
    
    # Additional check for question words that indicate analytical intent
    question_indicators = [
        # Portuguese
        'qual', 'quais', 'como', 'onde', 'quando', 'por que', 'porque', 'quantos', 'quantas',
        'existe', 'existem', 'há', 'pode', 'podem', 'deve', 'devem', 'é', 'são',
        # English
        'what', 'which', 'how', 'where', 'when', 'why', 'how many', 'how much',
        'is', 'are', 'can', 'could', 'should', 'would', 'do', 'does', 'did'
    ]
    
    has_question_indicator = any(indicator in query_lower for indicator in question_indicators)
    
    # If it has question indicators and some data-related terms, it's likely valid
    basic_data_terms = [
        # Portuguese
        'dados', 'arquivo', 'csv', 'tabela', 'coluna', 'linha', 'valor', 'campo',
        # English
        'data', 'file', 'csv', 'table', 'column', 'row', 'value', 'field'
    ]
    
    has_basic_data_terms = any(term in query_lower for term in basic_data_terms)
    
    return has_question_indicator and has_basic_data_terms

def analyze_data(df):
    """Generate initial analysis of the CSV data."""
    analysis = {}
    
    # 1. Initial analysis of the records
    total_records = len(df)
    regular_records = len(df[df['Class'] == 0])
    fraud_records = len(df[df['Class'] == 1])
    fraud_percentage = (fraud_records / total_records) * 100
    regular_percentage = (regular_records / total_records) * 100
    
    analysis['records'] = {
        'total': total_records,
        'regular': regular_records,
        'fraudulent': fraud_records,
        'regular_percentage': regular_percentage,
        'fraud_percentage': fraud_percentage
    }
    
    # 2. Total time in batch
    total_time = df['Time'].max() - df['Time'].min()
    analysis['time'] = {
        'total_seconds': total_time,
        'total_hours': total_time / 3600,
        'total_days': total_time / (3600 * 24)
    }
    
    # 3. Analysis of amounts
    regular_df = df[df['Class'] == 0]
    fraud_df = df[df['Class'] == 1]
    
    # Get amount statistics
    regular_min = regular_df['Amount'].min()
    regular_max = regular_df['Amount'].max()
    regular_avg = regular_df['Amount'].mean()
    regular_total = regular_df['Amount'].sum()
    
    fraud_min = fraud_df['Amount'].min() if not fraud_df.empty else 0
    fraud_max = fraud_df['Amount'].max() if not fraud_df.empty else 0
    fraud_avg = fraud_df['Amount'].mean() if not fraud_df.empty else 0
    fraud_total = fraud_df['Amount'].sum()
    
    total_amount = regular_total + fraud_total
    regular_amount_percentage = (regular_total / total_amount) * 100
    fraud_amount_percentage = (fraud_total / total_amount) * 100
    
    analysis['amounts'] = {
        'regular_min': regular_min,
        'regular_max': regular_max,
        'regular_avg': regular_avg,
        'regular_total': regular_total,
        'fraud_min': fraud_min,
        'fraud_max': fraud_max,
        'fraud_avg': fraud_avg,
        'fraud_total': fraud_total,
        'total': total_amount,
        'regular_percentage': regular_amount_percentage,
        'fraud_percentage': fraud_amount_percentage
    }
    
    return analysis

def generate_graph(df, graph_type):
    """Generate a graph based on the data and requested type."""
    plt.figure(figsize=(10, 6))
    
    if graph_type == "fraud_distribution":
        # Create a pie chart of fraud vs regular transactions
        labels = ['Regular', 'Fraudulent']
        sizes = [len(df[df['Class'] == 0]), len(df[df['Class'] == 1])]
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Distribution of Regular vs Fraudulent Transactions')
        
    elif graph_type == "amount_distribution":
        # Create histograms of transaction amounts
        plt.hist(df[df['Class'] == 0]['Amount'], alpha=0.5, label='Regular')
        plt.hist(df[df['Class'] == 1]['Amount'], alpha=0.5, label='Fraudulent')
        plt.xlabel('Amount')
        plt.ylabel('Frequency')
        plt.title('Distribution of Transaction Amounts')
        plt.legend()
        
    elif graph_type == "time_series":
        # Create a time series plot of transactions
        df_grouped = df.groupby(['Time', 'Class']).size().unstack().fillna(0)
        if 0 in df_grouped.columns:
            plt.plot(df_grouped.index, df_grouped[0], label='Regular')
        if 1 in df_grouped.columns:
            plt.plot(df_grouped.index, df_grouped[1], label='Fraudulent')
        plt.xlabel('Time')
        plt.ylabel('Number of Transactions')
        plt.title('Transactions Over Time')
        plt.legend()
    
    # Save the figure to a temporary file
    fig_path = "temp_graph.png"
    plt.savefig(fig_path)
    plt.close()
    
    return fig_path

# Check if API key is set
if not os.getenv("GOOGLE_API_KEY"):
    st.error("Please set your GOOGLE_API_KEY in a .env file")
    st.stop()

# Set page configuration
st.set_page_config(
    page_title="CSV AI Parser",
    page_icon="📊",
    layout="wide"
)

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
            data_preview = coordinator.process_file(uploaded_file)
        
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
                analysis_results = analyze_data(data_preview)
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
                graph_path = generate_graph(st.session_state.data, selected_graph)
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