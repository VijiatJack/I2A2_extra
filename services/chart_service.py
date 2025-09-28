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
    
    def get_supported_chart_types(self) -> dict:
        """
        Get supported chart types with descriptions.
        
        Returns:
            dict: Dictionary of chart types and their descriptions
        """
        return {
            'fraud_distribution': 'Fraud vs Regular Distribution',
            'amount_distribution': 'Amount Distribution',
            'time_series': 'Transactions Over Time'
        }
    
    def validate_chart_requirements(self, data: pd.DataFrame, chart_type: str) -> Tuple[bool, str]:
        """
        Validate if data meets requirements for the specified chart type.
        
        Args:
            data (pd.DataFrame): Data to validate
            chart_type (str): Type of chart to validate for
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if data is None or data.empty:
            return False, "Data cannot be None or empty"
        
        if chart_type == 'fraud_distribution':
            return True, ""  # Can work with any data
        
        elif chart_type == 'amount_distribution':
            amount_columns = [col for col in data.columns if 'amount' in col.lower() or 'value' in col.lower()]
            numeric_columns = data.select_dtypes(include=['number']).columns
            
            if not amount_columns and len(numeric_columns) == 0:
                return False, "No numeric columns found for amount distribution"
            return True, ""
        
        elif chart_type == 'time_series':
            time_columns = [col for col in data.columns if 'time' in col.lower() or 'date' in col.lower()]
            if not time_columns:
                return False, "No time columns found for time series chart"
            return True, ""
        
        else:
            return False, f"Unsupported chart type: {chart_type}"
    
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
        
        try:
            response = self.model.generate_content(prompt)
            suggestions = self._parse_chart_suggestions(response.text)
            return suggestions
        except Exception as e:
            # Fallback to default suggestions
            return self._get_default_chart_suggestions(data, language)
    
    def _get_ai_chart_suggestions(self, data: pd.DataFrame, chart_type: str, language: str) -> Dict:
        """Get AI suggestions for chart configuration."""
        data_info = self._analyze_data_structure(data)
        
        if language == 'pt_BR':
            prompt = f"""
            Para um gráfico do tipo '{chart_type}' com os seguintes dados:
            
            {data_info}
            
            Sugira:
            1. Título apropriado em português
            2. Rótulos dos eixos em português
            3. Cores recomendadas
            4. Colunas mais relevantes para usar
            
            Responda em formato JSON.
            """
        else:
            prompt = f"""
            For a '{chart_type}' chart with the following data:
            
            {data_info}
            
            Suggest:
            1. Appropriate title in English
            2. Axis labels in English
            3. Recommended colors
            4. Most relevant columns to use
            
            Respond in JSON format.
            """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse the JSON response (simplified for now)
            return {
                'title': f"Data Visualization - {chart_type.replace('_', ' ').title()}",
                'xlabel': 'X Axis',
                'ylabel': 'Y Axis',
                'colors': ['#1f77b4', '#ff7f0e', '#2ca02c']
            }
        except Exception:
            return {
                'title': f"Data Visualization - {chart_type.replace('_', ' ').title()}",
                'xlabel': 'X Axis',
                'ylabel': 'Y Axis',
                'colors': ['#1f77b4', '#ff7f0e', '#2ca02c']
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
        """Get default chart suggestions as fallback."""
        if language == 'pt_BR':
            return {
                'histogram': 'Histograma - Distribuição de valores numéricos',
                'scatter': 'Gráfico de Dispersão - Relação entre duas variáveis',
                'bar': 'Gráfico de Barras - Comparação de categorias',
                'line': 'Gráfico de Linha - Tendências ao longo do tempo'
            }
        else:
            return {
                'histogram': 'Histogram - Distribution of numeric values',
                'scatter': 'Scatter Plot - Relationship between two variables',
                'bar': 'Bar Chart - Comparison of categories',
                'line': 'Line Chart - Trends over time'
            }
    
    def _generate_enhanced_chart(self, data: pd.DataFrame, chart_type: str, config: Dict, language: str) -> str:
        """Generate enhanced chart with AI suggestions."""
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
        """Generate a bar chart."""
        plt.figure(figsize=(10, 6))
        
        # Find categorical and numeric columns
        categorical_columns = data.select_dtypes(include=['object', 'category']).columns
        numeric_columns = data.select_dtypes(include=['number']).columns
        
        if len(categorical_columns) == 0 or len(numeric_columns) == 0:
            raise ValueError("Need both categorical and numeric columns for bar chart")
        
        cat_col = categorical_columns[0]
        num_col = numeric_columns[0]
        
        # Group by categorical column and sum numeric values
        grouped_data = data.groupby(cat_col)[num_col].sum()
        
        plt.bar(grouped_data.index, grouped_data.values)
        
        # Set labels based on language
        if language == 'pt_BR':
            plt.title(f'Gráfico de Barras: {num_col} por {cat_col}')
            plt.xlabel(cat_col)
            plt.ylabel(num_col)
        else:
            plt.title(f'Bar Chart: {num_col} by {cat_col}')
            plt.xlabel(cat_col)
            plt.ylabel(num_col)
        
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