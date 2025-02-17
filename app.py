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

# Set up Streamlit
st.title("📅 Smart Calendar with AI")
st.write("Plan your tasks efficiently with AI-powered suggestions!")

# Authenticate Google Gemini API
genai.configure(api_key="AIzaSyDh5of7uhi5vnYkOlKHLMOcAw15YfGzgVo")  # Replace with your Gemini API key

def suggest_event(user_input):
    """Use Gemini AI to suggest an event based on user input."""
    model = genai.GenerativeModel("gemini-pro")  # Choose Gemini model
    response = model.generate_content(f"Suggest an event for: {user_input}")
    return response.text

# Authenticate and initialize Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'service-account.json'  # Update this path

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

# Connect to SQLite database
conn = sqlite3.connect('calendar.db', check_same_thread=False)
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS events
             (id INTEGER PRIMARY KEY, task TEXT, start_date TEXT, end_date TEXT)''')
conn.commit()

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_task_details(user_input):
    """Extract task details like date and time from user input."""
    doc = nlp(user_input)
    task = user_input
    start_date = None
    end_date = None
    
    for ent in doc.ents:
        if ent.label_ == "DATE":
            if not start_date:
                start_date = parse(ent.text, fuzzy=True)
            else:
                end_date = parse(ent.text, fuzzy=True)
    
    if not end_date:
        end_date = start_date
    
    return task, start_date, end_date

def prioritize_tasks(tasks):
    """Prioritize tasks based on their importance and deadlines."""
    # Simple rule-based prioritization
    tasks.sort(key=lambda x: (x['end_date'], x['importance']), reverse=True)
    return tasks

def detect_conflicts(events, new_event):
    """Detect conflicts between existing events and a new event."""
    for event in events:
        if (new_event['start_date'] <= event['end_date'] and new_event['end_date'] >= event['start_date']):
            return True
    return False

def suggest_alternative_time(events, new_event):
    """Suggest alternative time slots for a new event."""
    alternative_start = new_event['start_date']
    alternative_end = new_event['end_date']
    
    while detect_conflicts(events, {"start_date": alternative_start, "end_date": alternative_end}):
        alternative_start += timedelta(days=1)
        alternative_end += timedelta(days=1)
    
    return alternative_start, alternative_end

def generate_summary(events, period="day"):
    """Generate a summary of tasks for the specified period."""
    today = datetime.today()
    if period == "day":
        summary = [event for event in events if event['start_date'].date() == today.date()]
    elif period == "week":
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        summary = [event for event in events if start_of_week <= event['start_date'] <= end_of_week]
    return summary

# User input for tasks
user_input = st.text_input("Enter your task:")
if user_input:
    task, start_date, end_date = extract_task_details(user_input)
    st.write(f"Task: {task}")
    st.write(f"Start Date: {start_date}")
    st.write(f"End Date: {end_date}")
    
    suggestion = suggest_event(user_input)
    st.write(f"💡 AI Suggestion: {suggestion}")

# Add event to database & Google Calendar
if st.button('Add Event'):
    if user_input and start_date and end_date:
        # Store event in SQLite
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

# Generate daily and weekly summaries
daily_summary = generate_summary(rows, period="day")
st.write("Daily Summary:")
for event in daily_summary:
    st.write(event)

weekly_summary = generate_summary(rows, period="week")
st.write("Weekly Summary:")
for event in weekly_summary:
    st.write(event)
