from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag
from vertexai.generative_models import GenerativeModel, Tool
from google.cloud.aiplatform_v1beta1.types import EncryptionSpec
import vertexai
import requests
import json

from .rag import SnykFAQRag
 


rag_store = SnykFAQRag(collection_name="csv_collection",chroma_dir="chroma_dir")

try:
    test = rag_store.collection.peek()
    is_empty = not test or len(test.get("ids",[])) == 0
except Exception:
    res = rag_store.collection.query(query_texts=["snyk"], n_results=1)
    is_empty = (len(res.get("documents",[[]])[0]) == 0)

if is_empty:
    print("Ingesting csv into chroma db")
    rag_store.read_csv("./agents/snyk_agent/synk_channel_questions.csv")

def snyk_rag_tool(query:str, top_k: int = 3):
    """
    Retrieves answers to questions about snyk

    Parameters:
    - query (str): The user query asking questions about snyk

    Returns:
    - answer to the user's query from the snyk RAG

    Use this tool when the user asks questions about snyk, how its used or any query regarding snyk
    """
    return rag_store.rag_query(query=query, top_k=top_k)

def fetch_project_details(project_name: str)-> str:
    """
    Retrieves the vulnerability details about a project that is scanned by snyk

    Parameters:
    - project_name (str): The Github repository project scanned by snyk

    Returns:
    - JSON service payload with snyk scan results

    Use this tool when the user provides a project name asks about scan results about the project or vulnerabilties about the project
    """

    url = f"https://api.snyk.io/rest/orgs?version=2024-10-15&name={project_name}"
    try:
        headers = {
            "Authorization": "XXXXX",
            "Content-Type": "application/json"
        }
        r = requests.get(url,timeout=20,headers=headers)
        r.raise_for_status()
        data = r.json()
        items = data.get("data",[])
        if not items:
            return json.dumps({"error":f"No details found for project {project_name}"})
        project_id = items[0].get("id")
        if project_id:
            proj_url = f"https://api.snyk.io/rest/orgs/{project_id}/issues?version=2024-10-15&status=open"
            p_headers = {
                "Authorization": "XXXXX",
                "Content-Type": "application/json"
            }
            r = requests.get(proj_url,timeout=20,headers=p_headers)
            r.raise_for_status()
            data = r.json()
            details = data.get("data",[])
            return json.dumps({"project_details":details}, ensure_ascii=False)

        else:
            return json.dumps({"error":f"No details found for project {project_name}"})      
         
    except Exception as e:
        return json.dumps({"error":str(e)})


snyk_agent = Agent(
    name="snyk_agent",
    model="gemini-2.0-flash-001",
    description="Answers questions about snyk",
    instruction="""
    If the query is not about Snyk route back to the coordinator to find the appropriate agent.
    You are a security agent specializing in answering questions regarding Snyk or getting project details or vulnerability details of a project.
    - When the user asks a question about Snyk, call the provided snyk_rag_tool to fetch relevant csv based context. Use that context to craft a helpful, concise answer. If the context does not contain an answer, say 
    you could not find specific information.
    - When the user asks a question about a project and provides a project name, use the provided fetch_project_details to get details about the project and use the response to create a helpful concise answer. If
    no project details were found from the fetch_project_details tool, respond saying no project details were found. Ensure the response is detailed with a list of vulnerabilities with a section for each severity, ensure all vulnerability
    details are mentioned including the CVE ID when available. Provide a well structured reply with good detail that is easy to read with proper sections.
    """,
    tools=[snyk_rag_tool,fetch_project_details]
    )