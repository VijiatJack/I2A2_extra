# 🔮 DataVision AI - Análise Inteligente de Dados

A sophisticated multi-agent application that uses Google AI (Gemini) to parse CSV files and provide intelligent data analysis with natural language queries. Features advanced data analysis capabilities, multilingual support, and comprehensive data visualization for any type of dataset.

## ✨ Features

### Core Functionality
- **Smart CSV Processing**: Upload and automatically analyze any CSV file
- **Natural Language Queries**: Ask questions about your data in plain language
- **AI-Powered Insights**: Get intelligent analysis and recommendations for any dataset
- **Multi-Agent Architecture**: Specialized agents for different processing tasks

### Advanced Features
- **🌍 Multilingual Support**: Full support for Portuguese (Brazil) and English
- **📈 Data Visualization**: Interactive graphs and charts with AI-suggested visualizations
- **🔍 Pattern Recognition**: Advanced analysis for any type of data patterns
- **📊 Comprehensive Data Analysis**: Advanced statistical summaries and intelligent data sampling
- **🎯 Contextual Validation**: Smart question validation in multiple languages
- **💡 Technical Opinions**: Get expert assessments of your dataset quality
- **🧠 Intelligent Data Sampling**: Smart sampling strategies for large datasets including head/tail, random, and stratified sampling
- **📋 Data Quality Assessment**: Comprehensive analysis of missing values, duplicates, and data integrity

### Data Analysis Capabilities
- **Statistical Analysis**: Mean, median, standard deviation, and distribution analysis
- **Universal Data Processing**: Analyze any type of CSV data - sales, marketing, scientific, financial, etc.
- **Time Series Analysis**: Temporal pattern recognition and trend analysis for any time-based data
- **Data Quality Assessment**: Missing values, duplicates, and data structure evaluation
- **Visual Analytics**: Multiple chart types including histograms, scatter plots, line charts, bar charts, pie charts, box plots, and heatmaps
- **Intelligent Sampling**: Advanced sampling strategies for large datasets
- **Pattern Recognition**: Correlation analysis and value distribution insights
- **Chunked Processing**: Efficient handling of large datasets through intelligent chunking

## 🏗️ Project Structure

```
I2A2_extra/
├── agents/                 # Multi-agent system
│   ├── __init__.py
│   ├── base_agent.py      # Base agent class
│   ├── coordinator.py     # Main coordinator agent
│   ├── csv_agent.py       # CSV processing agent
│   ├── query_agent.py     # Query processing agent
│   └── insight_agent.py   # Insight generation agent
├── config/                # Configuration management
│   ├── __init__.py
│   └── settings.py        # Application settings and environment handling
├── services/              # Business logic services
│   ├── __init__.py
│   ├── chart_service.py   # Chart generation and AI-powered visualization
│   ├── data_analysis_service.py  # Advanced data analysis and sampling
│   ├── data_service.py    # Core data processing operations
│   └── file_service.py    # File handling and validation
├── utils/                 # Utility functions and constants
│   ├── __init__.py
│   ├── constants.py       # Application-wide constants
│   └── validation.py      # Data validation utilities
├── app.py                 # Main Streamlit application
├── languages.py           # Multilingual support
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── EXAMPLE_CSV_FORMAT.md # CSV format documentation
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google AI API key (Gemini Pro model)
- Internet connection for API calls

### Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/VijiatJack/I2A2_extra](https://github.com/VijiatJack/I2A2_extra.git)
   cd I2A2_extra
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google AI API key:
   # GEMINI_API_KEY=your_GEMINI_API_KEY_here
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** and navigate to `http://localhost:8501`

## 📖 How to Use

### Basic Usage
1. **Select Language**: Choose between Portuguese (Brazil) or English in the sidebar
2. **Upload CSV File**: Use the file uploader to select any CSV file
3. **Review Analysis**: View automatic statistical analysis and data preview
4. **Explore AI Visualizations**: Generate AI-suggested charts and graphs tailored to your data
5. **Ask Questions**: Enter natural language questions about your data
6. **Get Insights**: Receive AI-powered responses and additional insights

### Supported Question Types

#### Data Description (English/Portuguese)
- "What are the data types?" / "Quais são os tipos de dados?"
- "Show me the distribution of variables" / "Mostre a distribuição das variáveis"
- "What are the basic statistics?" / "Quais são as estatísticas básicas?"
- "Describe the structure of this data" / "Descreva a estrutura destes dados"

#### Pattern Analysis
- "Are there any temporal patterns?" / "Existem padrões temporais?"
- "Show me clustering in the data" / "Mostre agrupamentos nos dados"
- "What trends can you identify?" / "Que tendências você identifica?"
- "Find correlations between variables" / "Encontre correlações entre variáveis"

#### Anomaly Detection
- "Find outliers in the data" / "Encontre outliers nos dados"
- "Are there unusual values?" / "Há valores incomuns?"
- "Identify irregular patterns" / "Identifique padrões irregulares"
- "What data points seem anomalous?" / "Que pontos de dados parecem anômalos?"

#### General Analysis
- "What's your opinion on this dataset?" / "Qual sua opinião sobre este dataset?"
- "How would you evaluate data quality?" / "Como você avalia a qualidade dos dados?"
- "What insights can you provide?" / "Que insights você pode fornecer?"
- "Summarize the key findings" / "Resuma as principais descobertas"

## 🔧 Configuration

### Environment Variables
Create a `.env` file with the following variables:

```env
# Required: Google AI API Key
GEMINI_API_KEY=your_GEMINI_API_KEY_here

# Optional: Suppress Google Cloud warnings (if desired)
GRPC_VERBOSITY=ERROR
GRPC_TRACE=""
```

### CSV File Requirements
- **Format**: Standard CSV with headers
- **Encoding**: UTF-8 recommended
- **Size**: No strict limit, but larger files may take longer to process
- **Data Types**: Supports any type of data - numerical, categorical, text, dates, etc.
- **Use Cases**: Sales data, marketing analytics, scientific datasets, financial records, survey responses, etc.

## 🤖 Agent System Architecture

### Coordinator Agent
- **Role**: Orchestrates the entire workflow
- **Responsibilities**: File processing coordination, query routing, session management
- **Features**: Smart data caching, technical opinion generation, universal data handling

### CSV Agent
- **Role**: Handles CSV file processing and validation
- **Responsibilities**: File parsing, data cleaning, format validation
- **Features**: Error handling, data type inference, universal CSV support

### Query Agent
- **Role**: Processes natural language queries
- **Responsibilities**: Query interpretation, AI model interaction using Gemini
- **Features**: Context-aware responses, multilingual support, comprehensive data context provision

### Insight Agent
- **Role**: Generates additional insights and analysis
- **Responsibilities**: Pattern recognition, statistical analysis, comprehensive data insights
- **Features**: Automated insights, trend identification, advanced data analysis integration

## 🔧 Services Architecture

### Chart Service
- **Purpose**: Handles all data visualization and AI-powered chart generation
- **Features**: 7+ chart types (histogram, scatter, line, bar, pie, box, heatmap), AI-suggested visualizations, automatic chart selection based on data types
- **AI Integration**: Intelligent chart recommendations based on data structure and content

### Data Analysis Service
- **Purpose**: Provides comprehensive data analysis and intelligent sampling
- **Features**: Statistical summaries, data quality assessment, pattern analysis, chunked processing
- **Sampling Strategies**: Head/tail sampling, random sampling, stratified sampling

### Data Service
- **Purpose**: Core data processing and analysis operations
- **Features**: Universal data analysis, time series analysis, data validation, pattern recognition

### File Service
- **Purpose**: File handling, validation, and processing
- **Features**: CSV parsing, encoding detection, file validation, universal format support

## 🌐 Multilingual Support

The application supports:
- **Portuguese (Brazil)**: Complete UI and query processing
- **English (US)**: Complete UI and query processing
- **Contextual Validation**: Smart question validation in both languages
- **Dynamic Language Switching**: Change language without losing session data
- **AI Chart Labels**: Automatic chart labeling in selected language

## 📊 Visualization Options

### AI-Powered Chart Suggestions
- **Histogram**: Distribution analysis for numerical data
- **Scatter Plot**: Relationship analysis between variables
- **Line Chart**: Trend analysis over time or sequences
- **Bar Chart**: Categorical data comparison
- **Pie Chart**: Proportion and percentage visualization
- **Box Plot**: Statistical distribution and outlier detection
- **Heatmap**: Correlation matrix and pattern visualization

### Smart Chart Selection
- AI analyzes your data structure and suggests the most appropriate visualizations
- Automatic detection of data types (numerical, categorical, temporal)
- Intelligent column selection for multi-variable charts
- Multilingual chart titles and labels

## 🔒 Security & Privacy

- **API Key Protection**: Environment variables for sensitive data
- **Local Processing**: Data processed locally, only queries sent to AI
- **No Data Storage**: Files processed in memory, not saved permanently
- **Session Management**: Secure session state handling
- **Universal Data Support**: Works with any CSV data without restrictions

## 🐛 Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**
   - Ensure `.env` file exists with valid API key
   - Check API key permissions and quotas

2. **"ALTS credentials warning"**
   - This is normal for local development
   - Add `GRPC_VERBOSITY=ERROR` to `.env` to suppress

3. **CSV parsing errors**
   - Ensure CSV has proper headers
   - Check file encoding (UTF-8 recommended)
   - Verify file is not corrupted

4. **Memory issues with large files**
   - Consider processing smaller chunks
   - Ensure sufficient system memory

5. **Chart generation errors**
   - Ensure data has appropriate columns for selected chart type
   - Check for missing or invalid data values

## 🎯 Use Cases

DataVision AI can analyze any type of CSV data:

### Business & Marketing
- Sales performance analysis
- Customer behavior patterns
- Marketing campaign effectiveness
- Revenue trends and forecasting

### Scientific & Research
- Experimental data analysis
- Survey response analysis
- Research dataset exploration
- Statistical hypothesis testing

### Financial & Operations
- Financial performance metrics
- Operational efficiency analysis
- Budget and expense tracking
- Risk assessment and monitoring

### Personal & Educational
- Personal data tracking
- Academic research projects
- Learning dataset exploration
- Data science education

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google AI (Gemini)**: For providing the AI capabilities
- **Streamlit**: For the excellent web framework
- **Python Community**: For the amazing ecosystem of data science libraries

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the [Issues](../../issues) page
3. Create a new issue with detailed information about your problem

---

**🔮 DataVision AI - Transforming Data into Intelligence**
