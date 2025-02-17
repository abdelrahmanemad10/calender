import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta

# Configure Gemini API
genai.configure(api_key="YOUR_GEMINI_API_KEY")  # Replace with your Gemini API key

# Initialize Gemini model
model = genai.GenerativeModel('gemini-pro')

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

        # Generate daily goal and review using Gemini
        prompt = f"""
        Create a study plan for Day {day} for the course: {course}.
        - Include a clear goal for the day.
        - Add a review task to reinforce learning.
        - Provide a suggestion for better understanding (e.g., practical applications, tips).
        """
        response = model.generate_content(prompt)
        daily_plan = response.text

        # Add to schedule
        schedule.append({
            "Day": day,
            "Date": current_date.strftime("%Y-%m-%d"),
            "Course": course,
            "Plan": daily_plan
        })

        # Increment date
        current_date += timedelta(days=1)

    # Display Schedule
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
