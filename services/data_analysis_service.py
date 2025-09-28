"""
Data Analysis Service for comprehensive data representation to AI agents.

This service provides intelligent data sampling, statistical summaries, and 
comprehensive data context to enable better AI analysis and insights.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import json


class DataAnalysisService:
    """Service for providing comprehensive data analysis and intelligent sampling."""
    
    def __init__(self, max_sample_size: int = 100, chunk_size: int = 1000):
        """
        Initialize the data analysis service.
        
        Args:
            max_sample_size: Maximum number of rows to include in samples
            chunk_size: Size of chunks for processing large datasets
        """
        self.max_sample_size = max_sample_size
        self.chunk_size = chunk_size
    
    def get_comprehensive_data_info(self, data: pd.DataFrame) -> str:
        """
        Get comprehensive information about the DataFrame for AI analysis.
        
        Args:
            data: The DataFrame to analyze
            
        Returns:
            str: Comprehensive data information formatted for AI consumption
        """
        info_sections = []
        
        # Basic information
        info_sections.append(self._get_basic_info(data))
        
        # Data quality assessment
        info_sections.append(self._get_data_quality_info(data))
        
        # Statistical summary
        info_sections.append(self._get_statistical_summary(data))
        
        # Intelligent sampling
        info_sections.append(self._get_intelligent_sample(data))
        
        # Pattern analysis
        info_sections.append(self._get_pattern_analysis(data))
        
        return "\n\n".join(info_sections)
    
    def _get_basic_info(self, data: pd.DataFrame) -> str:
        """Get basic dataset information."""
        info = "=== DATASET OVERVIEW ===\n"
        info += f"• Total rows: {len(data):,}\n"
        info += f"• Total columns: {len(data.columns)}\n"
        info += f"• Memory usage: {data.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n"
        info += f"• Columns: {', '.join(data.columns)}"
        return info
    
    def _get_data_quality_info(self, data: pd.DataFrame) -> str:
        """Analyze data quality issues."""
        info = "=== DATA QUALITY ASSESSMENT ===\n"
        
        # Missing values
        missing_info = data.isnull().sum()
        missing_pct = (missing_info / len(data) * 100).round(2)
        
        if missing_info.sum() > 0:
            info += "Missing values:\n"
            for col in missing_info[missing_info > 0].index:
                info += f"  • {col}: {missing_info[col]} ({missing_pct[col]}%)\n"
        else:
            info += "• No missing values detected\n"
        
        # Duplicate rows
        duplicates = data.duplicated().sum()
        if duplicates > 0:
            info += f"• Duplicate rows: {duplicates} ({duplicates/len(data)*100:.2f}%)\n"
        else:
            info += "• No duplicate rows detected\n"
        
        # Data types
        info += "\nData types:\n"
        for col, dtype in data.dtypes.items():
            unique_count = data[col].nunique()
            info += f"  • {col}: {dtype} ({unique_count:,} unique values)\n"
        
        return info
    
    def _get_statistical_summary(self, data: pd.DataFrame) -> str:
        """Get comprehensive statistical summary."""
        info = "=== STATISTICAL SUMMARY ===\n"
        
        # Numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            info += "Numeric columns summary:\n"
            stats = data[numeric_cols].describe()
            info += stats.to_string()
            info += "\n\n"
        
        # Categorical columns
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            info += "Categorical columns summary:\n"
            for col in categorical_cols:
                unique_count = data[col].nunique()
                most_common = data[col].value_counts().head(3)
                info += f"  • {col}: {unique_count} unique values\n"
                info += f"    Top values: {dict(most_common)}\n"
        
        return info
    
    def _get_intelligent_sample(self, data: pd.DataFrame) -> str:
        """Get intelligent sample of the data."""
        info = "=== INTELLIGENT DATA SAMPLE ===\n"
        
        sample_data = self._create_intelligent_sample(data)
        
        info += f"Sample strategy: {sample_data['strategy']}\n"
        info += f"Sample size: {len(sample_data['data'])} rows\n\n"
        
        info += "Sample data:\n"
        info += sample_data['data'].to_string(max_rows=50, max_cols=10)
        
        if sample_data.get('additional_info'):
            info += f"\n\nAdditional sampling info:\n{sample_data['additional_info']}"
        
        return info
    
    def _create_intelligent_sample(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Create an intelligent sample of the data based on various strategies.
        
        Returns:
            Dict containing sample data, strategy used, and additional info
        """
        total_rows = len(data)
        
        if total_rows <= self.max_sample_size:
            return {
                'data': data,
                'strategy': 'Complete dataset (small size)',
                'additional_info': None
            }
        
        # For larger datasets, use stratified sampling if possible
        sample_strategies = []
        
        # Strategy 1: Random sampling with head/tail
        head_tail_sample = pd.concat([
            data.head(self.max_sample_size // 3),
            data.sample(n=self.max_sample_size // 3, random_state=42),
            data.tail(self.max_sample_size // 3)
        ]).drop_duplicates()
        
        sample_strategies.append({
            'data': head_tail_sample,
            'strategy': 'Head + Random + Tail sampling',
            'additional_info': f'Includes first {self.max_sample_size // 3}, random {self.max_sample_size // 3}, and last {self.max_sample_size // 3} rows'
        })
        
        # Strategy 2: Stratified sampling if categorical columns exist
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            try:
                # Use the first categorical column for stratification
                strat_col = categorical_cols[0]
                stratified_sample = data.groupby(strat_col, group_keys=False).apply(
                    lambda x: x.sample(min(len(x), max(1, self.max_sample_size // data[strat_col].nunique())), 
                                     random_state=42)
                ).reset_index(drop=True)
                
                sample_strategies.append({
                    'data': stratified_sample.head(self.max_sample_size),
                    'strategy': f'Stratified sampling by {strat_col}',
                    'additional_info': f'Stratified by {strat_col} with {data[strat_col].nunique()} categories'
                })
            except:
                pass
        
        # Return the best strategy (prefer stratified if available)
        return sample_strategies[-1] if len(sample_strategies) > 1 else sample_strategies[0]
    
    def _get_pattern_analysis(self, data: pd.DataFrame) -> str:
        """Analyze patterns and relationships in the data."""
        info = "=== PATTERN ANALYSIS ===\n"
        
        # Correlation analysis for numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = data[numeric_cols].corr()
            
            # Find strong correlations
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:  # Strong correlation threshold
                        strong_corr.append((
                            corr_matrix.columns[i], 
                            corr_matrix.columns[j], 
                            corr_val
                        ))
            
            if strong_corr:
                info += "Strong correlations (|r| > 0.7):\n"
                for col1, col2, corr_val in strong_corr:
                    info += f"  • {col1} ↔ {col2}: {corr_val:.3f}\n"
            else:
                info += "• No strong correlations detected\n"
        
        # Value distribution analysis
        info += "\nValue distribution insights:\n"
        for col in data.columns:
            if data[col].dtype in ['object', 'category']:
                # Categorical distribution
                value_counts = data[col].value_counts()
                if len(value_counts) <= 10:
                    info += f"  • {col}: Evenly distributed across {len(value_counts)} categories\n"
                else:
                    top_pct = value_counts.iloc[0] / len(data) * 100
                    info += f"  • {col}: {len(value_counts)} categories, top category: {top_pct:.1f}%\n"
            else:
                # Numeric distribution
                skewness = data[col].skew()
                if abs(skewness) > 1:
                    direction = "right" if skewness > 0 else "left"
                    info += f"  • {col}: Highly skewed {direction} (skew: {skewness:.2f})\n"
        
        return info
    
    def get_chunked_analysis(self, data: pd.DataFrame, analysis_type: str = "summary") -> List[Dict[str, Any]]:
        """
        Analyze large datasets in chunks for memory efficiency.
        
        Args:
            data: The DataFrame to analyze
            analysis_type: Type of analysis ('summary', 'patterns', 'quality')
            
        Returns:
            List of analysis results for each chunk
        """
        chunks = []
        total_rows = len(data)
        
        for start_idx in range(0, total_rows, self.chunk_size):
            end_idx = min(start_idx + self.chunk_size, total_rows)
            chunk = data.iloc[start_idx:end_idx]
            
            chunk_analysis = {
                'chunk_id': len(chunks) + 1,
                'start_row': start_idx + 1,
                'end_row': end_idx,
                'size': len(chunk)
            }
            
            if analysis_type == "summary":
                chunk_analysis['analysis'] = self._get_statistical_summary(chunk)
            elif analysis_type == "quality":
                chunk_analysis['analysis'] = self._get_data_quality_info(chunk)
            elif analysis_type == "patterns":
                chunk_analysis['analysis'] = self._get_pattern_analysis(chunk)
            
            chunks.append(chunk_analysis)
        
        return chunks
    
    def get_ai_optimized_context(self, data: pd.DataFrame, context_type: str = "comprehensive") -> str:
        """
        Get AI-optimized data context based on the specific needs.
        
        Args:
            data: The DataFrame to analyze
            context_type: Type of context needed ('comprehensive', 'quick', 'statistical')
            
        Returns:
            str: Formatted context optimized for AI consumption
        """
        if context_type == "quick":
            return f"{self._get_basic_info(data)}\n\n{self._get_intelligent_sample(data)}"
        elif context_type == "statistical":
            return f"{self._get_basic_info(data)}\n\n{self._get_statistical_summary(data)}"
        else:  # comprehensive
            return self.get_comprehensive_data_info(data)