import streamlit as st  
import google.generativeai as genai  
import os  
import logging  
import pandas as pd  
from datetime import datetime, timedelta

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

# Function to generate AI suggestion using Gemini API  
def get_ai_suggestion(user_input, api_key):  
    if not api_key:  
        st.error("API key is missing.")  
        return "API key is missing."
    
    try:  
        genai.configure(api_key=api_key)  
        model = genai.GenerativeModel("gemini-pro")  
        
        prompt = f"""  
        You are a study assistant. For the topic described below, provide a concise explanation and tips for better understanding:  
        {user_input}  
        
        Response format:  
        - Brief explanation  
        - Key points  
        - Study tips  
        """  
        
        response = model.generate_content(prompt)  
        return response.text.strip()  
    except Exception as e:  
        st.error(f"AI error: {e}")  
        return "Could not retrieve AI suggestion."  

# Function to assign tasks for 45 days  
def assign_tasks():  
    api_key = get_api_key()  
    if api_key is None:  
        st.error("⚠️ API Key not found. Please provide a valid API Key.")  
        return  

    # Define tasks and their estimated durations  
    tasks = {  
        "التوزيع الكهربائي": {"lectures": 19, "duration": 2.5},  
        "ريفيت": {"lectures": 8, "duration": 2.5},  
        "شوب دراوينج": {"lectures": 6, "duration": 2.5},  
    }  
    
    total_days = 45  
    study_plan = []  
    
    for task, details in tasks.items():  
        lectures = details["lectures"]  
        duration = details["duration"]  
        for i in range(lectures):  
            # Assign study day for each lecture  
            study_plan.append({"day": len(study_plan) + 1, "task": task, "lecture": i + 1, "duration": duration})  
    
    # Create a DataFrame  
    study_df = pd.DataFrame(study_plan)  
    
    # Add AI tips for each task  
    for idx, row in study_df.iterrows():  
        task = row["task"]  
        ai_tips = get_ai_suggestion(f"Explain the topic of {task}", api_key)  
        study_df.at[idx, "AI_Tips"] = ai_tips  
    
    # Display the study plan with AI suggestions  
    st.subheader("Study Plan for 45 Days")  
    st.dataframe(study_df)  

# Main Streamlit App with Enhanced Features  
def main():  
    st.title("📅 Smart Calendar with AI Assistance")  
    
    # Initialize key components  
    api_key = get_api_key()  
    
    if not api_key:  
        st.error("Critical setup errors. Please check configuration.")  
        return  
    
    # Assign tasks  
    assign_tasks()

if __name__ == "__main__":  
    main()  
