import time
from google.cloud import aiplatform

# Initialize the Vertex AI SDK
aiplatform.init(project="df-es-test", location="us-central1")

# Create an endpoint
endpoint = aiplatform.Endpoint(
    "https://us-central1-dialogflow.googleapis.com/v3/projects/df-es-test/locations/us-central1/agents/212ffc6c-12fd-4694-b22b-0d0622c5593a"
)

# Define the query
query = "What is the capital of France?"

# Function to send a query and measure response time
def query_agent(query):
    start_time = time.time()
    response = endpoint.predict(instances=[{"query": query}])
    end_time = time.time()
    return response, end_time - start_time

# Send the query and get the response
response, response_time = query_agent(query)

# Analyze response accuracy
correct_answer = "Paris"
if response.predictions[0]["text"] == correct_answer:
    print("Correct answer!")
else:
    print("Incorrect answer.")
    print("Actual response:", response.predictions[0]["text"])

print(f"Response time: {response_time:.4f} seconds")