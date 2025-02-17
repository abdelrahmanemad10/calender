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

# Set up Streamlit
st.title("📅 Smart Calendar with AI")
st.write("Plan your tasks efficiently with AI-powered suggestions!")

# Authenticate Google Gemini API
API_KEY = os.getenv("AIzaSyDh5of7uhi5vnYkOlKHLMOcAw15YfGzgVo")  # Use environment variable for security
if not API_KEY:
    st.error("❌ Missing Gemini API key! Please set the GEMINI_API_KEY environment variable.")
    st.stop()

genai.configure(api_key=API_KEY)

def suggest_event(user_input):
    """Use Gemini AI to suggest an event based on user input."""
    model = genai.GenerativeModel("gemini-pro")  # Choose Gemini model
    response = model.generate_content(f"Suggest an event for: {user_input}")
    return response.candidates[0].content if response.candidates else "No suggestion available."

# Authenticate and initialize Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'service-account.json'  # Update this path

try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
except Exception as e:
    st.error(f"❌ Google Calendar API authentication failed: {e}")
    st.stop()

# Connect to SQLite database
conn = sqlite3.connect('calendar.db', check_same_thread=False)
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS events
             (id INTEGER PRIMARY KEY, task TEXT, start_date TEXT, end_date TEXT)''')
conn.commit()

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    st.error("❌ spaCy model not found. Run `python -m spacy download en_core_web_sm` to install it.")
    st.stop()

def extract_task_details(user_input):
    """Extract task details like date and time from user input."""
    doc = nlp(user_input)
    start_date, end_date = None, None
    
    for ent in doc.ents:
        if ent.label_ == "DATE":
            if not start_date:
                start_date = parse(ent.text, fuzzy=True)
            else:
                end_date = parse(ent.text, fuzzy=True)
    
    if not end_date:
        end_date = start_date
    
    return user_input, start_date, end_date

def generate_summary(events, period="day"):
    """Generate a summary of tasks for the specified period."""
    today = datetime.today()
    summary = []
    
    if period == "day":
        summary = [event for event in events if parse(event[2]).date() == today.date()]
    elif period == "week":
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        summary = [event for event in events if start_of_week.date() <= parse(event[2]).date() <= end_of_week.date()]
    
    return summary

# User input for tasks
user_input = st.text_input("Enter your task:")
if user_input:
    task, start_date, end_date = extract_task_details(user_input)
    if start_date:
        st.write(f"**Task:** {task}")
        st.write(f"**Start Date:** {start_date.strftime('%Y-%m-%d')}")
        st.write(f"**End Date:** {end_date.strftime('%Y-%m-%d')}")
        suggestion = suggest_event(user_input)
        st.write(f"💡 **AI Suggestion:** {suggestion}")
    else:
        st.warning("⚠️ Could not extract a valid date. Please enter a specific date in your task description.")

# Add event to database & Google Calendar
if st.button('Add Event'):
    if user_input and start_date and end_date:
        c.execute("INSERT INTO events (task, start_date, end_date) VALUES (?, ?, ?)",
                  (user_input, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        conn.commit()
        
        # Add event to Google Calendar
        event = {
            'summary': user_input,
            'start': {'date': start_date.strftime("%Y-%m-%d")},
            'end': {'date': end_date.strftime("%Y-%m-%d")},
        }
        service.events().insert(calendarId='primary', body=event).execute()
        st.success(f"✅ Event '{user_input}' added successfully!")

# Display stored events
st.subheader("📌 Your Events")
c.execute("SELECT * FROM events")
rows = c.fetchall()
if rows:
    for row in rows:
        st.write(f"📅 **{row[1]}** | {row[2]} → {row[3]}")
else:
    st.write("No events added yet.")

# Visualization
df = pd.DataFrame(rows, columns=['ID', 'Task', 'Start', 'End'])
if not df.empty:
    fig = px.timeline(df, x_start="Start", x_end="End", y="Task", title="Your Schedule")
    st.plotly_chart(fig)

# Generate summaries
daily_summary = generate_summary(rows, period="day")
st.write("**Daily Summary:**")
for event in daily_summary:
    st.write(f"✅ {event[1]} - {event[2]}")

weekly_summary = generate_summary(rows, period="week")
st.write("**Weekly Summary:**")
for event in weekly_summary:
    st.write(f"📌 {event[1]} - {event[2]}")

# Close database connection
conn.close()
