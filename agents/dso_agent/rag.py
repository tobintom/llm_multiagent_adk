import os
from typing import List, Dict, Any, Optional
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import requests
from bs4 import BeautifulSoup
import tiktoken
from chromadb.utils import embedding_functions

CHROMA_DIR = os.path.join(os.path.dirname(__file__),"..","chroma_db")

class DSOFAQRag:
    def __init__(self,
                 collection_name: str = "dso_collection",
                 chroma_dir:Optional[str] = CHROMA_DIR,
                 embedding_model: str = "all-MiniLM-L6-v2",
                 persist:bool = True) -> None:
        
        self.model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

        settings = Settings(
            chroma_db_impl = "duckdb+parquet",
            persist_directory = os.path.abspath(chroma_dir) if persist else None
        )
        self.client = chromadb.PersistentClient(path=os.path.abspath(chroma_dir))

        def sbert_embed_fn(texts: List[str]) -> List[List[float]]:
            return [emb.toList() for emb in self.model.encode(texts, show_progress_bar=False)]
        
        # self.embed_fn = embedding_functions.EmbeddingFunction(
        #     sbert_embed_fn,
        #     embedding_dimensions=self.embedding_dim
        # )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
           # embedding_function=self.embed_fn
        )
    

    def embed_text(self, txt:str):
        embedding = self.model.encode(txt).tolist()
        return embedding
    
    def scrape_page(self, page: str) -> str:
        with open(page, "r", encoding="utf-8") as file:
                html_content = file.read()
                soup = BeautifulSoup(html_content, "html.parser")
                for script in soup(["script","style"]):
                    script.decompose()
                return soup.get_text(separator=" ", strip=True)
    
    def chun_text(self, txt:str, max_tokens: int = 300) -> list[str]:
        enc = tiktoken.get_encoding("cl100k_base")
        tokens = enc.encode(txt)
        chunks = []
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i+max_tokens]
            chunk_text = enc.decode(chunk_tokens)
            chunks.append(chunk_text)
        return chunks
    
    def embed_web_pages(self):
        pages = [("/path/to/site1.html","https://internal-site-url1"),
                  #| 
                  #|Multiple Downloaded Sites
                  #|
                 ("/path/to/site2.html","https://internal-site-url2")
                  
                ]
        for page in pages:
            text = self.scrape_page(page[0])
            chunks = self.chun_text(text)
            for i, chunk in enumerate(chunks):
                embedding = self.embed_text(chunk)
                self.collection.add(
                    ids=[f"{page[1]}-{i}"],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"source":page[1]}]
                )     

    def rag_query(self, query: str, top_k: int = 3) :

        query_emb = self.embed_text(query)
        results = self.collection.query(query_embeddings=[query_emb],n_results=top_k)
        docs = results["documents"][0]
        sources = [meta["source"] for meta in results["metadatas"][0]]
        return docs, sources

         
