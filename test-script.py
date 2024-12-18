import subprocess
import json
import tempfile
import csv
from datetime import datetime
import argparse

def get_access_token():
    """Get the access token using gcloud."""
    result = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
    return result.stdout.strip()

def query_agent(url, query_text):
    """Send a query to the Vertex AI agent and return the response."""
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "x-goog-user-project": "df-es-test",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    payload = {
         "debugMode": True,
        "queryInput": {
            "text": {
                "text": query_text
            },
            "languageCode": "en"
        },
        "queryParams": {
             "llmModelSettings": {
            "model": "gemini-pro"
        },
        "playbookStateOverride": {
            "currentSessionTrace": {
                "actions": [],
                "name": "projects/df-es-test/locations/us-central1/agents/212ffc6c-12fd-4694-b22b-0d0622c5593a/playbooks/00000000-0000-0000-0000-000000000000/examples/-"
            }
        }
        }
        
    }

    
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        json.dump(payload, temp_file)
        temp_file_name = temp_file.name
    
    curl_command = [
        "curl", "-X", "POST",
        "-H", f"Authorization: Bearer {get_access_token()}",
        "-H", "x-goog-user-project: df-es-test",
        "-H", "Content-Type: application/json; charset=utf-8",
        "-d", f"@{temp_file_name}",
        url
    ]
    
    result = subprocess.run(curl_command, capture_output=True, text=True)
    
    # Clean up the temporary file
    subprocess.run(["rm", temp_file_name])
    
    return json.loads(result.stdout)

def format_response(response,query):
    """Extract and format relevant information from the response."""
    query_result = response.get('queryResult', {})
    
    formatted_response = {
        "Query": query,
        "Response": query_result.get('responseMessages', [{}])[0].get('text', {}).get('text', ['N/A'])[0],
        "Intent Detection Confidence": query_result.get('intentDetectionConfidence', 'N/A'),
        "Match Type": query_result.get('match', {}).get('matchType', 'N/A'),
        "Confidence": query_result.get('match', {}).get('confidence', 'N/A')
    }
    
    return formatted_response

def read_queries_from_file(file_path):
    """Read queries from a file, one query per line."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def main():

    # Read queries from the input file
    queries = read_queries_from_file('queries-1.txt')
    # Create a CSV file with a timestamp in the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"agent_responses_{timestamp}.csv"
    url = "https://us-central1-dialogflow.googleapis.com/v3/projects/df-es-test/locations/us-central1/agents/212ffc6c-12fd-4694-b22b-0d0622c5593a/sessions/session-2:detectIntent"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Query", "Response", "Intent Detection Confidence", "Match Type", "Confidence"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for query in queries:
            print(f"\nProcessing query: {query}")
            response = query_agent(url, query)
            print(response)
            #return
            formatted = format_response(response,query)
            
            writer.writerow(formatted)
            
            print("Response written to CSV.")
        
    print(f"\nAll responses have been written to {csv_filename}")

if __name__ == "__main__":
    main()