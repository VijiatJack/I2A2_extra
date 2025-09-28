# CSV Format Documentation

This document describes the supported CSV file formats that work with the CSV AI Parser application.

## General CSV Requirements

### Basic Format
- **File Extension**: `.csv`
- **Encoding**: UTF-8 (recommended), Latin-1, ISO-8859-1, or CP1252
- **Headers**: First row must contain column names
- **Separator**: Comma (`,`), Pipe (`|`), Semicolon (`;`), or Tab (`\t`) - automatically detected
- **Decimal Separator**: Period (`.`) for numeric values

### File Structure
```csv
Column1,Column2,Column3,...
value1,value2,value3,...
value1,value2,value3,...
```

Or with pipe separator:
```csv
Column1|Column2|Column3|...
value1|value2|value3|...
value1|value2|value3|...
```

## Supported Data Types

The application can analyze various types of CSV files, but works particularly well with:

### 1. **Fraud Detection Datasets**
For optimal fraud detection analysis, include these columns:

#### Required Columns:
- **Class** or **fraud** or **is_fraud**: Binary indicator (0/1 or False/True)
  - `0` or `False` = Regular/Normal transaction
  - `1` or `True` = Fraudulent transaction

#### Recommended Columns:
- **Time**: Timestamp or time-related information
- **Amount**: Transaction amount (numeric)
- **V1, V2, ..., V28**: Feature columns (common in anonymized datasets)

#### Example Structure:
```csv
Time,V1,V2,V3,...,V28,Amount,Class
0,1.234,-0.567,2.345,...,-1.234,149.62,0
1,2.345,1.234,-0.567,...,0.567,2.69,0
2,-1.234,0.567,1.234,...,2.345,378.66,1
```

### 2. **General Datasets**
The application can analyze any CSV with:
- **Numeric columns**: For statistical analysis
- **Categorical columns**: For distribution analysis
- **Date/Time columns**: For temporal analysis
- **Text columns**: For basic analysis

#### Example Structure:
```csv
Date,Category,Amount,Status,Description
2024-01-01,Food,25.50,Completed,Restaurant purchase
2024-01-02,Transport,15.00,Completed,Bus ticket
2024-01-03,Shopping,125.99,Pending,Online purchase
```

## Data Quality Guidelines

### Best Practices
1. **Clean Headers**: Use descriptive, single-word column names
2. **Consistent Data Types**: Keep the same data type within each column
3. **Handle Missing Values**: Use empty cells or consistent placeholders (e.g., "N/A")
4. **Numeric Formatting**: Use consistent decimal notation
5. **Date Formatting**: Use standard date formats (YYYY-MM-DD, MM/DD/YYYY, etc.)

### Common Issues to Avoid
- **Mixed Data Types**: Don't mix numbers and text in the same column
- **Special Characters**: Avoid special characters in headers
- **Inconsistent Formatting**: Keep date and number formats consistent
- **Very Large Files**: Files over 100MB may take longer to process

## Example Datasets That Work Well

### 1. Credit Card Fraud Detection
```csv
Time,V1,V2,V3,V4,V5,Amount,Class
0,-1.359807,-0.072781,2.536347,1.378155,-0.338321,149.62,0
1,1.191857,0.266151,0.166480,0.448154,0.060018,2.69,0
2,-1.358354,-1.340163,1.773209,0.379780,-0.503198,378.66,1
```

### 2. Sales Data
```csv
Date,Product,Category,Amount,Quantity,Customer_Type
2024-01-01,Laptop,Electronics,999.99,1,Premium
2024-01-01,Mouse,Electronics,29.99,2,Regular
2024-01-02,Coffee,Food,4.50,1,Regular
```

### 3. Financial Transactions
```csv
Transaction_ID,Date,Amount,Type,Account,Balance
TXN001,2024-01-01,500.00,Deposit,Checking,1500.00
TXN002,2024-01-01,-50.00,Withdrawal,Checking,1450.00
TXN003,2024-01-02,1000.00,Transfer,Savings,2450.00
```

## Supported Analysis Types

Based on your CSV format, the application can provide:

### For Fraud Detection Data:
- Fraud vs. regular transaction distribution
- Amount analysis by transaction type
- Temporal pattern analysis
- Anomaly detection
- Feature correlation analysis

### For General Data:
- Statistical summaries (mean, median, std dev)
- Distribution analysis
- Missing value analysis
- Data quality assessment
- Trend analysis (if time data is present)

## File Size Recommendations

- **Optimal**: 1MB - 50MB
- **Good**: 50MB - 100MB
- **Acceptable**: 100MB - 500MB
- **Large**: 500MB+ (may require longer processing time)

## Getting Started

1. Prepare your CSV file following the guidelines above
2. Upload it to the application
3. The system will automatically detect the format and provide appropriate analysis
4. Ask questions in natural language about your data

## Need Help?

If your CSV file doesn't work as expected:
1. Check that it follows the basic format requirements
2. Ensure headers are in the first row
3. Verify data consistency within columns
4. Try with a smaller sample of your data first

For fraud detection specifically, make sure you have a binary classification column (Class, fraud, or is_fraud).