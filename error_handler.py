import streamlit as st
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_errors(func):
    """Decorator to handle errors gracefully in Streamlit"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in {func.__name__}: {error_msg}")
            logger.error(traceback.format_exc())
            
            st.error(f"❌ An error occurred: {error_msg}")
            
            with st.expander("🔍 Error Details (for debugging)"):
                st.code(traceback.format_exc())
            
            st.info("💡 Try refreshing the page or uploading a different file.")
            return None
    
    return wrapper

def safe_execute(func, *args, **kwargs):
    """Safely execute a function and handle errors"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def validate_data(data):
    """Validate uploaded data"""
    if data is None:
        return False, "No data provided"
    
    if data.empty:
        return False, "Data is empty"
    
    if len(data.columns) == 0:
        return False, "No columns found"
    
    return True, "Data is valid"

def safe_numeric_operation(operation, *args):
    """Safely perform numeric operations"""
    try:
        result = operation(*args)
        if result is None or (hasattr(result, '__len__') and len(result) == 0):
            return None
        return result
    except (ZeroDivisionError, ValueError, TypeError) as e:
        st.warning(f"Numeric operation failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error in numeric operation: {str(e)}")
        return None
