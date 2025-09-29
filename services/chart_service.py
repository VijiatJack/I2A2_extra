"""
Chart generation service for the CSV AI Parser application.

This module provides chart generation functionality following
the Single Responsibility Principle and Clean Code practices.
"""

import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, Tuple, Dict, List
import os
import tempfile
import google.generativeai as genai
from config.settings import get_app_settings
from utils.constants import DEFAULT_MODEL_NAME, API_KEY_ENV_VAR


class ChartService:
    """
    Service class for chart generation operations.
    
    This class encapsulates all chart generation logic, providing
    a clean interface for creating various types of visualizations.
    """
    
    def __init__(self):
        """Initialize the chart service."""
        self._settings = get_app_settings()
        self._temp_files = []  # Track temporary files for cleanup
        
        # Configure Google AI for graph suggestions
        genai.configure(api_key=os.getenv(API_KEY_ENV_VAR))
        self.model = genai.GenerativeModel(DEFAULT_MODEL_NAME)
    
    def generate_chart(self, data: pd.DataFrame, chart_type: str) -> str:
        """
        Generate a chart based on the specified type.
        
        Args:
            data (pd.DataFrame): Data to visualize
            chart_type (str): Type of chart to generate
            
        Returns:
            str: Path to the generated chart image
            
        Raises:
            ValueError: If chart type is not supported or data is invalid
        """
        if data is None or data.empty:
            raise ValueError("Data cannot be None or empty")
        
        chart_generators = {
            'fraud_distribution': self._generate_fraud_distribution,
            'amount_distribution': self._generate_amount_distribution,
            'time_series': self._generate_time_series
        }
        
        if chart_type not in chart_generators:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        return chart_generators[chart_type](data)
    
    def _generate_fraud_distribution(self, data: pd.DataFrame) -> str:
        """
        Generate fraud vs regular distribution chart.
        
        Args:
            data (pd.DataFrame): Data containing fraud classification
            
        Returns:
            str: Path to the generated chart
        """
        plt.figure(figsize=(
            self._settings.default_chart_width / 100,
            self._settings.default_chart_height / 100
        ))
        
        if 'Class' not in data.columns:
            # Create a simple data distribution chart for general datasets
            plt.hist(data.iloc[:, 0] if len(data.columns) > 0 else [], bins=30, alpha=0.7)
            plt.xlabel('Values')
            plt.ylabel('Frequency')
            plt.title('Data Distribution')
        else:
            # Fraud detection specific chart
            fraud_counts = data['Class'].value_counts()
            labels = ['Regular', 'Fraudulent']
            colors = ['#2ca02c', '#d62728']  # Green for regular, red for fraud
            
            plt.pie(fraud_counts.values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title('Fraud vs Regular Transactions Distribution')
        
        return self._save_and_return_path()
    
    def _generate_amount_distribution(self, data: pd.DataFrame) -> str:
        """
        Generate amount distribution chart.
        
        Args:
            data (pd.DataFrame): Data containing amount information
            
        Returns:
            str: Path to the generated chart
        """
        plt.figure(figsize=(
            self._settings.default_chart_width / 100,
            self._settings.default_chart_height / 100
        ))
        
        # Find amount column
        amount_columns = [col for col in data.columns if 'amount' in col.lower() or 'value' in col.lower()]
        
        if not amount_columns:
            # Use the first numeric column if no amount column found
            numeric_columns = data.select_dtypes(include=['number']).columns
            if len(numeric_columns) > 0:
                amount_column = numeric_columns[0]
            else:
                raise ValueError("No numeric columns found for amount distribution")
        else:
            amount_column = amount_columns[0]
        
        if 'Class' in data.columns:
            # Separate distributions for fraud detection data
            regular_amounts = data[data['Class'] == 0][amount_column]
            fraud_amounts = data[data['Class'] == 1][amount_column]
            
            plt.hist(regular_amounts, bins=50, alpha=0.7, label='Regular', color='#2ca02c')
            if len(fraud_amounts) > 0:
                plt.hist(fraud_amounts, bins=50, alpha=0.7, label='Fraudulent', color='#d62728')
            
            plt.xlabel('Amount')
            plt.ylabel('Frequency')
            plt.title('Amount Distribution by Transaction Type')
            plt.legend()
        else:
            # General amount distribution
            plt.hist(data[amount_column], bins=50, alpha=0.7, color='#1f77b4')
            plt.xlabel(f'{amount_column}')
            plt.ylabel('Frequency')
            plt.title(f'{amount_column} Distribution')
        
        return self._save_and_return_path()
    
    def _generate_time_series(self, data: pd.DataFrame) -> str:
        """
        Generate time series chart.
        
        Args:
            data (pd.DataFrame): Data containing time information
            
        Returns:
            str: Path to the generated chart
        """
        plt.figure(figsize=(
            self._settings.default_chart_width / 100,
            self._settings.default_chart_height / 100
        ))
        
        # Find time column
        time_columns = [col for col in data.columns if 'time' in col.lower() or 'date' in col.lower()]
        
        if not time_columns:
            raise ValueError("No time columns found for time series chart")
        
        time_column = time_columns[0]
        
        try:
            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(data[time_column]):
                time_data = pd.to_datetime(data[time_column], errors='coerce')
            else:
                time_data = data[time_column]
            
            # Create a copy of data with the time column
            df_with_time = data.copy()
            df_with_time[time_column] = time_data
            
            # Remove rows with invalid dates
            df_with_time = df_with_time.dropna(subset=[time_column])
            
            if len(df_with_time) == 0:
                raise ValueError("No valid time data found")
            
            # Group by time periods (daily aggregation)
            df_with_time['date'] = df_with_time[time_column].dt.date
            
            if 'Class' in data.columns:
                # Fraud detection time series
                df_grouped = df_with_time.groupby(['date', 'Class']).size().unstack(fill_value=0)
                
                if 0 in df_grouped.columns:
                    plt.plot(df_grouped.index, df_grouped[0], label='Regular', color='#2ca02c')
                if 1 in df_grouped.columns:
                    plt.plot(df_grouped.index, df_grouped[1], label='Fraudulent', color='#d62728')
                
                plt.xlabel('Date')
                plt.ylabel('Number of Transactions')
                plt.title('Transactions Over Time')
                plt.legend()
            else:
                # General time series
                df_grouped = df_with_time.groupby('date').size()
                plt.plot(df_grouped.index, df_grouped.values, color='#1f77b4')
                plt.xlabel('Date')
                plt.ylabel('Count')
                plt.title('Data Points Over Time')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
        except Exception as e:
            raise ValueError(f"Error generating time series chart: {str(e)}")
        
        return self._save_and_return_path()
    
    def _save_and_return_path(self) -> str:
        """
        Save the current matplotlib figure and return the file path.
        
        Returns:
            str: Path to the saved chart file
        """
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # Save the figure
        plt.savefig(temp_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        # Track the temporary file for cleanup
        self._temp_files.append(temp_path)
        
        return temp_path
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary chart files."""
        for temp_file in self._temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass  # Ignore cleanup errors
        
        self._temp_files.clear()
    

    

    
    def generate_graph(self, data: pd.DataFrame, chart_type: str, language: str = 'en_US') -> str:
        """
        Generate a graph with AI-powered suggestions and multilingual support.
        
        Args:
            data (pd.DataFrame): Data to visualize
            chart_type (str): Type of chart to generate
            language (str): Language for chart labels and titles
            
        Returns:
            str: Path to the generated chart image
            
        Raises:
            ValueError: If chart type is not supported or data is invalid
        """
        if data is None or data.empty:
            raise ValueError("Data cannot be None or empty")
        
        # Get AI-suggested chart configuration
        chart_config = self._get_ai_chart_suggestions(data, chart_type, language)
        
        # Generate the chart using existing methods with AI enhancements
        return self._generate_enhanced_chart(data, chart_type, chart_config, language)
    
    def get_ai_suggested_charts(self, data: pd.DataFrame, language: str = 'en_US') -> Dict[str, str]:
        """
        Get AI-suggested chart types based on the data content.
        
        Args:
            data (pd.DataFrame): The data to analyze
            language (str): Language for suggestions
            
        Returns:
            Dict[str, str]: Dictionary of chart types and their descriptions
        """
        try:
            # Analyze data structure
            data_info = self._analyze_data_structure(data)
            
            # Generate AI suggestions
            if language == 'pt_BR':
                prompt = f"""
                Analise os seguintes dados CSV e sugira os 3-5 tipos de gráficos mais apropriados:
                
                {data_info}
                
                Para cada sugestão, forneça:
                1. Tipo de gráfico (use nomes técnicos em inglês como 'histogram', 'scatter', 'line', 'bar', 'pie')
                2. Descrição CURTA em português (máximo 6 palavras) do que o gráfico mostraria
                
                Formato da resposta:
                tipo_grafico: Descrição curta em português
                
                Exemplo:
                histogram: Distribuição de valores
                scatter: Relação entre variáveis
                """
            else:
                prompt = f"""
                Analyze the following CSV data and suggest the 3-5 most appropriate chart types:
                
                {data_info}
                
                For each suggestion, provide:
                1. Chart type (use technical names like 'histogram', 'scatter', 'line', 'bar', 'pie')
                2. SHORT description in English (maximum 6 words) of what the chart would show
                
                Response format:
                chart_type: Short description in English
                
                Example:
                histogram: Distribution of values
                scatter: Relationship between variables
                """
            
            response = self.model.generate_content(prompt)
            ai_suggestions = self._parse_chart_suggestions(response.text)
            
            # Ensure we have exactly 5 suggestions
            if ai_suggestions and len(ai_suggestions) >= 3:
                # Take first 5 suggestions from AI
                suggestions = dict(list(ai_suggestions.items())[:5])
                
                # If we have less than 5, fill with defaults
                if len(suggestions) < 5:
                    defaults = self._get_default_chart_suggestions(data, language)
                    for key, value in defaults.items():
                        if key not in suggestions and len(suggestions) < 5:
                            suggestions[key] = value
            else:
                # Fallback to default suggestions
                suggestions = self._get_default_chart_suggestions(data, language)
            
            return suggestions
            
        except Exception as e:
            # Always return default suggestions as fallback
            return self._get_default_chart_suggestions(data, language)
    
    def _get_ai_chart_suggestions(self, data: pd.DataFrame, chart_type: str, language: str) -> Dict:
        """Get AI suggestions for chart configuration with proper column selection."""
        data_info = self._analyze_data_structure(data)
        
        if language == 'pt_BR':
            prompt = f"""
            Para um gráfico do tipo '{chart_type}' com os seguintes dados:
            
            {data_info}
            
            Analise os dados e retorne APENAS um JSON válido com a seguinte estrutura:
            {{
                "type": "{chart_type}",
                "x_column": "nome_da_coluna_x",
                "y_column": "nome_da_coluna_y",
                "title": "Título do gráfico (máximo 6 palavras)",
                "xlabel": "Rótulo do eixo X",
                "ylabel": "Rótulo do eixo Y",
                "transformation": "Descrição de qualquer transformação necessária nos dados (opcional)",
                "colors": ["#1f77b4", "#ff7f0e", "#2ca02c"]
            }}
            
            REGRAS:
            - Use apenas colunas que existem nos dados
            - Para histogram: apenas x_column é necessário (y_column pode ser null)
            - Para pie: apenas x_column (categórica) é necessário (y_column pode ser null)
            - Para scatter/line: x_column e y_column são necessários
            - Para bar: x_column (categórica) é necessário, y_column opcional
            - Para box: x_column (numérica) é necessário (y_column pode ser null)
            - Para heatmap: use correlações entre colunas numéricas (x_column e y_column podem ser null)
            - Se precisar de transformações como "primeiro dígito", "agrupamento", etc., descreva no campo "transformation"
            - Escolha as colunas mais relevantes e interessantes para análise
            """
        else:
            prompt = f"""
            For a '{chart_type}' chart with the following data:
            
            {data_info}
            
            Analyze the data and return ONLY a valid JSON with this structure:
            {{
                "type": "{chart_type}",
                "x_column": "x_column_name",
                "y_column": "y_column_name",
                "title": "Chart title (max 6 words)",
                "description": "Brief description of what the chart would show",
                "transformation": "Description of any data transformation needed (optional)"
            }}
            
            RULES:
            - Use only columns that exist in the data
            - For histogram: only x_column is needed (y_column can be null)
            - For pie: only x_column (categorical) is needed (y_column can be null)
            - For scatter/line: both x_column and y_column are needed
            - For bar: x_column (categorical) is needed, y_column optional
            - For box: x_column (numerical) is needed (y_column can be null)
            - For heatmap: use correlations between numerical columns (x_column and y_column can be null)
            - If transformations like "first digit", "grouping", etc. are needed, describe in "transformation" field
            - Choose the most relevant and interesting columns for analysis
            """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean and parse JSON response
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].strip()
            
            import json
            chart_config = json.loads(response_text)
            
            # Validate that required fields exist
            if 'type' not in chart_config:
                chart_config['type'] = chart_type
            if 'title' not in chart_config:
                chart_config['title'] = f"Data Visualization - {chart_type.replace('_', ' ').title()}"
            if 'xlabel' not in chart_config:
                chart_config['xlabel'] = 'X Axis'
            if 'ylabel' not in chart_config:
                chart_config['ylabel'] = 'Y Axis'
            if 'colors' not in chart_config:
                chart_config['colors'] = ['#1f77b4', '#ff7f0e', '#2ca02c']
            
            return chart_config
            
        except Exception as e:
            # Return fallback configuration
            return {
                'type': chart_type,
                'title': f"Data Visualization - {chart_type.replace('_', ' ').title()}",
                'xlabel': 'X Axis',
                'ylabel': 'Y Axis',
                'colors': ['#1f77b4', '#ff7f0e', '#2ca02c'],
                'x_column': None,
                'y_column': None
            }
    
    def _analyze_data_structure(self, data: pd.DataFrame) -> str:
        """Analyze data structure for AI suggestions."""
        info = []
        info.append(f"Dataset shape: {data.shape[0]} rows, {data.shape[1]} columns")
        info.append(f"Columns: {', '.join(data.columns.tolist())}")
        
        # Analyze column types
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = data.select_dtypes(include=['datetime']).columns.tolist()
        
        if numeric_cols:
            info.append(f"Numeric columns: {', '.join(numeric_cols)}")
        if categorical_cols:
            info.append(f"Categorical columns: {', '.join(categorical_cols)}")
        if datetime_cols:
            info.append(f"DateTime columns: {', '.join(datetime_cols)}")
        
        # Sample data
        info.append(f"Sample data (first 3 rows):")
        info.append(data.head(3).to_string())
        
        return '\n'.join(info)
    
    def _parse_chart_suggestions(self, response_text: str) -> Dict[str, str]:
        """Parse AI response into chart suggestions."""
        suggestions = {}
        lines = response_text.strip().split('\n')
        
        # Common chart type keywords to look for
        chart_keywords = {
            'histogram': ['histogram', 'histograma'],
            'scatter': ['scatter', 'dispersão', 'dispersao'],
            'bar': ['bar', 'barra', 'barras'],
            'line': ['line', 'linha', 'linear'],
            'pie': ['pie', 'pizza', 'torta'],
            'box': ['box', 'boxplot', 'caixa'],
            'area': ['area', 'área']
        }
        
        for line in lines:
            line_lower = line.lower()
            
            # Try to parse format "chart_type: description"
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    chart_type = parts[0].strip().lower()
                    description = parts[1].strip()
                    
                    # Clean up chart type (remove numbers, bullets, etc.)
                    chart_type = ''.join(c for c in chart_type if c.isalpha())
                    
                    if chart_type in chart_keywords:
                        suggestions[chart_type] = description
                    else:
                        # Try to match with keywords
                        for key, keywords in chart_keywords.items():
                            if any(keyword in chart_type for keyword in keywords):
                                suggestions[key] = description
                                break
            
            # Also look for chart types mentioned in the text
            for chart_type, keywords in chart_keywords.items():
                for keyword in keywords:
                    if keyword in line_lower and chart_type not in suggestions:
                        # Extract description from the line
                        description = line.strip()
                        suggestions[chart_type] = description
                        break
        
        return suggestions
    
    def _get_default_chart_suggestions(self, data: pd.DataFrame, language: str) -> Dict[str, str]:
        """Get default chart suggestions as fallback, filtered by data compatibility."""
        # Check data characteristics
        numeric_columns = data.select_dtypes(include=['number']).columns
        categorical_columns = data.select_dtypes(include=['object', 'category']).columns
        
        suggestions = {}
        
        if language == 'pt_BR':
            # Always include histogram if there are numeric columns
            if len(numeric_columns) > 0:
                suggestions['histogram'] = 'Histograma - Distribuição de valores numéricos'
            
            # Include scatter plot only if there are at least 2 numeric columns
            if len(numeric_columns) >= 2:
                suggestions['scatter'] = 'Gráfico de Dispersão - Relação entre duas variáveis'
            
            # Include bar chart if there are categorical columns
            if len(categorical_columns) > 0:
                suggestions['bar'] = 'Gráfico de Barras - Comparação de categorias'
            
            # Include line chart if there are numeric columns (can work with index)
            if len(numeric_columns) > 0:
                suggestions['line'] = 'Gráfico de Linha - Tendências ao longo do tempo'
            
            # Include pie chart if there are categorical columns
            if len(categorical_columns) > 0:
                suggestions['pie'] = 'Gráfico de Pizza - Proporções de categorias'
        else:
            # Always include histogram if there are numeric columns
            if len(numeric_columns) > 0:
                suggestions['histogram'] = 'Histogram - Distribution of numeric values'
            
            # Include scatter plot only if there are at least 2 numeric columns
            if len(numeric_columns) >= 2:
                suggestions['scatter'] = 'Scatter Plot - Relationship between two variables'
            
            # Include bar chart if there are categorical columns
            if len(categorical_columns) > 0:
                suggestions['bar'] = 'Bar Chart - Comparison of categories'
            
            # Include line chart if there are numeric columns (can work with index)
            if len(numeric_columns) > 0:
                suggestions['line'] = 'Line Chart - Trends over time'
            
            # Include pie chart if there are categorical columns
            if len(categorical_columns) > 0:
                suggestions['pie'] = 'Pie Chart - Category proportions'
        
        # Ensure we have at least 5 suggestions by adding generic ones if needed
        if len(suggestions) < 5:
            if language == 'pt_BR':
                fallback_suggestions = {
                    'box': 'Gráfico de Caixa - Distribuição e outliers',
                    'heatmap': 'Mapa de Calor - Correlações entre variáveis'
                }
            else:
                fallback_suggestions = {
                    'box': 'Box Plot - Distribution and outliers',
                    'heatmap': 'Heatmap - Variable correlations'
                }
            
            for key, value in fallback_suggestions.items():
                if len(suggestions) < 5:
                    suggestions[key] = value
        
        return suggestions
    
    def _generate_enhanced_chart(self, data: pd.DataFrame, chart_type: str, config: Dict, language: str) -> str:
        """Generate enhanced chart with AI configuration and transformation support."""
        
        # Apply transformations if specified
        if 'transformation' in config and config['transformation']:
            data = self._apply_data_transformation(data, config)
        
        # Handle standard chart types directly
        standard_chart_generators = {
            'histogram': self._generate_histogram,
            'scatter': self._generate_scatter,
            'line': self._generate_line,
            'bar': self._generate_bar,
            'pie': self._generate_pie,
            'box': self._generate_box,
            'heatmap': self._generate_heatmap
        }
        
        # Check if it's a standard chart type
        if chart_type in standard_chart_generators:
            return standard_chart_generators[chart_type](data, config, language)
        
        # Fall back to existing chart generation methods for legacy types
        legacy_chart_generators = {
            'fraud_distribution': self._generate_fraud_distribution,
            'amount_distribution': self._generate_amount_distribution,
            'time_series': self._generate_time_series
        }
        
        if chart_type in legacy_chart_generators:
            return legacy_chart_generators[chart_type](data)
        
        # If chart type is not supported, raise an error
        raise ValueError(f"Unsupported chart type: {chart_type}")
    
    def _apply_data_transformation(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Apply data transformations based on AI configuration."""
        transformation = config.get('transformation', '').lower()
        
        if not transformation:
            return data
        
        # Handle first digit/character extraction
        if any(keyword in transformation for keyword in ['primeiro', 'first', 'dígito', 'digit', 'caractere', 'character']):
            # Find the source column from x_column or detect from transformation description
            source_column = config.get('x_column')
            
            if not source_column:
                # Try to detect column from transformation text
                for col in data.columns:
                    if col.lower() in transformation:
                        source_column = col
                        break
            
            if source_column and source_column in data.columns:
                
                # Create new column with first character/digit
                first_char_col = f"first_char_of_{source_column}"
                data[first_char_col] = data[source_column].astype(str).str[0]
                
                # Count frequencies
                freq_data = data[first_char_col].value_counts().reset_index()
                freq_data.columns = [first_char_col, 'count']
                
                # Ensure all digits 0-9 are present if dealing with digits
                if 'dígito' in transformation or 'digit' in transformation:
                    all_digits = pd.DataFrame({first_char_col: [str(i) for i in range(10)]})
                    freq_data = all_digits.merge(freq_data, on=first_char_col, how='left')
                    freq_data['count'] = freq_data['count'].fillna(0)
                
                # Update config to use the new columns
                config['x_column'] = first_char_col
                config['y_column'] = 'count'
                
                return freq_data
        
        # Handle other transformations as needed
        # Add more transformation logic here
        
        return data
    
    def _generate_histogram(self, data: pd.DataFrame, config: Dict, language: str) -> str:
        """Generate a histogram chart."""
        plt.figure(figsize=(10, 6))
        
        # Find the best numeric column for histogram
        numeric_columns = data.select_dtypes(include=['number']).columns
        if len(numeric_columns) == 0:
            raise ValueError("No numeric columns found for histogram")
        
        # Use the first numeric column or a specific one if mentioned in config
        column = numeric_columns[0]
        
        # Create histogram
        plt.hist(data[column].dropna(), bins=30, alpha=0.7, edgecolor='black')
        
        # Set labels based on language
        if language == 'pt_BR':
            plt.title(f'Histograma de {column}')
            plt.xlabel(column)
            plt.ylabel('Frequência')
        else:
            plt.title(f'Histogram of {column}')
            plt.xlabel(column)
            plt.ylabel('Frequency')
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return self._save_and_return_path()
    
    def generate_custom_chart(self, data: pd.DataFrame, user_description: str, language: str = 'en_US', conversation_history: List[str] = None) -> str:
        """
        Generate a custom chart based on user's natural language description.
        
        Args:
            data (pd.DataFrame): Data to visualize
            user_description (str): Natural language description of desired chart
            language (str): Language for chart labels and AI interaction
            
        Returns:
            str: Path to the generated chart image
            
        Raises:
            ValueError: If description is invalid or chart cannot be generated
        """
        if data is None or data.empty:
            raise ValueError("Data cannot be None or empty")
        
        if not user_description or not user_description.strip():
            raise ValueError("Chart description cannot be empty")
        
        # Get AI interpretation of the user's request
        chart_config = self._interpret_custom_chart_request(data, user_description, language, conversation_history)
        
        if not chart_config:
            raise ValueError("Could not interpret chart request")
        
        # Generate the chart based on AI interpretation
        return self._generate_enhanced_chart(data, chart_config['type'], chart_config, language)
    
    def _interpret_custom_chart_request(self, data: pd.DataFrame, user_description: str, language: str, conversation_history: List[str] = None) -> Dict:
        """
        Use AI to interpret user's natural language chart request.
        
        Args:
            data (pd.DataFrame): Available data
            user_description (str): User's chart description
            language (str): Language for AI interaction
            
        Returns:
            Dict: Chart configuration with type, columns, and parameters
        """
        try:
            # Analyze data structure
            data_info = self._analyze_data_structure(data)
            
            # Build conversation context if available
            context = ""
            if conversation_history and len(conversation_history) > 0:
                if language == 'pt_BR':
                    context = f"\nCONTEXTO DA CONVERSA ANTERIOR:\n"
                    for i, entry in enumerate(conversation_history[-5:], 1):  # Last 5 entries
                        context += f"{i}. {entry}\n"
                else:
                    context = f"\nPREVIOUS CONVERSATION CONTEXT:\n"
                    for i, entry in enumerate(conversation_history[-5:], 1):  # Last 5 entries
                        context += f"{i}. {entry}\n"
            
            # Create prompt for AI interpretation
            if language == 'pt_BR':
                prompt = f"""
                Analise a seguinte solicitação de gráfico do usuário e os dados disponíveis.
                
                DADOS DISPONÍVEIS:
                {data_info}
                {context}
                SOLICITAÇÃO DO USUÁRIO:
                "{user_description}"
                
                Por favor, interprete a solicitação e retorne APENAS um JSON válido com a seguinte estrutura:
                {{
                    "type": "histogram|scatter|line|bar|pie|box|heatmap",
                    "x_column": "nome_da_coluna_x",
                    "y_column": "nome_da_coluna_y",
                    "title": "Título do gráfico (máximo 6 palavras)",
                    "description": "Breve descrição do gráfico",
                    "transformation": "Descrição de qualquer transformação necessária nos dados (opcional)"
                }}
                
                REGRAS:
                - Use apenas colunas que existem nos dados
                - Para histograma: apenas x_column é necessário
                - Para gráfico de pizza: apenas x_column (categórica) é necessário
                - Para scatter/line: x_column e y_column são necessários
                - Para bar: x_column (categorical) e opcionalmente y_column
                - Para box: x_column (numérica) é necessário
                - Para heatmap: use correlações entre colunas numéricas
                - Se a solicitação mencionar "primeiro dígito", "primeiros caracteres", ou transformações similares, inclua isso no campo "transformation"
                - Para agrupamentos especiais, use o campo "transformation" para descrever a operação
                - Considere o contexto da conversa anterior para melhor interpretação
                """
            else:
                prompt = f"""
                Analyze the following user chart request and available data.
                
                AVAILABLE DATA:
                {data_info}
                {context}
                USER REQUEST:
                "{user_description}"
                
                Please interpret the request and return ONLY a valid JSON with this structure:
                {{
                    "type": "histogram|scatter|line|bar|pie|box|heatmap",
                    "x_column": "x_column_name",
                    "y_column": "y_column_name",
                    "title": "Chart title (max 6 words)",
                    "description": "Brief chart description",
                    "transformation": "Description of any data transformation needed (optional)"
                }}
                
                RULES:
                - Use only columns that exist in the data
                - For histogram: only x_column is needed
                - For pie chart: only x_column (categorical) is needed
                - For scatter/line: both x_column and y_column are needed
                - For bar: x_column (categorical) and optionally y_column
                - For box: x_column (numerical) is needed
                - For heatmap: use correlations between numerical columns
                - If the request mentions "first digit", "first characters", or similar transformations, include this in the "transformation" field
                - For special groupings, use the "transformation" field to describe the operation
                - Consider the previous conversation context for better interpretation
                """
            
            print(f"DEBUG: Sending prompt to AI model...")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean and parse JSON response
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].strip()
            
            import json
            chart_config = json.loads(response_text)
            
            # Validate the configuration
            if not self._validate_chart_config(chart_config, data):
                return None
            
            return chart_config
            
        except Exception as e:
            return None
    
    def _validate_chart_config(self, config: Dict, data: pd.DataFrame) -> bool:
        """
        Validate that the chart configuration is valid for the given data.
        
        Args:
            config (Dict): Chart configuration
            data (pd.DataFrame): Available data
            
        Returns:
            bool: True if configuration is valid
        """
        try:
            # Check required fields
            if 'type' not in config:
                return False
            
            chart_type = config['type']
            if chart_type not in ['histogram', 'scatter', 'line', 'bar', 'pie', 'box', 'heatmap']:
                return False
            
            # Check if transformation is specified - if so, skip column existence checks
            # as the columns will be created during transformation
            has_transformation = config.get('transformation') and config['transformation'].strip()
            
            if not has_transformation:
                # Check column existence only if no transformation is specified
                if 'x_column' in config and config['x_column']:
                    if config['x_column'] not in data.columns:
                        return False
                
                if 'y_column' in config and config['y_column']:
                    if config['y_column'] not in data.columns:
                        return False
            
            # Type-specific validation
            if chart_type in ['scatter', 'line'] and not (config.get('x_column') and config.get('y_column')):
                return False
            
            if chart_type in ['histogram', 'pie', 'box'] and not config.get('x_column'):
                return False
            
            return True
            
        except Exception as e:
            return False
    
    def _generate_scatter(self, data: pd.DataFrame, config: Dict, language: str) -> str:
        """Generate a scatter plot."""
        plt.figure(figsize=(10, 6))
        
        # Find numeric columns for scatter plot
        numeric_columns = data.select_dtypes(include=['number']).columns
        if len(numeric_columns) < 2:
            raise ValueError("Need at least 2 numeric columns for scatter plot")
        
        x_col, y_col = numeric_columns[0], numeric_columns[1]
        
        plt.scatter(data[x_col], data[y_col], alpha=0.6)
        
        # Set labels based on language
        if language == 'pt_BR':
            plt.title(f'Gráfico de Dispersão: {x_col} vs {y_col}')
            plt.xlabel(x_col)
            plt.ylabel(y_col)
        else:
            plt.title(f'Scatter Plot: {x_col} vs {y_col}')
            plt.xlabel(x_col)
            plt.ylabel(y_col)
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return self._save_and_return_path()
    
    def _generate_line(self, data: pd.DataFrame, config: Dict, language: str) -> str:
        """Generate a line chart."""
        plt.figure(figsize=(12, 6))
        
        # Find numeric columns
        numeric_columns = data.select_dtypes(include=['number']).columns
        if len(numeric_columns) == 0:
            raise ValueError("No numeric columns found for line chart")
        
        # Use index as x-axis and first numeric column as y-axis
        y_col = numeric_columns[0]
        plt.plot(data.index, data[y_col], marker='o', linewidth=2, markersize=4)
        
        # Set labels based on language
        if language == 'pt_BR':
            plt.title(f'Gráfico de Linha: {y_col}')
            plt.xlabel('Índice')
            plt.ylabel(y_col)
        else:
            plt.title(f'Line Chart: {y_col}')
            plt.xlabel('Index')
            plt.ylabel(y_col)
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return self._save_and_return_path()
    
    def _generate_bar(self, data: pd.DataFrame, config: Dict, language: str) -> str:
        """Generate a bar chart with AI configuration support."""
        plt.figure(figsize=(10, 6))
        
        # Get configuration from AI
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        title = config.get('title', '')
        xlabel = config.get('xlabel', '')
        ylabel = config.get('ylabel', '')
        
        # If we have both x and y columns specified, use them directly
        if x_col and y_col and x_col in data.columns and y_col in data.columns:
            plt.bar(data[x_col], data[y_col])
            
            plt.title(title or f'{y_col} by {x_col}')
            plt.xlabel(xlabel or x_col)
            plt.ylabel(ylabel or y_col)
            
        # If only x_column is specified, count occurrences
        elif x_col and x_col in data.columns:
            grouped_data = data[x_col].value_counts().sort_index()
            plt.bar(grouped_data.index, grouped_data.values)
            
            plt.title(title or f'Count by {x_col}')
            plt.xlabel(xlabel or x_col)
            plt.ylabel(ylabel or ('Contagem' if language == 'pt_BR' else 'Count'))
            
        else:
            # Fallback to automatic column selection
            categorical_columns = data.select_dtypes(include=['object', 'category']).columns
            numeric_columns = data.select_dtypes(include=['number']).columns
            
            if len(categorical_columns) > 0:
                cat_col = categorical_columns[0]
                grouped_data = data.groupby(cat_col).size()
                plt.bar(grouped_data.index, grouped_data.values)
                
                plt.title(title or f'Count by {cat_col}')
                plt.xlabel(xlabel or cat_col)
                plt.ylabel(ylabel or ('Contagem' if language == 'pt_BR' else 'Count'))
            else:
                raise ValueError("No suitable columns found for bar chart")
        
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return self._save_and_return_path()
    
    def _generate_pie(self, data: pd.DataFrame, config: Dict, language: str) -> str:
        """Generate a pie chart."""
        plt.figure(figsize=(8, 8))
        
        # Find categorical columns
        categorical_columns = data.select_dtypes(include=['object', 'category']).columns
        if len(categorical_columns) == 0:
            raise ValueError("No categorical columns found for pie chart")
        
        cat_col = categorical_columns[0]
        value_counts = data[cat_col].value_counts()
        
        plt.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%', startangle=90)
        
        # Set title based on language
        if language == 'pt_BR':
            plt.title(f'Gráfico de Pizza: Distribuição de {cat_col}')
        else:
            plt.title(f'Pie Chart: Distribution of {cat_col}')
        
        plt.axis('equal')
        plt.tight_layout()
        
        return self._save_and_return_path()
    
    def _generate_box(self, data: pd.DataFrame, config: Dict, language: str) -> str:
        """Generate a box plot."""
        plt.figure(figsize=(10, 6))
        
        # Find numeric columns
        numeric_columns = data.select_dtypes(include=['number']).columns
        if len(numeric_columns) == 0:
            raise ValueError("No numeric columns found for box plot")
        
        # Create box plot for all numeric columns
        data[numeric_columns].boxplot()
        
        # Set labels based on language
        if language == 'pt_BR':
            plt.title('Gráfico de Caixa')
            plt.ylabel('Valores')
        else:
            plt.title('Box Plot')
            plt.ylabel('Values')
        
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return self._save_and_return_path()
    
    def _generate_heatmap(self, data: pd.DataFrame, config: Dict, language: str) -> str:
        """Generate a heatmap of correlations."""
        plt.figure(figsize=(10, 8))
        
        # Find numeric columns for correlation
        numeric_columns = data.select_dtypes(include=['number']).columns
        if len(numeric_columns) < 2:
            raise ValueError("Need at least 2 numeric columns for heatmap")
        
        # Calculate correlation matrix
        correlation_matrix = data[numeric_columns].corr()
        
        # Create heatmap
        import matplotlib.pyplot as plt
        import numpy as np
        
        im = plt.imshow(correlation_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        plt.colorbar(im)
        
        # Set ticks and labels
        plt.xticks(range(len(correlation_matrix.columns)), correlation_matrix.columns, rotation=45)
        plt.yticks(range(len(correlation_matrix.columns)), correlation_matrix.columns)
        
        # Add correlation values as text
        for i in range(len(correlation_matrix.columns)):
            for j in range(len(correlation_matrix.columns)):
                plt.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}', 
                        ha='center', va='center', color='white' if abs(correlation_matrix.iloc[i, j]) > 0.5 else 'black')
        
        # Set title based on language
        if language == 'pt_BR':
            plt.title('Mapa de Calor: Correlações')
        else:
            plt.title('Heatmap: Correlations')
        
        plt.tight_layout()
        
        return self._save_and_return_path()