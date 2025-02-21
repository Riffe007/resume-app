import os
import time
import json
from openai import AzureOpenAI

# ✅ Load environment variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")  # ✅ Consistent naming
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

# ✅ Ensure required credentials are set
missing_vars = [var for var in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_KEY", "VECTOR_STORE_ID"] if not globals()[var]]
if missing_vars:
    raise ValueError(f"❌ Missing required environment variables: {', '.join(missing_vars)}")

# ✅ Initialize OpenAI Client
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,  # ✅ Using AZURE_OPENAI_KEY
    api_version="2024-05-01-preview"
)

# ✅ Create Assistant with function calling & file search
assistant = client.beta.assistants.create(
    model="gpt-4o-2024-08-06-gpt-4o-resume-gen-v1",  # Replace with your fine-tuned model name
    name="Intelligent Career Assistant",
    instructions="""
    You are an AI-powered resume generator. Your task is to create **ATS-friendly, professionally formatted resumes** based on job descriptions and applicant details.

    **Key Features:**
    - **Retrieve** relevant experience from the vector store.
    - **Extract** important skills and qualifications from job descriptions.
    - **Format** resumes using **clear sections** (Summary, Skills, Experience, Education).
    - **Ensure ATS Optimization** (use industry keywords, bullet points, and clean structure).
    
    **Guidelines:**
    - Always retrieve **relevant experience** first before generating content.
    - Keep descriptions concise, using **action verbs** and **industry terms**.
    - DO NOT generate fake information—only use retrieved content.
    """,
    tools=[{"type": "file_search"}],
    tool_resources={"file_search": {"vector_store_ids": [VECTOR_STORE_ID]}},
    temperature=0.38,
    top_p=0.88
)

print(f"✅ Assistant created successfully: {assistant.id}")

# ✅ Create a new thread
thread = client.beta.threads.create()
print(f"✅ Thread created: {thread.id}")

# ✅ Send Message to the Assistant
job_description = "Senior AI Engineer with expertise in machine learning, cloud computing, and NLP."
applicant_details = "Timothy Riffe, AI/ML Engineer with 14+ years experience in AI, Finance, and Government Contracting."

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=f"""
    👤 **Applicant Details:**
    {applicant_details}

    📝 **Job Description:**
    {job_description}

    🔎 **Use the file_search tool to find relevant experience.**
    """
)

print(f"✅ Message sent to Assistant: {message.id}")

# ✅ Run the Assistant
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)

# ✅ Function: Retrieve relevant experience from vector store
def retrieve_relevant_experience(job_description):
    """Queries vector store for relevant experience using vector search."""
    search_payload = {
        "query": job_description,
        "top_k": 5
    }
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }
    
    search_url = f"{AZURE_OPENAI_ENDPOINT}/vectorstores/{VECTOR_STORE_ID}/search"

    try:
        response = client.session.post(search_url, headers=headers, json=search_payload)
        response_data = response.json()
        return "\n".join([match["text"] for match in response_data.get("matches", [])])
    except Exception as e:
        print(f"❌ Error retrieving experience: {str(e)}")
        return ""

# ✅ Loop until completion
while run.status in ['queued', 'in_progress']:
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

# ✅ Handle Assistant's Response
if run.status == 'completed':
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print("📝 Assistant Response:", messages[0]["content"])

elif run.status == 'requires_action':
    print("⚠️ Assistant requires function execution.")

    # ✅ Execute required functions
    if "tool_calls" in run.required_action:
        for action in run.required_action["tool_calls"]:
            function_name = action["name"]
            function_arguments = action["arguments"]

            if function_name == "retrieve_relevant_experience":
                print("🔍 Retrieving relevant experience...")
                
                # ✅ Retrieve and send back the experience
                relevant_experience = retrieve_relevant_experience(function_arguments["job_description"])
                client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="function",
                    content=json.dumps({"retrieved_experience": relevant_experience})
                )
                print("✅ Experience sent back to Assistant.")

        # ✅ Run Assistant Again After Function Execution
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)

else:
    print(f"❌ Assistant failed with status: {run.status}")
