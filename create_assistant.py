import os
import time
import json
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Load environment variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

# Ensure required credentials are set
if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY or not VECTOR_STORE_ID:
    raise ValueError("Missing required environment variables: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, or VECTOR_STORE_ID.")

# Initialize OpenAI Client
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-05-01-preview"
)

# Create Assistant with function calling & file search
assistant = client.beta.assistants.create(
    model="gpt-4o-2024-08-06-gpt-4o-resume-gen-v1",  # Replace with your fine-tuned model name
    name="Intelligent Career Assistant",
    instructions="You are an AI-powered resume generator. Generate ATS-friendly, professionally formatted resumes based on job descriptions and applicant details.",
    tools=[
        {"type": "file_search"},
        {"type": "function", "function": {
            "name": "generate_resume",
            "description": "Generate a tailored resume using the fine-tuned GPT model and vector store.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_description": {"type": "string", "description": "The job description provided by the user."},
                    "applicant_details": {"type": "string", "description": "Applicant's experience, skills, and details."}
                },
                "required": ["job_description", "applicant_details"]
            }
        }},
        {"type": "function", "function": {
            "name": "retrieve_relevant_experience",
            "description": "Retrieve relevant experience from the vector store for enhanced resume generation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_description": {"type": "string", "description": "Job description to search for relevant experience."}
                },
                "required": ["job_description"]
            }
        }}
    ],
    tool_resources={"file_search": {"vector_store_ids": [VECTOR_STORE_ID]}},
    temperature=0.38,
    top_p=0.88
)

print(f"✅ Assistant created successfully: {assistant.id}")

# Create a thread
thread = client.beta.threads.create()
print(f"✅ Thread created: {thread.id}")

# **Step 1: Retrieve relevant experience from the vector store**
def retrieve_relevant_experience(job_description):
    """Search vector store for relevant resume content."""
    try:
        search_results = client.beta.vector_stores.files.search(
            vector_store_id=VECTOR_STORE_ID,
            query=job_description,
            max_results=5
        )
        return "\n".join([doc["text"] for doc in search_results["data"]])
    except Exception as e:
        print(f"❌ Error retrieving experience: {str(e)}")
        return ""

# Sample job description & applicant details
job_description = "Senior AI Engineer with expertise in machine learning, cloud computing, and NLP."
applicant_details = "Timothy Riffe, AI/ML Engineer with 14+ years experience in AI, Finance, and Government Contracting."

retrieved_experience = retrieve_relevant_experience(job_description)

# **Step 2: Send Message to the Assistant**
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=f"Generate a resume for:\n\n👤 **Applicant Details:**\n{applicant_details}\n\n📝 **Job Description:**\n{job_description}\n\n📂 **Relevant Experience Retrieved:**\n{retrieved_experience}"
)

print(f"✅ Message sent to Assistant: {message.id}")

# **Step 3: Run the Assistant**
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)

# **Step 4: Loop until the run completes or requires function execution**
while run.status in ['queued', 'in_progress']:
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

# **Step 5: Process the Assistant's Response**
if run.status == 'completed':
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print("📝 Assistant Response:", messages)
elif run.status == 'requires_action':
    print("⚠️ Assistant requires function execution.")
    for required_function in run.required_action.get("function_call", []):
        function_name = required_function["name"]
        function_arguments = required_function["arguments"]

        if function_name == "generate_resume":
            print("📄 Generating resume...")
            # Call the resume generation function (to be implemented)
        elif function_name == "retrieve_relevant_experience":
            print("🔍 Retrieving relevant experience...")
            # Call vector store search again if needed

else:
    print(f"❌ Assistant failed with status: {run.status}")
