import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# DeepSeek API configuration
DEEPSEEK_API_KEY = "sk-25beabda581c4ad1860748026a587ac5"  # Replace with your DeepSeek API key
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # Replace with the actual API endpoint

# Streamlit App Title
st.title("📚 Personalized 45-Day Study Scheduler")
st.write("Generate a customized study schedule with daily goals, reviews, and AI suggestions!")

# User Inputs
st.sidebar.header("Input Your Study Preferences")
course_names = st.sidebar.text_input("Enter Course Names (comma-separated):", "Electrical Distribution, Revit, Shop Drawing")
start_date = st.sidebar.date_input("Select Start Date:", datetime.today())
study_hours_per_day = st.sidebar.number_input("Study Hours Per Day:", min_value=1, max_value=8, value=2)

# Parse course names
courses = [course.strip() for course in course_names.split(",")]

# Function to call DeepSeek API
def generate_with_deepseek(prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",  # Replace with the correct model name
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        st.error(f"Failed to call DeepSeek API: {response.status_code} - {response.text}")
        return None

# Generate Schedule Button
if st.sidebar.button("Generate Schedule"):
    st.sidebar.success("Generating your 45-day study schedule...")

    # Initialize schedule
    schedule = []
    current_date = start_date

    # Loop through 45 days
    for day in range(1, 46):
        # Select a course for the day (rotate through courses)
        course = courses[(day - 1) % len(courses)]

        # Generate daily goal and review using DeepSeek
        prompt = f"""
        Create a study plan for Day {day} for the course: {course}.
        - Include a clear goal for the day.
        - Add a review task to reinforce learning.
        - Provide a suggestion for better understanding (e.g., practical applications, tips).
        """
        daily_plan = generate_with_deepseek(prompt)
        if not daily_plan:
            break  # Stop if API call fails

        # Add to schedule
        schedule.append({
            "Day": day,
            "Date": current_date.strftime("%Y-%m-%d"),
            "Course": course,
            "Plan": daily_plan
        })

        # Add a delay to avoid rate limits
        time.sleep(2)  # Wait 2 seconds between requests

        # Increment date
        current_date += timedelta(days=1)

    # Display Schedule
    if schedule:
        st.header("Your 45-Day Study Schedule")
        for entry in schedule:
            st.subheader(f"Day {entry['Day']} ({entry['Date']}) - {entry['Course']}")
            st.write(entry["Plan"])
            st.markdown("---")

        # Download Schedule as CSV
        import pandas as pd
        df = pd.DataFrame(schedule)
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Schedule as CSV",
            data=csv,
            file_name="45_day_study_schedule.csv",
            mime="text/csv"
        )
