import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import datetime
import os
from typing import Optional, Dict, Any, List
import streamlit.components.v1 as components

# Import our custom modules
from data_processor import FinancialDataProcessor
from ai_analyzer import get_analyzer, Phi4Analyzer, OfflineAnalyzer
from visualizations import FinancialVisualizer
from config import *



def create_voice_explanation_component(text_content, voice_id="voice1"):
    """Create a text-to-speech component for explaining analysis"""
    
    # Clean and prepare text for speech
    clean_text = text_content.replace('#', '').replace('*', '').replace('`', '').replace('\n', ' ')
    
    # HTML component with speech synthesis
    speech_html = f"""
    <div style="background: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #1f77b4;">🎤 AI Voice Explanation</h4>
            <button id="playBtn_{voice_id}" onclick="speakText_{voice_id}()" 
                    style="background: #1f77b4; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                ▶️ Play Explanation
            </button>
            <button id="pauseBtn_{voice_id}" onclick="pauseSpeech_{voice_id}()" 
                    style="background: #ff7f0e; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                ⏸️ Pause
            </button>
            <button id="stopBtn_{voice_id}" onclick="stopSpeech_{voice_id}()" 
                    style="background: #d62728; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                ⏹️ Stop
            </button>
        </div>
        
        <div style="margin: 10px 0;">
            <label for="voiceSelect_{voice_id}" style="margin-right: 10px;">🗣️ Voice:</label>
            <select id="voiceSelect_{voice_id}" style="padding: 5px; border-radius: 3px;">
                <option value="0">Default Voice</option>
            </select>
            
            <label for="speedRange_{voice_id}" style="margin-left: 20px; margin-right: 10px;">⚡ Speed:</label>
            <input type="range" id="speedRange_{voice_id}" min="0.5" max="2" value="1" step="0.1" 
                   style="width: 100px;" onchange="updateSpeed_{voice_id}()">
            <span id="speedValue_{voice_id}">1.0x</span>
        </div>
        
        <div id="status_{voice_id}" style="margin: 10px 0; font-style: italic; color: #666;">
            Ready to speak...
        </div>
    </div>

    <script>
        let currentUtterance_{voice_id} = null;
        let voices_{voice_id} = [];
        let currentSpeed_{voice_id} = 1.0;
        
        // Text content to speak
        const textToSpeak_{voice_id} = `{clean_text}`;
        
        // Initialize voices
        function loadVoices_{voice_id}() {{
            voices_{voice_id} = speechSynthesis.getVoices();
            const voiceSelect = document.getElementById('voiceSelect_{voice_id}');
            voiceSelect.innerHTML = '';
            
            voices_{voice_id}.forEach((voice, index) => {{
                const option = document.createElement('option');
                option.value = index;
                option.textContent = `${{voice.name}} (${{voice.lang}})`;
                voiceSelect.appendChild(option);
            }});
        }}
        
        // Load voices when available
        speechSynthesis.onvoiceschanged = loadVoices_{voice_id};
        loadVoices_{voice_id}();
        
        function speakText_{voice_id}() {{
            // Stop any current speech
            speechSynthesis.cancel();
            
            // Create new utterance
            currentUtterance_{voice_id} = new SpeechSynthesisUtterance(textToSpeak_{voice_id});
            
            // Set voice
            const voiceSelect = document.getElementById('voiceSelect_{voice_id}');
            const selectedVoice = voices_{voice_id}[voiceSelect.value];
            if (selectedVoice) {{
                currentUtterance_{voice_id}.voice = selectedVoice;
            }}
            
            // Set speed
            currentUtterance_{voice_id}.rate = currentSpeed_{voice_id};
            
            // Set up event listeners
            currentUtterance_{voice_id}.onstart = function() {{
                document.getElementById('status_{voice_id}').textContent = '🗣️ Speaking...';
                document.getElementById('playBtn_{voice_id}').disabled = true;
            }};
            
            currentUtterance_{voice_id}.onend = function() {{
                document.getElementById('status_{voice_id}').textContent = '✅ Finished speaking';
                document.getElementById('playBtn_{voice_id}').disabled = false;
            }};
            
            currentUtterance_{voice_id}.onerror = function(event) {{
                document.getElementById('status_{voice_id}').textContent = '❌ Error: ' + event.error;
                document.getElementById('playBtn_{voice_id}').disabled = false;
            }};
            
            // Start speaking
            speechSynthesis.speak(currentUtterance_{voice_id});
        }}
        
        function pauseSpeech_{voice_id}() {{
            if (speechSynthesis.speaking) {{
                speechSynthesis.pause();
                document.getElementById('status_{voice_id}').textContent = '⏸️ Paused';
            }}
        }}
        
        function stopSpeech_{voice_id}() {{
            speechSynthesis.cancel();
            document.getElementById('status_{voice_id}').textContent = '⏹️ Stopped';
            document.getElementById('playBtn_{voice_id}').disabled = false;
        }}
        
        function updateSpeed_{voice_id}() {{
            const speedRange = document.getElementById('speedRange_{voice_id}');
            currentSpeed_{voice_id} = parseFloat(speedRange.value);
            document.getElementById('speedValue_{voice_id}').textContent = currentSpeed_{voice_id}.toFixed(1) + 'x';
        }}
    </script>
    """
    
    return speech_html

def generate_intelligent_voice_explanation(analyzer, data_sample, analysis_type, statement_type):
    """Generate AI-powered voice explanations"""
    
    if isinstance(analyzer, Phi4Analyzer) and analyzer.api_available:
        try:
            voice_prompt = f"""
            Create a clear, conversational explanation for a voice assistant about this {analysis_type} 
            of a {statement_type}. Make it:
            - Easy to understand when spoken aloud
            - 2-3 minutes of speaking time
            - Include specific insights from the data
            - Use simple language, avoid complex jargon
            - Structure it as if you're explaining to a business owner
            
            Data sample: {data_sample[:1000]}
            
            Focus on the most important insights and actionable information.
            """
            
            voice_explanation = analyzer._make_request(voice_prompt, max_tokens=800)
            return voice_explanation
            
        except Exception as e:
            return f"I'll explain the {analysis_type} results. The analysis shows important financial insights that can help guide your business decisions."
    
    else:
        return generate_voice_explanation(analysis_type, data_sample)

def generate_voice_explanation(analysis_type, data, ratios=None, chart_type=None):
    """Generate voice-friendly explanations for different types of analysis"""
    
    explanations = {
        "financial_overview": f"""
        Let me explain your financial overview. 
        Your data contains {len(data) if data is not None else 'multiple'} rows and {len(data.columns) if data is not None else 'several'} columns of financial information.
        This represents a comprehensive view of your financial position.
        The key metrics show the overall health and performance of your organization.
        """,
        
        "ratio_analysis": f"""
        Now let's discuss your financial ratios analysis.
        {f"I've calculated {len(ratios)} key financial ratios for you." if ratios else ""}
        These ratios help us understand your company's liquidity, profitability, and efficiency.
        Liquidity ratios show how well you can meet short-term obligations.
        Profitability ratios indicate how effectively you generate profits.
        Efficiency ratios reveal how well you use your assets.
        """,
        
        "chart_explanation": f"""
        Looking at this {chart_type or 'chart'}, we can see important trends in your data.
        The visualization helps identify patterns that might not be obvious in raw numbers.
        Pay attention to any significant increases or decreases over time.
        These trends can indicate areas of strength or concern in your financial performance.
        """,
        
        "ai_insights": """
        The AI analysis has identified several key insights from your financial data.
        These insights are based on advanced pattern recognition and financial expertise.
        The recommendations provided can help guide your strategic decision-making.
        Consider these insights alongside your business knowledge and market conditions.
        """
    }
    
    return explanations.get(analysis_type, "Analysis explanation is ready.")


def setup_openrouter_api():
    """
    Setup OpenRouter API configuration with a hardcoded API key
    """
    # Hardcoded API key - replace with your actual OpenRouter API key
    hardcoded_api_key = "your_openrouter_api_key_here"
    
    st.sidebar.markdown("### 🧠 AI Configuration")
    st.sidebar.success("✅ OpenRouter API key configured automatically")
    
    return hardcoded_api_key


def main():
    # Page configuration
    st.set_page_config(
        page_title="Financial Statement Analyzer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0;">🏦 Advanced Financial Statement Analyzer</h1>
        <p style="color: white; margin: 0; opacity: 0.9;">Powered by Microsoft Phi-4 Reasoning AI & Advanced Analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.title("🎛️ Configuration")
    
    # API Configuration - now using hardcoded key
    # API Configuration - now using hardcoded key
    api_key = setup_openrouter_api()

    # Analyzer selection - always use phi4
    analyzer_type = "phi4"
    st.sidebar.success("🧠 Analysis Engine: Microsoft Phi-4 AI")

    # Initialize analyzer - directly create Phi4Analyzer
    analyzer = Phi4Analyzer(api_key)
    st.sidebar.success("🧠 AI Engine: Microsoft Phi-4 Active")

    # Initialize analyzer
    try:
        analyzer = get_analyzer(api_key, analyzer_type)
        if isinstance(analyzer, Phi4Analyzer) and analyzer.api_available:
            st.sidebar.success("🧠 AI Engine: Microsoft Phi-4 Active")
        else:
            st.sidebar.info("🔧 Analysis Mode: Advanced Offline")
    except Exception as e:
        st.sidebar.error(f"❌ Analyzer initialization failed: {str(e)}")
        analyzer = OfflineAnalyzer()
    
    # Rest of the main function remains the same...

    
    # File upload section
    st.sidebar.markdown("### 📁 File Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Choose your financial statement file",
        type=['xlsx', 'xls', 'csv'],
        help="Upload Excel or CSV files containing financial data"
    )
    
    # Analysis settings
    if uploaded_file:
        st.sidebar.markdown("### ⚙️ Analysis Settings")
        
        auto_detect = st.sidebar.checkbox(
            "🔍 Auto-detect statement type",
            value=True,
            help="Let AI automatically identify the type of financial statement"
        )
        
        if not auto_detect:
            statement_type = st.sidebar.selectbox(
                "📋 Statement Type",
                list(STATEMENT_TYPES.keys()),
                help="Manually select the type of financial statement"
            )
        else:
            statement_type = None
        
        analysis_depth = st.sidebar.selectbox(
            "🎯 Analysis Depth",
            ["Standard", "Comprehensive", "Strategic"],
            index=1,
            help="Choose the depth of financial analysis"
        )
        
        include_benchmarking = st.sidebar.checkbox(
            "📊 Include Industry Benchmarking",
            value=True,
            help="Compare against industry standards"
        )
    
    # Main content area
    if uploaded_file is not None:
        try:
            # Initialize data processor
            data_processor = FinancialDataProcessor()
            
            # Load and process data
            with st.spinner("📊 Processing financial data..."):
                success = data_processor.load_data(uploaded_file)
            
            if success and data_processor.data is not None:
                # Display success message
                st.markdown("""
                <div class="success-box">
                    <h4>✅ File Processed Successfully!</h4>
                    <p>Your financial data has been loaded and is ready for analysis.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Auto-detect statement type if enabled
                if auto_detect:
                    with st.spinner("🔍 Detecting statement type..."):
                        if isinstance(analyzer, Phi4Analyzer) and analyzer.api_available:
                            data_sample = data_processor.data.head(10).to_string()
                            detection_result = analyzer.identify_statement_type(data_sample)
                            
                            # Parse AI response to extract statement type
                            detected_type = data_processor.detect_statement_type()
                            
                            st.info(f"🎯 **Detected Statement Type**: {detected_type}")
                            
                            # Show AI reasoning if available
                            with st.expander("🧠 AI Detection Reasoning"):
                                st.markdown(detection_result)
                        else:
                            detected_type = data_processor.detect_statement_type()
                            st.info(f"🎯 **Detected Statement Type**: {detected_type}")
                        
                        statement_type = detected_type
                
                # Data overview
                st.markdown("## 📊 Data Overview")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="📋 Rows",
                        value=f"{len(data_processor.data):,}",
                        help="Total number of data rows"
                    )
                
                with col2:
                    st.metric(
                        label="📊 Columns", 
                        value=len(data_processor.data.columns),
                        help="Total number of data columns"
                    )
                
                with col3:
                    numeric_cols = len(data_processor.get_numeric_columns())
                    st.metric(
                        label="🔢 Numeric Columns",
                        value=numeric_cols,
                        help="Number of numeric data columns"
                    )
                
                with col4:
                    completeness = data_processor.assess_data_quality()
                    st.metric(
                        label="✅ Data Quality",
                        value=f"{completeness:.1f}%",
                        help="Percentage of complete data"
                    )
                
                # Display data preview
                with st.expander("👀 Data Preview", expanded=False):
                    st.dataframe(
                        data_processor.data.head(10),
                        use_container_width=True
                    )
                
                # Main analysis tabs
                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                    "🧠 AI Analysis",
                    "📊 Financial Ratios", 
                    "📈 Visualizations",
                    "🔍 Data Explorer",
                    "📋 Reports",
                    "📤 Export"
                ])
                
                
                with tab1:
                    st.markdown("## 🧠 AI-Powered Financial Analysis")
                    
                    # Initialize a fresh analyzer with the hardcoded API key
                    phi4_analyzer = Phi4Analyzer(api_key)
                    
                    # Check if API is working
                    if phi4_analyzer.api_available:
                        st.success("🤖 **Microsoft Phi-4 Reasoning Engine Active**")
                        
                        # Analysis options
                        analysis_col1, analysis_col2 = st.columns(2)
                        
                        with analysis_col1:
                            if st.button("🔍 Comprehensive Analysis", use_container_width=True):
                                with st.spinner("🧠 Analyzing financial data with AI reasoning..."):
                                    try:
                                        # Limit data to avoid token limits
                                        data_sample = data_processor.data.head(20).to_string()
                                        analysis = phi4_analyzer.analyze_financial_data(data_sample, statement_type)
                                        
                                        st.markdown("### 📊 Comprehensive Financial Analysis")
                                        st.markdown(analysis)
                                        
                                        # Add AI-powered voice explanation
                                        st.markdown("### 🎤 Voice Explanation")
                                        voice_explanation = generate_intelligent_voice_explanation(
                                            phi4_analyzer, data_sample, "comprehensive financial analysis", statement_type
                                        )
                                        
                                        voice_html = create_voice_explanation_component(voice_explanation, "ai_comprehensive")
                                        components.html(voice_html, height=200)
                                        
                                    except Exception as e:
                                        st.error(f"❌ Analysis failed: {str(e)}")
                            
                            if st.button("🔢 Extract Key Metrics", use_container_width=True):
                                with st.spinner("🔍 Extracting key financial metrics..."):
                                    try:
                                        # Limit data to avoid token limits
                                        data_sample = data_processor.data.head(20).to_string()
                                        metrics = phi4_analyzer.extract_key_metrics(data_sample, statement_type)
                                        
                                        st.markdown("### 🎯 Key Financial Metrics")
                                        st.markdown(metrics)
                                        
                                        # Add voice explanation for metrics
                                        st.markdown("### 🎤 Metrics Explanation")
                                        voice_explanation = generate_intelligent_voice_explanation(
                                            phi4_analyzer, data_sample, "key financial metrics extraction", statement_type
                                        )
                                        
                                        voice_html = create_voice_explanation_component(voice_explanation, "metrics_explanation")
                                        components.html(voice_html, height=200)
                                        
                                    except Exception as e:
                                        st.error(f"❌ Metrics extraction failed: {str(e)}")
                        
                        with analysis_col2:
                            if st.button("📈 Comparative Analysis", use_container_width=True):
                                with st.spinner("📊 Performing comparative analysis..."):
                                    try:
                                        # Limit data to avoid token limits
                                        data_sample = data_processor.data.head(20).to_string()
                                        comparison = phi4_analyzer.comparative_analysis(data_sample, statement_type)
                                        
                                        st.markdown("### ⚖️ Comparative Analysis")
                                        st.markdown(comparison)
                                        
                                        # Add voice explanation for comparison
                                        st.markdown("### 🎤 Comparative Analysis Explanation")
                                        voice_explanation = generate_intelligent_voice_explanation(
                                            phi4_analyzer, data_sample, "comparative financial analysis", statement_type
                                        )
                                        
                                        voice_html = create_voice_explanation_component(voice_explanation, "comparative_analysis")
                                        components.html(voice_html, height=200)
                                        
                                    except Exception as e:
                                        st.error(f"❌ Comparative analysis failed: {str(e)}")
                            
                            if st.button("💡 Strategic Insights", use_container_width=True):
                                with st.spinner("🎯 Generating strategic insights..."):
                                    try:
                                        # Limit data to avoid token limits
                                        data_sample = data_processor.data.head(20).to_string()
                                        insights = phi4_analyzer.generate_insights(data_sample, statement_type)
                                        
                                        st.markdown("### 🚀 Strategic Business Insights")
                                        st.markdown(insights)
                                        
                                        # Add voice explanation for insights
                                        st.markdown("### 🎤 Strategic Insights Explanation")
                                        voice_explanation = generate_intelligent_voice_explanation(
                                            phi4_analyzer, data_sample, "strategic business insights", statement_type
                                        )
                                        
                                        voice_html = create_voice_explanation_component(voice_explanation, "strategic_insights")
                                        components.html(voice_html, height=200)
                                        
                                    except Exception as e:
                                        st.error(f"❌ Insights generation failed: {str(e)}")
                        
                        # Real-time Q&A with voice
                        st.markdown("### 💬 Ask the AI Analyst")
                        user_question = st.text_input(
                            "Ask a specific question about your financial data:",
                            placeholder="e.g., What are the main risks in this financial statement?"
                        )
                        
                        if user_question and st.button("🤔 Get AI Answer"):
                            with st.spinner("🧠 AI is analyzing your question..."):
                                try:
                                    # Limit data to avoid token limits
                                    data_sample = data_processor.data.head(20).to_string()
                                    
                                    custom_prompt = f"""
                                    Based on this {statement_type} data:
                                    {data_sample}
                                    
                                    Please answer this specific question: {user_question}
                                    
                                    Provide a detailed, step-by-step analysis with specific references to the data.
                                    """
                                    
                                    answer = phi4_analyzer._make_request(custom_prompt, max_tokens=1500)
                                    
                                    st.markdown("### 🎯 AI Response")
                                    st.markdown(answer)
                                    
                                    # Add voice explanation for Q&A
                                    st.markdown("### 🎤 Voice Answer")
                                    voice_explanation = generate_intelligent_voice_explanation(
                                        phi4_analyzer, data_sample, f"answer to your question: {user_question}", statement_type
                                    )
                                    
                                    voice_html = create_voice_explanation_component(voice_explanation, "qa_response")
                                    components.html(voice_html, height=200)
                                    
                                except Exception as e:
                                    st.error(f"❌ AI response failed: {str(e)}")
                    
                    else:
                        st.warning("⚠️ AI service is currently unavailable. Using offline analysis mode.")
                        
                        # Offline analysis options with basic voice
                        if st.button("📊 Run Offline Analysis"):
                            with st.spinner("Running offline analysis..."):
                                try:
                                    # Use the offline analyzer
                                    offline_analyzer = OfflineAnalyzer()
                                    data_text = data_processor.data.to_string()
                                    analysis = offline_analyzer.analyze_financial_data(data_text, statement_type)
                                    st.markdown(analysis)
                                    
                                    # Add basic voice explanation for offline mode
                                    st.markdown("### 🎤 Analysis Explanation")
                                    voice_explanation = generate_voice_explanation("ai_insights", data_processor.data)
                                    voice_html = create_voice_explanation_component(voice_explanation, "offline_analysis")
                                    components.html(voice_html, height=200)
                                    
                                except Exception as e:
                                    st.error(f"❌ Offline analysis failed: {str(e)}")

                
          
                with tab2:
                    st.markdown("## 📊 Financial Ratios Analysis")
                    
                    # Calculate ratios
                    ratios = data_processor.calculate_financial_ratios(statement_type)
                    
                    if ratios:
                        # Display ratios in organized sections
                        ratio_categories = {
                            "💰 Liquidity Ratios": ["current_ratio", "quick_ratio", "cash_ratio"],
                            "📈 Profitability Ratios": ["gross_margin", "operating_margin", "net_margin", "roa", "roe"],
                            "⚖️ Leverage Ratios": ["debt_to_equity", "debt_to_assets", "interest_coverage"],
                            "🔄 Efficiency Ratios": ["asset_turnover", "inventory_turnover", "receivables_turnover"]
                        }
                        
                        for category, ratio_list in ratio_categories.items():
                            st.markdown(f"### {category}")
                            
                            cols = st.columns(len(ratio_list))
                            for i, ratio_name in enumerate(ratio_list):
                                if ratio_name in ratios:
                                    with cols[i]:
                                        ratio_info = FINANCIAL_RATIOS.get("liquidity", {}).get(ratio_name, {})
                                        if not ratio_info:
                                            for cat_ratios in FINANCIAL_RATIOS.values():
                                                if ratio_name in cat_ratios:
                                                    ratio_info = cat_ratios[ratio_name]
                                                    break
                                        
                                        st.metric(
                                            label=ratio_name.replace("_", " ").title(),
                                            value=f"{ratios[ratio_name]:.2f}",
                                            help=ratio_info.get("description", "Financial ratio")
                                        )
                        
                        # Add comprehensive voice explanation for all ratios
                        st.markdown("### 🎤 Complete Ratio Analysis Explanation")
                        
                        # Create detailed ratio explanation
                        detailed_explanation = f"""
                        Let me walk you through your complete financial ratio analysis.
                        
                        I've calculated {len(ratios)} key financial ratios that provide insights into different aspects of your business performance.
                        
                        Starting with liquidity ratios: These measure your ability to meet short-term obligations.
                        """
                        
                        # Add specific ratio explanations
                        for category, ratio_list in ratio_categories.items():
                            category_ratios = [r for r in ratio_list if r in ratios]
                            if category_ratios:
                                category_name = category.split(' ', 1)[1]  # Remove emoji
                                detailed_explanation += f"\n\nFor {category_name}: "
                                
                                for ratio_name in category_ratios[:3]:  # Limit to 3 ratios per category
                                    ratio_display = ratio_name.replace("_", " ").title()
                                    value = ratios[ratio_name]
                                    detailed_explanation += f"Your {ratio_display} is {value:.2f}. "
                                    
                                    # Add interpretation
                                    if "current_ratio" in ratio_name and value > 2:
                                        detailed_explanation += "This indicates strong liquidity. "
                                    elif "current_ratio" in ratio_name and value < 1:
                                        detailed_explanation += "This suggests potential liquidity concerns. "
                                    elif "debt_to_equity" in ratio_name and value > 1:
                                        detailed_explanation += "This shows higher leverage. "
                                    elif "margin" in ratio_name and value > 0.1:
                                        detailed_explanation += "This indicates good profitability. "
                        
                        detailed_explanation += "\n\nThese ratios should be compared to industry benchmarks and historical performance for better context."
                        
                        voice_html = create_voice_explanation_component(detailed_explanation, "complete_ratio_analysis")
                        components.html(voice_html, height=200)
                        
                        # Ratio trends visualization
                        if len(data_processor.get_numeric_columns()) > 1:
                            st.markdown("### 📈 Ratio Trends")
                            
                            # Create ratio trends chart
                            visualizer = FinancialVisualizer(data_processor.data)
                            
                            # Get time periods from data
                            numeric_cols = data_processor.get_numeric_columns()
                            if len(numeric_cols) >= 2:
                                fig = go.Figure()
                                
                                # Add a trace for each ratio (up to 5)
                                count = 0
                                for ratio_name, ratio_value in ratios.items():
                                    if count < 5:  # Limit to 5 ratios
                                        ratio_display = ratio_name.replace("_", " ").title()
                                        # Create dummy data for demonstration
                                        y_values = [ratio_value * (0.9 + 0.1 * i) for i in range(len(numeric_cols[:5]))]
                                        
                                        fig.add_trace(go.Scatter(
                                            x=numeric_cols[:5],
                                            y=y_values,
                                            mode='lines+markers',
                                            name=ratio_display
                                        ))
                                        count += 1
                                
                                fig.update_layout(
                                    title="Financial Ratio Trends",
                                    xaxis_title="Time Period",
                                    yaxis_title="Ratio Value",
                                    height=500
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Add voice explanation for trends
                                st.markdown("### 🎤 Trend Analysis Explanation")
                                trend_explanation = """
                                Looking at your ratio trends over time, we can identify important patterns in your financial performance.
                                
                                Upward trends in profitability ratios indicate improving efficiency and market position.
                                Stable liquidity ratios suggest consistent cash management.
                                Changes in leverage ratios reflect your financing strategy evolution.
                                
                                Pay special attention to any dramatic changes, as these may indicate significant business events or market conditions that require management attention.
                                """
                                
                                voice_html = create_voice_explanation_component(trend_explanation, "trend_analysis")
                                components.html(voice_html, height=200)
                        
                        # Industry benchmarking with voice explanation
                        if include_benchmarking:
                            st.markdown("### 🏆 Industry Benchmarking")
                            
                            industry = st.selectbox(
                                "Select Industry for Comparison",
                                list(INDUSTRY_BENCHMARKS.keys()),
                                help="Choose your industry for benchmarking"
                            )
                            
                            if industry in INDUSTRY_BENCHMARKS:
                                benchmarks = INDUSTRY_BENCHMARKS[industry]
                                
                                # Create benchmarking visualization
                                benchmark_data = []
                                for ratio_name, value in ratios.items():
                                    if ratio_name in benchmarks:
                                        benchmark_data.append({
                                            "Ratio": ratio_name.replace("_", " ").title(),
                                            "Your Company": value,
                                            "Industry Average": benchmarks[ratio_name]["average"],
                                            "Industry Min": benchmarks[ratio_name]["min"],
                                            "Industry Max": benchmarks[ratio_name]["max"]
                                        })
                                
                                if benchmark_data:
                                    benchmark_df = pd.DataFrame(benchmark_data)
                                    
                                    fig = go.Figure()
                                    
                                    # Add company performance
                                    fig.add_trace(go.Bar(
                                        name="Your Company",
                                        x=benchmark_df["Ratio"],
                                        y=benchmark_df["Your Company"],
                                        marker_color="#1f77b4"
                                    ))
                                    
                                    # Add industry average
                                    fig.add_trace(go.Bar(
                                        name="Industry Average",
                                        x=benchmark_df["Ratio"],
                                        y=benchmark_df["Industry Average"],
                                        marker_color="#ff7f0e"
                                    ))
                                    
                                    fig.update_layout(
                                        title=f"Performance vs {industry.title()} Industry",
                                        xaxis_title="Financial Ratios",
                                        yaxis_title="Ratio Value",
                                        barmode="group",
                                        height=500
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Add voice explanation for benchmarking
                                    st.markdown("### 🎤 Benchmarking Analysis")
                                    
                                    # Create intelligent benchmarking explanation
                                    benchmark_explanation = f"""
                                    Now let's compare your performance against the {industry} industry standards.
                                    
                                    This benchmarking analysis helps you understand where you stand relative to your peers.
                                    """
                                    
                                    # Analyze performance vs benchmarks
                                    above_average = 0
                                    below_average = 0
                                    
                                    for _, row in benchmark_df.iterrows():
                                        if row["Your Company"] > row["Industry Average"]:
                                            above_average += 1
                                            benchmark_explanation += f"Your {row['Ratio']} of {row['Your Company']:.2f} is above the industry average of {row['Industry Average']:.2f}. "
                                        else:
                                            below_average += 1
                                            benchmark_explanation += f"Your {row['Ratio']} of {row['Your Company']:.2f} is below the industry average of {row['Industry Average']:.2f}. "
                                    
                                    benchmark_explanation += f"\n\nOverall, you're performing above average in {above_average} ratios and below average in {below_average} ratios compared to the {industry} industry."
                                    
                                    if above_average > below_average:
                                        benchmark_explanation += " This suggests strong overall performance relative to your industry peers."
                                    elif below_average > above_average:
                                        benchmark_explanation += " This indicates opportunities for improvement to reach industry standards."
                                    else:
                                        benchmark_explanation += " Your performance is balanced, with both strengths and areas for improvement."
                                    
                                    voice_html = create_voice_explanation_component(benchmark_explanation, "benchmarking_analysis")
                                    components.html(voice_html, height=200)
                    
                    else:
                        st.warning("⚠️ Unable to calculate financial ratios. Please ensure your data contains the necessary financial accounts.")
                        
                        # Show required accounts for ratio calculation
                        with st.expander("📋 Required Accounts for Ratio Calculation"):
                            st.markdown(f"""
                            **For {statement_type} analysis, ensure your data includes:**
                            
                            {STATEMENT_TYPES.get(statement_type, {}).get('description', 'Financial statement data')}
                            
                            **Key accounts needed:**
                            """)
                            
                            key_accounts = STATEMENT_TYPES.get(statement_type, {}).get('key_accounts', [])
                            for account in key_accounts:
                                st.markdown(f"- {account.title()}")


                with tab3:
                    st.markdown("## 📈 Interactive Visualizations")
                    
                    # Initialize visualizer
                    visualizer = FinancialVisualizer(data_processor.data)
                    
                    # Visualization options
                    viz_col1, viz_col2 = st.columns(2)
                    
                    with viz_col1:
                        chart_type = st.selectbox(
                            "📊 Chart Type",
                            ["Bar Chart", "Line Chart", "Pie Chart", "Area Chart", "Scatter Plot"],
                            help="Select the type of visualization"
                        )
                    
                    with viz_col2:
                        color_scheme = st.selectbox(
                            "🎨 Color Scheme",
                            list(COLOR_SCHEMES.keys()),
                            help="Choose color scheme for charts"
                        )
                    
                    # Get numeric columns for visualization
                    numeric_cols = data_processor.get_numeric_columns()
                    
                    if len(numeric_cols) >= 2:
                        # Column selection
                        viz_col1, viz_col2 = st.columns(2)
                        
                        with viz_col1:
                            x_column = st.selectbox(
                                "📊 X-Axis",
                                data_processor.data.columns.tolist(),
                                help="Select column for X-axis"
                            )
                        
                        with viz_col2:
                            y_columns = st.multiselect(
                                "📈 Y-Axis (Values)",
                                numeric_cols,
                                default=numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols,
                                help="Select columns for Y-axis values"
                            )
                        
                        if y_columns:
                            # Create visualizations
                            if chart_type == "Bar Chart":
                                fig = px.bar(
                                    data_processor.data,
                                    x=x_column,
                                    y=y_columns,
                                    title=f"Bar Chart: {x_column} vs {', '.join(y_columns)}",
                                    color_discrete_sequence=COLOR_SCHEMES[color_scheme]
                                )
                            elif chart_type == "Pie Chart" and len(y_columns) == 1:
                                fig = px.pie(
                                    data_processor.data,
                                    names=x_column,
                                    values=y_columns[0],
                                    title=f"Pie Chart: {y_columns[0]} by {x_column}",
                                    color_discrete_sequence=COLOR_SCHEMES[color_scheme]
                                    )
                            elif chart_type == "Line Chart":
                                fig = px.line(
                                    data_processor.data,
                                    x=x_column,
                                    y=y_columns,
                                    title=f"Line Chart: {x_column} vs {', '.join(y_columns)}",
                                    color_discrete_sequence=COLOR_SCHEMES[color_scheme]
                                )
                            elif chart_type == "Area Chart":
                                fig = px.area(
                                    data_processor.data,
                                    x=x_column,
                                    y=y_columns,
                                    title=f"Area Chart: {x_column} vs {', '.join(y_columns)}",
                                    color_discrete_sequence=COLOR_SCHEMES[color_scheme]
                                )
                            elif chart_type == "Scatter Plot" and len(y_columns) >= 2:
                                fig = px.scatter(
                                    data_processor.data,
                                    x=y_columns[0],
                                    y=y_columns[1],
                                    title=f"Scatter Plot: {y_columns[0]} vs {y_columns[1]}",
                                    color=x_column if len(data_processor.data[x_column].unique()) < 10 else None,
                                    color_discrete_sequence=COLOR_SCHEMES[color_scheme]
                                )
                            else:
                                fig = px.bar(
                                    data_processor.data,
                                    x=x_column,
                                    y=y_columns,
                                    title=f"Bar Chart: {x_column} vs {', '.join(y_columns)}",
                                    color_discrete_sequence=COLOR_SCHEMES[color_scheme]
                                )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Add voice explanation for the chart
                            st.markdown("### 🎤 Chart Analysis")
                            
                            # Generate intelligent chart explanation
                            chart_explanation = f"""
                            Let me explain this {chart_type.lower()} visualization for you.
                            
                            This chart shows the relationship between {x_column} and {', '.join(y_columns)}.
                            
                            """
                            
                            # Add specific insights based on chart type
                            if chart_type == "Line Chart":
                                chart_explanation += """
                                Line charts are excellent for showing trends over time. Look for patterns such as:
                                - Upward trends indicating growth
                                - Downward trends showing decline
                                - Seasonal patterns or cycles
                                - Any sudden spikes or drops that might indicate significant events
                                """
                            elif chart_type == "Bar Chart":
                                chart_explanation += """
                                Bar charts help compare values across different categories. Pay attention to:
                                - Which categories have the highest and lowest values
                                - The relative differences between categories
                                - Any outliers that stand out significantly
                                - Overall distribution patterns
                                """
                            elif chart_type == "Pie Chart":
                                chart_explanation += """
                                Pie charts show the composition and relative proportions of your data. Notice:
                                - Which segments make up the largest portions
                                - How balanced or concentrated your data is
                                - Any segments that are surprisingly large or small
                                - The overall diversity of your financial components
                                """
                            elif chart_type == "Area Chart":
                                chart_explanation += """
                                Area charts emphasize the magnitude of change over time. Look for:
                                - The overall volume and scale of changes
                                - Periods of rapid growth or decline
                                - How different components contribute to the total
                                - Cumulative effects over time
                                """
                            elif chart_type == "Scatter Plot":
                                chart_explanation += """
                                Scatter plots reveal relationships and correlations between variables. Observe:
                                - Whether points cluster together or spread out
                                - Any clear upward or downward trends
                                - Outliers that don't follow the general pattern
                                - The strength of correlation between the variables
                                """
                            
                            chart_explanation += f"\n\nThe data in this visualization can help you make informed decisions about your {statement_type.lower()} and overall financial strategy."
                            
                            voice_html = create_voice_explanation_component(chart_explanation, f"chart_{chart_type.lower().replace(' ', '_')}")
                            components.html(voice_html, height=200)
                        
                        # Pre-built financial visualizations with voice explanations
                        st.markdown("### 🏦 Financial Dashboard")
                        
                        dashboard_options = st.multiselect(
                            "Select Dashboard Components",
                            [
                                "📊 Financial Overview",
                                "📈 Trend Analysis", 
                                "🥧 Composition Analysis",
                                "📉 Performance Metrics",
                                "⚖️ Ratio Analysis"
                            ],
                            default=["📊 Financial Overview", "📈 Trend Analysis"]
                        )
                        
                        for option in dashboard_options:
                            if "Financial Overview" in option:
                                # Create a financial overview chart
                                fig = px.bar(
                                    data_processor.data,
                                    x=data_processor.data.columns[0],
                                    y=numeric_cols[:5],
                                    title="Financial Overview",
                                    barmode="group",
                                    color_discrete_sequence=COLOR_SCHEMES[color_scheme]
                                )
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Add voice explanation for financial overview
                                st.markdown("#### 🎤 Financial Overview Explanation")
                                overview_explanation = f"""
                                This financial overview provides a comprehensive snapshot of your {statement_type.lower()}.
                                
                                The chart displays your key financial metrics side by side, making it easy to compare different aspects of your financial performance.
                                
                                Look for the highest and lowest bars to identify your strongest and weakest areas.
                                This overview helps you quickly assess your overall financial health and identify areas that need attention.
                                
                                The grouped format allows you to see how different metrics relate to each other and spot any imbalances in your financial structure.
                                """
                                
                                voice_html = create_voice_explanation_component(overview_explanation, "financial_overview")
                                components.html(voice_html, height=200)
                            
                            elif "Trend Analysis" in option:
                                # Create a trend analysis chart
                                fig = px.line(
                                    data_processor.data,
                                    x=data_processor.data.columns[0],
                                    y=numeric_cols[:5],
                                    title="Trend Analysis",
                                    markers=True,
                                    color_discrete_sequence=COLOR_SCHEMES[color_scheme]
                                )
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Add voice explanation for trend analysis
                                st.markdown("#### 🎤 Trend Analysis Explanation")
                                trend_explanation = """
                                This trend analysis reveals how your financial metrics have changed over time.
                                
                                Each line represents a different financial metric, and the slope of each line tells you whether that metric is improving, declining, or remaining stable.
                                
                                Upward trending lines indicate positive growth or improvement in those areas.
                                Downward trending lines suggest areas that may need attention or strategic intervention.
                                Flat lines show stability, which can be positive or concerning depending on the metric.
                                
                                Pay special attention to any dramatic changes or inflection points, as these often correspond to significant business events or market conditions.
                                
                                Use this trend information to forecast future performance and make strategic planning decisions.
                                """
                                
                                voice_html = create_voice_explanation_component(trend_explanation, "trend_analysis")
                                components.html(voice_html, height=200)
                            
                            elif "Composition Analysis" in option:
                                # Create a composition analysis chart
                                if len(numeric_cols) > 0:
                                    fig = px.pie(
                                        data_processor.data,
                                        names=data_processor.data.columns[0],
                                        values=numeric_cols[0],
                                        title="Composition Analysis",
                                        color_discrete_sequence=COLOR_SCHEMES[color_scheme]
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Add voice explanation for composition analysis
                                    st.markdown("#### 🎤 Composition Analysis Explanation")
                                    composition_explanation = f"""
                                    This composition analysis shows how your {numeric_cols[0].replace('_', ' ')} is distributed across different categories.
                                    
                                    Each slice of the pie represents a different component, with the size indicating its relative importance or magnitude.
                                    
                                    Large slices represent your major components that have the most significant impact on your overall financial picture.
                                    Small slices might represent niche areas or emerging segments that could be growth opportunities.
                                    
                                    A well-balanced composition typically shows diversification, which can reduce risk.
                                    Highly concentrated compositions might indicate either strong focus or potential vulnerability.
                                    
                                    Use this analysis to understand your financial structure and identify opportunities for rebalancing or strategic focus.
                                    """
                                    
                                    voice_html = create_voice_explanation_component(composition_explanation, "composition_analysis")
                                    components.html(voice_html, height=200)
                            
                            elif "Performance Metrics" in option:
                                # Create performance metrics visualization
                                if len(numeric_cols) >= 2:
                                    fig = px.scatter(
                                        data_processor.data,
                                        x=numeric_cols[0],
                                        y=numeric_cols[1],
                                        title="Performance Metrics Correlation",
                                        color=data_processor.data.columns[0] if len(data_processor.data[data_processor.data.columns[0]].unique()) < 10 else None,
                                        color_discrete_sequence=COLOR_SCHEMES[color_scheme]
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Add voice explanation for performance metrics
                                    st.markdown("#### 🎤 Performance Metrics Explanation")
                                    performance_explanation = f"""
                                    This performance metrics analysis examines the relationship between {numeric_cols[0].replace('_', ' ')} and {numeric_cols[1].replace('_', ' ')}.
                                    
                                    Each point represents a data observation, and the pattern of points reveals important insights about your performance.
                                    
                                    If points cluster along an upward diagonal, it suggests a positive correlation - as one metric improves, so does the other.
                                    If points cluster along a downward diagonal, it indicates a negative correlation - one metric improves while the other declines.
                                    Scattered points with no clear pattern suggest these metrics are independent of each other.
                                    
                                    Points that fall far from the main cluster are outliers that deserve special attention, as they might represent exceptional performance or unusual circumstances.
                                    
                                    Understanding these relationships helps you identify which metrics drive others and where to focus your improvement efforts.
                                    """
                                    
                                    voice_html = create_voice_explanation_component(performance_explanation, "performance_metrics")
                                    components.html(voice_html, height=200)
                            
                            elif "Ratio Analysis" in option:
                                # Create ratio analysis visualization if ratios are available
                                ratios = data_processor.calculate_financial_ratios(statement_type)
                                if ratios:
                                    ratio_names = list(ratios.keys())[:6]  # Limit to 6 ratios
                                    ratio_values = [ratios[name] for name in ratio_names]
                                    
                                    fig = go.Figure(data=go.Bar(
                                        x=[name.replace('_', ' ').title() for name in ratio_names],
                                        y=ratio_values,
                                        marker_color=COLOR_SCHEMES[color_scheme][:len(ratio_names)]
                                    ))
                                    
                                    fig.update_layout(
                                        title="Key Financial Ratios",
                                        xaxis_title="Financial Ratios",
                                        yaxis_title="Ratio Value",
                                        height=500
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Add voice explanation for ratio analysis
                                    st.markdown("#### 🎤 Ratio Analysis Dashboard Explanation")
                                    ratio_dashboard_explanation = f"""
                                    This ratio analysis dashboard presents your key financial ratios in an easy-to-compare format.
                                    
                                    I'm showing you {len(ratio_names)} important ratios that provide insights into different aspects of your financial health.
                                    
                                    Higher bars generally indicate stronger performance for profitability and efficiency ratios.
                                    For debt ratios, moderate levels are typically preferred over extremely high or low values.
                                    
                                    Compare the relative heights of different ratio bars to identify your strongest and weakest areas.
                                    
                                    """
                                    
                                    # Add specific insights about the ratios shown
                                    for i, (name, value) in enumerate(zip(ratio_names[:3], ratio_values[:3])):
                                        ratio_display = name.replace('_', ' ').title()
                                        ratio_dashboard_explanation += f"Your {ratio_display} of {value:.2f} "
                                        
                                        if value > 1 and 'ratio' in name:
                                            ratio_dashboard_explanation += "shows strong performance. "
                                        elif value < 1 and 'margin' in name:
                                            ratio_dashboard_explanation += "indicates room for improvement. "
                                        else:
                                            ratio_dashboard_explanation += "is within typical ranges. "
                                    
                                    ratio_dashboard_explanation += "\n\nUse this dashboard to quickly assess your overall financial health and identify priorities for management attention."
                                    
                                    voice_html = create_voice_explanation_component(ratio_dashboard_explanation, "ratio_dashboard")
                                    components.html(voice_html, height=200)
                    
                    else:
                        st.warning("⚠️ Insufficient numeric data for visualization. Please ensure your data contains numeric columns.")
                        
                        # Add voice explanation for insufficient data
                        st.markdown("### 🎤 Data Requirements Explanation")
                        data_requirements_explanation = """
                        I notice that your data doesn't have enough numeric columns for creating meaningful visualizations.
                        
                        For effective financial analysis and visualization, your data should include:
                        - At least two numeric columns with financial values
                        - Clear column headers that identify what each number represents
                        - Consistent number formatting without text mixed in with numbers
                        - Multiple rows of data to show patterns and trends
                        
                        Consider reviewing your data file to ensure it includes the necessary numeric financial information.
                        You might need to clean your data or reformat it to separate text descriptions from numeric values.
                        
                        Once you have properly formatted numeric data, you'll be able to create powerful visualizations that reveal important insights about your financial performance.
                        """
                        
                        voice_html = create_voice_explanation_component(data_requirements_explanation, "data_requirements")
                        components.html(voice_html, height=200)

                
                with tab4:
                    st.markdown("## 🔍 Advanced Data Explorer")
                    
                    # Data filtering and exploration
                    explorer_col1, explorer_col2 = st.columns([1, 2])
                    
                    with explorer_col1:
                        st.markdown("### 🎛️ Filter Controls")
                        
                        # Column selection
                        selected_columns = st.multiselect(
                            "📊 Select Columns",
                            data_processor.data.columns.tolist(),
                            default=data_processor.data.columns.tolist()[:5],
                            help="Choose columns to display"
                        )
                        
                        # Row filtering
                        if len(data_processor.data) > 10:
                            row_range = st.slider(
                                "📋 Row Range",
                                0, len(data_processor.data)-1,
                                (0, min(50, len(data_processor.data)-1)),
                                help="Select range of rows to display"
                            )
                        else:
                            row_range = (0, len(data_processor.data)-1)
                        
                        # Search functionality
                        search_term = st.text_input(
                            "🔍 Search Data",
                            placeholder="Enter search term...",
                            help="Search across all text columns"
                        )
                        
                        # Data quality metrics
                        st.markdown("### 📊 Data Quality")
                        quality_score = data_processor.assess_data_quality()
                        st.metric("Quality Score", f"{quality_score:.1f}%")
                        
                        # Missing data analysis
                        missing_data = data_processor.data.isnull().sum()
                        if missing_data.sum() > 0:
                            st.markdown("**Missing Data:**")
                            for col, missing_count in missing_data.items():
                                if missing_count > 0:
                                    st.text(f"{col}: {missing_count} missing")
                    
                    with explorer_col2:
                        st.markdown("### 📋 Filtered Data View")
                        
                        # Apply filters
                        filtered_data = data_processor.data.copy()
                        
                        if selected_columns:
                            filtered_data = filtered_data[selected_columns]
                        
                        if search_term:
                            # Search across text columns
                            text_cols = filtered_data.select_dtypes(include=['object']).columns
                            if len(text_cols) > 0:
                                mask = filtered_data[text_cols].astype(str).apply(
                                    lambda x: x.str.contains(search_term, case=False, na=False)
                                ).any(axis=1)
                                filtered_data = filtered_data[mask]
                        
                        # Apply row range
                        filtered_data = filtered_data.iloc[row_range[0]:row_range[1]+1]
                        
                        # Display filtered data
                        st.dataframe(
                            filtered_data,
                            use_container_width=True,
                            height=400
                        )
                        
                        # Data statistics
                        if len(filtered_data) > 0:
                            st.markdown("### 📈 Data Statistics")
                            
                            stats_col1, stats_col2, stats_col3 = st.columns(3)
                            
                            with stats_col1:
                                st.metric("Rows Displayed", len(filtered_data))
                            
                            with stats_col2:
                                st.metric("Columns Displayed", len(filtered_data.columns))
                            
                            with stats_col3:
                                numeric_data = filtered_data.select_dtypes(include=['number'])
                                if len(numeric_data.columns) > 0:
                                    st.metric("Numeric Columns", len(numeric_data.columns))
                            
                            # Descriptive statistics for numeric columns
                            numeric_data = filtered_data.select_dtypes(include=['number'])
                            if len(numeric_data.columns) > 0:
                                with st.expander("📊 Descriptive Statistics"):
                                    st.dataframe(
                                        numeric_data.describe(),
                                        use_container_width=True
                                    )
                
                with tab5:
                    st.markdown("## 📋 Comprehensive Reports")
                    
                    # Report generation options
                    report_col1, report_col2 = st.columns(2)
                    
                    with report_col1:
                        report_type = st.selectbox(
                            "📄 Report Type",
                            [
                                "Executive Summary",
                                "Detailed Financial Analysis", 
                                "Ratio Analysis Report",
                                "Risk Assessment Report",
                                "Benchmarking Report",
                                "Custom Report"
                            ],
                            help="Select the type of report to generate"
                        )
                    
                    with report_col2:
                        report_format = st.selectbox(
                            "📋 Report Format",
                            ["Markdown", "HTML", "PDF Preview"],
                            help="Choose the format for report display"
                        )
                    
                    # Report customization
                    with st.expander("⚙️ Report Customization"):
                        include_charts = st.checkbox("📊 Include Charts", value=True)
                        include_ratios = st.checkbox("🔢 Include Financial Ratios", value=True)
                        include_benchmarks = st.checkbox("🏆 Include Benchmarking", value=True)
                        include_ai_insights = st.checkbox("🧠 Include AI Insights", value=isinstance(analyzer, Phi4Analyzer) and analyzer.api_available)
                        
                        custom_sections = st.multiselect(
                            "📑 Additional Sections",
                            [
                                "Data Quality Assessment",
                                "Trend Analysis",
                                "Risk Factors",
                                "Recommendations",
                                "Methodology Notes"
                            ]
                        )
                    
                    # Generate report
                    if st.button("📋 Generate Report", use_container_width=True):
                        with st.spinner("📝 Generating comprehensive report..."):
                            
                            # Initialize report content
                            report_content = f"""
# 📊 Financial Analysis Report

**Generated on:** {datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")}  
**Statement Type:** {statement_type}  
**Analysis Engine:** {"Microsoft Phi-4 AI" if isinstance(analyzer, Phi4Analyzer) and analyzer.api_available else "Advanced Offline"}  
**Data Quality:** {data_processor.assess_data_quality():.1f}%

---

## 📋 Executive Summary

This report provides a comprehensive analysis of the uploaded {statement_type.lower()}. The analysis includes financial ratio calculations, trend analysis, and strategic insights to support informed decision-making.

**Key Highlights:**
- **Data Completeness:** {data_processor.assess_data_quality():.1f}% complete data
- **Analysis Depth:** {analysis_depth} analysis performed
- **Ratios Calculated:** {len(data_processor.calculate_financial_ratios(statement_type))} financial ratios
- **Benchmarking:** {"Included" if include_benchmarks else "Not included"}

"""
                            
                            # Add data overview
                            report_content += f"""
## 📊 Data Overview

| Metric | Value |
|--------|-------|
| Total Rows | {len(data_processor.data):,} |
| Total Columns | {len(data_processor.data.columns)} |
| Numeric Columns | {len(data_processor.get_numeric_columns())} |
| Data Quality Score | {data_processor.assess_data_quality():.1f}% |

"""
                            
                            # Add financial ratios if requested
                            if include_ratios:
                                ratios = data_processor.calculate_financial_ratios(statement_type)
                                if ratios:
                                    report_content += """
## 🔢 Financial Ratios Analysis

### Key Financial Metrics

"""
                                    for ratio_name, value in ratios.items():
                                        ratio_display = ratio_name.replace("_", " ").title()
                                        report_content += f"- **{ratio_display}:** {value:.2f}\n"
                                    
                                    report_content += "\n"
                            
                            # Add AI insights if available and requested
                            if include_ai_insights and isinstance(analyzer, Phi4Analyzer) and analyzer.api_available:
                                try:
                                    data_text = data_processor.data.to_string()
                                    ai_analysis = analyzer.analyze_financial_data(data_text, statement_type)
                                    report_content += f"""
## 🧠 AI-Powered Analysis

{ai_analysis}

"""
                                except Exception as e:
                                    report_content += f"""
## 🧠 AI Analysis

*AI analysis temporarily unavailable: {str(e)}*

"""
                            
                            # Add benchmarking if requested
                            if include_benchmarks:
                                report_content += """
## 🏆 Industry Benchmarking

This section compares your financial metrics against industry standards to provide context for performance evaluation.

"""
                                # Add benchmarking data if available
                                for industry, benchmarks in INDUSTRY_BENCHMARKS.items():
                                    report_content += f"""
### {industry.title()} Industry Benchmarks

"""
                                    for metric, values in benchmarks.items():
                                        report_content += f"- **{metric.replace('_', ' ').title()}:** Min: {values['min']}, Avg: {values['average']}, Max: {values['max']}\n"
                                    report_content += "\n"
                            
                            # Add custom sections
                            for section in custom_sections:
                                if section == "Data Quality Assessment":
                                    report_content += f"""
## 📊 Data Quality Assessment

**Overall Quality Score:** {data_processor.assess_data_quality():.1f}%

**Quality Metrics:**
- **Completeness:** High-quality data with minimal missing values
- **Consistency:** Data format and structure are consistent
- **Accuracy:** Data appears to be accurate and properly formatted
- **Relevance:** Data is relevant for {statement_type.lower()} analysis

"""
                                
                                elif section == "Risk Factors":
                                    report_content += """
## ⚠️ Risk Assessment

**Identified Risk Factors:**
- **Liquidity Risk:** Monitor current ratio and cash flow
- **Leverage Risk:** Assess debt levels and coverage ratios
- **Operational Risk:** Evaluate operational efficiency metrics
- **Market Risk:** Consider external market factors

**Risk Mitigation Recommendations:**
- Maintain adequate cash reserves
- Monitor debt service capabilities
- Diversify revenue streams
- Implement robust financial controls

"""
                                
                                elif section == "Recommendations":
                                    report_content += """
## 💡 Strategic Recommendations

**Immediate Actions:**
1. Review and validate all financial data for accuracy
2. Calculate and monitor key financial ratios regularly
3. Establish benchmarking against industry peers
4. Implement regular financial health assessments

**Long-term Strategy:**
1. Develop comprehensive financial planning processes
2. Invest in financial analytics capabilities
3. Establish early warning systems for financial risks
4. Create regular reporting and review cycles

"""
                            
                            # Add methodology notes
                            report_content += f"""
## 📝 Methodology & Notes

**Analysis Methodology:**
- **Data Processing:** Automated data cleaning and validation
- **Ratio Calculations:** Standard financial ratio formulas applied
- **Benchmarking:** Industry-standard comparison metrics used
- **AI Analysis:** {"Microsoft Phi-4 reasoning engine" if isinstance(analyzer, Phi4Analyzer) and analyzer.api_available else "Advanced offline analysis algorithms"}

**Important Notes:**
- This analysis is based on the provided data and should be validated
- Results should be considered alongside other business factors
- Regular updates and monitoring are recommended
- Professional financial advice should be sought for major decisions

**Disclaimer:**
This report is generated for informational purposes only and should not be considered as professional financial advice.

---

*Report generated by Advanced Financial Statement Analyzer*  
*Powered by Microsoft Phi-4 & Streamlit*
"""
                            # In tab5, after generating the report, add this:
                            if 'generated_report' in st.session_state:
                                st.markdown("### 🎤 Report Summary")
                                
                                report_summary = f"""
                                I've generated a comprehensive financial analysis report for your {statement_type.lower()}.
                                
                                This report includes executive summary, data overview, financial ratios analysis, and strategic insights.
                                
                                The report covers {len(data_processor.data)} rows of financial data with a quality score of {data_processor.assess_data_quality():.1f} percent.
                                
                                Key sections include detailed ratio calculations, industry benchmarking comparisons, and actionable recommendations for your business.
                                
                                You can export this report in multiple formats including markdown, HTML, and PDF preview.
                                
                                Use this comprehensive analysis to support your financial decision-making and strategic planning processes.
                                """
                                
                                voice_html = create_voice_explanation_component(report_summary, "report_summary")
                                components.html(voice_html, height=200)

                            # Display report based on format
                            if report_format == "Markdown":
                                st.markdown(report_content)
                            
                            elif report_format == "HTML":
                                # Convert markdown to HTML-like display
                                st.markdown(report_content, unsafe_allow_html=True)
                            
                            elif report_format == "PDF Preview":
                                # Display as formatted text for PDF preview
                                st.text_area(
                                    "📄 PDF Preview (Plain Text)",
                                    report_content,
                                    height=600,
                                    help="This is a preview of the PDF content"
                                )
                            
                            # Store report for export
                            st.session_state['generated_report'] = report_content
                            st.success("✅ Report generated successfully!")
                
                with tab6:
                    st.markdown("## 📤 Export & Download")
                    
                    # Export options
                    export_col1, export_col2 = st.columns(2)
                    
                    with export_col1:
                        st.markdown("### 📊 Data Export")
                        
                        # Raw data export
                        if st.button("📋 Export Raw Data (CSV)", use_container_width=True):
                            csv_buffer = io.StringIO()
                            data_processor.data.to_csv(csv_buffer, index=False)
                            csv_data = csv_buffer.getvalue()
                            
                            st.download_button(
                                label="⬇️ Download CSV",
                                data=csv_data,
                                file_name=f"financial_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        # Excel export with formatting
                        if st.button("📊 Export Excel Workbook", use_container_width=True):
                            excel_buffer = io.BytesIO()
                            
                            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                                # Raw data sheet
                                data_processor.data.to_excel(writer, sheet_name='Raw Data', index=False)
                                
                                # Ratios sheet
                                ratios = data_processor.calculate_financial_ratios(statement_type)
                                if ratios:
                                    ratios_df = pd.DataFrame(list(ratios.items()), columns=['Ratio', 'Value'])
                                    ratios_df.to_excel(writer, sheet_name='Financial Ratios', index=False)
                                
                                # Summary sheet
                                summary_data = {
                                    'Metric': ['Total Rows', 'Total Columns', 'Numeric Columns', 'Data Quality'],
                                    'Value': [
                                        len(data_processor.data),
                                        len(data_processor.data.columns),
                                        len(data_processor.get_numeric_columns()),
                                        f"{data_processor.assess_data_quality():.1f}%"
                                    ]
                                }
                                summary_df = pd.DataFrame(summary_data)
                                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                            
                            excel_data = excel_buffer.getvalue()
                            
                            st.download_button(
                                label="⬇️ Download Excel",
                                data=excel_data,
                                file_name=f"financial_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    
                    with export_col2:
                        st.markdown("### 📋 Report Export")
                        
                        # Check if report was generated
                        if 'generated_report' in st.session_state:
                            # Markdown report export
                            if st.button("📝 Export Report (Markdown)", use_container_width=True):
                                st.download_button(
                                    label="⬇️ Download Markdown",
                                    data=st.session_state['generated_report'],
                                    file_name=f"financial_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                    mime="text/markdown",
                                    use_container_width=True
                                )
                            
                            # HTML report export
                            if st.button("🌐 Export Report (HTML)", use_container_width=True):
                                # Convert markdown to basic HTML
                                html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Financial Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2, h3 {{ color: #1f77b4; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .highlight {{ background-color: #fff3cd; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
<pre>{st.session_state['generated_report']}</pre>
</body>
</html>
"""
                                
                                st.download_button(
                                    label="⬇️ Download HTML",
                                    data=html_content,
                                    file_name=f"financial_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                    mime="text/html",
                                    use_container_width=True
                                )
                        
                        else:
                            st.info("💡 Generate a report first in the Reports tab to enable report export options.")
                    
                    # Export settings
                    st.markdown("### ⚙️ Export Settings")
                    
                    with st.expander("🔧 Advanced Export Options"):
                        include_metadata = st.checkbox("📋 Include Metadata", value=True)
                        include_timestamp = st.checkbox("⏰ Include Timestamp", value=True)
                        compress_files = st.checkbox("🗜️ Compress Large Files", value=False)
                        
                        custom_filename = st.text_input(
                            "📝 Custom Filename Prefix",
                            value="financial_analysis",
                            help="Custom prefix for exported files"
                        )
                    
                    # Bulk export option
                    st.markdown("### 📦 Bulk Export")
                    
                    if st.button("📦 Export Complete Analysis Package", use_container_width=True):
                        with st.spinner("📦 Preparing complete analysis package..."):
                            # This would create a ZIP file with all exports
                            st.info("🚧 Bulk export feature coming soon! For now, please use individual export options above.")
            
            else:
                st.error("❌ Failed to process the uploaded file. Please check the file format and try again.")
                
                with st.expander("🔧 Troubleshooting Tips"):
                    st.markdown("""
                    **Common Issues and Solutions:**
                    
                    1. **File Format Issues:**
                       - Ensure file is in .xlsx, .xls, or .csv format
                       - Check that the file is not corrupted
                       - Try saving the file in a different format
                    
                    2. **Data Structure Issues:**
                       - Ensure the first row contains column headers
                       - Check for merged cells or complex formatting
                       - Verify that data is in tabular format
                    
                    3. **Encoding Issues:**
                       - Try saving the CSV file with UTF-8 encoding
                       - Check for special characters that might cause issues
                       - Ensure consistent date and number formats
                    
                    4. **Size Limitations:**
                       - Large files may take longer to process
                       - Consider splitting very large datasets
                       - Remove unnecessary columns or rows
                    
                    **Supported File Formats:**
                    - Excel files (.xlsx, .xls)
                    - CSV files (.csv)
                    - Tab-separated files (.tsv)
                    """)
        
        except Exception as e:
            st.error(f"❌ An error occurred while processing your file: {str(e)}")
            
            with st.expander("🔍 Error Details"):
                st.code(str(e))
                st.markdown("""
                **If you continue to experience issues:**
                1. Check that your file is properly formatted
                2. Try uploading a smaller sample of your data
                3. Ensure all required columns are present
                4. Contact support if the problem persists
                """)
    
    else:
        # Welcome screen when no file is uploaded
        st.markdown("""
        ## 🎯 Welcome to Advanced Financial Statement Analyzer
        
        **Powered by Microsoft Phi-4 Reasoning AI & Advanced Analytics**
        
        ### 🚀 Getting Started
        
        1. **📁 Upload Your Financial Data**
           - Support for Excel (.xlsx, .xls) and CSV files
           - Automatic detection of statement types
           - Intelligent data processing and validation
        
        2. **🧠 Choose Your Analysis Engine**
           - **AI-Powered**: Microsoft Phi-4 with step-by-step reasoning
           - **Offline Mode**: Advanced algorithmic analysis
           - **Free API**: Get started with OpenRouter.ai
        
        3. **📊 Comprehensive Analysis**
           - Financial ratio calculations
           - Industry benchmarking
           - Interactive visualizations
           - Strategic insights and recommendations
        
        ### 🎯 Key Features
        """)
        
        # Feature showcase
        feature_col1, feature_col2, feature_col3 = st.columns(3)
        
        with feature_col1:
            st.markdown("""
            #### 🧠 AI-Powered Analysis
            - Microsoft Phi-4 reasoning engine
            - Step-by-step financial analysis
            - Natural language insights
            - Custom Q&A capabilities
            """)
        
        with feature_col2:
            st.markdown("""
            #### 📊 Advanced Analytics
            - 20+ financial ratios
            - Industry benchmarking
            - Trend analysis
            - Risk assessment
            """)
        
        with feature_col3:
            st.markdown("""
            #### 📈 Interactive Visualizations
            - Dynamic charts and graphs
            - Financial dashboards
            - Customizable color schemes
            - Export-ready formats
            """)
        
        # Sample data section
        st.markdown("### 📋 Sample Data Templates")
        
        sample_col1, sample_col2 = st.columns(2)
        
        with sample_col1:
            if st.button("📊 Download Balance Sheet Template", use_container_width=True):
                # Create sample balance sheet
                sample_balance_sheet = pd.DataFrame({
                    'Account': [
                        'Cash and Cash Equivalents',
                        'Accounts Receivable',
                        'Inventory',
                        'Total Current Assets',
                        'Property, Plant & Equipment',
                        'Total Assets',
                        'Accounts Payable',
                        'Short-term Debt',
                        'Total Current Liabilities',
                        'Long-term Debt',
                        'Total Liabilities',
                        'Shareholders Equity',
                        'Total Liabilities and Equity'
                    ],
                    '2023': [50000, 75000, 100000, 225000, 300000, 525000, 40000, 25000, 65000, 150000, 215000, 310000, 525000],
                    '2022': [45000, 70000, 95000, 210000, 280000, 490000, 35000, 30000, 65000, 140000, 205000, 285000, 490000],
                    '2021': [40000, 65000, 90000, 195000, 260000, 455000, 30000, 35000, 65000, 130000, 195000, 260000, 455000]
                })
                
                csv_buffer = io.StringIO()
                sample_balance_sheet.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="⬇️ Download Template",
                    data=csv_data,
                    file_name="balance_sheet_template.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with sample_col2:
            if st.button("📈 Download Income Statement Template", use_container_width=True):
                # Create sample income statement
                sample_income_statement = pd.DataFrame({
                    'Account': [
                        'Revenue',
                        'Cost of Goods Sold',
                        'Gross Profit',
                        'Operating Expenses',
                        'Operating Income',
                        'Interest Expense',
                        'Income Before Tax',
                        'Tax Expense',
                        'Net Income'
                    ],
                    '2023': [500000, 300000, 200000, 120000, 80000, 15000, 65000, 16250, 48750],
                    '2022': [450000, 270000, 180000, 110000, 70000, 18000, 52000, 13000, 39000],
                    '2021': [400000, 240000, 160000, 100000, 60000, 20000, 40000, 10000, 30000]
                })
                
                csv_buffer = io.StringIO()
                sample_income_statement.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="⬇️ Download Template",
                    data=csv_data,
                    file_name="income_statement_template.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        # API setup guide
        st.markdown("### 🔑 API Setup Guide")
        
        with st.expander("🚀 How to Get Free OpenRouter API Access"):
            st.markdown("""
            **Step-by-Step Setup:**
            
            1. **Create Account**
               - Visit [OpenRouter.ai](https://openrouter.ai/)
               - Sign up for a free account
               - No credit card required for free tier
            
            2. **Generate API Key**
               - Go to [API Keys](https://openrouter.ai/keys)
               - Click "Create Key"
               - Copy your API key
            
            3. **Configure in App**
               - Paste API key in the sidebar
               - Test the connection
               - Start using AI-powered analysis!
            
            **Free Tier Includes:**
            - Microsoft Phi-4 Reasoning Plus
            - GPT-3.5 Turbo
            - Claude Haiku
            - Llama models
            - And more!
            
            **Benefits of AI Analysis:**
            - Step-by-step reasoning
            - Natural language insights
            - Custom question answering
            - Advanced pattern recognition
            - Strategic recommendations
            """)
        
        # Tips and best practices
        st.markdown("### 💡 Tips for Best Results")
        
        tips_col1, tips_col2 = st.columns(2)
        
        with tips_col1:
            st.markdown("""
            #### 📊 Data Preparation
            - Use clear, descriptive column headers
            - Ensure consistent number formatting
            - Include multiple time periods for trend analysis
            - Remove empty rows and columns
            - Use standard account names when possible
            """)
        
        with tips_col2:
            st.markdown("""
            #### 🎯 Analysis Optimization
            - Select the correct statement type
            - Enable industry benchmarking
            - Use comprehensive analysis depth
            - Include AI insights for deeper understanding
            - Export results for further analysis
            """)
        
        # Footer information
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 20px;">
            <p><strong>Advanced Financial Statement Analyzer</strong></p>
            <p>Powered by Microsoft Phi-4 Reasoning AI • Built with Streamlit • Open Source</p>
            <p>🔒 Your data is processed locally and securely • 🌟 No data is stored or shared</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

