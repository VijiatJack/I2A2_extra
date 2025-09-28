# CSV AI Parser 📊

A sophisticated multi-agent application that uses Google AI (Gemini) to parse CSV files and provide intelligent data analysis with natural language queries. Features advanced fraud detection capabilities, multilingual support, and comprehensive data visualization.

## ✨ Features

### Core Functionality
- **Smart CSV Processing**: Upload and automatically analyze CSV files
- **Natural Language Queries**: Ask questions about your data in plain language
- **AI-Powered Insights**: Get intelligent analysis and recommendations
- **Multi-Agent Architecture**: Specialized agents for different processing tasks

### Advanced Features
- **🌍 Multilingual Support**: Full support for Portuguese (Brazil) and English
- **📈 Data Visualization**: Interactive graphs and charts
- **🔍 Fraud Detection**: Specialized analysis for fraud detection datasets
- **📊 Initial Data Analysis**: Automatic statistical summaries and insights
- **🎯 Contextual Validation**: Smart question validation in multiple languages
- **💡 Technical Opinions**: Get expert assessments of your dataset quality

### Data Analysis Capabilities
- **Statistical Analysis**: Mean, median, standard deviation, and distribution analysis
- **Fraud Detection**: Specialized metrics for fraud vs. regular transaction analysis
- **Time Series Analysis**: Temporal pattern recognition and trend analysis
- **Data Quality Assessment**: Missing values, duplicates, and data structure evaluation
- **Visual Analytics**: Multiple chart types including distributions and time series

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
├── app.py                 # Main Streamlit application
├── languages.py           # Multilingual support
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
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
   git clone <repository-url>
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
   # GOOGLE_API_KEY=your_google_api_key_here
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** and navigate to `http://localhost:8501`

## 📖 How to Use

### Basic Usage
1. **Select Language**: Choose between Portuguese (Brazil) or English in the sidebar
2. **Upload CSV File**: Use the file uploader to select your CSV file
3. **Review Analysis**: View automatic statistical analysis and data preview
4. **Explore Visualizations**: Generate various charts and graphs
5. **Ask Questions**: Enter natural language questions about your data
6. **Get Insights**: Receive AI-powered responses and additional insights

### Supported Question Types

#### Data Description (English/Portuguese)
- "What are the data types?" / "Quais são os tipos de dados?"
- "Show me the distribution of variables" / "Mostre a distribuição das variáveis"
- "What are the basic statistics?" / "Quais são as estatísticas básicas?"

#### Pattern Analysis
- "Are there any temporal patterns?" / "Existem padrões temporais?"
- "Show me clustering in the data" / "Mostre agrupamentos nos dados"
- "What trends can you identify?" / "Que tendências você identifica?"

#### Anomaly Detection
- "Find outliers in the data" / "Encontre outliers nos dados"
- "Are there suspicious transactions?" / "Há transações suspeitas?"
- "Identify irregular patterns" / "Identifique padrões irregulares"

#### General Opinions
- "What's your opinion on this dataset?" / "Qual sua opinião sobre este dataset?"
- "How would you evaluate data quality?" / "Como você avalia a qualidade dos dados?"

## 🔧 Configuration

### Environment Variables
Create a `.env` file with the following variables:

```env
# Required: Google AI API Key
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Suppress Google Cloud warnings (if desired)
GRPC_VERBOSITY=ERROR
GRPC_TRACE=""
```

### CSV File Requirements
- **Format**: Standard CSV with headers
- **Encoding**: UTF-8 recommended
- **Size**: No strict limit, but larger files may take longer to process
- **Fraud Detection**: For fraud analysis, include a column named 'Class', 'fraud', or 'is_fraud'

## 🤖 Agent System Architecture

### Coordinator Agent
- **Role**: Orchestrates the entire workflow
- **Responsibilities**: File processing coordination, query routing, session management
- **Features**: Smart data caching, technical opinion generation

### CSV Agent
- **Role**: Handles CSV file processing and validation
- **Responsibilities**: File parsing, data cleaning, format validation
- **Features**: Error handling, data type inference

### Query Agent
- **Role**: Processes natural language queries
- **Responsibilities**: Query interpretation, AI model interaction
- **Features**: Context-aware responses, multilingual support

### Insight Agent
- **Role**: Generates additional insights and analysis
- **Responsibilities**: Pattern recognition, statistical analysis
- **Features**: Automated insights, trend identification

## 🌐 Multilingual Support

The application supports:
- **Portuguese (Brazil)**: Complete UI and query processing
- **English (US)**: Complete UI and query processing
- **Contextual Validation**: Smart question validation in both languages
- **Dynamic Language Switching**: Change language without losing session data

## 📊 Visualization Options

- **Fraud Distribution**: Pie chart showing fraud vs. regular transactions
- **Amount Distribution**: Histogram of transaction amounts
- **Time Series**: Transaction patterns over time
- **Interactive Charts**: Powered by Matplotlib with automatic saving

## 🔒 Security & Privacy

- **API Key Protection**: Environment variables for sensitive data
- **Local Processing**: Data processed locally, only queries sent to AI
- **No Data Storage**: Files processed in memory, not saved permanently
- **Session Management**: Secure session state handling

## 🐛 Troubleshooting

### Common Issues

1. **"GOOGLE_API_KEY not found"**
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

**Made with ❤️ for intelligent data analysis**