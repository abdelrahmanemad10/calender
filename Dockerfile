FROM python:3.10-slim  

WORKDIR /app  

# Install system dependencies  
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*  

# Copy requirements and install Python dependencies  
COPY requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt  

# Download spaCy model during build  
RUN python -m spacy download en_core_web_sm  

# Copy application code  
COPY . .  

# Expose port and set entrypoint  
EXPOSE 8501  

ENTRYPOINT ["streamlit", "run", "app.py"]
