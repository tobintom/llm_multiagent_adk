import os
from typing import List, Dict, Any, Optional
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

CHROMA_DIR = os.path.join(os.path.dirname(__file__),"..","chroma_db")

class SnykFAQRag:
    def __init__(self,
                 collection_name: str = "csv_collection",
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
    

    def read_csv(self, csv_path: str, text_columns: Optional[List[str]] = None):
        print(os.getcwd())
        df = pd.read_csv(csv_path, dtype=str).fillna("")

        if text_columns is None:
            text_columns = [c for c in df.columns]
        docs = []
        metadatas = []
        ids = []
        
        for _, row in df.iterrows():
            doc_text = " | ".join([f"{col}: {row[col]}" for col in text_columns])
            docs.append(doc_text)
            row_meta = {col: row[col] for col in df.columns}            
            metadatas.append(row_meta)

        ids = [str(i) for i in range(len(docs))]
        self.collection.add(
            ids = ids,
            documents=docs,
            metadatas=metadatas
        )

    def rag_query(self, query: str, top_k: int = 3) -> Dict[str, Any]:

        results = self.collection.query(query_texts=[query], n_results=top_k)

        hits = []         

        docs = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]
        metadatas = results.get("metadatas",[[]])[0]
        distances = results.get("distances",[[]])[0]

        for i in range(len(docs)):
            hits.append({
                "id":ids[i],
                "document" : docs[i],
                "metadata" : metadatas[i],
                "distance" : float(distances[i]) if i < len(distances) else None
            })
        
        context_parts = []
        for h in hits:
            snippet = h["document"]
            context_parts.append(f"[id={h['id']}] {snippet}")
        
        context = "\n\n".join(context_parts) if context_parts else "No context found"

        return {
            "query" : query,
            "top_k" : top_k,
            "context" : context,
            "hits" : hits
        }
