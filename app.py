import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import pandas as pd
import os

# Set up Streamlit page configuration
st.set_page_config(page_title="Smart Study Calendar", page_icon="📅", layout="wide")

# Fetch API Key from Streamlit Secrets or environment
def get_api_key():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        try:
            api_key = st.secrets['GEMINI_API_KEY']
        except Exception as e:
            st.error("❌ API Key not found.")
            return None
    return api_key

# Function to generate AI suggestion using Gemini API
def get_ai_suggestion(user_input, api_key):
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

# Define course details
courses = {
    "Electrical Distribution": {"lectures": 19, "time_per_lecture": 2.25},  # Average 2.25 hours
    "Revit": {"lectures": 8, "time_per_lecture": 2.25},
    "Shop Drawing": {"lectures": 6, "time_per_lecture": 2.25},
}

# Calculate total time for each course
total_time = {course: details["lectures"] * details["time_per_lecture"] for course, details in courses.items()}

# Total time required
total_study_time = sum(total_time.values())

# Days available for study (45 days, excluding Fridays)
study_days = 45 - 9  # Exclude Fridays (9 days)
time_per_day = total_study_time / study_days

# Create study schedule
study_schedule = []
current_date = datetime.today()

for i in range(study_days):
    day_schedule = {}
    day_schedule["Date"] = current_date.strftime("%Y-%m-%d")
    day_schedule["Topic"] = None  # Will be filled dynamically
    day_schedule["AI_Tips"] = None  # Will be filled dynamically
    study_schedule.append(day_schedule)
    current_date += timedelta(days=1)

# Display the calendar table
st.title("📅 Smart Study Calendar")
st.subheader("Your Study Plan for the Next 45 Days")
st.write(f"Total study time: {total_study_time:.2f} hours. Study time per day: {time_per_day:.2f} hours.")

# Table to display the daily tasks
study_df = pd.DataFrame(study_schedule)

# Function to distribute topics and study time across days
def assign_tasks():
    topic_order = ["Electrical Distribution", "Revit", "Shop Drawing"]
    remaining_time = time_per_day
    
    for idx, row in study_df.iterrows():
        topic = topic_order[idx % len(topic_order)]
        study_df.at[idx, "Topic"] = topic
        study_df.at[idx, "AI_Tips"] = get_ai_suggestion(f"Explain the topic of {topic}", api_key)
        remaining_time -= courses[topic]["time_per_lecture"]
        if remaining_time <= 0:
            remaining_time = time_per_day  # Reset for next day

assign_tasks()

# Show the schedule with AI tips
st.dataframe(study_df)

# Extra features: Allow users to input any question about their calendar
user_query = st.text_input("Ask your smart assistant about today's study task or any question:")
if user_query:
    ai_response = get_ai_suggestion(user_query, get_api_key())
    st.info(f"AI Response: {ai_response}")

