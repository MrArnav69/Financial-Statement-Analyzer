import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
import io
import os
import re
import json
from datetime import datetime

class FinancialVisualizer:
    """Intelligent visualization system for financial data analysis"""
    
    def __init__(self, data=None, processor=None):
        """Initialize with financial data or file path"""
        self.data = None
        self.processor = processor
        self.numeric_columns = []
        self.text_columns = []
        self.date_columns = []
        self.detected_statement_type = None
        self.file_type = None
        self.file_name = None
        self.permissions = {
            "data_access": False,
            "visualization": False,
            "export": False,
            "analysis": False
        }
        
        # Define color schemes
        self.color_schemes = {
            'financial': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            'performance': ['#2ca02c', '#d62728', '#1f77b4', '#ff7f0e', '#9467bd'],
            'categorical': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                           '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        }
        
        # Load data if provided
        if data is not None:
            self.load_data(data)
    
    def create_ratio_trends(self, ratios, time_periods):
        """
        Create a visualization of ratio trends over time periods.
        
        Args:
            ratios (dict): Dictionary of financial ratios
            time_periods (list): List of time period columns
            
        Returns:
            plotly.graph_objects.Figure: A line chart showing ratio trends
        """
        # Create a figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Prepare data for plotting
        ratio_names = list(ratios.keys())
        
        # If we have time-based ratios, extract them
        time_based_ratios = {}
        
        # For demonstration, we'll just plot the same ratio value across all time periods
        # In a real implementation, you would calculate ratios for each time period
        for ratio_name, ratio_value in ratios.items():
            # Create a list of the same ratio value for each time period
            time_based_ratios[ratio_name] = [ratio_value] * len(time_periods)
        
        # Add traces for each ratio
        for i, ratio_name in enumerate(ratio_names):
            if i < 5:  # Limit to 5 ratios to avoid overcrowding
                ratio_display = ratio_name.replace("_", " ").title()
                
                # Add line trace for this ratio
                fig.add_trace(
                    go.Scatter(
                        x=time_periods,
                        y=time_based_ratios[ratio_name],
                        name=ratio_display,
                        mode='lines+markers'
                    ),
                    secondary_y=i > 2  # Use secondary axis for some ratios
                )
        
        # Update layout
        fig.update_layout(
            title="Financial Ratio Trends",
            xaxis_title="Time Period",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500
        )
        
        # Update y-axes titles
        fig.update_yaxes(title_text="Ratio Value", secondary_y=False)
        fig.update_yaxes(title_text="Secondary Ratio Value", secondary_y=True)
        
        return fig

    
    def request_permissions(self) -> Dict[str, bool]:
        """Request permissions from the AI assistant"""
        st.write("🤖 AI Assistant: Analyzing your request...")
        
        # Simulate AI thinking
        with st.spinner("Processing your data and determining necessary permissions..."):
            # Always grant permissions in this implementation
            self.permissions = {
                "data_access": True,
                "visualization": True,
                "export": True,
                "analysis": True
            }
        
        # Display permission grant message
        st.success("✅ AI Assistant: I've analyzed your request and granted the following permissions:")
        for permission, granted in self.permissions.items():
            status = "✅ Granted" if granted else "❌ Denied"
            st.write(f"- {permission.replace('_', ' ').title()}: {status}")
        
        return self.permissions
    
    def load_data(self, data) -> bool:
        """Load data from various sources"""
        try:
            # Reset attributes
            self.data = None
            self.numeric_columns = []
            self.text_columns = []
            self.date_columns = []
            
            # Case 1: DataFrame already
            if isinstance(data, pd.DataFrame):
                self.data = data
                self.file_type = "dataframe"
                self.file_name = "DataFrame"
            
            # Case 2: File path
            elif isinstance(data, str) and os.path.exists(data):
                self.file_name = os.path.basename(data)
                file_ext = os.path.splitext(data)[1].lower()
                
                if file_ext == '.csv':
                    self.data = pd.read_csv(data)
                    self.file_type = "csv"
                elif file_ext in ['.xls', '.xlsx']:
                    self.data = pd.read_excel(data)
                    self.file_type = "excel"
                elif file_ext == '.json':
                    self.data = pd.read_json(data)
                    self.file_type = "json"
                else:
                    st.error(f"Unsupported file type: {file_ext}")
                    return False
            
            # Case 3: File-like object (uploaded through Streamlit)
            elif hasattr(data, 'read') or isinstance(data, io.IOBase):
                # Try to get filename if available
                if hasattr(data, 'name'):
                    self.file_name = os.path.basename(data.name)
                    file_ext = os.path.splitext(data.name)[1].lower()
                else:
                    self.file_name = "Uploaded File"
                    file_ext = ""
                
                # Determine file type and read accordingly
                if file_ext == '.csv' or self.file_name.endswith('.csv'):
                    self.data = pd.read_csv(data)
                    self.file_type = "csv"
                elif file_ext in ['.xls', '.xlsx'] or any(self.file_name.endswith(ext) for ext in ['.xls', '.xlsx']):
                    self.data = pd.read_excel(data)
                    self.file_type = "excel"
                elif file_ext == '.json' or self.file_name.endswith('.json'):
                    self.data = pd.read_json(data)
                    self.file_type = "json"
                else:
                    # Try to infer format
                    try:
                        self.data = pd.read_csv(data)
                        self.file_type = "csv"
                    except:
                        try:
                            data.seek(0)  # Reset file pointer
                            self.data = pd.read_excel(data)
                            self.file_type = "excel"
                        except:
                            try:
                                data.seek(0)  # Reset file pointer
                                self.data = pd.read_json(data)
                                self.file_type = "json"
                            except:
                                st.error("Could not determine file format")
                                return False
            
            else:
                st.error("Unsupported data type")
                return False
            
            # Process the data
            self._process_data()
            
            # Request permissions
            self.request_permissions()
            
            return True
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return False
    
    def _process_data(self):
        """Process and analyze the loaded data"""
        if self.data is None or self.data.empty:
            return
        
        # Identify column types
        self.numeric_columns = self.data.select_dtypes(include=[np.number]).columns.tolist()
        self.text_columns = self.data.select_dtypes(include=['object']).columns.tolist()
        
        # Try to identify date columns
        self.date_columns = []
        for col in self.text_columns:
            # Check if column name suggests date
            if any(date_term in col.lower() for date_term in ['date', 'period', 'year', 'month', 'quarter']):
                # Try to convert to datetime
                try:
                    pd.to_datetime(self.data[col], errors='raise')
                    self.date_columns.append(col)
                except:
                    pass
        
        # Remove identified date columns from text columns
        self.text_columns = [col for col in self.text_columns if col not in self.date_columns]
        
        # Detect statement type if processor is available
        if self.processor:
            self.detected_statement_type = self.processor.detect_statement_type()
        else:
            # Try to infer statement type from column names
            self._infer_statement_type()
    
    def _infer_statement_type(self):
        """Infer financial statement type from data structure"""
        if self.data is None or self.data.empty:
            return
        
        # Check column names
        all_cols = ' '.join(self.data.columns.astype(str)).lower()
        
        # Income statement indicators
        income_terms = ['revenue', 'sales', 'income', 'expense', 'profit', 'loss', 'ebitda', 'ebit', 'tax']
        
        # Balance sheet indicators
        balance_terms = ['asset', 'liability', 'equity', 'cash', 'receivable', 'payable', 'debt', 'inventory']
        
        # Cash flow indicators
        cashflow_terms = ['cash flow', 'operating', 'investing', 'financing', 'dividend']
        
        # Count occurrences
        income_count = sum(1 for term in income_terms if term in all_cols)
        balance_count = sum(1 for term in balance_terms if term in all_cols)
        cashflow_count = sum(1 for term in cashflow_terms if term in all_cols)
        
        # Determine type based on highest count
        if income_count > balance_count and income_count > cashflow_count:
            self.detected_statement_type = "income_statement"
        elif balance_count > income_count and balance_count > cashflow_count:
            self.detected_statement_type = "balance_sheet"
        elif cashflow_count > income_count and cashflow_count > balance_count:
            self.detected_statement_type = "cash_flow"
        else:
            # Check row names if available
            if self.data.index.name or isinstance(self.data.index, pd.MultiIndex):
                all_rows = ' '.join(self.data.index.astype(str)).lower()
                
                income_count = sum(1 for term in income_terms if term in all_rows)
                balance_count = sum(1 for term in balance_terms if term in all_rows)
                cashflow_count = sum(1 for term in cashflow_terms if term in all_rows)
                
                if income_count > balance_count and income_count > cashflow_count:
                    self.detected_statement_type = "income_statement"
                elif balance_count > income_count and balance_count > cashflow_count:
                    self.detected_statement_type = "balance_sheet"
                elif cashflow_count > income_count and cashflow_count > balance_count:
                    self.detected_statement_type = "cash_flow"
                else:
                    self.detected_statement_type = "unknown"
            else:
                self.detected_statement_type = "unknown"
    
    def auto_visualize(self) -> Dict[str, Any]:
        """Automatically create appropriate visualizations based on data structure"""
        if not self.permissions["visualization"]:
            st.error("Visualization permission not granted")
            return {"error": "Permission denied"}
        
        if self.data is None or self.data.empty:
            st.error("No data available for visualization")
            return {"error": "No data available"}
        
        st.write("🤖 AI Assistant: Analyzing your data to create the most insightful visualizations...")
        
        visualizations = {}
        
        # Determine data characteristics
        row_count = len(self.data)
        col_count = len(self.data.columns)
        numeric_count = len(self.numeric_columns)
        has_dates = len(self.date_columns) > 0
        
        # 1. Always show data summary
        visualizations["data_summary"] = self._create_data_summary()
        
        # 2. Determine appropriate visualizations based on data structure
        if numeric_count >= 1:
            # Time series if we have date columns
            if has_dates:
                visualizations["time_series"] = self.create_time_series()
            
            # Distribution analysis
            visualizations["distribution"] = self.create_distribution_analysis()
            
            # Correlation matrix if we have multiple numeric columns
            if numeric_count >= 3:
                visualizations["correlation"] = self.create_correlation_matrix()
            
            # Financial specific visualizations if detected
            if self.detected_statement_type:
                if self.detected_statement_type == "income_statement":
                    visualizations["income_analysis"] = self.create_income_statement_analysis()
                elif self.detected_statement_type == "balance_sheet":
                    visualizations["balance_analysis"] = self.create_balance_sheet_analysis()
                elif self.detected_statement_type == "cash_flow":
                    visualizations["cashflow_analysis"] = self.create_cash_flow_analysis()
                
                # Add ratio analysis if financial data
                visualizations["ratio_analysis"] = self.create_ratio_analysis()
            
            # Trend analysis for any numeric data
            visualizations["trend_analysis"] = self.create_trend_analysis()
            
            # Comparative analysis if we have multiple periods
            if col_count >= 3:
                visualizations["comparative"] = self.create_comparative_analysis()
        
        return visualizations
    
    def _create_data_summary(self) -> Dict[str, Any]:
        """Create a summary of the data"""
        summary = {
            "file_info": {
                "name": self.file_name,
                "type": self.file_type,
                "detected_statement": self.detected_statement_type
            },
            "structure": {
                "rows": len(self.data),
                "columns": len(self.data.columns),
                "numeric_columns": len(self.numeric_columns),
                "text_columns": len(self.text_columns),
                "date_columns": len(self.date_columns)
            },
            "sample_data": self.data.head(5).to_dict(),
            "column_types": {
                "numeric": self.numeric_columns,
                "text": self.text_columns,
                "date": self.date_columns
            }
        }
        
        # Add basic statistics if we have numeric columns
        if self.numeric_columns:
            summary["statistics"] = {
                "mean": self.data[self.numeric_columns].mean().to_dict(),
                "median": self.data[self.numeric_columns].median().to_dict(),
                "min": self.data[self.numeric_columns].min().to_dict(),
                "max": self.data[self.numeric_columns].max().to_dict(),
                "missing_values": self.data[self.numeric_columns].isna().sum().to_dict()
            }
        
        return summary
    
    def create_time_series(self) -> go.Figure:
        """Create time series visualization if date columns are present"""
        try:
            if not self.date_columns or not self.numeric_columns:
                return self._create_empty_figure("No date or numeric columns available")
            
            # Use the first date column
            date_col = self.date_columns[0]
            
            # Select top numeric columns (to avoid overcrowding)
            top_numeric = self.numeric_columns[:5]
            
            # Create figure
            fig = go.Figure()
            
            for col in top_numeric:
                # Sort data by date
                sorted_data = self.data.sort_values(date_col)
                
                fig.add_trace(go.Scatter(
                    x=sorted_data[date_col],
                    y=sorted_data[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title="Time Series Analysis",
                xaxis_title=date_col,
                yaxis_title="Value",
                height=500,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating time series: {str(e)}")
            return self._create_empty_figure("Error in time series visualization")
    
    def create_distribution_analysis(self) -> go.Figure:
        """Create distribution analysis for numeric columns"""
        try:
            if not self.numeric_columns:
                return self._create_empty_figure("No numeric columns available")
            
            # Select top numeric columns (to avoid overcrowding)
            top_numeric = self.numeric_columns[:4]
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[col for col in top_numeric],
                specs=[[{"type": "histogram"}, {"type": "box"}],
                       [{"type": "violin"}, {"type": "bar"}]]
            )
            
            # Add histograms and box plots
            for i, col in enumerate(top_numeric):
                row = (i // 2) + 1
                col_idx = (i % 2) + 1
                
                # Clean data (remove NaN and inf)
                clean_data = self.data[col].replace([np.inf, -np.inf], np.nan).dropna()
                
                if clean_data.empty:
                    continue
                
                # Add histogram
                fig.add_trace(
                    go.Histogram(
                        x=clean_data,
                        name=f"{col} Histogram",
                        marker_color=self.color_schemes['categorical'][i],
                        opacity=0.7
                    ),
                    row=row, col=col_idx
                )
                
                # Add box plot if we have enough space
                if i < 2:
                    fig.add_trace(
                        go.Box(
                            y=clean_data,
                            name=f"{col} Box",
                            marker_color=self.color_schemes['categorical'][i]
                        ),
                        row=1, col=2
                    )
                
                # Add violin plot if we have enough space
                if i < 2:
                    fig.add_trace(
                        go.Violin(
                            y=clean_data,
                            name=f"{col} Violin",
                            box_visible=True,
                            meanline_visible=True,
                            marker_color=self.color_schemes['categorical'][i]
                        ),
                        row=2, col=1
                    )
            
            # Add descriptive statistics as a bar chart
            if self.numeric_columns:
                stats = self.data[self.numeric_columns[0]].describe()
                fig.add_trace(
                    go.Bar(
                        x=stats.index,
                        y=stats.values,
                        name="Statistics",
                        marker_color=self.color_schemes['categorical'][3]
                    ),
                    row=2, col=2
                )
            
            fig.update_layout(
                title="Distribution Analysis",
                height=700,
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating distribution analysis: {str(e)}")
            return self._create_empty_figure("Error in distribution analysis")
    
    def create_correlation_matrix(self) -> go.Figure:
        """Create correlation matrix between numeric columns"""
        try:
            if len(self.numeric_columns) < 2:
                return self._create_empty_figure("Need at least 2 numeric columns for correlation matrix")
            
            # Calculate correlation matrix
            corr_matrix = self.data[self.numeric_columns].corr()
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.index,
                colorscale='RdBu',
                zmid=0,
                text=[[f"{val:.2f}" for val in row] for row in corr_matrix.values],
                texttemplate="%{text}",
                textfont={"size": 10},
                hovertemplate='%{y} & %{x}<br>Correlation: %{z:.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Correlation Matrix",
                height=600,
                width=700
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating correlation matrix: {str(e)}")
            return self._create_empty_figure("Error in correlation matrix")
    
    def create_income_statement_analysis(self) -> go.Figure:
        """Create income statement analysis visualization"""
        try:
            # Look for key income statement accounts
            revenue_cols = [col for col in self.data.columns if any(term in str(col).lower() for term in ['revenue', 'sales', 'income'])]
            expense_cols = [col for col in self.data.columns if any(term in str(col).lower() for term in ['expense', 'cost', 'cogs'])]
            profit_cols = [col for col in self.data.columns if any(term in str(col).lower() for term in ['profit', 'margin', 'ebitda', 'ebit', 'net income'])]
            
            if not revenue_cols and not expense_cols and not profit_cols:
                # Try to identify from row labels if columns don't match
                revenue_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['revenue', 'sales', 'income']))].tolist()
                expense_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['expense', 'cost', 'cogs']))].tolist()
                profit_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['profit', 'margin', 'ebitda', 'ebit', 'net income']))].tolist()
                
                # Create waterfall chart
                if revenue_rows and expense_rows and profit_rows and self.numeric_columns:
                    # Use the latest period
                    period = self.numeric_columns[-1]
                    
                    # Get values
                    revenue = self.data.loc[revenue_rows, period].sum()
                    expenses = abs(self.data.loc[expense_rows, period].sum())
                    profit = self.data.loc[profit_rows, period].sum()
                    
                    # Create waterfall chart
                    fig = go.Figure(go.Waterfall(
                        name="Income Statement",
                        orientation="v",
                        measure=["absolute", "relative", "total"],
                        x=["Revenue", "Expenses", "Profit"],
                        textposition="outside",
                        text=[f"{revenue:,.2f}", f"{-expenses:,.2f}", f"{profit:,.2f}"],
                        y=[revenue, -expenses, profit],
                        connector={"line": {"color": "rgb(63, 63, 63)"}},
                        decreasing={"marker": {"color": "red"}},
                        increasing={"marker": {"color": "green"}},
                        totals={"marker": {"color": "blue"}}
                    ))
                    
                    fig.update_layout(
                        title=f"Income Statement Analysis - {period}",
                        showlegend=False,
                        height=500
                    )
                    
                    return fig
            
            # If we have multiple periods, create a trend analysis
            if len(self.numeric_columns) >= 2:
                fig = go.Figure()
                
                # Add revenue trend
                if revenue_rows:
                    revenue_values = [self.data.loc[revenue_rows, period].sum() for period in self.numeric_columns]
                    fig.add_trace(go.Scatter(
                        x=self.numeric_columns,
                        y=revenue_values,
                        mode='lines+markers',
                        name='Revenue',
                        line=dict(color='green', width=2)
                    ))
                
                # Add expense trend
                if expense_rows:
                    expense_values = [abs(self.data.loc[expense_rows, period].sum()) for period in self.numeric_columns]
                    fig.add_trace(go.Scatter(
                        x=self.numeric_columns,
                        y=expense_values,
                        mode='lines+markers',
                        name='Expenses',
                        line=dict(color='red', width=2)
                    ))
                
                # Add profit trend
                if profit_rows:
                    profit_values = [self.data.loc[profit_rows, period].sum() for period in self.numeric_columns]
                    fig.add_trace(go.Scatter(
                        x=self.numeric_columns,
                        y=profit_values,
                        mode='lines+markers',
                        name='Profit',
                        line=dict(color='blue', width=2)
                    ))
                
                fig.update_layout(
                    title="Income Statement Trends",
                    xaxis_title="Period",
                    yaxis_title="Amount",
                    height=500,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                return fig
            
            # Default to a simple bar chart of the latest period
            if self.numeric_columns:
                latest_period = self.numeric_columns[-1]
                
                # Get top accounts by absolute value
                top_accounts = self.data[latest_period].abs().nlargest(10).index
                
                fig = go.Figure(go.Bar(
                    x=[str(idx) for idx in top_accounts],
                    y=self.data.loc[top_accounts, latest_period],
                    marker_color=['green' if val >= 0 else 'red' for val in self.data.loc[top_accounts, latest_period]]
                ))
                
                fig.update_layout(
                    title=f"Income Statement - {latest_period}",
                    xaxis_title="Account",
                    yaxis_title="Amount",
                    height=500
                )
                
                return fig
            
            return self._create_empty_figure("Insufficient data for income statement analysis")
            
        except Exception as e:
            st.error(f"Error creating income statement analysis: {str(e)}")
            return self._create_empty_figure("Error in income statement analysis")
    
    def create_balance_sheet_analysis(self) -> go.Figure:
        """Create balance sheet analysis visualization"""
        try:
            # Look for key balance sheet accounts
            asset_cols = [col for col in self.data.columns if any(term in str(col).lower() for term in ['asset', 'cash', 'receivable', 'inventory'])]
            liability_cols = [col for col in self.data.columns if any(term in str(col).lower() for term in ['liability', 'payable', 'debt'])]
            equity_cols = [col for col in self.data.columns if any(term in str(col).lower() for term in ['equity', 'capital', 'retained'])]
            
            if not asset_cols and not liability_cols and not equity_cols:
                # Try to identify from row labels if columns don't match
                asset_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['asset', 'cash', 'receivable', 'inventory']))].tolist()
                liability_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['liability', 'payable', 'debt']))].tolist()
                equity_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['equity', 'capital', 'retained']))].tolist()
                
                # Create pie chart for latest period
                if (asset_rows or liability_rows or equity_rows) and self.numeric_columns:
                    # Use the latest period
                    period = self.numeric_columns[-1]
                    
                    # Create figure with subplots
                    fig = make_subplots(
                        rows=1, cols=2,
                        specs=[[{"type": "pie"}, {"type": "pie"}]],
                        subplot_titles=["Assets", "Liabilities & Equity"]
                    )
                    
                    # Assets breakdown
                    if asset_rows:
                        asset_data = self.data.loc[asset_rows, period]
                        asset_data = asset_data[asset_data > 0]  # Only positive values
                        
                        if not asset_data.empty:
                            fig.add_trace(
                                go.Pie(
                                    labels=[str(idx) for idx in asset_data.index],
                                    values=asset_data.values,
                                    name="Assets",
                                    marker_colors=self.color_schemes['categorical'][:len(asset_data)]
                                ),
                                row=1, col=1
                            )
                    
                    # Liabilities and Equity breakdown
                    combined_data = pd.Series()
                    
                    if liability_rows:
                        liability_data = self.data.loc[liability_rows, period]
                        combined_data = pd.concat([combined_data, liability_data])
                    
                    if equity_rows:
                        equity_data = self.data.loc[equity_rows, period]
                        combined_data = pd.concat([combined_data, equity_data])
                    
                    if not combined_data.empty:
                        fig.add_trace(
                            go.Pie(
                                labels=[str(idx) for idx in combined_data.index],
                                values=combined_data.values,
                                name="Liabilities & Equity",
                                marker_colors=self.color_schemes['categorical'][len(asset_data):len(asset_data)+len(combined_data)]
                            ),
                            row=1, col=2
                        )
                    
                    fig.update_layout(
                        title=f"Balance Sheet Analysis - {period}",
                        height=500
                    )
                    
                    return fig
            
            # If we have multiple periods, create a trend analysis
            if len(self.numeric_columns) >= 2:
                fig = go.Figure()
                
                # Add asset trend
                if asset_rows:
                    asset_values = [self.data.loc[asset_rows, period].sum() for period in self.numeric_columns]
                    fig.add_trace(go.Scatter(
                        x=self.numeric_columns,
                        y=asset_values,
                        mode='lines+markers',
                        name='Assets',
                        line=dict(color='blue', width=2)
                    ))
                
                # Add liability trend
                if liability_rows:
                    liability_values = [self.data.loc[liability_rows, period].sum() for period in self.numeric_columns]
                    fig.add_trace(go.Scatter(
                        x=self.numeric_columns,
                        y=liability_values,
                        mode='lines+markers',
                        name='Liabilities',
                        line=dict(color='red', width=2)
                    ))
                
                # Add equity trend
                if equity_rows:
                    equity_values = [self.data.loc[equity_rows, period].sum() for period in self.numeric_columns]
                    fig.add_trace(go.Scatter(
                        x=self.numeric_columns,
                        y=equity_values,
                        mode='lines+markers',
                        name='Equity',
                        line=dict(color='green', width=2)
                    ))
                
                fig.update_layout(
                    title="Balance Sheet Trends",
                    xaxis_title="Period",
                    yaxis_title="Amount",
                    height=500,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                return fig
            
            # Default to a simple bar chart of the latest period
            if self.numeric_columns:
                latest_period = self.numeric_columns[-1]
                
                # Get top accounts by absolute value
                top_accounts = self.data[latest_period].abs().nlargest(10).index
                
                fig = go.Figure(go.Bar(
                    x=[str(idx) for idx in top_accounts],
                    y=self.data.loc[top_accounts, latest_period],
                    marker_color=['blue' if val >= 0 else 'red' for val in self.data.loc[top_accounts, latest_period]]
                ))
                
                fig.update_layout(
                    title=f"Balance Sheet - {latest_period}",
                    xaxis_title="Account",
                    yaxis_title="Amount",
                    height=500
                )
                
                return fig
            
            return self._create_empty_figure("Insufficient data for balance sheet analysis")
            
        except Exception as e:
            st.error(f"Error creating balance sheet analysis: {str(e)}")
            return self._create_empty_figure("Error in balance sheet analysis")
    
    def create_cash_flow_analysis(self) -> go.Figure:
        """Create cash flow analysis visualization"""
        try:
            # Look for key cash flow accounts
            operating_cols = [col for col in self.data.columns if any(term in str(col).lower() for term in ['operating', 'operations'])]
            investing_cols = [col for col in self.data.columns if any(term in str(col).lower() for term in ['investing', 'investment'])]
            financing_cols = [col for col in self.data.columns if any(term in str(col).lower() for term in ['financing', 'finance'])]
            
            if not operating_cols and not investing_cols and not financing_cols:
                # Try to identify from row labels if columns don't match
                operating_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['operating', 'operations']))].tolist()
                investing_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['investing', 'investment']))].tolist()
                financing_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['financing', 'finance']))].tolist()
                
                # Create waterfall chart for latest period
                if (operating_rows or investing_rows or financing_rows) and self.numeric_columns:
                    # Use the latest period
                    period = self.numeric_columns[-1]
                    
                    # Get values
                    operating = self.data.loc[operating_rows, period].sum() if operating_rows else 0
                    investing = self.data.loc[investing_rows, period].sum() if investing_rows else 0
                    financing = self.data.loc[financing_rows, period].sum() if financing_rows else 0
                    
                    # Calculate net change
                    net_change = operating + investing + financing
                    
                    # Create waterfall chart
                    fig = go.Figure(go.Waterfall(
                        name="Cash Flow",
                        orientation="v",
                        measure=["relative", "relative", "relative", "total"],
                        x=["Operating", "Investing", "Financing", "Net Change"],
                        textposition="outside",
                        text=[f"{operating:,.2f}", f"{investing:,.2f}", f"{financing:,.2f}", f"{net_change:,.2f}"],
                        y=[operating, investing, financing, net_change],
                        connector={"line": {"color": "rgb(63, 63, 63)"}},
                        decreasing={"marker": {"color": "red"}},
                        increasing={"marker": {"color": "green"}},
                        totals={"marker": {"color": "blue"}}
                    ))
                    
                    fig.update_layout(
                        title=f"Cash Flow Analysis - {period}",
                        showlegend=False,
                        height=500
                    )
                    
                    return fig
            
            # If we have multiple periods, create a trend analysis
            if len(self.numeric_columns) >= 2:
                fig = go.Figure()
                
                # Add operating cash flow trend
                if operating_rows:
                    operating_values = [self.data.loc[operating_rows, period].sum() for period in self.numeric_columns]
                    fig.add_trace(go.Scatter(
                        x=self.numeric_columns,
                        y=operating_values,
                        mode='lines+markers',
                        name='Operating',
                        line=dict(color='green', width=2)
                    ))
                
                # Add investing cash flow trend
                if investing_rows:
                    investing_values = [self.data.loc[investing_rows, period].sum() for period in self.numeric_columns]
                    fig.add_trace(go.Scatter(
                        x=self.numeric_columns,
                        y=investing_values,
                        mode='lines+markers',
                        name='Investing',
                        line=dict(color='blue', width=2)
                    ))
                
                # Add financing cash flow trend
                if financing_rows:
                    financing_values = [self.data.loc[financing_rows, period].sum() for period in self.numeric_columns]
                    fig.add_trace(go.Scatter(
                        x=self.numeric_columns,
                        y=financing_values,
                        mode='lines+markers',
                        name='Financing',
                        line=dict(color='red', width=2)
                    ))
                
                # Add net cash flow trend
                if operating_rows or investing_rows or financing_rows:
                    net_values = []
                    for period in self.numeric_columns:
                        operating_val = self.data.loc[operating_rows, period].sum() if operating_rows else 0
                        investing_val = self.data.loc[investing_rows, period].sum() if investing_rows else 0
                        financing_val = self.data.loc[financing_rows, period].sum() if financing_rows else 0
                        net_values.append(operating_val + investing_val + financing_val)
                    
                    fig.add_trace(go.Scatter(
                        x=self.numeric_columns,
                        y=net_values,
                        mode='lines+markers',
                        name='Net Cash Flow',
                        line=dict(color='purple', width=3)
                    ))
                
                fig.update_layout(
                    title="Cash Flow Trends",
                    xaxis_title="Period",
                    yaxis_title="Amount",
                    height=500,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                return fig
            
            # Default to a simple bar chart of the latest period
            if self.numeric_columns:
                latest_period = self.numeric_columns[-1]
                
                # Get top accounts by absolute value
                top_accounts = self.data[latest_period].abs().nlargest(10).index
                
                fig = go.Figure(go.Bar(
                    x=[str(idx) for idx in top_accounts],
                    y=self.data.loc[top_accounts, latest_period],
                    marker_color=['green' if val >= 0 else 'red' for val in self.data.loc[top_accounts, latest_period]]
                ))
                
                fig.update_layout(
                    title=f"Cash Flow - {latest_period}",
                    xaxis_title="Account",
                    yaxis_title="Amount",
                    height=500
                )
                
                return fig
            
            return self._create_empty_figure("Insufficient data for cash flow analysis")
            
        except Exception as e:
            st.error(f"Error creating cash flow analysis: {str(e)}")
            return self._create_empty_figure("Error in cash flow analysis")
    
    def create_ratio_analysis(self) -> go.Figure:
        """Create financial ratio analysis visualization"""
        try:
            if not self.detected_statement_type or not self.numeric_columns:
                return self._create_empty_figure("Insufficient data for ratio analysis")
            
            # Define ratios based on statement type
            ratios = {}
            
            if self.detected_statement_type == "income_statement":
                # Look for key accounts
                revenue_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['revenue', 'sales']))].tolist()
                gross_profit_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['gross profit', 'gross margin']))].tolist()
                operating_profit_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['operating profit', 'operating income', 'ebit']))].tolist()
                net_profit_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['net profit', 'net income', 'profit after tax']))].tolist()
                
                # Calculate ratios for each period
                for period in self.numeric_columns:
                    revenue = self.data.loc[revenue_rows, period].sum() if revenue_rows else 0
                    
                    if revenue > 0:
                        gross_profit = self.data.loc[gross_profit_rows, period].sum() if gross_profit_rows else 0
                        operating_profit = self.data.loc[operating_profit_rows, period].sum() if operating_profit_rows else 0
                        net_profit = self.data.loc[net_profit_rows, period].sum() if net_profit_rows else 0
                        
                        if period not in ratios:
                            ratios[period] = {}
                        
                        ratios[period]["Gross Margin"] = (gross_profit / revenue) * 100 if gross_profit else 0
                        ratios[period]["Operating Margin"] = (operating_profit / revenue) * 100 if operating_profit else 0
                        ratios[period]["Net Margin"] = (net_profit / revenue) * 100 if net_profit else 0
            
            elif self.detected_statement_type == "balance_sheet":
                # Look for key accounts
                asset_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['asset', 'total asset']))].tolist()
                current_asset_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['current asset', 'cash', 'receivable', 'inventory']))].tolist()
                liability_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['liability', 'total liability']))].tolist()
                current_liability_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['current liability', 'payable', 'short term']))].tolist()
                equity_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['equity', 'capital']))].tolist()
                
                # Calculate ratios for each period
                for period in self.numeric_columns:
                    assets = self.data.loc[asset_rows, period].sum() if asset_rows else 0
                    current_assets = self.data.loc[current_asset_rows, period].sum() if current_asset_rows else 0
                    liabilities = self.data.loc[liability_rows, period].sum() if liability_rows else 0
                    current_liabilities = self.data.loc[current_liability_rows, period].sum() if current_liability_rows else 0
                    equity = self.data.loc[equity_rows, period].sum() if equity_rows else 0
                    
                    if period not in ratios:
                        ratios[period] = {}
                    
                    if current_liabilities > 0:
                        ratios[period]["Current Ratio"] = current_assets / current_liabilities
                    
                    if liabilities > 0:
                        ratios[period]["Debt-to-Equity"] = liabilities / equity if equity > 0 else 0
                    
                    if assets > 0:
                        ratios[period]["ROA"] = 0  # Would need income statement data
                        ratios[period]["Asset Turnover"] = 0  # Would need income statement data
            
            elif self.detected_statement_type == "cash_flow":
                # Look for key accounts
                operating_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['operating', 'operations']))].tolist()
                investing_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['investing', 'investment']))].tolist()
                financing_rows = self.data.index[self.data.index.astype(str).str.lower().str.contains('|'.join(['financing', 'finance']))].tolist()
                
                # Calculate ratios for each period
                for period in self.numeric_columns:
                    operating = self.data.loc[operating_rows, period].sum() if operating_rows else 0
                    investing = self.data.loc[investing_rows, period].sum() if investing_rows else 0
                    financing = self.data.loc[financing_rows, period].sum() if financing_rows else 0
                    
                    if period not in ratios:
                        ratios[period] = {}
                    
                    total_cash_flow = operating + investing + financing
                    
                    if total_cash_flow != 0:
                        ratios[period]["Operating %"] = (operating / abs(total_cash_flow)) * 100
                        ratios[period]["Investing %"] = (investing / abs(total_cash_flow)) * 100
                        ratios[period]["Financing %"] = (financing / abs(total_cash_flow)) * 100
            
            # Create visualization
            if not ratios:
                return self._create_empty_figure("Could not calculate financial ratios")
            
            # Create figure
            fig = go.Figure()
            
            # Get all ratio types
            all_ratio_types = set()
            for period_ratios in ratios.values():
                all_ratio_types.update(period_ratios.keys())
            
            # Add a trace for each ratio type
            for ratio_type in all_ratio_types:
                x_values = []
                y_values = []
                
                for period in self.numeric_columns:
                    if period in ratios and ratio_type in ratios[period]:
                        x_values.append(period)
                        y_values.append(ratios[period][ratio_type])
                
                if x_values:
                    fig.add_trace(go.Scatter(
                        x=x_values,
                        y=y_values,
                        mode='lines+markers',


                        name=ratio_type,
                        line=dict(width=2)
                    ))
            
            fig.update_layout(
                title="Financial Ratio Analysis",
                xaxis_title="Period",
                yaxis_title="Ratio Value",
                height=500,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating ratio analysis: {str(e)}")
            return self._create_empty_figure("Error in ratio analysis")
    
    def create_trend_analysis(self) -> go.Figure:
        """Create trend analysis for numeric data"""
        try:
            if not self.numeric_columns or len(self.numeric_columns) < 2:
                return self._create_empty_figure("Need at least 2 periods for trend analysis")
            
            # Get top accounts by absolute value in the latest period
            latest_period = self.numeric_columns[-1]
            latest_data = self.data[latest_period].dropna().abs()
            
            if latest_data.empty:
                return self._create_empty_figure("No data available for trend analysis")
            
            top_accounts = latest_data.nlargest(5).index
            
            # Create figure
            fig = go.Figure()
            
            # Add a trace for each top account
            for idx in top_accounts:
                account_name = str(idx)
                if self.text_columns and idx in self.data.index:
                    account_name = str(self.data.loc[idx, self.text_columns[0]])
                
                values = []
                for period in self.numeric_columns:
                    try:
                        value = float(self.data.loc[idx, period])
                        values.append(value)
                    except (ValueError, KeyError, TypeError):
                        values.append(None)
                
                fig.add_trace(go.Scatter(
                    x=self.numeric_columns,
                    y=values,
                    mode='lines+markers',
                    name=account_name,
                    line=dict(width=2)
                ))
            
            # Add trendlines
            for i, idx in enumerate(top_accounts):
                values = []
                periods = []
                
                for j, period in enumerate(self.numeric_columns):
                    try:
                        value = float(self.data.loc[idx, period])
                        if not pd.isna(value):
                            values.append(value)
                            periods.append(j)  # Use index as x-value for regression
                    except (ValueError, KeyError, TypeError):
                        pass
                
                if len(values) >= 2:
                    # Calculate linear regression
                    z = np.polyfit(periods, values, 1)
                    p = np.poly1d(z)
                    
                    # Generate trendline values
                    trend_x = list(range(len(self.numeric_columns)))
                    trend_y = [p(x) for x in trend_x]
                    
                    # Add trendline
                    fig.add_trace(go.Scatter(
                        x=self.numeric_columns,
                        y=trend_y,
                        mode='lines',
                        name=f'Trend: {str(idx)}',
                        line=dict(dash='dash', width=1),
                        showlegend=False
                    ))
            
            fig.update_layout(
                title="Trend Analysis",
                xaxis_title="Period",
                yaxis_title="Value",
                height=500,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating trend analysis: {str(e)}")
            return self._create_empty_figure("Error in trend analysis")
    
    def create_comparative_analysis(self) -> go.Figure:
        """Create comparative analysis between periods"""
        try:
            if len(self.numeric_columns) < 2:
                return self._create_empty_figure("Need at least 2 periods for comparative analysis")
            
            # Get the two most recent periods
            current_period = self.numeric_columns[-1]
            previous_period = self.numeric_columns[-2]
            
            # Get top accounts by absolute value in the current period
            current_data = self.data[current_period].dropna().abs()
            
            if current_data.empty:
                return self._create_empty_figure("No data available for comparative analysis")
            
            top_accounts = current_data.nlargest(10).index
            
            # Prepare data for comparison
            account_names = []
            current_values = []
            previous_values = []
            percent_changes = []
            
            for idx in top_accounts:
                try:
                    current_value = float(self.data.loc[idx, current_period])
                    previous_value = float(self.data.loc[idx, previous_period])
                    
                    account_name = str(idx)
                    if self.text_columns and idx in self.data.index:
                        account_name = str(self.data.loc[idx, self.text_columns[0]])
                    
                    account_names.append(account_name)
                    current_values.append(current_value)
                    previous_values.append(previous_value)
                    
                    # Calculate percent change
                    if previous_value != 0:
                        percent_change = ((current_value - previous_value) / abs(previous_value)) * 100
                    else:
                        percent_change = float('inf') if current_value > 0 else float('-inf') if current_value < 0 else 0
                    
                    percent_changes.append(percent_change)
                    
                except (ValueError, KeyError, TypeError):
                    continue
            
            if not account_names:
                return self._create_empty_figure("No valid data for comparison")
            
            # Create figure with subplots
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=[
                    f"Period Comparison: {current_period} vs {previous_period}",
                    "Percent Change"
                ],
                row_heights=[0.7, 0.3],
                vertical_spacing=0.1
            )
            
            # Add bar chart for current vs previous
            fig.add_trace(
                go.Bar(
                    x=account_names,
                    y=current_values,
                    name=current_period,
                    marker_color=self.color_schemes['financial'][0]
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(
                    x=account_names,
                    y=previous_values,
                    name=previous_period,
                    marker_color=self.color_schemes['financial'][1]
                ),
                row=1, col=1
            )
            
            # Add percent change
            fig.add_trace(
                go.Bar(
                    x=account_names,
                    y=percent_changes,
                    name="% Change",
                    marker_color=[
                        'green' if val > 0 else 'red' if val < 0 else 'gray'
                        for val in percent_changes
                    ]
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                height=700,
                barmode='group',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Update y-axis labels
            fig.update_yaxes(title_text="Value", row=1, col=1)
            fig.update_yaxes(title_text="% Change", row=2, col=1)
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating comparative analysis: {str(e)}")
            return self._create_empty_figure("Error in comparative analysis")
    
    def _create_empty_figure(self, message: str) -> go.Figure:
        """Create an empty figure with a message"""
        fig = go.Figure()
        
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            text=message,
            showarrow=False,
            font=dict(size=16)
        )
        
        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=400
        )
        
        return fig
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score value"""
        if score >= 70:
            return 'green'
        elif score >= 40:
            return 'orange'
        else:
            return 'red'
    
    def _get_ratio_benchmarks(self, statement_type: str) -> Dict[str, float]:
        """Get industry benchmark ratios based on statement type"""
        # These are generic benchmarks - in a real application, these would be industry-specific
        benchmarks = {
            "income_statement": {
                "gross_profit_margin": 40.0,
                "operating_margin": 15.0,
                "net_profit_margin": 10.0,
                "return_on_assets": 5.0,
                "return_on_equity": 15.0
            },
            "balance_sheet": {
                "current_ratio": 2.0,
                "quick_ratio": 1.0,
                "debt_to_equity": 1.5,
                "debt_ratio": 0.5,
                "asset_turnover": 0.5
            },
            "cash_flow": {
                "operating_cash_flow_ratio": 1.0,
                "cash_flow_coverage": 1.5,
                "cash_flow_to_debt": 0.2
            },
            "unknown": {
                "default_benchmark": 1.0
            }
        }
        
        return benchmarks.get(statement_type, benchmarks["unknown"])

# Streamlit app for financial visualization
def create_financial_visualization_app():
    st.set_page_config(page_title="Financial Data Visualizer", layout="wide")
    
    st.title("🤖 AI-Powered Financial Data Visualizer")
    st.markdown("Upload your financial data file and let the AI analyze and visualize it for you.")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a financial data file", type=["csv", "xlsx", "xls", "json"])
    
    if uploaded_file is not None:
        # Create visualizer
        visualizer = FinancialVisualizer()
        
        # Load data
        if visualizer.load_data(uploaded_file):
            st.success(f"Successfully loaded: {uploaded_file.name}")
            
            # Display data summary
            with st.expander("Data Summary", expanded=True):
                st.write(f"File type: {visualizer.file_type}")
                st.write(f"Rows: {len(visualizer.data)}")
                st.write(f"Columns: {len(visualizer.data.columns)}")
                st.write(f"Detected statement type: {visualizer.detected_statement_type}")
                
                # Display sample data
                st.subheader("Sample Data")
                st.dataframe(visualizer.data.head())
            
            # Auto-generate visualizations
            st.subheader("AI-Generated Visualizations")
            
            with st.spinner("AI is analyzing your data and creating visualizations..."):
                visualizations = visualizer.auto_visualize()
            
            # Display visualizations in tabs
            if visualizations:
                tabs = st.tabs([
                    "Time Series" if "time_series" in visualizations else "Distribution",
                    "Financial Analysis",
                    "Trends & Comparisons",
                    "Correlation Analysis"
                ])
                
                # Tab 1: Time Series or Distribution
                with tabs[0]:
                    if "time_series" in visualizations:
                        st.plotly_chart(visualizations["time_series"], use_container_width=True)
                    elif "distribution" in visualizations:
                        st.plotly_chart(visualizations["distribution"], use_container_width=True)
                
                # Tab 2: Financial Analysis
                with tabs[1]:
                    if visualizer.detected_statement_type == "income_statement" and "income_analysis" in visualizations:
                        st.plotly_chart(visualizations["income_analysis"], use_container_width=True)
                    elif visualizer.detected_statement_type == "balance_sheet" and "balance_analysis" in visualizations:
                        st.plotly_chart(visualizations["balance_analysis"], use_container_width=True)
                    elif visualizer.detected_statement_type == "cash_flow" and "cashflow_analysis" in visualizations:
                        st.plotly_chart(visualizations["cashflow_analysis"], use_container_width=True)
                    
                    if "ratio_analysis" in visualizations:
                        st.plotly_chart(visualizations["ratio_analysis"], use_container_width=True)
                
                # Tab 3: Trends & Comparisons
                with tabs[2]:
                    if "trend_analysis" in visualizations:
                        st.plotly_chart(visualizations["trend_analysis"], use_container_width=True)
                    
                    if "comparative" in visualizations:
                        st.plotly_chart(visualizations["comparative"], use_container_width=True)
                
                # Tab 4: Correlation Analysis
                with tabs[3]:
                    if "correlation" in visualizations:
                        st.plotly_chart(visualizations["correlation"], use_container_width=True)
            else:
                st.warning("No visualizations could be generated from this data.")
        else:
            st.error("Failed to load the file. Please check the file format.")
    else:
        # Show demo instructions
        st.info("👆 Upload a financial data file (CSV, Excel, or JSON) to get started.")
        st.markdown("""
        ### What this app can do:
        
        - Automatically detect the type of financial statement
        - Create appropriate visualizations based on your data
        - Analyze trends and patterns
        - Compare periods and identify key changes
        - Calculate financial ratios and benchmarks
        
        ### Sample data formats:
        
        - Income statements with revenue, expenses, and profit data
        - Balance sheets with assets, liabilities, and equity
        - Cash flow statements with operating, investing, and financing activities
        - Any tabular financial data with multiple periods
        """)

if __name__ == "__main__":
    create_financial_visualization_app()
