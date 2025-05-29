import pandas as pd
import numpy as np
import io
import re
from typing import Optional, Dict, Any, List, Union
import streamlit as st

class FinancialDataProcessor:
    """
    Advanced Financial Data Processing and Analysis
    """
    
    def __init__(self):
        self.data = None
        self.original_data = None
        self.data_quality_score = 0.0
        self.statement_type = None
        self.numeric_columns = []
        self.text_columns = []
        
        # Common financial account patterns for auto-detection
        self.account_patterns = {
            'Balance Sheet': {
                'assets': ['cash', 'receivable', 'inventory', 'asset', 'equipment', 'property'],
                'liabilities': ['payable', 'debt', 'liability', 'loan', 'note'],
                'equity': ['equity', 'capital', 'retained', 'earnings', 'stock']
            },
            'Income Statement': {
                'revenue': ['revenue', 'sales', 'income', 'fees'],
                'expenses': ['expense', 'cost', 'depreciation', 'interest', 'tax'],
                'profit': ['profit', 'earnings', 'margin', 'ebitda']
            },
            'Cash Flow Statement': {
                'operating': ['operating', 'operations', 'working capital'],
                'investing': ['investing', 'investment', 'capex', 'acquisition'],
                'financing': ['financing', 'dividend', 'debt', 'equity']
            }
        }
    
    def load_data(self, uploaded_file) -> bool:
        """
        Load and process uploaded financial data
        """
        try:
            # Get file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            # Read file based on extension
            if file_extension in ['xlsx', 'xls']:
                self.data = pd.read_excel(uploaded_file, engine='openpyxl')
            elif file_extension == 'csv':
                # Try different encodings
                try:
                    self.data = pd.read_csv(uploaded_file, encoding='utf-8')
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    self.data = pd.read_csv(uploaded_file, encoding='latin-1')
            else:
                st.error(f"Unsupported file format: {file_extension}")
                return False
            
            # Store original data
            self.original_data = self.data.copy()
            
            # Clean and process data
            self._clean_data()
            self._identify_column_types()
            self._assess_data_quality()
            
            return True
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return False
    
    def _clean_data(self):
        """
        Clean and standardize the data
        """
        if self.data is None:
            return
        
        # Remove completely empty rows and columns
        self.data = self.data.dropna(how='all').dropna(axis=1, how='all')
        
        # Clean column names
        self.data.columns = self.data.columns.astype(str)
        self.data.columns = [col.strip() for col in self.data.columns]
        
        # Handle numeric columns
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                # Try to convert to numeric if it looks like numbers
                numeric_series = pd.to_numeric(self.data[col], errors='coerce')
                if not numeric_series.isna().all():
                    # If more than 50% of values are numeric, convert the column
                    if (numeric_series.notna().sum() / len(numeric_series)) > 0.5:
                        self.data[col] = numeric_series
        
        # Reset index
        self.data = self.data.reset_index(drop=True)
    
    def _identify_column_types(self):
        """
        Identify numeric and text columns
        """
        if self.data is None:
            return
        
        self.numeric_columns = list(self.data.select_dtypes(include=[np.number]).columns)
        self.text_columns = list(self.data.select_dtypes(include=['object']).columns)
    
    def _assess_data_quality(self):
        """
        Assess overall data quality
        """
        if self.data is None:
            self.data_quality_score = 0.0
            return
        
        total_cells = self.data.size
        non_null_cells = self.data.count().sum()
        
        # Calculate completeness score
        completeness = (non_null_cells / total_cells) * 100 if total_cells > 0 else 0
        
        # Adjust for data consistency and format
        consistency_bonus = 0
        if len(self.numeric_columns) > 0:
            consistency_bonus += 10  # Bonus for having numeric data
        
        if len(self.data.columns) >= 3:
            consistency_bonus += 5   # Bonus for reasonable number of columns
        
        self.data_quality_score = min(100, completeness + consistency_bonus)
    
    def assess_data_quality(self) -> float:
        """
        Return data quality score
        """
        return self.data_quality_score
    
    def get_numeric_columns(self) -> List[str]:
        """
        Get list of numeric columns
        """
        return self.numeric_columns
    
    def get_text_columns(self) -> List[str]:
        """
        Get list of text columns
        """
        return self.text_columns
    
    def detect_statement_type(self) -> str:
        """
        Automatically detect the type of financial statement
        """
        if self.data is None:
            return "Unknown"
        
        # Convert all text data to lowercase for pattern matching
        text_data = ""
        for col in self.text_columns:
            text_data += " " + " ".join(self.data[col].astype(str).str.lower())
        
        # Score each statement type
        scores = {}
        
        for statement_type, categories in self.account_patterns.items():
            score = 0
            for category, keywords in categories.items():
                for keyword in keywords:
                    score += text_data.count(keyword)
            scores[statement_type] = score
        
        # Return the statement type with highest score
        if max(scores.values()) > 0:
            detected_type = max(scores, key=scores.get)
            self.statement_type = detected_type
            return detected_type
        else:
            self.statement_type = "General Financial Data"
            return "General Financial Data"
    
    def calculate_financial_ratios(self, statement_type: str) -> Dict[str, float]:
        """
        Calculate financial ratios based on statement type
        """
        if self.data is None or len(self.numeric_columns) < 2:
            return {}
        
        ratios = {}
        
        try:
            if statement_type == "Balance Sheet":
                ratios.update(self._calculate_balance_sheet_ratios())
            elif statement_type == "Income Statement":
                ratios.update(self._calculate_income_statement_ratios())
            elif statement_type == "Cash Flow Statement":
                ratios.update(self._calculate_cash_flow_ratios())
            else:
                ratios.update(self._calculate_general_ratios())
        
        except Exception as e:
            st.warning(f"Some ratios could not be calculated: {str(e)}")
        
        return ratios
    
    def _calculate_balance_sheet_ratios(self) -> Dict[str, float]:
        """
        Calculate balance sheet specific ratios
        """
        ratios = {}
        
        # Find relevant accounts using pattern matching
        accounts = self._find_accounts_by_pattern()
        
        try:
            # Current Ratio
            if 'current_assets' in accounts and 'current_liabilities' in accounts:
                current_assets = self._get_account_value(accounts['current_assets'])
                current_liabilities = self._get_account_value(accounts['current_liabilities'])
                if current_liabilities != 0:
                    ratios['current_ratio'] = current_assets / current_liabilities
            
            # Quick Ratio (if cash and receivables can be identified)
            if all(k in accounts for k in ['cash', 'receivables', 'current_liabilities']):
                cash = self._get_account_value(accounts['cash'])
                receivables = self._get_account_value(accounts['receivables'])
                current_liabilities = self._get_account_value(accounts['current_liabilities'])
                if current_liabilities != 0:
                    ratios['quick_ratio'] = (cash + receivables) / current_liabilities
            
            # Debt to Equity
            if 'total_debt' in accounts and 'total_equity' in accounts:
                total_debt = self._get_account_value(accounts['total_debt'])
                total_equity = self._get_account_value(accounts['total_equity'])
                if total_equity != 0:
                    ratios['debt_to_equity'] = total_debt / total_equity
            
            # Asset ratios using largest values as proxies
            numeric_data = self.data[self.numeric_columns]
            if len(numeric_data.columns) >= 2:
                # Use largest values as total assets and equity proxies
                sorted_totals = numeric_data.iloc[-1].sort_values(ascending=False)
                if len(sorted_totals) >= 2:
                    total_assets = sorted_totals.iloc[0]
                    equity_proxy = sorted_totals.iloc[1]
                    if equity_proxy != 0:
                        ratios['asset_to_equity'] = total_assets / equity_proxy
        
        except Exception as e:
            pass  # Continue with other ratios
        
        return ratios
    
    def _calculate_income_statement_ratios(self) -> Dict[str, float]:
        """
        Calculate income statement specific ratios
        """
        ratios = {}
        
        accounts = self._find_accounts_by_pattern()
        
        try:
            # Gross Margin
            if 'revenue' in accounts and 'cost_of_sales' in accounts:
                revenue = self._get_account_value(accounts['revenue'])
                cogs = self._get_account_value(accounts['cost_of_sales'])
                if revenue != 0:
                    ratios['gross_margin'] = ((revenue - cogs) / revenue) * 100
            
            # Operating Margin
            if 'revenue' in accounts and 'operating_income' in accounts:
                revenue = self._get_account_value(accounts['revenue'])
                operating_income = self._get_account_value(accounts['operating_income'])
                if revenue != 0:
                    ratios['operating_margin'] = (operating_income / revenue) * 100
            
            # Net Margin
            if 'revenue' in accounts and 'net_income' in accounts:
                revenue = self._get_account_value(accounts['revenue'])
                net_income = self._get_account_value(accounts['net_income'])
                if revenue != 0:
                    ratios['net_margin'] = (net_income / revenue) * 100
            
            # Growth rates (if multiple periods)
            if len(self.numeric_columns) >= 2:
                for i in range(1, len(self.numeric_columns)):
                    current_period = self.numeric_columns[i]
                    previous_period = self.numeric_columns[i-1]
                    
                    # Revenue growth
                    if 'revenue' in accounts:
                        current_rev = self.data.loc[accounts['revenue'], current_period]
                        previous_rev = self.data.loc[accounts['revenue'], previous_period]
                        if previous_rev != 0:
                            growth = ((current_rev - previous_rev) / previous_rev) * 100
                            ratios[f'revenue_growth_{current_period}'] = growth
        
        except Exception as e:
            pass
        
        return ratios
    
    def _calculate_cash_flow_ratios(self) -> Dict[str, float]:
        """
        Calculate cash flow specific ratios
        """
        ratios = {}
        
        try:
            # Operating Cash Flow ratios
            numeric_data = self.data[self.numeric_columns]
            
            # Use pattern matching to find cash flow components
            operating_cf = self._find_value_by_keywords(['operating', 'operations'])
            investing_cf = self._find_value_by_keywords(['investing', 'investment'])
            financing_cf = self._find_value_by_keywords(['financing', 'dividend'])
            
            if operating_cf is not None and investing_cf is not None:
                if investing_cf != 0:
                    ratios['operating_to_investing'] = operating_cf / abs(investing_cf)
            
            if operating_cf is not None and financing_cf is not None:
                if financing_cf != 0:
                    ratios['operating_to_financing'] = operating_cf / abs(financing_cf)
        
        except Exception as e:
            pass
        
        return ratios
    
    def _calculate_general_ratios(self) -> Dict[str, float]:
        """
        Calculate general financial ratios when statement type is unknown
        """
        ratios = {}
        
        try:
            numeric_data = self.data[self.numeric_columns]
            
            if len(numeric_data.columns) >= 2:
                # Calculate basic ratios between numeric columns
                for i, col1 in enumerate(numeric_data.columns):
                    for j, col2 in enumerate(numeric_data.columns):
                        if i != j:
                            values1 = numeric_data[col1].dropna()
                            values2 = numeric_data[col2].dropna()
                            
                            if len(values1) > 0 and len(values2) > 0:
                                # Calculate ratio of means
                                mean1 = values1.mean()
                                mean2 = values2.mean()
                                
                                if mean2 != 0:
                                    ratio_name = f"{col1}_to_{col2}_ratio"
                                    ratios[ratio_name] = mean1 / mean2
                
                # Calculate growth rates between periods
                if len(numeric_data.columns) >= 2:
                    for i in range(len(numeric_data)):
                        row_data = numeric_data.iloc[i]
                        non_zero_values = row_data[row_data != 0]
                        
                        if len(non_zero_values) >= 2:
                            for j in range(1, len(non_zero_values)):
                                current = non_zero_values.iloc[j]
                                previous = non_zero_values.iloc[j-1]
                                
                                if previous != 0:
                                    growth = ((current - previous) / previous) * 100
                                    growth_name = f"growth_rate_period_{j}"
                                    ratios[growth_name] = growth
        
        except Exception as e:
            pass
        
        return ratios
    
    def _find_accounts_by_pattern(self) -> Dict[str, int]:
        """
        Find account rows by matching keywords
        """
        accounts = {}
        
        if not self.text_columns:
            return accounts
        
        # Use the first text column as account names
        account_column = self.text_columns[0]
        
        # Define keyword patterns for different accounts
        patterns = {
            'cash': ['cash', 'cash equivalents', 'cash and cash'],
            'receivables': ['receivable', 'accounts receivable', 'trade receivable'],
            'inventory': ['inventory', 'stock', 'merchandise'],
            'current_assets': ['current assets', 'total current assets'],
            'total_assets': ['total assets', 'total asset'],
            'current_liabilities': ['current liabilities', 'total current liabilities'],
            'total_debt': ['total debt', 'total liabilities', 'debt'],
            'total_equity': ['equity', 'shareholders equity', 'stockholders equity', 'total equity'],
            'revenue': ['revenue', 'sales', 'total revenue', 'net sales', 'income'],
            'cost_of_sales': ['cost of sales', 'cost of goods sold', 'cogs'],
            'operating_income': ['operating income', 'operating profit', 'ebit'],
            'net_income': ['net income', 'net profit', 'net earnings', 'profit']
        }
        
        # Search for accounts
        for account_type, keywords in patterns.items():
            for idx, account_name in enumerate(self.data[account_column].astype(str).str.lower()):
                for keyword in keywords:
                    if keyword in account_name:
                        accounts[account_type] = idx
                        break
                if account_type in accounts:
                    break
        
        return accounts
    
    def _get_account_value(self, row_index: int, column_index: int = -1) -> float:
        """
        Get account value from specified row and column
        """
        try:
            if column_index == -1:
                # Use the last numeric column (most recent period)
                if self.numeric_columns:
                    return float(self.data.loc[row_index, self.numeric_columns[-1]])
            else:
                return float(self.data.iloc[row_index, column_index])
        except (IndexError, ValueError, TypeError):
            return 0.0
        
        return 0.0
    
    def _find_value_by_keywords(self, keywords: List[str]) -> Optional[float]:
        """
        Find a value by searching for keywords in text columns
        """
        if not self.text_columns or not self.numeric_columns:
            return None
        
        account_column = self.text_columns[0]
        value_column = self.numeric_columns[-1]  # Use most recent period
        
        for idx, account_name in enumerate(self.data[account_column].astype(str).str.lower()):
            for keyword in keywords:
                if keyword in account_name:
                    try:
                        return float(self.data.loc[idx, value_column])
                    except (ValueError, TypeError):
                        continue
        
        return None
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for the dataset
        """
        if self.data is None:
            return {}
        
        stats = {
            'total_rows': len(self.data),
            'total_columns': len(self.data.columns),
            'numeric_columns': len(self.numeric_columns),
            'text_columns': len(self.text_columns),
            'data_quality_score': self.data_quality_score,
            'missing_values': self.data.isnull().sum().sum(),
            'statement_type': self.statement_type or 'Unknown'
        }
        
        # Add numeric statistics
        if self.numeric_columns:
            numeric_data = self.data[self.numeric_columns]
            stats.update({
                'numeric_mean': numeric_data.mean().to_dict(),
                'numeric_std': numeric_data.std().to_dict(),
                'numeric_min': numeric_data.min().to_dict(),
                'numeric_max': numeric_data.max().to_dict()
            })
        
        return stats
    
    def get_data_preview(self, rows: int = 10) -> pd.DataFrame:
        """
        Get a preview of the data
        """
        if self.data is None:
            return pd.DataFrame()
        
        return self.data.head(rows)
    
    def search_data(self, search_term: str) -> pd.DataFrame:
        """
        Search for specific terms in the data
        """
        if self.data is None or not search_term:
            return pd.DataFrame()
        
        # Search in text columns
        mask = pd.Series([False] * len(self.data))
        
        for col in self.text_columns:
            mask |= self.data[col].astype(str).str.contains(search_term, case=False, na=False)
        
        return self.data[mask]
    
    def filter_data(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply filters to the data
        """
        if self.data is None:
            return pd.DataFrame()
        
        filtered_data = self.data.copy()
        
        for column, filter_value in filters.items():
            if column in filtered_data.columns:
                if isinstance(filter_value, dict):
                    # Range filter for numeric columns
                    if 'min' in filter_value and 'max' in filter_value:
                        filtered_data = filtered_data[
                            (filtered_data[column] >= filter_value['min']) &
                            (filtered_data[column] <= filter_value['max'])
                        ]
                else:
                    # Exact match filter
                    filtered_data = filtered_data[filtered_data[column] == filter_value]
        
        return filtered_data
    
    def export_to_excel(self, filename: str = None) -> bytes:
        """
        Export data to Excel format
        """
        if self.data is None:
            return b''
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Main data sheet
            self.data.to_excel(writer, sheet_name='Financial Data', index=False)
            
            # Summary sheet
            summary_stats = self.get_summary_statistics()
            summary_df = pd.DataFrame(list(summary_stats.items()), columns=['Metric', 'Value'])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Ratios sheet if available
            if self.statement_type:
                ratios = self.calculate_financial_ratios(self.statement_type)
                if ratios:
                    ratios_df = pd.DataFrame(list(ratios.items()), columns=['Ratio', 'Value'])
                    ratios_df.to_excel(writer, sheet_name='Financial Ratios', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    def validate_data_structure(self) -> Dict[str, Any]:
        """
        Validate the structure of financial data
        """
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': []
        }
        
        if self.data is None:
            validation_results['is_valid'] = False
            validation_results['errors'].append("No data loaded")
            return validation_results
        
        # Check for minimum data requirements
        if len(self.data) < 3:
            validation_results['warnings'].append("Dataset has very few rows (less than 3)")
        
        if len(self.data.columns) < 2:
            validation_results['errors'].append("Dataset must have at least 2 columns")
            validation_results['is_valid'] = False
        
        # Check for numeric data
        if len(self.numeric_columns) == 0:
            validation_results['warnings'].append("No numeric columns found - ratio calculations may be limited")
        
        # Check for text columns (account names)
        if len(self.text_columns) == 0:
            validation_results['warnings'].append("No text columns found - account identification may be difficult")
        
        # Check data quality
        if self.data_quality_score < 70:
            validation_results['warnings'].append(f"Data quality score is low ({self.data_quality_score:.1f}%)")
        
        # Check for missing values
        missing_percentage = (self.data.isnull().sum().sum() / self.data.size) * 100
        if missing_percentage > 20:
            validation_results['warnings'].append(f"High percentage of missing values ({missing_percentage:.1f}%)")
        
        # Suggestions for improvement
        if len(self.numeric_columns) < 3:
            validation_results['suggestions'].append("Include multiple time periods for better trend analysis")
        
        if not any(keyword in str(self.data.iloc[:, 0]).lower() for keyword in ['revenue', 'assets', 'cash']):
            validation_results['suggestions'].append("Ensure first column contains account names for better analysis")
        
        return validation_results
    
    def get_trend_analysis(self) -> Dict[str, Any]:
        """
        Perform trend analysis on numeric data
        """
        trends = {}
        
        if len(self.numeric_columns) < 2:
            return trends
        
        try:
            numeric_data = self.data[self.numeric_columns]
            
            # Calculate period-over-period changes
            for i in range(len(numeric_data)):
                row_data = numeric_data.iloc[i]
                row_name = f"Row_{i}"
                
                # Try to get account name if available
                if self.text_columns:
                    account_name = str(self.data.iloc[i, 0])
                    if account_name and account_name != 'nan':
                        row_name = account_name
                
                # Calculate changes between periods
                changes = []
                percentages = []
                
                for j in range(1, len(row_data)):
                    current = row_data.iloc[j]
                    previous = row_data.iloc[j-1]
                    
                    if pd.notna(current) and pd.notna(previous):
                        change = current - previous
                        changes.append(change)
                        
                        if previous != 0:
                            percentage = (change / previous) * 100
                            percentages.append(percentage)
                        else:
                            percentages.append(0)
                
                if changes:
                    trends[row_name] = {
                        'absolute_changes': changes,
                        'percentage_changes': percentages,
                        'average_change': np.mean(changes),
                        'average_percentage_change': np.mean(percentages),
                        'trend_direction': 'increasing' if np.mean(changes) > 0 else 'decreasing'
                    }
        
        except Exception as e:
            st.warning(f"Trend analysis error: {str(e)}")
        
        return trends
    
    def get_outlier_analysis(self) -> Dict[str, Any]:
        """
        Identify outliers in the financial data
        """
        outliers = {}
        
        if not self.numeric_columns:
            return outliers
        
        try:
            numeric_data = self.data[self.numeric_columns]
            
            for column in numeric_data.columns:
                col_data = numeric_data[column].dropna()
                
                if len(col_data) > 3:  # Need at least 4 data points
                    Q1 = col_data.quantile(0.25)
                    Q3 = col_data.quantile(0.75)
                    IQR = Q3 - Q1
                    
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outlier_indices = col_data[(col_data < lower_bound) | (col_data > upper_bound)].index
                    
                    if len(outlier_indices) > 0:
                        outliers[column] = {
                            'outlier_count': len(outlier_indices),
                            'outlier_indices': outlier_indices.tolist(),
                            'outlier_values': col_data[outlier_indices].tolist(),
                            'lower_bound': lower_bound,
                            'upper_bound': upper_bound
                        }
        
        except Exception as e:
            st.warning(f"Outlier analysis error: {str(e)}")
        
        return outliers
    
    def get_correlation_analysis(self) -> pd.DataFrame:
        """
        Calculate correlation matrix for numeric columns
        """
        if len(self.numeric_columns) < 2:
            return pd.DataFrame()
        
        try:
            numeric_data = self.data[self.numeric_columns]
            correlation_matrix = numeric_data.corr()
            return correlation_matrix
        
        except Exception as e:
            st.warning(f"Correlation analysis error: {str(e)}")
            return pd.DataFrame()
    
    def generate_data_profile(self) -> Dict[str, Any]:
        """
        Generate a comprehensive data profile
        """
        profile = {
            'basic_info': self.get_summary_statistics(),
            'validation': self.validate_data_structure(),
            'trends': self.get_trend_analysis(),
            'outliers': self.get_outlier_analysis()
        }
        
        # Add correlation analysis if applicable
        correlation_matrix = self.get_correlation_analysis()
        if not correlation_matrix.empty:
            profile['correlations'] = correlation_matrix.to_dict()
        
        return profile

# Utility functions for data processing
def detect_financial_statement_type(data: pd.DataFrame) -> str:
    """
    Standalone function to detect financial statement type
    """
    processor = FinancialDataProcessor()
    processor.data = data
    processor._identify_column_types()
    return processor.detect_statement_type()

def calculate_basic_ratios(data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate basic financial ratios from any financial data
    """
    processor = FinancialDataProcessor()
    processor.data = data
    processor._identify_column_types()
    statement_type = processor.detect_statement_type()
    return processor.calculate_financial_ratios(statement_type)

def clean_financial_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize financial data
    """
    processor = FinancialDataProcessor()
    processor.data = data.copy()
    processor._clean_data()
    return processor.data

def validate_financial_data(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate financial data structure and quality
    """
    processor = FinancialDataProcessor()
    processor.data = data
    processor._identify_column_types()
    processor._assess_data_quality()
    return processor.validate_data_structure()

# Constants for financial analysis
COMMON_FINANCIAL_ACCOUNTS = {
    'balance_sheet': {
        'assets': [
            'cash', 'cash and cash equivalents', 'short-term investments',
            'accounts receivable', 'inventory', 'prepaid expenses',
            'property plant equipment', 'intangible assets', 'goodwill'
        ],
        'liabilities': [
            'accounts payable', 'accrued liabilities', 'short-term debt',
            'long-term debt', 'deferred tax liabilities', 'pension obligations'
        ],
        'equity': [
            'common stock', 'retained earnings', 'additional paid-in capital',
            'treasury stock', 'accumulated other comprehensive income'
        ]
    },
    'income_statement': {
        'revenue': [
            'revenue', 'net sales', 'total revenue', 'sales revenue',
            'service revenue', 'operating revenue'
        ],
        'expenses': [
            'cost of goods sold', 'cost of sales', 'operating expenses',
            'selling general administrative', 'research development',
            'depreciation', 'amortization', 'interest expense', 'tax expense'
        ],
        'profit_metrics': [
            'gross profit', 'operating income', 'ebit', 'ebitda',
            'net income', 'earnings per share'
        ]
    },
    'cash_flow': {
        'operating': [
            'net income', 'depreciation', 'amortization', 'working capital changes',
            'accounts receivable changes', 'inventory changes', 'accounts payable changes'
        ],
        'investing': [
            'capital expenditures', 'acquisitions', 'asset sales',
            'investment purchases', 'investment sales'
        ],
        'financing': [
            'debt issuance', 'debt repayment', 'dividend payments',
            'stock repurchases', 'stock issuance'
        ]
    }
}

FINANCIAL_RATIO_DEFINITIONS = {
    'liquidity': {
        'current_ratio': {
            'formula': 'Current Assets / Current Liabilities',
            'description': 'Measures ability to pay short-term obligations',
            'good_range': (1.5, 3.0),
            'interpretation': 'Higher is generally better, but too high may indicate inefficient use of assets'
        },
        'quick_ratio': {
            'formula': '(Current Assets - Inventory) / Current Liabilities',
            'description': 'Measures ability to pay short-term obligations with liquid assets',
            'good_range': (1.0, 1.5),
            'interpretation': 'Should be at least 1.0 for healthy liquidity'
        },
        'cash_ratio': {
            'formula': 'Cash and Cash Equivalents / Current Liabilities',
            'description': 'Most conservative liquidity measure',
            'good_range': (0.1, 0.5),
            'interpretation': 'Shows ability to pay debts with cash on hand'
        }
    },
    'profitability': {
        'gross_margin': {
            'formula': '(Revenue - COGS) / Revenue * 100',
            'description': 'Percentage of revenue retained after direct costs',
            'good_range': (20, 50),
            'interpretation': 'Higher margins indicate better pricing power and cost control'
        },
        'operating_margin': {
            'formula': 'Operating Income / Revenue * 100',
            'description': 'Percentage of revenue retained after operating expenses',
            'good_range': (10, 30),
            'interpretation': 'Shows operational efficiency and cost management'
        },
        'net_margin': {
            'formula': 'Net Income / Revenue * 100',
            'description': 'Percentage of revenue retained as profit',
            'good_range': (5, 20),
            'interpretation': 'Overall profitability after all expenses'
        },
        'roa': {
            'formula': 'Net Income / Total Assets * 100',
            'description': 'Return on Assets - efficiency of asset utilization',
            'good_range': (5, 15),
            'interpretation': 'Higher ROA indicates more efficient asset use'
        },
        'roe': {
            'formula': 'Net Income / Shareholders Equity * 100',
            'description': 'Return on Equity - return to shareholders',
            'good_range': (10, 25),
            'interpretation': 'Higher ROE indicates better returns to equity holders'
        }
    },
    'leverage': {
        'debt_to_equity': {
            'formula': 'Total Debt / Total Equity',
            'description': 'Measures financial leverage and risk',
            'good_range': (0.3, 1.0),
            'interpretation': 'Lower ratios indicate less financial risk'
        },
        'debt_to_assets': {
            'formula': 'Total Debt / Total Assets',
            'description': 'Percentage of assets financed by debt',
            'good_range': (0.2, 0.6),
            'interpretation': 'Lower ratios indicate less leverage and risk'
        },
        'interest_coverage': {
            'formula': 'EBIT / Interest Expense',
            'description': 'Ability to pay interest on debt',
            'good_range': (2.5, 10.0),
            'interpretation': 'Higher ratios indicate better ability to service debt'
        }
    },
    'efficiency': {
        'asset_turnover': {
            'formula': 'Revenue / Total Assets',
            'description': 'Efficiency of asset utilization to generate sales',
            'good_range': (0.5, 2.0),
            'interpretation': 'Higher ratios indicate more efficient asset use'
        },
        'inventory_turnover': {
            'formula': 'COGS / Average Inventory',
            'description': 'How quickly inventory is sold',
            'good_range': (4, 12),
            'interpretation': 'Higher turnover indicates efficient inventory management'
        },
        'receivables_turnover': {
            'formula': 'Revenue / Average Accounts Receivable',
            'description': 'How quickly receivables are collected',
            'good_range': (6, 15),
            'interpretation': 'Higher turnover indicates efficient collection'
        }
    }
}

def get_ratio_interpretation(ratio_name: str, value: float) -> Dict[str, str]:
    """
    Get interpretation of a financial ratio value
    """
    interpretation = {
        'status': 'unknown',
        'message': 'No interpretation available',
        'recommendation': 'Monitor this metric'
    }
    
    # Find the ratio definition
    ratio_info = None
    for category in FINANCIAL_RATIO_DEFINITIONS.values():
        if ratio_name in category:
            ratio_info = category[ratio_name]
            break
    
    if not ratio_info:
        return interpretation
    
    good_range = ratio_info.get('good_range', (0, float('inf')))
    
    if good_range[0] <= value <= good_range[1]:
        interpretation['status'] = 'good'
        interpretation['message'] = f'Value ({value:.2f}) is within healthy range'
        interpretation['recommendation'] = 'Maintain current performance'
    elif value < good_range[0]:
        interpretation['status'] = 'low'
        interpretation['message'] = f'Value ({value:.2f}) is below recommended range'
        interpretation['recommendation'] = 'Consider strategies to improve this metric'
    else:
        interpretation['status'] = 'high'
        interpretation['message'] = f'Value ({value:.2f}) is above recommended range'
        interpretation['recommendation'] = 'Evaluate if this level is sustainable and optimal'
    
    return interpretation

def calculate_industry_percentile(ratio_name: str, value: float, industry: str = 'general') -> float:
    """
    Calculate percentile ranking for a ratio within industry benchmarks
    """
    # This would typically use real industry data
    # For now, we'll use simplified benchmarks
    
    industry_benchmarks = {
        'general': {
            'current_ratio': {'p25': 1.2, 'p50': 1.8, 'p75': 2.5},
            'quick_ratio': {'p25': 0.8, 'p50': 1.1, 'p75': 1.5},
            'debt_to_equity': {'p25': 0.3, 'p50': 0.6, 'p75': 1.0},
            'gross_margin': {'p25': 15, 'p50': 25, 'p75': 40},
            'net_margin': {'p25': 3, 'p50': 8, 'p75': 15}
        }
    }
    
    benchmarks = industry_benchmarks.get(industry, industry_benchmarks['general'])
    ratio_benchmarks = benchmarks.get(ratio_name)
    
    if not ratio_benchmarks:
        return 50.0  # Default to median if no benchmark available
    
    if value <= ratio_benchmarks['p25']:
        return 25.0
    elif value <= ratio_benchmarks['p50']:
        return 50.0
    elif value <= ratio_benchmarks['p75']:
        return 75.0
    else:
        return 90.0

class AdvancedFinancialAnalyzer:
    """
    Advanced financial analysis with statistical methods
    """
    
    def __init__(self, data_processor: FinancialDataProcessor):
        self.processor = data_processor
        self.data = data_processor.data
        self.numeric_columns = data_processor.numeric_columns
    
    def perform_dupont_analysis(self) -> Dict[str, float]:
        """
        Perform DuPont analysis to break down ROE
        """
        dupont = {}
        
        try:
            accounts = self.processor._find_accounts_by_pattern()
            
            if all(key in accounts for key in ['net_income', 'revenue', 'total_assets', 'total_equity']):
                net_income = self.processor._get_account_value(accounts['net_income'])
                revenue = self.processor._get_account_value(accounts['revenue'])
                total_assets = self.processor._get_account_value(accounts['total_assets'])
                total_equity = self.processor._get_account_value(accounts['total_equity'])
                
                if revenue != 0 and total_assets != 0 and total_equity != 0:
                    # DuPont components
                    profit_margin = (net_income / revenue) * 100
                    asset_turnover = revenue / total_assets
                    equity_multiplier = total_assets / total_equity
                    roe = (net_income / total_equity) * 100
                    
                    dupont = {
                        'profit_margin': profit_margin,
                        'asset_turnover': asset_turnover,
                        'equity_multiplier': equity_multiplier,
                        'roe': roe,
                        'roe_calculated': profit_margin * asset_turnover * equity_multiplier / 100
                    }
        
        except Exception as e:
            st.warning(f"DuPont analysis error: {str(e)}")
        
        return dupont
    
    def calculate_z_score(self) -> float:
        """
        Calculate Altman Z-Score for bankruptcy prediction
        """
        try:
            accounts = self.processor._find_accounts_by_pattern()
            
            # Required components for Z-Score
            required_accounts = ['current_assets', 'current_liabilities', 'total_assets', 
                               'total_equity', 'revenue', 'net_income']
            
            if not all(acc in accounts for acc in required_accounts):
                return 0.0
            
            # Get values
            current_assets = self.processor._get_account_value(accounts['current_assets'])
            current_liabilities = self.processor._get_account_value(accounts['current_liabilities'])
            total_assets = self.processor._get_account_value(accounts['total_assets'])
            total_equity = self.processor._get_account_value(accounts['total_equity'])
            revenue = self.processor._get_account_value(accounts['revenue'])
            net_income = self.processor._get_account_value(accounts['net_income'])
            
            if total_assets == 0:
                return 0.0
            
            # Calculate Z-Score components
            working_capital = current_assets - current_liabilities
            retained_earnings = net_income  # Simplified assumption
            
            x1 = working_capital / total_assets
            x2 = retained_earnings / total_assets
            x3 = net_income / total_assets  # EBIT approximation
            x4 = total_equity / (total_assets - total_equity)  # Market value approximation
            x5 = revenue / total_assets
            
            # Altman Z-Score formula
            z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5
            
            return z_score
        
        except Exception as e:
            st.warning(f"Z-Score calculation error: {str(e)}")
            return 0.0
    
    def perform_variance_analysis(self) -> Dict[str, Any]:
        """
        Perform variance analysis between periods
        """
        variance_analysis = {}
        
        if len(self.numeric_columns) < 2:
            return variance_analysis
        
        try:
            for i in range(len(self.data)):
                row_data = self.data.iloc[i][self.numeric_columns]
                
                # Get account name
                account_name = f"Account_{i}"
                if self.processor.text_columns:
                    account_name = str(self.data.iloc[i, 0])
                
                # Calculate variances between consecutive periods
                variances = []
                for j in range(1, len(row_data)):
                    current = row_data.iloc[j]
                    previous = row_data.iloc[j-1]
                    
                    if pd.notna(current) and pd.notna(previous) and previous != 0:
                        variance = ((current - previous) / previous) * 100
                        variances.append({
                            'period': f"{self.numeric_columns[j-1]} to {self.numeric_columns[j]}",
                            'absolute_change': current - previous,
                            'percentage_change': variance,
                            'favorable': variance > 0  # Simplified assumption
                        })
                
                if variances:
                    variance_analysis[account_name] = variances
        
        except Exception as e:
            st.warning(f"Variance analysis error: {str(e)}")
        
        return variance_analysis
    
    def calculate_financial_strength_score(self) -> Dict[str, Any]:
        """
        Calculate overall financial strength score
        """
        score_components = {
            'liquidity_score': 0,
            'profitability_score': 0,
            'leverage_score': 0,
            'efficiency_score': 0,
            'overall_score': 0
        }
        
        try:
            ratios = self.processor.calculate_financial_ratios(
                self.processor.statement_type or 'General Financial Data'
            )
            
            # Score each category (0-100)
            
            # Liquidity scoring
            liquidity_ratios = ['current_ratio', 'quick_ratio', 'cash_ratio']
            liquidity_scores = []
            for ratio in liquidity_ratios:
                if ratio in ratios:
                    interpretation = get_ratio_interpretation(ratio, ratios[ratio])
                    if interpretation['status'] == 'good':
                        liquidity_scores.append(100)
                    elif interpretation['status'] == 'low':
                        liquidity_scores.append(40)
                    else:
                        liquidity_scores.append(70)
            
            if liquidity_scores:
                score_components['liquidity_score'] = np.mean(liquidity_scores)
            
            # Profitability scoring
            profitability_ratios = ['gross_margin', 'operating_margin', 'net_margin', 'roa', 'roe']
            profitability_scores = []
            for ratio in profitability_ratios:
                if ratio in ratios:
                    interpretation = get_ratio_interpretation(ratio, ratios[ratio])
                    if interpretation['status'] == 'good':
                        profitability_scores.append(100)
                    elif interpretation['status'] == 'low':
                        profitability_scores.append(30)
                    else:
                        profitability_scores.append(80)
            
            if profitability_scores:
                score_components['profitability_score'] = np.mean(profitability_scores)
            
            # Leverage scoring (lower debt is better)
            leverage_ratios = ['debt_to_equity', 'debt_to_assets', 'interest_coverage']
            leverage_scores = []
            for ratio in leverage_ratios:
                if ratio in ratios:
                    interpretation = get_ratio_interpretation(ratio, ratios[ratio])
                    if interpretation['status'] == 'good':
                        leverage_scores.append(100)
                    elif interpretation['status'] == 'high':
                        leverage_scores.append(40)  # High leverage is risky
                    else:
                        leverage_scores.append(70)
            
            if leverage_scores:
                score_components['leverage_score'] = np.mean(leverage_scores)
            
            # Efficiency scoring
            efficiency_ratios = ['asset_turnover', 'inventory_turnover', 'receivables_turnover']
            efficiency_scores = []
            for ratio in efficiency_ratios:
                if ratio in ratios:
                    interpretation = get_ratio_interpretation(ratio, ratios[ratio])
                    if interpretation['status'] == 'good':
                        efficiency_scores.append(100)
                    elif interpretation['status'] == 'low':
                        efficiency_scores.append(50)
                    else:
                        efficiency_scores.append(85)
            
            if efficiency_scores:
                score_components['efficiency_score'] = np.mean(efficiency_scores)
            
            # Calculate overall score
            scores = [score for score in score_components.values() if score > 0]
            if scores:
                score_components['overall_score'] = np.mean(scores)
            
            # Add Z-Score component if available
            z_score = self.calculate_z_score()
            if z_score > 0:
                score_components['z_score'] = z_score
                score_components['bankruptcy_risk'] = self._interpret_z_score(z_score)
        
        except Exception as e:
            st.warning(f"Financial strength scoring error: {str(e)}")
        
        return score_components
    
    def _interpret_z_score(self, z_score: float) -> str:
        """
        Interpret Altman Z-Score
        """
        if z_score > 2.99:
            return "Low bankruptcy risk"
        elif z_score > 1.8:
            return "Moderate bankruptcy risk"
        else:
            return "High bankruptcy risk"
    
    def generate_financial_insights(self) -> List[str]:
        """
        Generate actionable financial insights
        """
        insights = []
        
        try:
            ratios = self.processor.calculate_financial_ratios(
                self.processor.statement_type or 'General Financial Data'
            )
            
            strength_score = self.calculate_financial_strength_score()
            trends = self.processor.get_trend_analysis()
            
            # Overall financial health insight
            overall_score = strength_score.get('overall_score', 0)
            if overall_score >= 80:
                insights.append("🟢 Strong overall financial health with good performance across key metrics")
            elif overall_score >= 60:
                insights.append("🟡 Moderate financial health with some areas for improvement")
            else:
                insights.append("🔴 Financial health needs attention - consider reviewing key performance areas")
            
            # Liquidity insights
            liquidity_score = strength_score.get('liquidity_score', 0)
            if liquidity_score < 60:
                insights.append("💧 Liquidity may be a concern - monitor cash flow and current ratio")
            
            # Profitability insights
            profitability_score = strength_score.get('profitability_score', 0)
            if profitability_score < 60:
                insights.append("📈 Profitability could be improved - review cost structure and pricing")
            
            # Leverage insights
            leverage_score = strength_score.get('leverage_score', 0)
            if leverage_score < 60:
                insights.append("⚖️ Debt levels may be high - consider debt reduction strategies")
            
            # Trend insights
            declining_trends = []
            improving_trends = []
            
            for account, trend_data in trends.items():
                avg_change = trend_data.get('average_percentage_change', 0)
                if avg_change < -10:
                    declining_trends.append(account)
                elif avg_change > 10:
                    improving_trends.append(account)
            
            if declining_trends:
                insights.append(f"📉 Declining trends detected in: {', '.join(declining_trends[:3])}")
            
            if improving_trends:
                insights.append(f"📊 Positive trends observed in: {', '.join(improving_trends[:3])}")
            
            # Z-Score insights
            z_score = strength_score.get('z_score', 0)
            if z_score > 0:
                risk_level = strength_score.get('bankruptcy_risk', '')
                if 'High' in risk_level:
                    insights.append("⚠️ Z-Score indicates elevated financial distress risk")
                elif 'Low' in risk_level:
                    insights.append("✅ Z-Score indicates low financial distress risk")
            
            # Data quality insights
            data_quality = self.processor.assess_data_quality()
            if data_quality < 80:
                insights.append(f"📊 Data quality score is {data_quality:.1f}% - consider data validation")
            
            # Industry comparison insights
            if len(ratios) > 0:
                insights.append("🏭 Consider benchmarking against industry peers for better context")
            
            # Recommendations based on statement type
            if self.processor.statement_type == "Balance Sheet":
                insights.append("💼 Focus on asset efficiency and debt management strategies")
            elif self.processor.statement_type == "Income Statement":
                insights.append("💰 Monitor revenue growth and cost control initiatives")
            elif self.processor.statement_type == "Cash Flow Statement":
                insights.append("💸 Ensure positive operating cash flow and efficient capital allocation")
        
        except Exception as e:
            insights.append(f"⚠️ Error generating insights: {str(e)}")
        
        return insights
    
    def perform_scenario_analysis(self, scenarios: Dict[str, float]) -> Dict[str, Any]:
        """
        Perform scenario analysis on key metrics
        """
        scenario_results = {}
        
        try:
            base_ratios = self.processor.calculate_financial_ratios(
                self.processor.statement_type or 'General Financial Data'
            )
            
            for scenario_name, change_percentage in scenarios.items():
                scenario_ratios = {}
                
                # Apply percentage change to relevant ratios
                for ratio_name, base_value in base_ratios.items():
                    if 'revenue' in ratio_name.lower() or 'income' in ratio_name.lower():
                        # Apply change to revenue/income related ratios
                        new_value = base_value * (1 + change_percentage / 100)
                        scenario_ratios[ratio_name] = new_value
                    else:
                        scenario_ratios[ratio_name] = base_value
                
                scenario_results[scenario_name] = {
                    'ratios': scenario_ratios,
                    'change_percentage': change_percentage,
                    'impact_summary': self._summarize_scenario_impact(base_ratios, scenario_ratios)
                }
        
        except Exception as e:
            st.warning(f"Scenario analysis error: {str(e)}")
        
        return scenario_results
    
    def _summarize_scenario_impact(self, base_ratios: Dict[str, float], 
                                 scenario_ratios: Dict[str, float]) -> str:
        """
        Summarize the impact of a scenario
        """
        significant_changes = []
        
        for ratio_name in base_ratios:
            if ratio_name in scenario_ratios:
                base_value = base_ratios[ratio_name]
                scenario_value = scenario_ratios[ratio_name]
                
                if base_value != 0:
                    change_pct = ((scenario_value - base_value) / base_value) * 100
                    if abs(change_pct) > 5:  # Significant change threshold
                        direction = "increase" if change_pct > 0 else "decrease"
                        significant_changes.append(f"{ratio_name}: {abs(change_pct):.1f}% {direction}")
        
        if significant_changes:
            return f"Significant changes: {', '.join(significant_changes[:3])}"
        else:
            return "Minimal impact on key ratios"

# Export functions for external use
__all__ = [
    'FinancialDataProcessor',
    'AdvancedFinancialAnalyzer',
    'detect_financial_statement_type',
    'calculate_basic_ratios',
    'clean_financial_data',
    'validate_financial_data',
    'get_ratio_interpretation',
    'calculate_industry_percentile',
    'FINANCIAL_RATIO_DEFINITIONS',
    'COMMON_FINANCIAL_ACCOUNTS'
]

# Version and metadata
__version__ = "1.0.0"
__author__ = "Advanced Financial Statement Analyzer"
__description__ = "Comprehensive financial data processing and analysis toolkit"

# Configuration constants
DEFAULT_CONFIG = {
    'data_quality_threshold': 70.0,
    'outlier_detection_method': 'iqr',
    'correlation_threshold': 0.7,
    'trend_analysis_periods': 3,
    'ratio_calculation_precision': 2,
    'benchmark_industries': ['technology', 'manufacturing', 'retail', 'healthcare', 'finance'],
    'supported_file_formats': ['.xlsx', '.xls', '.csv', '.tsv'],
    'max_file_size_mb': 50,
    'default_currency': 'USD'
}

def get_processor_config() -> Dict[str, Any]:
    """
    Get default configuration for the data processor
    """
    return DEFAULT_CONFIG.copy()

def validate_file_format(filename: str) -> bool:
    """
    Validate if file format is supported
    """
    file_extension = '.' + filename.split('.')[-1].lower()
    return file_extension in DEFAULT_CONFIG['supported_file_formats']

def estimate_processing_time(file_size_mb: float, num_rows: int = None) -> str:
    """
    Estimate processing time based on file characteristics
    """
    if file_size_mb < 1:
        return "< 10 seconds"
    elif file_size_mb < 5:
        return "10-30 seconds"
    elif file_size_mb < 20:
        return "30-60 seconds"
    else:
        return "1-3 minutes"

# Error handling classes
class DataProcessingError(Exception):
    """Custom exception for data processing errors"""
    pass

class InsufficientDataError(DataProcessingError):
    """Exception raised when data is insufficient for analysis"""
    pass

class UnsupportedFormatError(DataProcessingError):
    """Exception raised when file format is not supported"""
    pass

class DataQualityError(DataProcessingError):
    """Exception raised when data quality is too low"""
    pass

# Logging configuration
import logging

def setup_processor_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Setup logging for the data processor
    """
    logger = logging.getLogger("financial_data_processor")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# Initialize default logger
processor_logger = setup_processor_logging()

# Helper functions for advanced analysis
def calculate_compound_annual_growth_rate(start_value: float, end_value: float, periods: int) -> float:
    """
    Calculate Compound Annual Growth Rate (CAGR)
    """
    if start_value <= 0 or end_value <= 0 or periods <= 0:
        return 0.0
    
    return (pow(end_value / start_value, 1 / periods) - 1) * 100

def calculate_coefficient_of_variation(values: List[float]) -> float:
    """
    Calculate coefficient of variation (risk-adjusted return measure)
    """
    if not values or len(values) < 2:
        return 0.0
    
    mean_val = np.mean(values)
    std_val = np.std(values)
    
    if mean_val == 0:
        return 0.0
    
    return (std_val / mean_val) * 100

def detect_seasonality(values: List[float], periods_per_year: int = 4) -> Dict[str, Any]:
    """
    Detect seasonal patterns in financial data
    """
    seasonality_info = {
        'has_seasonality': False,
        'seasonal_strength': 0.0,
        'peak_period': None,
        'trough_period': None
    }
    
    if len(values) < periods_per_year * 2:
        return seasonality_info
    
    try:
        # Simple seasonality detection using period averages
        period_averages = []
        for i in range(periods_per_year):
            period_values = [values[j] for j in range(i, len(values), periods_per_year)]
            if period_values:
                period_averages.append(np.mean(period_values))
        
        if period_averages:
            overall_mean = np.mean(period_averages)
            period_variations = [(avg - overall_mean) / overall_mean * 100 for avg in period_averages]
            
            max_variation = max(abs(var) for var in period_variations)
            
            if max_variation > 10:  # 10% threshold for seasonality
                seasonality_info['has_seasonality'] = True
                seasonality_info['seasonal_strength'] = max_variation
                seasonality_info['peak_period'] = period_variations.index(max(period_variations)) + 1
                seasonality_info['trough_period'] = period_variations.index(min(period_variations)) + 1
    
    except Exception:
        pass
    
    return seasonality_info

# Final validation
if __name__ == "__main__":
    # Test the data processor
    print("✅ Financial Data Processor module loaded successfully")
    print(f"📊 Version: {__version__}")
    print(f"🔧 Supported formats: {DEFAULT_CONFIG['supported_file_formats']}")
    print(f"📈 Available ratio categories: {list(FINANCIAL_RATIO_DEFINITIONS.keys())}")

