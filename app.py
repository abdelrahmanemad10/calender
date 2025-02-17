import streamlit as st  
import google.generativeai as genai  
import os  
import pandas as pd  
from datetime import datetime, timedelta  

# Configure logging  
import logging  
logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__)  

# Set up Streamlit page configuration  
st.set_page_config(  
    page_title="Smart Study Calendar",  
    page_icon="📅",  
    layout="wide"  
)  

# Secure API Key Handling  
def get_api_key():  
    """Retrieve API key securely"""  
    api_key = os.getenv('GEMINI_API_KEY')  
    if not api_key:  
        try:  
            api_key = st.secrets['GEMINI_API_KEY']  
        except Exception as e:  
            st.error("❌ API Key not found. Please configure in environment or Streamlit secrets.")  
            return None  
    return api_key  

# Enhanced Gemini AI Suggestion with Additional Features  
def get_ai_suggestion_enhanced(user_input, api_key):  
    """Generate enhanced AI event suggestion with additional features"""  
    try:  
        genai.configure(api_key=api_key)  
        model = genai.GenerativeModel("gemini-pro")  
        
        prompt = f"""  
        You are a smart study assistant.   
        Provide a detailed summary for the following task: {user_input}  
        
        Suggestion format:  
        - Summary of the task  
        - Key points to focus on  
        - Recommended study duration  
        - Suggested study method (e.g., notes, videos, etc.)  
        """  

        response = model.generate_content(prompt)  
        return response.text.strip()  
    except Exception as e:  
        logger.error(f"AI suggestion generation error: {e}")  
        return "Unable to generate AI suggestion at this moment."  

# Function to create study schedule  
def create_study_schedule(tasks, study_duration=45):  
    """Create a study schedule for the given tasks across the study duration."""  
    start_date = datetime.now()  
    schedule = []  
    
    for i, task in enumerate(tasks):  
        study_date = start_date + timedelta(days=(i * (study_duration // len(tasks))))  
        schedule.append({"task": task["المهمة"], "date": study_date.strftime('%Y-%m-%d'), "link": task["الرابط"]})  
        
    return schedule  

# Main Streamlit App with Enhanced Features  
def main():  
    st.title("📅 Smart Study Calendar with AI Assistance")  
    
    # Initialize key components  
    api_key = get_api_key()  
    
    if not api_key:  
        st.error("Critical setup errors. Please check configuration.")  
        return  

    # User Input Section  
    with st.form("study_schedule_input"):  
        tasks_input = st.text_area("Enter your study tasks and links (separate by commas)")  
        submit_button = st.form_submit_button("Generate Study Schedule")  

    if submit_button and tasks_input:  
        # Process tasks input  
        tasks_list = tasks_input.split(",")  
        tasks = [{"المهمة": task.strip(), "الرابط": "https://www.youtube.com/"} for task in tasks_list]  
        
        # Create study schedule  
        schedule = create_study_schedule(tasks)  
        
        # Generate AI Suggestions  
        for task in schedule:  
            ai_suggestion = get_ai_suggestion_enhanced(task["task"], api_key)  
            
            # Display Study Schedule and Suggestions  
            col1, col2 = st.columns(2)  
            with col1:  
                st.subheader(f"Task: {task['task']}")  
                st.write(f"**Study Date:** {task['date']}")  
                st.write(f"**Study Link:** [Click Here]({task['link']})")  
            
            with col2:  
                st.subheader("AI Suggestion")  
                st.info(ai_suggestion)  

if __name__ == "__main__":  
    main()  
