import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Streamlit page configuration
st.set_page_config(
    page_title="Smart Calendar with Gemini AI",
    page_icon="📅",
    layout="wide"
)

# Retrieve API key securely
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
def get_ai_suggestion(user_input, api_key):
    """Generate enhanced AI event suggestion with additional features"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        
        prompt = f"""
        You are a study mentor. Explain the following topic in detail and provide insights for better understanding:
        {user_input}
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        logger.error(f"AI suggestion generation error: {e}")
        return "Unable to generate AI suggestion at this moment."

# Study Plan Data
study_plan = [
    {"Topic": "Electrical Distribution Course - Lecture 1", "Duration": "2 hours", "Video Link": "https://www.youtube.com/watch?v=T0CqOBY9TiQ&list=PLxNbro6QtRYsFAcXhy9rXoE2y9mJ-iTu9"},
    {"Topic": "Electrical Distribution Course - Lecture 2", "Duration": "2 hours", "Video Link": "https://www.youtube.com/watch?v=T0CqOBY9TiQ&list=PLxNbro6QtRYsFAcXhy9rXoE2y9mJ-iTu9"},
    {"Topic": "Revit Course - Lecture 1", "Duration": "2.5 hours", "Video Link": "https://www.youtube.com/watch?v=h_w-Z_vFa4M&list=PLxNbro6QtRYv3fDvna8e6fJhOvtrnIlj8"},
    {"Topic": "Revit Course - Lecture 2", "Duration": "2.5 hours", "Video Link": "https://www.youtube.com/watch?v=h_w-Z_vFa4M&list=PLxNbro6QtRYv3fDvna8e6fJhOvtrnIlj8"},
    {"Topic": "Shop Drawing Course - Lecture 1", "Duration": "2.5 hours", "Video Link": "https://www.youtube.com/watch?v=h_w-Z_vFa4M&list=PLxNbro6QtRYv3fDvna8e6fJhOvtrnIlj8"},
    {"Topic": "Shop Drawing Course - Lecture 2", "Duration": "2.5 hours", "Video Link": "https://www.youtube.com/watch?v=h_w-Z_vFa4M&list=PLxNbro6QtRYv3fDvna8e6fJhOvtrnIlj8"}
]

# Display Table with Video Links and Course Topics
def display_study_plan():
    df = pd.DataFrame(study_plan)
    
    # Display table with clickable video links
    st.subheader("Study Plan with Video Links")
    st.dataframe(df)

# Process tasks with Gemini AI suggestions
def assign_ai_suggestions():
    api_key = get_api_key()
    if not api_key:
        st.error("API Key is missing. Please configure it to proceed.")
        return

    # Assigning AI suggestions for each task
    for idx, task in enumerate(study_plan):
        study_plan[idx]["AI_Tips"] = get_ai_suggestion(f"Explain the topic of {task['Topic']}", api_key)

# Main Streamlit App
def main():
    st.title("📅 Smart Study Plan with AI Assistance")
    
    # Display the study plan with course details
    display_study_plan()

    # Button to get AI suggestions for each task
    if st.button("Get AI Study Tips"):
        assign_ai_suggestions()

        # Display AI Tips for each task
        st.subheader("AI Tips for Each Topic")
        for task in study_plan:
            st.write(f"**{task['Topic']}**:")
            st.info(task["AI_Tips"])

if __name__ == "__main__":
    main()
