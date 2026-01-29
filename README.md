# Financial Statement Analyzer

A comprehensive analytical platform designed for automated financial data processing, ratio calculation, and AI-driven insights. This system provides professional-grade tools for interpreting balance sheets, income statements, and cash flow reports.

## Overview

The Financial Statement Analyzer is a Streamlit-based application that automates the extraction and analysis of financial metrics from structured data files. It leverages advanced data processing techniques and large language models (LLMs) to provide deep insights into organizational financial health.

## Core Features

- **Automated Statement Detection**: Intelligent identification of financial statement types (Balance Sheet, Income Statement, Cash Flow Statement) using heuristic and machine learning patterns.
- **AI-Powered Analysis**: Integration with Microsoft Phi-4 via OpenRouter for generating strategic insights and qualitative assessments of financial data.
- **Financial Ratio Engine**: Automatic calculation of over 20 critical financial ratios across liquidity, profitability, leverage, and efficiency categories.
- **Interactive Visualizations**: Dynamic reporting using Plotly to visualize trends, comparative performance, and component compositions.
- **Standardized Benchmarking**: Comparison of organizational metrics against industry-standard benchmarks for technology, manufacturing, retail, and financial services sectors.
- **Data Quality Assessment**: Built-in verification protocols to ensure data completeness and accuracy before analysis.
- **Multi-Format Export**: Capability to export comprehensive reports in Excel, PDF, and CSV formats.

## Technical Architecture

The system is built with a modular architecture to ensure scalability and maintainability:

- **Frontend**: Streamlit-based interactive dashboard.
- **Data Processor**: Custom-built `FinancialDataProcessor` class utilizing Pandas and NumPy for rigorous data cleaning and ratio calculation.
- **AI Engine**: `Phi4Analyzer` and `OfflineAnalyzer` modules for dual-mode qualitative analysis.
- **Visualization Suite**: `FinancialVisualizer` for rendering complex financial charts.
- **Configuration Layer**: Centralized management of financial formulas, benchmarks, and system constants.

## Project Structure

The repository is organized into several key modules, each responsible for a specific domain of the application:

- **`main_app.py`**: The primary entry point for the Streamlit application. It manages the user interface, session state, and coordinates activities between the data processor, analyzer, and visualizer.
- **`data_processor.py`**: Contains the `FinancialDataProcessor` class. This module handles file ingestion, data cleaning, automated statement type detection, and the calculation of financial ratios.
- **`ai_analyzer.py`**: Defines the analytical backend, including the `Phi4Analyzer` for LLM-based insights and the `OfflineAnalyzer` for rule-based qualitative assessments.
- **`visualizations.py`**: Implements the `FinancialVisualizer` class, which generates complex Plotly-based charts and dashboards for financial reporting.
- **`config.py`**: A centralized configuration file containing financial ratio formulas, industry benchmarks, account mappings, and application-wide settings.
- **`error_handler.py`**: Provides standardized error management and logging across the application to ensure robust operation.
- **`requirements.txt`**: Enumerates the Python dependencies required to run the application.

## Technology Stack

- **Framework**: Streamlit
- **Data Analysis**: Pandas, NumPy, Scikit-learn, Statsmodels
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Integration**: Requests (OpenRouter API), Python-dotenv
- **File Handling**: Openpyxl, xlrd

## Installation

Ensure Python 3.8+ is installed on your system.

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd Financial-Statement-Analyzer
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables (optional for AI analysis):
   Create a `.env` file and add your OpenRouter API key:
   ```env
   OPENROUTER_API_KEY=your_api_key_here
   ```

## Usage

1. Launch the application:

   ```bash
   streamlit run main_app.py
   ```

2. Upload a financial statement in Excel (.xlsx, .xls) or CSV format.
3. Review the automatically detected statement type and data quality score.
4. Select the desired analysis depth (Standard, Comprehensive, or Strategic).
5. Explore the generated ratios, visualizations, and AI insights.
6. Export the finalized report for external review.

## Data Specifications

To ensure optimal analysis performance, input files should meet the following criteria:

- **Format**: `.csv`, `.xlsx`, or `.xls`.
- **Structure**: Clear column headers with financial account names and time periods.
- **Quality**: Minimum of 5 rows and 2 columns of data for meaningful ratio calculation.

## License

This project is licensed under the MIT License.
