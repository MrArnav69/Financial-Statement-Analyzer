import requests
import json
import os
from typing import Optional, Dict, Any
import time

class Phi4Analyzer:
    """
    Microsoft Phi-4 Financial Analyzer using OpenRouter API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "microsoft/phi-4-reasoning-plus:free"  # Free tier model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",  # Optional: for analytics
            "X-Title": "Financial Statement Analyzer"  # Optional: for analytics
        }
        
        # Verify API key is available
        if not self.api_key:
            print("⚠️ OpenRouter API key not found. Using offline analysis mode.")
            self.api_available = False
        else:
            self.api_available = True
            print("✅ OpenRouter API initialized successfully")
    
    def _make_request(self, prompt: str, max_tokens: int = 1500, temperature: float = 0.1) -> str:
        """
        Make a request to OpenRouter API
        """
        if not self.api_available:
            return self._fallback_analysis(prompt)
        
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": """You are an expert financial analyst with deep knowledge of financial statements, 
                        ratio analysis, and business strategy. Provide comprehensive, accurate, and actionable 
                        financial analysis with step-by-step reasoning. Focus on practical insights that can 
                        guide business decisions."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            
            elif response.status_code == 429:
                print("⚠️ Rate limit reached. Waiting before retry...")
                time.sleep(5)
                return self._fallback_analysis(prompt)
            
            elif response.status_code == 401:
                print("❌ Invalid API key. Please check your OpenRouter API key.")
                self.api_available = False
                return self._fallback_analysis(prompt)
            
            else:
                print(f"⚠️ API request failed with status {response.status_code}")
                return self._fallback_analysis(prompt)
                
        except requests.exceptions.Timeout:
            print("⚠️ API request timed out. Using offline analysis.")
            return self._fallback_analysis(prompt)
        
        except requests.exceptions.RequestException as e:
            print(f"⚠️ API request failed: {str(e)}")
            return self._fallback_analysis(prompt)
        
        except Exception as e:
            print(f"⚠️ Unexpected error: {str(e)}")
            return self._fallback_analysis(prompt)
    
    def _fallback_analysis(self, prompt: str) -> str:
        """
        Provide offline analysis when API is unavailable
        """
        return """
## 🔧 Offline Financial Analysis

**Analysis Mode**: Advanced Offline Intelligence

### 📊 Financial Health Assessment
- **Liquidity Analysis**: Evaluate current ratio, quick ratio, and cash position
- **Profitability Review**: Assess gross margin, operating margin, and net profit trends
- **Leverage Evaluation**: Analyze debt-to-equity ratio and interest coverage
- **Efficiency Metrics**: Review asset turnover and working capital management

### 🎯 Key Recommendations
1. **Monitor Cash Flow**: Ensure adequate liquidity for operations
2. **Optimize Margins**: Focus on cost management and pricing strategies
3. **Manage Debt Levels**: Maintain healthy debt-to-equity ratios
4. **Improve Efficiency**: Enhance asset utilization and operational processes

### 📈 Strategic Insights
- Compare performance against industry benchmarks
- Identify trends in key financial metrics
- Assess working capital requirements
- Evaluate investment opportunities and risks

*Note: For detailed AI-powered analysis with step-by-step reasoning, please provide a valid OpenRouter API key.*
        """
    
    def analyze_financial_data(self, data: str, statement_type: str) -> str:
        """
        Comprehensive financial analysis using Phi-4 reasoning
        """
        prompt = f"""
        Analyze this {statement_type} with comprehensive financial analysis:

        Data:
        {data[:3000]}  # Limit data size for API

        Please provide:
        1. **Executive Summary** - Key findings and overall financial health
        2. **Detailed Analysis** - Line-by-line examination of important items
        3. **Financial Ratios** - Calculate and interpret relevant ratios
        4. **Trend Analysis** - Identify patterns and changes over time
        5. **Risk Assessment** - Highlight potential financial risks
        6. **Strategic Recommendations** - Actionable business insights
        7. **Industry Context** - How this compares to typical industry performance

        Use step-by-step reasoning and provide specific, actionable insights.
        """
        
        return self._make_request(prompt, max_tokens=2000)
    
    def extract_key_metrics(self, data: str, statement_type: str) -> str:
        """
        Extract and analyze key financial metrics
        """
        prompt = f"""
        Extract and analyze the key financial metrics from this {statement_type}:

        Data:
        {data[:2500]}

        Focus on:
        1. **Primary Metrics** - Most important numbers for this statement type
        2. **Calculated Ratios** - Compute relevant financial ratios
        3. **Performance Indicators** - Key performance metrics
        4. **Benchmarking** - How these metrics compare to industry standards
        5. **Red Flags** - Any concerning metrics or trends
        6. **Strengths** - Positive financial indicators

        Provide specific numbers, calculations, and interpretations.
        """
        
        return self._make_request(prompt, max_tokens=1500)
    
    def identify_statement_type(self, data: str) -> str:
        """
        Identify the type of financial statement
        """
        prompt = f"""
        Analyze this financial data and identify the statement type:

        Data:
        {data[:2000]}

        Determine:
        1. **Statement Type** - Balance Sheet, Income Statement, Cash Flow, or Other
        2. **Confidence Level** - How certain are you of this classification
        3. **Key Indicators** - What specific elements led to this conclusion
        4. **Data Quality** - Assessment of completeness and structure
        5. **Recommendations** - Suggestions for optimal analysis approach

        Provide reasoning for your classification.
        """
        
        return self._make_request(prompt, max_tokens=1000)
    
    def comparative_analysis(self, data: str, statement_type: str) -> str:
        """
        Perform comparative analysis and benchmarking
        """
        prompt = f"""
        Perform comparative analysis for this {statement_type}:

        Data:
        {data[:2500]}

        Analyze:
        1. **Period-over-Period Comparison** - Changes between time periods
        2. **Industry Benchmarking** - How this compares to industry averages
        3. **Peer Analysis** - Comparison to similar companies
        4. **Best Practices** - Industry best practices and standards
        5. **Performance Gaps** - Areas needing improvement
        6. **Competitive Position** - Strengths and weaknesses vs competitors

        Provide specific comparisons and actionable insights.
        """
        
        return self._make_request(prompt, max_tokens=1800)
    
    def generate_insights(self, data: str, statement_type: str) -> str:
        """
        Generate strategic business insights
        """
        prompt = f"""
        Generate strategic business insights from this {statement_type}:

        Data:
        {data[:2500]}

        Provide:
        1. **Strategic Opportunities** - Growth and improvement opportunities
        2. **Risk Mitigation** - Strategies to address identified risks
        3. **Operational Efficiency** - Ways to improve operations
        4. **Financial Optimization** - Strategies to improve financial performance
        5. **Investment Priorities** - Where to focus resources
        6. **Long-term Outlook** - Future considerations and planning

        Focus on actionable, strategic recommendations for business leaders.
        """
        
        return self._make_request(prompt, max_tokens=1800)

class OfflineAnalyzer:
    """
    Offline financial analysis when AI is not available
    """
    
    def __init__(self):
        self.analysis_templates = {
            "Balance Sheet": self._balance_sheet_analysis,
            "Income Statement": self._income_statement_analysis,
            "Cash Flow Statement": self._cash_flow_analysis,
            "General Ledger": self._general_ledger_analysis
        }
    
    def analyze_financial_data(self, data: str, statement_type: str) -> str:
        """
        Provide offline financial analysis
        """
        if statement_type in self.analysis_templates:
            return self.analysis_templates[statement_type]()
        else:
            return self._generic_analysis()
    
    def extract_key_metrics(self, data: str, statement_type: str) -> str:
        """
        Extract key metrics offline
        """
        return f"""
## 🔢 Key Financial Metrics - {statement_type}

### 📊 Primary Metrics
- **Revenue Growth**: Monitor year-over-year revenue changes
- **Profit Margins**: Track gross, operating, and net margins
- **Return Ratios**: Calculate ROA, ROE, and ROI
- **Liquidity Ratios**: Assess current and quick ratios

### 📈 Performance Indicators
- **Efficiency Metrics**: Asset turnover and utilization rates
- **Leverage Ratios**: Debt-to-equity and coverage ratios
- **Growth Metrics**: Revenue and earnings growth rates
- **Quality Metrics**: Cash flow and earnings quality

### 🎯 Benchmarking
- Compare against industry averages
- Assess relative performance metrics
- Identify areas for improvement
- Track progress over time

*For detailed metric calculations and AI-powered insights, please configure OpenRouter API access.*
        """
    
    def identify_statement_type(self, data: str) -> str:
        """
        Basic statement type identification
        """
        return """
## 🔍 Statement Type Analysis

### 📋 Classification Method
Using keyword analysis and data structure patterns to identify statement type.

### 🎯 Identification Process
1. **Keyword Matching**: Search for characteristic account names
2. **Structure Analysis**: Examine data organization and format
3. **Pattern Recognition**: Identify typical statement patterns
4. **Confidence Assessment**: Evaluate classification certainty

### 💡 Recommendations
- Verify statement type manually if uncertain
- Ensure proper data formatting for accurate analysis
- Use specific statement type for optimal ratio calculations

*For advanced AI-powered statement identification, please configure OpenRouter API access.*
        """
    
    def comparative_analysis(self, data: str, statement_type: str) -> str:
        """
        Basic comparative analysis
        """
        return """
## 📊 Comparative Analysis Framework

### 🔄 Analysis Dimensions
1. **Time Series Analysis**: Period-over-period comparisons
2. **Industry Benchmarking**: Sector-specific comparisons
3. **Peer Analysis**: Similar company comparisons
4. **Best Practice Assessment**: Industry standard evaluation

### 📈 Key Comparison Areas
- **Financial Performance**: Revenue, profitability, efficiency
- **Financial Position**: Liquidity, leverage, asset quality
- **Growth Metrics**: Revenue growth, market expansion
- **Risk Indicators**: Financial stability and risk factors

### 🎯 Benchmarking Framework
- Industry average comparisons
- Percentile rankings
- Best-in-class analysis
- Improvement opportunities

*For detailed AI-powered comparative analysis, please configure OpenRouter API access.*
        """
    
    def generate_insights(self, data: str, statement_type: str) -> str:
        """
        Generate basic strategic insights
        """
        return """
## 🎯 Strategic Business Insights

### 🚀 Growth Opportunities
- **Revenue Enhancement**: Identify new revenue streams
- **Market Expansion**: Explore new markets and segments
- **Operational Efficiency**: Streamline processes and reduce costs
- **Technology Investment**: Leverage technology for competitive advantage

### ⚖️ Risk Management
- **Financial Risk**: Monitor liquidity and leverage levels
- **Operational Risk**: Assess operational dependencies and vulnerabilities
- **Market Risk**: Evaluate market position and competitive threats
- **Strategic Risk**: Consider long-term strategic challenges

### 💡 Optimization Strategies
- **Cost Management**: Identify cost reduction opportunities
- **Asset Utilization**: Improve asset efficiency and productivity
- **Working Capital**: Optimize cash conversion cycle
- **Capital Structure**: Balance debt and equity financing

*For detailed AI-powered strategic insights, please configure OpenRouter API access.*
        """
    
    def _balance_sheet_analysis(self) -> str:
        return """
## 🏦 Balance Sheet Analysis

### 📊 Financial Position Assessment
**Asset Analysis:**
- Current assets vs. non-current assets composition
- Asset quality and liquidity evaluation
- Investment in productive assets

**Liability Structure:**
- Current vs. long-term liability breakdown
- Debt maturity profile analysis
- Interest-bearing debt evaluation

**Equity Position:**
- Shareholders' equity composition
- Retained earnings trends
- Capital structure optimization

### 🎯 Key Focus Areas
1. **Liquidity Management**: Ensure adequate working capital
2. **Leverage Control**: Maintain optimal debt levels
3. **Asset Efficiency**: Maximize return on assets
4. **Capital Allocation**: Strategic investment decisions

*Configure OpenRouter API for detailed AI analysis with step-by-step reasoning.*
        """
    
    def _income_statement_analysis(self) -> str:
        return """
## 📈 Income Statement Analysis

### 💰 Profitability Assessment
**Revenue Analysis:**
- Revenue growth trends and sustainability
- Revenue mix and diversification
- Market share and competitive position

**Cost Structure:**
- Cost of goods sold efficiency
- Operating expense management
- Fixed vs. variable cost analysis

**Profitability Metrics:**
- Gross margin trends and benchmarking
- Operating leverage analysis
- Net profit margin optimization

### 🎯 Performance Optimization
1. **Revenue Growth**: Expand market reach and product offerings
2. **Cost Management**: Optimize operational efficiency
3. **Margin Improvement**: Enhance pricing and cost strategies
4. **Scalability**: Build sustainable growth platforms

*Configure OpenRouter API for comprehensive AI-powered profitability analysis.*
        """
    
    def _cash_flow_analysis(self) -> str:
        return """
## 💸 Cash Flow Statement Analysis

### 🔄 Cash Flow Assessment
**Operating Activities:**
- Cash generation from core operations
- Working capital management efficiency
- Operating cash flow sustainability

**Investing Activities:**
- Capital expenditure patterns
- Investment strategy evaluation
- Asset acquisition and disposal analysis

**Financing Activities:**
- Debt and equity financing decisions
- Dividend policy assessment
- Capital structure management

### 🎯 Cash Management Strategy
1. **Operating Efficiency**: Optimize cash conversion cycle
2. **Investment Planning**: Strategic capital allocation
3. **Financing Optimization**: Balance debt and equity
4. **Liquidity Management**: Maintain adequate cash reserves

*Configure OpenRouter API for detailed AI-powered cash flow analysis.*
        """
    
    def _general_ledger_analysis(self) -> str:
        return """
## 📚 General Ledger Analysis

### 🔍 Account-Level Assessment
**Transaction Analysis:**
- Account activity patterns and trends
- Transaction volume and frequency
- Unusual or irregular transactions

**Balance Verification:**
- Account balance reconciliation
- Period-end adjustments analysis
- Account classification accuracy

**Control Assessment:**
- Internal control effectiveness
- Segregation of duties evaluation
- Authorization and approval processes

### 🎯 Audit and Compliance Focus
1. **Data Integrity**: Ensure transaction accuracy
2. **Control Environment**: Strengthen internal controls
3. **Compliance Monitoring**: Maintain regulatory compliance
4. **Risk Management**: Identify and mitigate risks

*Configure OpenRouter API for advanced AI-powered ledger analysis.*
        """
    
    def _generic_analysis(self) -> str:
        return """
## 📊 Financial Data Analysis

### 🔍 General Assessment Framework
**Data Quality Review:**
- Completeness and accuracy assessment
- Consistency and reliability evaluation
- Format and structure analysis

**Financial Health Indicators:**
- Key performance metrics identification
- Trend analysis and pattern recognition
- Risk factor assessment

**Improvement Opportunities:**
- Performance enhancement areas
- Operational efficiency gains
- Strategic optimization potential

### 🎯 Next Steps
1. **Data Validation**: Verify data accuracy and completeness
2. **Detailed Analysis**: Conduct specific ratio calculations
3. **Benchmarking**: Compare against industry standards
4. **Action Planning**: Develop improvement strategies

*Configure OpenRouter API for comprehensive AI-powered analysis.*
        """

def get_analyzer(api_key: Optional[str] = None, analyzer_type: str = "phi4") -> Any:
    """
    Factory function to get the appropriate analyzer
    """
    if analyzer_type == "phi4" and api_key:
        return Phi4Analyzer(api_key)
    else:
        return OfflineAnalyzer()

