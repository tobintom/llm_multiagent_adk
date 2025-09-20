from google.adk.agents import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag
from vertexai.generative_models import GenerativeModel, Tool
from google.cloud.aiplatform_v1beta1.types import EncryptionSpec
import vertexai

from .rag import JFrogFAQRag

 

rag_store = JFrogFAQRag(collection_name="jfrog_collection",chroma_dir="chroma_dir")

try:
    test = rag_store.collection.peek()
    is_empty = not test or len(test.get("ids",[])) == 0
except Exception:
    res = rag_store.collection.query(query_texts=["jfrog"], n_results=1)
    is_empty = (len(res.get("documents",[[]])[0]) == 0)

if is_empty:
    print("Ingesting jfrog into chroma db")
    rag_store.embed_web_pages()

def jfrog_rag_tool(query:str, top_k: int = 3):
    docs, sources = rag_store.rag_query(query=query, top_k=top_k)
    combined = " | ".join(docs)
    refs = " , ".join(set(sources))

    return f"Answer candidates: {combined}\n (Sources: {refs})"

 

jfrog_agent = Agent(
    name="jfrog_agent",
    model="gemini-2.0-flash-001",
    description="Answers questions about jfrog from web pages",
    instruction="""
    If the query is not about Jfrog, third party libraries or container images, route back to the coordinator to find the appropriate agent.
    You are a security agent specializing in answering questions regarding JFrog which is the artifactory used, access to JFROG, best practices with jfrog and third party library and container scanning and uploading to jfrog. When the user asks a question, call the provided jfrog_rag_tool
    to fetch relevant jfrog based context. Use that context to craft a helpful, concise answer. Also include the url of the source page as reference for the user to check for more information.
    """,
    tools=[jfrog_rag_tool]
    )