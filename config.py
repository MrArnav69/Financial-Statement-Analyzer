"""
Configuration settings for the Financial Statement Analyzer
"""

# Statement types and their characteristics
STATEMENT_TYPES = {
    "Balance Sheet": {
        "description": "Statement of financial position showing assets, liabilities, and equity",
        "key_accounts": ["assets", "liabilities", "equity", "cash", "debt"],
        "ratios": ["current_ratio", "debt_to_equity", "roa", "roe"],
        "visualizations": ["balance_composition", "asset_breakdown", "leverage_analysis"]
    },
    "Income Statement": {
        "description": "Statement showing revenues, expenses, and profitability",
        "key_accounts": ["revenue", "expenses", "income", "profit", "sales"],
        "ratios": ["gross_margin", "operating_margin", "net_margin", "revenue_growth"],
        "visualizations": ["revenue_trends", "margin_analysis", "expense_breakdown"]
    },
    "Cash Flow Statement": {
        "description": "Statement showing cash inflows and outflows by activity",
        "key_accounts": ["operating", "investing", "financing", "cash_flow"],
        "ratios": ["operating_cash_ratio", "free_cash_flow", "cash_conversion"],
        "visualizations": ["cash_flow_trends", "activity_breakdown", "cash_generation"]
    },
    "General Ledger": {
        "description": "Detailed record of all financial transactions",
        "key_accounts": ["account", "debit", "credit", "balance", "transaction"],
        "ratios": ["account_turnover", "balance_trends", "transaction_volume"],
        "visualizations": ["account_analysis", "transaction_trends", "balance_movements"]
    }
}

# Financial ratio definitions
FINANCIAL_RATIOS = {
    "liquidity": {
        "current_ratio": {
            "formula": "Current Assets / Current Liabilities",
            "description": "Measures ability to pay short-term obligations",
            "benchmark": "1.5 - 3.0"
        },
        "quick_ratio": {
            "formula": "(Current Assets - Inventory) / Current Liabilities",
            "description": "Measures immediate liquidity without inventory",
            "benchmark": "1.0 - 1.5"
        },
        "cash_ratio": {
            "formula": "Cash / Current Liabilities",
            "description": "Most conservative liquidity measure",
            "benchmark": "0.1 - 0.2"
        }
    },
    "profitability": {
        "gross_margin": {
            "formula": "(Revenue - COGS) / Revenue * 100",
            "description": "Percentage of revenue after direct costs",
            "benchmark": "20% - 80%"
        },
        "operating_margin": {
            "formula": "Operating Income / Revenue * 100",
            "description": "Percentage of revenue after operating expenses",
            "benchmark": "5% - 25%"
        },
        "net_margin": {
            "formula": "Net Income / Revenue * 100",
            "description": "Percentage of revenue after all expenses",
            "benchmark": "3% - 20%"
        },
        "roa": {
            "formula": "Net Income / Total Assets * 100",
            "description": "Return on assets - efficiency of asset use",
            "benchmark": "5% - 15%"
        },
        "roe": {
            "formula": "Net Income / Shareholders Equity * 100",
            "description": "Return on equity - return to shareholders",
            "benchmark": "10% - 25%"
        }
    },
    "leverage": {
        "debt_to_equity": {
            "formula": "Total Debt / Total Equity",
            "description": "Financial leverage and capital structure",
            "benchmark": "0.3 - 0.6"
        },
        "debt_to_assets": {
            "formula": "Total Debt / Total Assets",
            "description": "Proportion of assets financed by debt",
            "benchmark": "0.2 - 0.4"
        },
        "interest_coverage": {
            "formula": "EBIT / Interest Expense",
            "description": "Ability to pay interest on debt",
            "benchmark": "2.5+"
        }
    },
    "efficiency": {
        "asset_turnover": {
            "formula": "Revenue / Total Assets",
            "description": "Efficiency of asset utilization",
            "benchmark": "0.5 - 2.0"
        },
        "inventory_turnover": {
            "formula": "COGS / Average Inventory",
            "description": "How quickly inventory is sold",
            "benchmark": "4 - 12"
        },
        "receivables_turnover": {
            "formula": "Revenue / Average Accounts Receivable",
            "description": "How quickly receivables are collected",
            "benchmark": "6 - 12"
        }
    }
}

# Chart color schemes
COLOR_SCHEMES = {
    "default": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
    "professional": ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#592E83", "#1B998B"],
    "financial": ["#0066CC", "#FF6B35", "#004225", "#8B0000", "#4B0082", "#008B8B"],
    "corporate": ["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087", "#f95d6a"]
}

# Industry benchmarks
INDUSTRY_BENCHMARKS = {
    "technology": {
        "gross_margin": {"min": 60, "max": 85, "average": 72},
        "operating_margin": {"min": 15, "max": 35, "average": 25},
        "current_ratio": {"min": 2.0, "max": 4.0, "average": 3.0},
        "debt_to_equity": {"min": 0.1, "max": 0.4, "average": 0.25}
    },
    "manufacturing": {
        "gross_margin": {"min": 20, "max": 40, "average": 30},
        "operating_margin": {"min": 5, "max": 15, "average": 10},
        "current_ratio": {"min": 1.2, "max": 2.5, "average": 1.8},
        "debt_to_equity": {"min": 0.3, "max": 0.7, "average": 0.5}
    },
    "retail": {
        "gross_margin": {"min": 25, "max": 50, "average": 37},
        "operating_margin": {"min": 3, "max": 12, "average": 7},
        "current_ratio": {"min": 1.0, "max": 2.0, "average": 1.5},
        "debt_to_equity": {"min": 0.4, "max": 0.8, "average": 0.6}
    },
    "financial_services": {
        "net_margin": {"min": 15, "max": 30, "average": 22},
        "roe": {"min": 10, "max": 20, "average": 15},
        "debt_to_equity": {"min": 3.0, "max": 8.0, "average": 5.5}
    }
}

# Data quality thresholds
DATA_QUALITY = {
    "completeness_threshold": 80,  # Minimum percentage of non-null values
    "numeric_threshold": 0.3,      # Minimum ratio of numeric columns
    "row_threshold": 5,            # Minimum number of rows
    "column_threshold": 2          # Minimum number of columns
}

# Export settings
EXPORT_SETTINGS = {
    "excel": {
        "max_rows": 1000000,
        "include_charts": True,
        "include_formatting": True
    },
    "csv": {
        "encoding": "utf-8",
        "separator": ",",
        "decimal": "."
    },
    "pdf": {
        "page_size": "A4",
        "orientation": "portrait",
        "include_charts": True
    }
}

# AI Analysis settings
AI_SETTINGS = {
    "phi4": {
        "max_tokens": 2000,
        "temperature": 0.1,
        "timeout": 30,
        "retry_attempts": 3
    },
    "offline": {
        "analysis_depth": "comprehensive",
        "include_benchmarks": True,
        "generate_insights": True
    }
}

# Visualization settings
VISUALIZATION_SETTINGS = {
    "chart_height": 400,
    "chart_width": 800,
    "font_size": 12,
    "title_font_size": 16,
    "show_grid": True,
    "show_legend": True,
    "interactive": True
}

# Account mapping for auto-detection
ACCOUNT_MAPPINGS = {
    "balance_sheet": {
        "assets": [
            "cash", "cash and cash equivalents", "accounts receivable", "inventory", 
            "current assets", "property plant equipment", "ppe", "total assets",
            "investments", "goodwill", "intangible assets", "fixed assets"
        ],
        "liabilities": [
            "accounts payable", "current liabilities", "short term debt", "long term debt",
            "total liabilities", "accrued expenses", "deferred revenue", "notes payable"
        ],
        "equity": [
            "shareholders equity", "stockholders equity", "retained earnings", "common stock",
            "total equity", "paid in capital", "treasury stock", "accumulated other comprehensive"
        ]
    },
    "income_statement": {
        "revenue": [
            "revenue", "sales", "net sales", "total revenue", "gross sales",
            "service revenue", "product revenue", "operating revenue"
        ],
        "expenses": [
            "cost of goods sold", "cogs", "operating expenses", "selling expenses",
            "administrative expenses", "depreciation", "amortization", "interest expense"
        ],
        "income": [
            "gross profit", "operating income", "net income", "earnings", "profit",
            "income before tax", "ebit", "ebitda"
        ]
    },
    "cash_flow": {
        "operating": [
            "operating activities", "cash from operations", "operating cash flow",
            "net income", "depreciation", "working capital changes"
        ],
        "investing": [
            "investing activities", "capital expenditures", "capex", "investments",
            "acquisitions", "asset sales", "investing cash flow"
        ],
        "financing": [
            "financing activities", "debt proceeds", "debt payments", "dividends",
            "stock issuance", "stock repurchase", "financing cash flow"
        ]
    }
}

# Error messages
ERROR_MESSAGES = {
    "file_upload": "Unable to process the uploaded file. Please check the file format and try again.",
    "data_processing": "Error processing financial data. Please verify the data structure.",
    "ratio_calculation": "Unable to calculate financial ratios. Required data may be missing.",
    "visualization": "Error creating visualizations. Please check your data format.",
    "ai_analysis": "AI analysis temporarily unavailable. Using offline analysis mode.",
    "export": "Error generating export file. Please try again or contact support."
}

# Success messages
SUCCESS_MESSAGES = {
    "file_upload": "File uploaded and processed successfully!",
    "analysis_complete": "Financial analysis completed successfully!",
    "ratios_calculated": "Financial ratios calculated successfully!",
    "export_ready": "Export file generated successfully!",
    "ai_active": "AI analysis engine activated successfully!"
}

# Help text
HELP_TEXT = {
    "file_upload": """
    Upload your financial statement file in Excel (.xlsx, .xls) or CSV (.csv) format.
    Ensure your data has clear column headers and is properly formatted.
    """,
    "statement_type": """
    Select the type of financial statement you're analyzing, or use auto-detection
    to let the AI identify the statement type automatically.
    """,
    "analysis_depth": """
    Choose the depth of analysis:
    - Standard: Basic ratios and visualizations
    - Comprehensive: Detailed analysis with benchmarking
    - Strategic: Full analysis with strategic insights and recommendations
    """,
    "financial_ratios": """
    Financial ratios are automatically calculated based on your statement type.
    Use the custom ratio calculator to create additional metrics specific to your needs.
    """,
    "visualizations": """
    Interactive charts are generated automatically based on your data.
    Use the custom chart builder to create specific visualizations for your analysis.
    """,
    "export": """
    Export your analysis in multiple formats:
    - Excel: Complete workbook with data and calculations
    - PDF: Professional report for presentations
    - CSV: Raw data for further analysis
    - HTML: Interactive dashboard for sharing
    """
}

# API Configuration (for future extensions)
API_CONFIG = {
    "phi4": {
        "base_url": "https://api.openai.com/v1",
        "model": "phi-4",
        "headers": {
            "Content-Type": "application/json"
        }
    },
    "backup_models": [
        "gpt-4",
        "gpt-3.5-turbo",
        "claude-3"
    ]
}

# Feature flags
FEATURE_FLAGS = {
    "enable_ai_analysis": True,
    "enable_auto_detection": True,
    "enable_benchmarking": True,
    "enable_export": True,
    "enable_custom_ratios": True,
    "enable_interactive_charts": True,
    "enable_dashboard": True,
    "enable_risk_analysis": True
}

# Version information
VERSION_INFO = {
    "app_version": "2.0.0",
    "ai_engine": "Microsoft Phi-4",
    "last_updated": "2024-12-19",
    "features": [
        "AI-Powered Analysis",
        "Automatic Statement Detection",
        "20+ Financial Ratios",
        "Interactive Visualizations",
        "Comprehensive Reporting",
        "Multi-format Export"
    ]
}
