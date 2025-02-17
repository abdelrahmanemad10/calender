import streamlit as st  
import google.generativeai as genai  
import google.auth  
from google.auth.transport.requests import Request  
from google.oauth2 import service_account  
import googleapiclient.discovery  
import plotly.express as px  
import pandas as pd  
import sqlite3  
from datetime import datetime, timedelta  
import spacy  
from dateutil.parser import parse  
import os  
import logging  

# Configure logging  
logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__)  

# Set up Streamlit page configuration  
st.set_page_config(  
    page_title="Smart Calendar AI",  
    page_icon="📅",  
    layout="wide"  
)  

# Secure API Key Handling  
def get_api_key():  
    """Retrieve API key securely"""  
    # Prioritize environment variable  
    api_key = os.getenv('GEMINI_API_KEY')  
    
    # Fallback to Streamlit secrets  
    if not api_key:  
        try:  
            api_key = st.secrets['GEMINI_API_KEY']  
        except Exception as e:  
            st.error("❌ API Key not found. Please configure in environment or Streamlit secrets.")  
            return None  
    
    return api_key  

# Robust SpaCy Model Loading  
@st.cache_resource  
def load_spacy_model():  
    """Load spaCy model with error handling"""  
    try:  
        nlp = spacy.load("en_core_web_sm")  
        return nlp  
    except OSError:  
        st.error("SpaCy model not found. Please install using 'python -m spacy download en_core_web_sm'")  
        return None  

# Enhanced Date Extraction  
def extract_advanced_dates(user_input, nlp):  
    """Advanced date extraction with multiple fallback methods"""  
    try:  
        # Try spaCy extraction  
        if nlp:  
            doc = nlp(user_input)  
            date_entities = [ent for ent in doc.ents if ent.label_ == "DATE"]  
            
            if date_entities:  
                try:  
                    start_date = parse(date_entities[0].text, fuzzy=True)  
                    end_date = parse(date_entities[-1].text, fuzzy=True) if len(date_entities) > 1 else start_date  
                    return start_date, end_date  
                except:  
                    pass  
        
        # Fallback to dateutil parsing  
        from dateutil.parser import parse  
        
        # Try parsing entire input  
        try:  
            parsed_date = parse(user_input, fuzzy=True)  
            return parsed_date, parsed_date + timedelta(days=1)  
        except:  
            # Last resort: use today's date  
            today = datetime.now()  
            return today, today + timedelta(days=1)  
    
    except Exception as e:  
        logger.error(f"Date extraction error: {e}")  
        return None, None  

# Gemini AI Suggestion with Error Handling  
def get_ai_suggestion(user_input, api_key):  
    """Generate AI event suggestion with robust error handling"""  
    try:  
        genai.configure(api_key=api_key)  
        model = genai.GenerativeModel("gemini-pro")  
        
        prompt = f"""  
        You are a smart calendar assistant.   
        Provide a concise, practical suggestion for the event described: {user_input}  
        
        Suggestion format:  
        - Brief event description  
        - Potential duration  
        - Any preparation tips  
        """  
        
        response = model.generate_content(prompt)  
        return response.text.strip()  
    
    except Exception as e:  
        logger.error(f"AI suggestion generation error: {e}")  
        return "Unable to generate AI suggestion at this moment."  

# Main Streamlit App  
def main():  
    st.title("📅 Smart Calendar with AI Assistance")  
    
    # Initialize key components  
    api_key = get_api_key()  
    nlp = load_spacy_model()  
    
    if not api_key or not nlp:  
        st.error("Critical setup errors. Please check configuration.")  
        return  
    
    # User Input Section  
    with st.form("event_input"):  
        user_input = st.text_input("Describe your event or task")  
        submit_button = st.form_submit_button("Process Event")  
    
    if submit_button and user_input:  
        # Extract dates  
        start_date, end_date = extract_advanced_dates(user_input, nlp)  
        
        if start_date:  
            # Generate AI Suggestion  
            ai_suggestion = get_ai_suggestion(user_input, api_key)  
            
            # Display Results  
            col1, col2 = st.columns(2)  
            
            with col1:  
                st.subheader("Event Details")  
                st.write(f"**Task:** {user_input}")  
                st.write(f"**Start Date:** {start_date.strftime('%Y-%m-%d')}")  
                st.write(f"**End Date:** {end_date.strftime('%Y-%m-%d')}")  
            
            with col2:  
                st.subheader("AI Suggestion")  
                st.info(ai_suggestion)  
        else:  
            st.warning("Could not extract a valid date from the input.")  

    # Additional features can be added here  

if __name__ == "__main__":  
    main()
