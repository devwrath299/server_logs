from flask import Flask, request, jsonify
import os
import vertexai
from vertexai.generative_models import GenerativeModel

app = Flask(__name__)

# Set up your Google PaLM API key via environment variable for security
os.environ["GOOGLE_API_KEY"] = "your-google-api-key"

# Initialize Vertex AI with the project ID and location
PROJECT_ID = "hackathon-hack-street-boys"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Function to analyze logs using Google Gemini 1.5
def analyze_logs_with_llm(logs):
    if not logs:
        return ["No logs provided"]

    # Create the prompt for log classification
    prompt = "Classify the following logs as either from a bot, a parser, or a legitimate user:\n"
    
    # Generate the prompt from logs
    for log in logs:
        prompt += f"IP: {log.get('ip', 'N/A')}, UserAgent: {log.get('user_agent', 'N/A')}, Referrer: {log.get('referrer', 'N/A')}, RequestPath: {log.get('request_path', 'N/A')}, Timestamp: {log.get('timestamp', 'N/A')}\n"
    
    prompt += """ 
We have server logs containing user activity, including requests from legitimate users, bots, and parsers. Your task is to **only create a table in the final output** that highlights anomalies based on the patterns and behaviors identified. The logs include fields such as IP, User Agent, Referrer, Request Path, and Timestamp.

### User Behavior Patterns:
- **Legitimate Users:** Moderate request frequency, valid referrer data, and activity during both peak and off-peak hours.
- **Bot Characteristics:** Known bots often use specific or blank user agents, make frequent requests, and may lack referrer data. Bots typically operate at unusual times or from uncommon geographic locations.

### Anomalous Patterns:
- **Blank Referrers**: Requests with blank referrer fields could indicate bot activity.
- **Request Frequency Spikes**: Sudden surges in requests from a single IP or user agent should be flagged.
- **Unusual Geographic Regions**: Requests from uncommon regions, deviating from typical user behavior, might indicate anomalies.

### Logs Data Sample:
- **Classify each entry** into one of the following categories:
  - **Legitimate User**
  - **Bot**
  - **Parser**
  - **Anomaly** (if the behavior is suspicious but unclear)

**Only create a table in the final output** that highlights anomalies, with columns for:
  - IP Address
  - User Agent
  - Referrer
  - Request Frequency
  - Geographic Location
  - Classification (Bot, Parser, Legitimate User, Anomaly)
  - **Reason for the anomaly classification**
  
**High-Alert Anomalies:** Mark any critical or high-risk anomalies clearly, such as those indicating:
  - High request frequency in a short period.
  - Requests from highly unusual geographic locations.
  - Potential malicious or aggressive bot activity.

Highlight anomalies in bold or red text for easy identification, and use **red** or a special symbol (⚠️) to denote high-alert anomalies.

**Provide only the table as the final output.**
"""

    try:
        # Use the GenerativeModel from Vertex AI (Gemini 1
        model = GenerativeModel("gemini-1.5-flash-002")

        # Generate the response from the model using the prompt
        response = model.generate_content(prompt)

        # Return the text response from Gemini 1.5 as a list of strings
        return response.text.split("\n")
    
    except Exception as e:
        return [f"Error occurred while analyzing logs: {str(e)}"]

# Endpoint to analyze logs
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get logs from the request body
        logs = request.get_json()

        # Call the function to classify the logs
        classifications = analyze_logs_with_llm(logs)

        # Return the classification result as JSON
        return jsonify({"classifications": classifications}) # Wrap in a dictionary

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    # No need to call app.run() in cloud environments, but included for local testing
    app.run(debug=True)

