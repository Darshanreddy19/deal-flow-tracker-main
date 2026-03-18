import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models
from brain import LLM
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import MODEL_NAME, dim_size

def upsert_to_qdrant(payload: dict):
    """
    Takes the deal analysis payload, chunks it, generates embeddings, 
    and stores it in Qdrant.
    """
    # 1. Initialize Gemini/GigaChat Embeddings
    llm_factory = LLM(provider=MODEL_NAME)
    embeddings_model = llm_factory.get_embedding_model()
    
    # 2. Initialize Qdrant Client
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"), 
        api_key=os.getenv("QDRANT_API_KEY")
    )
    
    collection_name = "deal_summaries"
    text_to_vectorize = payload["content"]

    # 3. Chunk the text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=400
    )
    chunks = text_splitter.split_text(text_to_vectorize)
    
    points_to_upsert = []
    dim = None

    # 4. Process chunks and format points
    for i, chunk in enumerate(chunks):
        vector = embeddings_model.embed_query(chunk)
        
        # Set collection dimensions based on the first vector
        if dim is None:
            dim = len(vector)
            if client.collection_exists(collection_name):
                collection_info = client.get_collection(collection_name)
                current_dim = collection_info.config.params.vectors.size
                if current_dim != dim:
                    print(f"Dimension mismatch: collection has {current_dim}, vector has {dim}. Recreating collection.")
                    client.delete_collection(collection_name)
                    client.create_collection(
                        collection_name=collection_name,
                        vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
                    )
            else:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
                )

        points_to_upsert.append(
            models.PointStruct(
                id=str(uuid.uuid4()), 
                vector=vector,
                payload={**payload["metadata"], "text": chunk, "chunk_index": i} 
            )
        )

    # 5. Upsert into Qdrant
    if points_to_upsert:
        client.upsert(
            collection_name=collection_name,
            points=points_to_upsert
        )
    print(f"Successfully upserted {len(chunks)} chunks for Deal {payload['metadata']['deal_id']} to Qdrant.")

# --- Integration Example ---
if __name__ == "__main__":
    # This is the result from our previous 'summary_generation' function
    sample_payload = {
        "content": "MedCorp Moscow and BioPharma Mumbai are stuck on INR-RUB rates.",
        "metadata": {
            "deal_id": "IND-RUS-2026-0042",
            "sector": "Pharmaceuticals",
            "fingerprints": ["CurrencyRisk", "SberbankHedging"],
            "risk_level": "High",
            "recommended_action": "Propose FX-Option-B"
        }
    }
    
    upsert_to_qdrant(sample_payload)