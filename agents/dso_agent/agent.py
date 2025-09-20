from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag
from vertexai.generative_models import GenerativeModel, Tool
from google.cloud.aiplatform_v1beta1.types import EncryptionSpec
import vertexai

from .rag import DSOFAQRag

rag_store = DSOFAQRag(collection_name="dso_collection",chroma_dir="chroma_dir")

try:
    test = rag_store.collection.peek()
    is_empty = not test or len(test.get("ids",[])) == 0
except Exception:
    res = rag_store.collection.query(query_texts=["wiz"], n_results=1)
    is_empty = (len(res.get("documents",[[]])[0]) == 0)    

if is_empty:
    print("Ingesting dso into chroma db")
    rag_store.embed_web_pages()

def dso_rag_tool(query:str, top_k: int = 3):
    docs, sources = rag_store.rag_query(query=query, top_k=top_k)
    combined = " | ".join(docs)
    refs = " , ".join(set(sources))

    return f"Answer candidates: {combined}\n (Sources: {refs})"

 

dso_agent = Agent(
    name="dso_agent",
    model="gemini-2.0-flash-001",
    description="Answers security questions about from web pages",
    instruction="""
    If the query cannot be answered, route back to the coordinator to find the appropriate agent.
    You are a security agent specializing in answering questions regarding security, standards, runbooks, processes on requesting snyk exceptions,
    creating exceptions on remediation vulnerabilities, questions related to archer, custom application mappings, control standards, questions related to wiz,
    control standards and procedures.
    When the user asks a question, call the provided dso_rag_tool to fetch relevant context. Use that context to craft a detailed helpful, concise answer.
    Always include the url of the source page as reference for the user to check for more information.
    """,
    tools=[dso_rag_tool]
    )
