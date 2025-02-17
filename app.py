import streamlit as st
import google.generativeai as genai
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import googleapiclient.discovery
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime

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
SERVICE_ACCOUNT_FILE = 'service-account.json'

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

# User input for tasks
user_input = st.text_input("Enter your task:")
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

if user_input:
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
